import psycopg2

conn = psycopg2.connect(
    host='payroll-db.c8jywgqc8s6z.us-east-1.rds.amazonaws.com',
    database='postgres',
    user='postgres',
    password='PasswordDatabase432',
    port=5432
)
cur = conn.cursor()
cur.execute('SELECT count(*) FROM employees;')
print('Local employee count:', cur.fetchone())
cur.execute('SELECT id, first_name, last_name, role FROM employees ORDER BY id;')
for row in cur.fetchall():
    print(row)
conn.close()
