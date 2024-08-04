import io
import json
from datetime import datetime
from typing import Any

import boto3
import qrcode

s3 = boto3.resource("s3")
bucket = s3.Bucket("bucket-djsklfh34ltn85439erhgjwe")


def qr_handler(event, _) -> dict[str, Any]:
    try:
        data = json.loads(event["body"])
        if not (to_encode := data["toEncode"]):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "No data provided"}),
            }

        buffer = io.BytesIO()

        qr_code = qrcode.make(to_encode)
        qr_code.save(buffer)

        key = f"qr-codes/{datetime.now().isoformat(timespec="seconds")}.png"
        bucket.put_object(
            Key=key,
            Body=buffer.getvalue(),
            ContentType="image/png",
            ACL="public-read",
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "QR code generated",
                    "link": f"https://bucket-djsklfh34ltn85439erhgjwe.s3.amazonaws.com/{key}",
                },
            ),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": str(e)}),
        }
