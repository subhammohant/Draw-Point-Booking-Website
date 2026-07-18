import sqlite3 
import os          
from flask import Flask,request,render_template,redirect,session,url_for
from werkzeug.security import generate_password_hash,check_password_hash  
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException




app=Flask(__name__)
app.secret_key="sihwfjbwfvjedghewvyh26746388ur9bvn@jhfryjbuf7w7bvy2_+++ubej"



#DATABASE FOR BOOKING WEBSITE
DATABASE="database/art_booking.db"


def create_database():
    conn =sqlite3.connect(DATABASE)
    cur = conn.cursor()
    
    #USERSTABLE
    cur.execute('''
                CREATE TABLE IF NOT EXISTS USER(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                    )''')
    
    #PRICING 
    cur.execute('''
                CREATE TABLE IF NOT EXISTS PRICING(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT  NOT NULL,
                    art_type TEXT UNIQUE NOT NULL,
                    style TEXT ,
                    min_price INTEGER,
                    max_price INTEGER)''')
    #BOOKINGS
    cur.execute('''
                CREATE TABLE IF NOT EXISTS BOOKINGS(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    booking_id TEXT UNIQUE,
                    user_id INTEGER NOT NULL,
                    pricing_id INTEGER NOT NULL,
                    art_type TEXT,
                    style TEXT NOT NULL,
                    description TEXT,
                    booking_date TEXT,
                    time_slot TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    email_SENT INTEGER DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES USER(id),
                    FOREIGN KEY (pricing_id) REFERENCES PRICING(id))''')
    
    conn.commit()
    conn.close()
    
#create home page route 
@app.route("/")

def index():
    
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    return render_template("index.html")

#---------------------------xxxxxxxxxxxxxxxxxxxxxx--------------------------------------------------------

# Registration route
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn =sqlite3.connect(DATABASE)
        cur =conn.cursor()
        
        try:
            cur.execute('''INSERT INTO USER(name,email,password) VALUES(?,?,?)''',(name,email,hashed_password))
            conn.commit()
            
        except sqlite3.IntegrityError:
            return "Email already exists"
        finally:
            conn.close()
        
        return redirect(url_for("login"))
    return render_template("register.html")


#Login route
@app.route("/login",methods=["GET","POST"])

def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        
        cur.execute("SELECT id, password FROM USER WHERE email=?",(email,))
        
        user = cur.fetchone()
        conn.close()
        
        if (user and check_password_hash(user[1],password)):
            session["user_id"]=user[0]
            
            print("Logged in user_id:", user[0])

            cur.execute("SELECT id, name, email FROM USER")
            print("Users in DB:", cur.fetchall())
            
            return redirect(url_for('index'))
        else:
            return "invalid email id"
        
    return render_template("login.html")

#logout route / session end route 

@app.route("/logout")
def logout():
    session.clear()
    
    return redirect(url_for("login"))         



#Pricing Route 

@app.route("/pricing")
def pricing():
    conn = sqlite3.connect(DATABASE)
    cur=conn.cursor()
    
    cur.execute("""
                SELECT category,art_type,style,min_price,max_price FROM PRICING""")
    
    prices = cur.fetchall()
    conn.close()
    
    return render_template("pricing.html",prices=prices)


#booking route 

@app.route("/booking",methods=["GET","POST"])
def booking():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    
    if request.method == "POST":
        pricing_id = request.form["pricing_id"]
        description = request.form["description"]
        booking_date = request.form["booking_date"]
        time_slot = request.form["time_slot"]
        print("pricing id recieved",pricing_id)
        
        cur.execute("SELECT art_type,style FROM PRICING WHERE id=?",(pricing_id,))
        data = cur.fetchone()
        art_type=data[0]
        style=data[1]
        
        #insert booking into BOOKINGS table
        cur.execute("""
                    INSERT INTO BOOKINGS(user_id,pricing_id,art_type,style,description,booking_date,time_slot) VALUES(?,?,?,?,?,?,?)""",
                    (session["user_id"],pricing_id,art_type,style,description,booking_date,time_slot))
        conn.commit()
        
        booking_id = cur.lastrowid
        booking_reference = f"ART{booking_id:04d}"
        
        print("booking id generated",booking_reference)
        
        #debug session 
        print("Session user id",session.get("user_id"))
        #get user email 
        cur.execute("SELECT email FROM USER WHERE id=?",(session["user_id"],))
        result = cur.fetchone()
        print("Query result",result)
        
        #show all users 
        cur.execute("SELECT id, name, email FROM USER")
        print("Users in DB:", cur.fetchall())
        
        if result is None:
            print("No user found with the given ID.")
            conn.close()
            return "User not found",400
        
        user_email = result[0]
        print("User email retrieved:", user_email)
        
        
        #send confirmation email
        send_email(user_email, booking_reference, art_type, style)
        
        return render_template("confirmation.html",booking_reference=booking_reference)
    
    
    
    cur.execute("""SELECT id, category, art_type, style, min_price, max_price FROM PRICING""")
    
    artwork = cur.fetchall()
    
    conn.close()
    
    
    return render_template("booking.html",artwork=artwork)





#Gallery route 
@app.route("/gallery")
def gallery():
    
    return render_template("gallery.html")


#Email sending function 

def send_email(receiver_mail, booking_id, art_type, style):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.environ["API_KEY"]

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    sender = {
        "name": "DrawPoint",
        "email": "subhammohanty397@gmail.com"
    }

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": receiver_mail}],
        sender=sender,
        subject="Booking Confirmation - DrawPoint",
        html_content=f"""
        <h2>Booking Confirmed!</h2>

        <p>Thank you for booking with DrawPoint.</p>

        <p><strong>Booking ID:</strong> {booking_id}</p>
        <p><strong>Art Type:</strong> {art_type}</p>
        <p><strong>Style:</strong> {style}</p>

        <p>Status: Pending</p>
        """
    )

    try:
        api_instance.send_transac_email(email)
        print("Email sent successfully")

    except ApiException as e:
        print("Brevo Error:", e)
    
      
    
   
#------------------------------------------xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx----------------------------------------

#App run code



if __name__ == '__main__':
    os.makedirs('database',exist_ok=True)
    create_database()
    app.run(debug=True)



             