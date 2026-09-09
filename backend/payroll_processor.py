import os
import sys
import psycopg2

def get_db_connection():
    """Connects using system environment variables with an automatic local fallback."""
    try:
        return psycopg2.connect(
            host="payroll-db.c8jywgqc8s6z.us-east-1.rds.amazonaws.com",
            database="postgres",
            user="postgres",
            password="PasswordDatabase432",
            sslmode="require"e AWS streaming data
        )
    except psycopg2.OperationalError as e:
        print(f" Database connection failed: {e}")
        sys.exit(1)
    
def calculate_and_save_payroll():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Fetching columns explicitly to match your updated schema array ordering
        cur.execute("SELECT id, first_name, last_name, base_salary, hourly_rate, role FROM employees;")
        employees = cur.fetchall()
        
        if not employees:
            print("No employee profiles found.")
            return
        
        print(f"\n--- Starting Cloud Payroll Processing for {len(employees)} Employees ---")
        
        for emp in employees:
            emp_id, first_name, last_name, base_salary, hourly_rate, role = emp
            gross_pay = 0.00
            
            # 2. Logic for Salaried Employees (Hourly rate is exactly zero)
            if float(hourly_rate) == 0.00:
                gross_pay = float(base_salary) / 12.0
                print(f"Salaried [{role}]: {first_name} {last_name} | Monthly Gross: R{gross_pay:.2f}")
            
            # 3. Logic for Hourly Employees (Pulls approved timecard metrics)
            else:
                cur.execute("""
                    SELECT regular_hours_worked, overtime_hours_worked 
                    FROM timecards 
                    WHERE employee_id = %s AND is_approved = TRUE;
                """, (emp_id,))
                timecard = cur.fetchone()
                
                if timecard:
                    reg_hours = float(timecard[0])
                    ot_hours = float(timecard[1])
                    # Basic calculation formulas adding 1.5x scaling multiplier for overtime work hours
                    gross_pay = (reg_hours * float(hourly_rate)) + (ot_hours * float(hourly_rate) * 1.5)
                    print(f" Hourly [{role}]: {first_name} {last_name} | Hours: {reg_hours + ot_hours} | Gross: R{gross_pay:.2f}")
                else:
                    print(f" Skipping Hourly [{role}]: {first_name} {last_name} (No approved timecards found)")
                    continue
            
            # 4. Payroll Deductions & Net Balances Calculation (20% flat tax)
            tax_deductions = round(gross_pay * 0.20, 2)
            net_pay = round(gross_pay - tax_deductions, 2)
            
            # 5. Commit record entries directly to the transactions log table
            cur.execute("""
                INSERT INTO pay_runs (employee_id, gross_pay, tax_deductions, net_pay, status)
                VALUES (%s, %s, %s, %s, 'Processed');
            """, (emp_id, gross_pay, tax_deductions, net_pay))
            
        conn.commit()
        print("---  Payroll Run Complete! Financial Ledger Records Saved Successfully. ---\n")
        
    except Exception as e:
        print(f" Core payroll script crash: {str(e)}")
        if conn:
            conn.rollback()
            
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    calculate_and_save_payroll()
