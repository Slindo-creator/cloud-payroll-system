import os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.environ['DB_HOST'],
    database=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD']
    sslmode='require'
)
cur = conn.cursor()
cur.execute('SELECT current_database(), inet_server_addr();')
print('Connected to:', cur.fetchone())
cur.execute('SELECT count(*) FROM employees;')
print('Employee count:', cur.fetchone())
cur.execute('SELECT id, first_name, last_name, role FROM employees ORDER BY id;')
for row in cur.fetchall():
    print(row)
conn.close()