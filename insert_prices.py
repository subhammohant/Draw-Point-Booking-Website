import os

import psycopg2

DATABASE_URL=os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

prices =[
    ("Academic","Lab Drawing","pencil",10,10),
    ("Academic","Engineering Drawing(EDG)","Custom",60,180),
    ("Non-Academic(Observational)","portrait","pencil shading",250,250),
    ("Non-Academic(Observational)","Landscape","pencil",250,250),
    ("Non-Academic(Observational)","Landscape-2","coloured",350,350),
    ("Comic/Manga","Normal shading","pencil",100,100),
    ("Comic/manga","Higher Shading","pencil",200,200),
    ("Comic/Manga","Colured","full colour",300,300)
]

cur.executemany("""
                INSERT INTO PRICING(
                    category,art_type,style,min_price,max_price)
                    VALUES(%s,%s,%s,%s,%s)""",prices)

conn.commit()
conn.close()

print("Prices added successfully")


