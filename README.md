 Cloud Payroll System
 
A cloud-based payroll pipeline that stores employee and pay data in AWS RDS (PostgreSQL), calculates pay, generates professional PDF payslips, and uploads them securely to AWS S3.
 
## Architecture
 
1. **Relational Data Tier (AWS RDS PostgreSQL)** — stores employees, pay runs, and related payroll data.
2. **Calculation Engine (`payroll_processor.py`)** — reads workforce data, calculates gross/tax/net pay, and writes results to the database.
3. **Document Delivery Pipeline (`payslip_generator.py`)** — pulls pay records via SQL joins, builds PDF payslips using ReportLab, and uploads them to S3.
4. **Cloud Object Storage (AWS S3)** — stores the generated PDF payslips.
Credentials are never hardcoded — the app reads database and AWS credentials from environment variables at runtime.
 
---
 
## 1. Clone the Repository
 
```bash
git clone https://github.com/Slindo-creator/cloud-payroll-system.git
cd cloud-payroll-system/backend
```
 
## 2. Set Up a Virtual Environment
 
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```
 
## 3. Install Dependencies

A `requirements.txt` file is included in the repo — install everything from it:

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

A `.env` file containing the required credentials is included alongside this project (shared separately from the public repo, since it contains live secrets — never commit it to source control).

**`.env` file format** (already provided):
```
DB_HOST=your-db-instance.xxxxxxxxxx.af-south-1.rds.amazonaws.com
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-database-password
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

**To load it into your shell before running the scripts:**

macOS/Linux:
```bash
export $(grep -v '^#' .env | xargs)
```

Windows (PowerShell):
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
    }
}
```
### Notes on setup
 
- **Database access**: the RDS security group must allow inbound connections on port 5432 from your current IP. If you get a connection timeout, check **RDS → your instance → Connectivity & security → VPC security group → Inbound rules**, and add your IP (find it with `curl ifconfig.me`) or temporarily allow `0.0.0.0/0` for testing.
- **Connections are encrypted**: the app enforces `sslmode='require'` when connecting to Postgres.
- **AWS CLI (optional)**: if you'd rather not export AWS keys manually, run `aws configure` once and boto3 will pick up credentials automatically from `~/.aws/credentials`.
## 5. Run the Pipeline
 
```bash
# Calculate pay and write records to the database
python payroll_processor.py
 
# Generate PDF payslips and upload them to S3
python payslip_generator.py
```
 
On success, you'll see a line like this for each employee:
 
```
Cloud Saved: s3://employee-payslips-project/2026/may/payslip_employee_name.pdf
```
 
## 6. Accessing the Generated Payslips

The generated PDFs are uploaded to S3 and removed from local disk automatically after each run.

**For grading/review purposes**, a set of pre-downloaded sample payslips is included in the `payslip_pdfs/` folder of this submission, so they can be viewed directly without needing AWS access — actual AWS account credentials (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`) are not shared, for security reasons (they carry write access to live cloud infrastructure).

If you have your own AWS credentials and want to fetch the PDFs directly from S3 (e.g. after running the pipeline yourself against your own bucket), you can do so with:

```python
import boto3

s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket='employee-payslips-project', Prefix='2026/may/')

for obj in response.get('Contents', []):
    key = obj['Key']
    filename = key.split('/')[-1]
    s3.download_file('employee-payslips-project', key, filename)
    print(f"Downloaded: {filename}")
```

---

## Security Notes

- Credentials are injected via environment variables, never committed to source control.
- Database connections require SSL (`sslmode='require'`).
- The S3-uploading IAM user should be scoped to only the permissions it needs (`s3:PutObject`, `s3:GetObject`) on the specific bucket, rather than full account access.

verification code - WTC-TZZR6J2F
