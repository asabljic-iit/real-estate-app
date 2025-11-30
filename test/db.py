import psycopg2
#pip3.9 install psycopg2-binary

# connect to the Database
conn = psycopg2.connect(host="localhost", 
                        database="university",
                        user="postgres", 
                        password="1234"
                        )


# cursor
cur = conn.cursor()

cur.execute("select * from instructor")

#rows = cur.fetchall()

for r in cur:
    print(f"id {r[0]} name {r[1]} dept {r[2]} salary {r[3]}")

# Close the cursor

cur.close()
# Close the Connection
conn.close()
