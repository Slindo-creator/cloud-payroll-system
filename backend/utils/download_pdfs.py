import boto3

s3 = boto3.client('s3')

with open('keys.txt') as f:
    keys = [line.strip() for line in f if line.strip()]

print(f"Found {len(keys)} keys to download")

for key in keys:
    filename = key.split('/')[-1]
    try:
        s3.download_file('employee-payslips-project', key, filename)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"FAILED on {key}: {e}")

print("Done")
