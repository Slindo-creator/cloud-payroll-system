cat > check_db.py << 'EOF'
import psycopg2

conn = psycopg2.connect(
    host='payroll-db.c8jywgqc8s6z.us-east-1.rds.amazonaws.com',
    database='postgres',
    user='postgres',
    password='PasswordDatabase432',
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
EOF