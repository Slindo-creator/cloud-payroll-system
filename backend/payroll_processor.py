import os
import sys

import psycopg2


def get_db_connection():
    """
    Connects to the database using environment variables.
    If variables are missing, it safely falls back to your local settings.
    """
    try:
        return psycopg2.connect(
            # On AWS, these look for the cloud credentials. On your PC, they use the defaults.
            host=os.environ.get("DB_HOST", "localhost"),
            database=os.environ.get("DB_NAME", "payroll_db"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "Slindo04"),
            port=os.environ.get("DB_PORT", "5432")
        )
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed! Check your credentials.\nError: {e}")
        sys.exit(1)
    
def calculate_and_save_payroll():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Fetch all employees from the database
        cur.execute("SELECT id, first_name, last_name, base_salary, hourly_rate FROM employees;")
        employees = cur.fetchall()
        
        if not employees:
            print("⚠️ No employees found in the database.")
            return
        
        print(f"--- Starting Payroll Process for {len(employees)} Employees ---")
        
        for emp in employees:
            emp_id, first_name, last_name, base_salary, hourly_rate = emp
            gross_pay = 0.00
            
            # 2. Logic for Salaried Employees
            if float(hourly_rate) == 0.00:
                # Calculates standard monthly income from their annual base salary rate
                gross_pay = float(base_salary) / 12.0
                print(f"Processing Salaried: {first_name} {last_name} | Monthly Gross: R{gross_pay:.2f}")
            
            # 3. Logic for Hourly Employees (Requires looking up their timecard)
            else:
                cur.execute("""
                    SELECT regular_hours_worked, overtime_hours_worked 
                    FROM timecards 
                    WHERE employee_id = %s AND is_approved = TRUE;
                """, (emp_id,))
                timecard = cur.fetchone()
                
                if timecard:
                    reg_hours, ot_hours = float(timecard[0]), float(timecard[1])
                    # Standard hours plus time-and-a-half (1.5x) for overtime hours
                    gross_pay = (reg_hours * float(hourly_rate)) + (ot_hours * float(hourly_rate) * 1.5)
                    print(f"Processing Hourly: {first_name} {last_name} | Hours: {reg_hours+ot_hours} | Gross: R{gross_pay:.2f}")
                else:
                    print(f"Skipping Hourly: {first_name} {last_name} (No approved timecard found)")
                    continue
            
            # 4. Standard structural taxation rate placeholder (20%)
            tax_deductions = round(gross_pay * 0.20, 2)
            net_pay = round(gross_pay - tax_deductions, 2)
            
            # 5. Insert calculations into the historical pay_runs ledger
            cur.execute("""
                INSERT INTO pay_runs (employee_id, gross_pay, tax_deductions, net_pay, status)
                VALUES (%s, %s, %s, %s, 'Processed');
            """, (emp_id, gross_pay, tax_deductions, net_pay))
            
        # Commit the transaction data to the tables safely
        conn.commit()
        print("--- Payroll Completed and Logged to Ledger Successfully! ---")
        
    except Exception as e:
        print(f"❌ Error processing payroll calculation: {str(e)}")
        if conn:
            conn.rollback() # Safely undo changes if something breaks mid-loop
            
    finally:
        # Guarantee that connections close even if an error occurs
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    calculate_and_save_payroll()
