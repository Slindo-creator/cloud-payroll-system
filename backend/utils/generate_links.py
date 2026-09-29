
import boto3

with open("keys.txt") as f:
    keys = [line.strip() for line in f if line.strip()]

s3 = boto3.client("s3")

with open("payslip_links.txt", "w") as out:
    for key in keys:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": "employee-payslips-project", "Key": key},
            ExpiresIn=604800
        )
        out.write(f"{key}\n{url}\n\n")
        print(f"Linked: {key}")

print("Done")

