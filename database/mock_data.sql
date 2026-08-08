INSERT INTO employees (first_name, last_name, email, cognito_sub, role, base_salary, hourly_rate)
VALUES (
    'Slindile', 
    'Zondo', 
    'slindile.zondo@company.com', 
    '11111111-1111-1111-1111-111111111111', 
    'HR_Admin', 
    60000.00, 
    0.00
);

INSERT INTO employees (first_name, last_name, email, cognito_sub, role, base_salary, hourly_rate)
VALUES (
    'Robby', 
    'Smith', 
    'robby.smith@company.com', 
    '22222222-2222-2222-2222-222222222222', 
    'Employee', 
    0.00, 
    25.50
);

INSERT INTO timecards (employee_id, pay_period_start, pay_period_end, regular_hours_worked, overtime_hours_worked, is_approved)
VALUES (
    (SELECT id FROM employees WHERE email = 'slindile.zondo@company.com'),
    '2026-03-01',
    '2026-03-14',
    80.00,
    10.50,
    TRUE
);

