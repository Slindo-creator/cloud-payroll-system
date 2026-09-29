# Cloud Payroll System

A cloud-based payroll processing pipeline that stores employee and payroll data in **AWS RDS PostgreSQL**, calculates employee pay, generates professional PDF payslips, and securely uploads the generated documents to **Amazon S3**.

This project demonstrates an end-to-end cloud workflow using **Python, PostgreSQL, AWS RDS, AWS S3, ReportLab, SQL, boto3, and environment-based credential management**.

---

## Architecture

The system consists of four main components:

```text
                         ┌──────────────────────┐
                         │   Employee & Pay     │
                         │        Data          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      AWS RDS         │
                         │     PostgreSQL       │
                         │                      │
                         │  Employees           │
                         │  Pay Runs            │
                         │  Payroll Records     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ payroll_processor.py │
                         │                      │
                         │  Gross Pay           │
                         │  Tax                 │
                         │  Net Pay             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ payslip_generator.py │
                         │                      │
                         │  SQL Queries/Joins   │
                         │  ReportLab PDFs      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       AWS S3         │
                         │                      │
                         │  PDF Payslips        │
                         │  Cloud Storage       │
                         └──────────────────────┘
```

# Project Structure

```text
cloud-payroll-system/
│
├── backend/
│   ├── .env                  # Not committed to GitHub
│   ├── payroll_processor.py
│   ├── payslip_generator.py
│   ├── requirements.txt
│   └── ...
│
├── payslip_pdfs/
│   ├── sample_payslip_1.pdf
│   ├── sample_payslip_2.pdf
│   └── ...
│
├── .gitignore
└── README.md
```





### Components

| Component                  | Purpose                                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **AWS RDS PostgreSQL**     | Stores employee, pay run, payroll, and related payroll data                                                        |
| **`payroll_processor.py`** | Reads workforce data, calculates gross pay, tax, and net pay, then writes the results to PostgreSQL                |
| **`payslip_generator.py`** | Retrieves payroll data using SQL queries and joins, generates PDF payslips using ReportLab, and uploads them to S3 |
| **AWS S3**                 | Stores generated PDF payslips in cloud object storage                                                              |

---

#  Technologies Used

* **Python**
* **PostgreSQL**
* **Amazon RDS**
* **Amazon S3**
* **boto3**
* **ReportLab**
* **psycopg2**
* **python-dotenv**
* **SQL**
* **Git / GitHub**

---

# Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/Slindo-creator/cloud-payroll-system.git
cd cloud-payroll-system/backend
```

---

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Install Dependencies

The repository includes a `requirements.txt` file containing all required Python dependencies.

```bash
pip install -r requirements.txt
```

---

# 4. Configure the `.env` File

> ** IMPORTANT — GRADING / REVIEW**
>
> The `.env` file is **intentionally not included in this public GitHub repository**.
>
> It contains sensitive credentials required to connect to the **AWS RDS PostgreSQL database** and **AWS services**. Committing these credentials to a public repository would expose live cloud infrastructure credentials.
>
> The required `.env` file has therefore been shared separately via Google Drive.

### Where to find the `.env` file

```text
Google Drive
└── CyberSecurity
    └── env file
```

Download the provided `env file` and place it inside the project's `backend/` directory.

The expected structure is:

```text
cloud-payroll-system/
└── backend/
    ├── .env
    ├── payroll_processor.py
    ├── payslip_generator.py
    ├── requirements.txt
    └── ...
```

### Environment Variables

The `.env` file contains the configuration required by the application:

```env
DB_HOST=your-db-instance.xxxxxxxxxx.af-south-1.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password

AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

The actual credential values are provided in the separately shared `.env` file.

**Do not commit the `.env` file to GitHub.**

---

## Loading Environment Variables

### macOS / Linux

```bash
export $(grep -v '^#' .env | xargs)
```

### Windows PowerShell

```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable(
            $matches[1].Trim(),
            $matches[2].Trim()
        )
    }
}
```

### AWS CLI Alternative

AWS credentials can alternatively be configured using:

```bash
aws configure
```

`boto3` can then retrieve the credentials from the AWS CLI credential configuration.

---

# 5. AWS RDS Database Configuration

The payroll system uses **PostgreSQL hosted on Amazon RDS**.

The RDS Security Group controls access to the database.


`

## Security Consideration

`0.0.0.0/0` allows connections from any IPv4 address and is **not recommended for a production database i used it to allows access temporary**.


# 7. Run the Payroll Pipeline

The application is executed in two stages.

## Step 1 — Process Payroll

Run:

```bash
python payroll_processor.py
```

The payroll processor:

1. Connects to the AWS RDS PostgreSQL database.
2. Reads employee and pay information.
3. Calculates gross pay.
4. Calculates tax.
5. Calculates net pay.
6. Writes the calculated payroll records to the database.

---

## Step 2 — Generate and Upload Payslips

Run:

```bash
python payslip_generator.py
```

The payslip generator:

1. Connects to the PostgreSQL database.
2. Retrieves payroll information using SQL queries and joins.
3. Generates professional PDF payslips using **ReportLab**.
4. Uploads each PDF to **Amazon S3**.
5. Removes the temporary local PDF after successful upload.

A successful upload produces output similar to:

```text
Cloud Saved: s3://employee-payslips-project/2026/may/payslip_employee_name.pdf
```

---

#  8. Payslip Storage

Generated payslips are stored in Amazon S3 using a structured path:

```text
s3://employee-payslips-project/
└── 2026/
    └── may/
        ├── payslip_employee_1.pdf
        ├── payslip_employee_2.pdf
        └── payslip_employee_3.pdf
```

The generated PDFs are uploaded to S3 and then removed from local disk after successful processing.

---

#  9. Sample Payslips for Review

For grading and review purposes, pre-downloaded sample payslips are included in:

```text
payslip_pdfs/
```

These files allow the generated PDF documents to be viewed directly without requiring the reviewer to access AWS.

The AWS credentials themselves are **not included in the public GitHub repository**.

---

# 10. Download Payslips from S3

If you have your own AWS credentials and want to retrieve the generated payslips directly from S3, the following Python example can be used:

```python
import boto3

s3 = boto3.client("s3")

bucket = "employee-payslips-project"
prefix = "2026/may/"

response = s3.list_objects_v2(
    Bucket=bucket,
    Prefix=prefix
)

for obj in response.get("Contents", []):
    key = obj["Key"]
    filename = key.split("/")[-1]

    s3.download_file(
        bucket,
        key,
        filename
    )

    print(f"Downloaded: {filename}")
```

---

**verification code - WTC-TZZR6J2F**

Cloud Payroll System Demo — (youtubelink)
