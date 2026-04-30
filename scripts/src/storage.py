import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from src.database import AWS_REGION, DYNAMODB_URL, _read_str_env


TELEMETRY_BUCKET_NAME = _read_str_env("TELEMETRY_BUCKET_NAME", "welltech-telemetry-history")
S3_ENDPOINT_URL = _read_str_env("S3_ENDPOINT_URL", DYNAMODB_URL)


def _build_s3_client():
    # En local usamos el mismo endpoint que DynamoDB porque LocalStack expone ambos servicios ahí.
    kwargs = {
        "region_name": AWS_REGION,
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", "local"),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", "local"),
    }

    if S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = S3_ENDPOINT_URL

    return boto3.client("s3", **kwargs)


local_s3 = _build_s3_client()


def init_storage():
    # Solo preparamos el bucket en el almacenamiento local para no interferir con un despliegue real.
    try:
        local_s3.head_bucket(Bucket=TELEMETRY_BUCKET_NAME)
        return
    except ClientError as error:
        error_code = str(error.response.get("Error", {}).get("Code") or "")
        if error_code not in {"404", "NoSuchBucket", "NotFound"}:
            raise

    create_kwargs = {"Bucket": TELEMETRY_BUCKET_NAME}
    if AWS_REGION and AWS_REGION != "us-east-1":
        create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": AWS_REGION}

    local_s3.create_bucket(**create_kwargs)
    print(f"Bucket created: {TELEMETRY_BUCKET_NAME}")


def save_telemetry_batch(normalized_payload):
    if not normalized_payload:
        return None

    readings = normalized_payload.get("readings") or []
    if not readings:
        return None

    mac = str(normalized_payload.get("mac") or "unknown").strip().lower()
    device_id = str(normalized_payload.get("deviceId") or mac or "unknown").strip()
    device_type = str(normalized_payload.get("deviceType") or "Standard").strip()
    layout = str(normalized_payload.get("layout") or "single").strip().lower()
    batch_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    date_prefix = now.strftime("%Y-%m-%d")
    object_key = (
        f"telemetry/date={date_prefix}/"
        f"deviceId={device_id}/"
        f"mac={mac}/"
        f"batch-{batch_id}.json"
    )

    payload = {
        "id": batch_id,
        "mac": mac,
        "deviceId": device_id,
        "deviceType": device_type,
        "layout": layout,
        "receivedAt": now.isoformat(),
        "readings": readings,
    }

    local_s3.put_object(
        Bucket=TELEMETRY_BUCKET_NAME,
        Key=object_key,
        Body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Telemetry batch stored in S3: s3://{TELEMETRY_BUCKET_NAME}/{object_key}")
    return object_key
