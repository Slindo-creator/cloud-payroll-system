import os
from dotenv import load_dotenv
load_dotenv()

try:
    conn = psycopg2.connect(
       host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        sslmode='require'
    )
    cur = conn.cursor()

    cur.execute('TRUNCATE pay_runs, timecards, employees RESTART IDENTITY CASCADE;')

    employees_data = [
        ('Sandile', 'Ngwenya', 'sandile.ngwenya@properties.co.za', 'Site Manager', 420000.00, 0.00),
        ('Slindile', 'Zondo', 'slindile.zondo@properties.co.za', 'HR_Admin', 300000.00, 0.00),
        ('Thabo', 'Mokoena', 'thabo.mokoena@properties.co.za', 'Project Director', 720000.00, 0.00),
        ('Lungile', 'Dlamini', 'lungile.dlamini@properties.co.za', 'Safety Officer', 240000.00, 0.00),
        ('Robby', 'Smith', 'robby.smith@zproperties.co.za', 'Senior Site Manager', 540000.00, 0.00),
        ('Sipho', 'Khumalo', 'sipho.khumalo@properties.co.za', 'Electrician', 0.00, 150.00),
        ('Lerato', 'Nkosi', 'lerato.nkosi@properties.co.za', 'Plumber', 0.00, 145.00),
        ('Zama', 'Ndlovu', 'zama.ndlovu@properties.co.za', 'General Worker', 0.00, 85.00)
    ]

    for emp in employees_data:
        cur.execute('''
            INSERT INTO employees (first_name, last_name, email, cognito_sub, role, base_salary, hourly_rate)
            VALUES (%s, %s, %s, '11111111-1111-1111-1111-111111111111', %s, %s, %s);
        ''', emp)
        print(f"Inserted: {emp[0]} {emp[1]}")

    timecards_data = [
        ('sipho.khumalo@properties.co.za', 80.00, 12.50),
        ('lerato.nkosi@properties.co.za', 80.00, 5.00),
        ('zama.ndlovu@properties.co.za', 80.00, 22.00)
    ]

    for tc in timecards_data:
        cur.execute('''
            INSERT INTO timecards (employee_id, pay_period_start, pay_period_end, regular_hours_worked, overtime_hours_worked, is_approved)
            VALUES ((SELECT id FROM employees WHERE email = %s), '2026-05-01', '2026-05-14', %s, %s, TRUE);
        ''', tc)
        print(f"Timecard added for: {tc[0]}")

    conn.commit()
    print("\n Commit successful — 8 employees + timecards saved.")

    cur.execute('SELECT count(*) FROM employees;')
    print("Verified count immediately after commit:", cur.fetchone())

except Exception as e:
    print(f"\n SCRIPT FAILED: {e}")
    if 'conn' in locals():
        conn.rollback()
        print("Transaction rolled back — nothing was saved.")

finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()