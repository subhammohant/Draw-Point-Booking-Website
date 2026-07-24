import os

import psycopg2

DATABASE_URL=os.environ.get("postgresql://drawpoint_user:KWxwoMHOoOGKKC6Ggic4v4HN7NdrQpO3@dpg-d9hfjnkm0tmc73ap4oo0-a/drawpoint")

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


