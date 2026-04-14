import os
from decimal import Decimal

import boto3


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")
USE_AWS_DYNAMODB = os.environ.get("USE_AWS_DYNAMODB", "false").strip().lower() == "true"
USE_AWS_ALERTS_TABLE = os.environ.get("USE_AWS_ALERTS_TABLE", "false").strip().lower() == "true"
DYNAMODB_URL = os.environ.get("DYNAMODB_URL", "").strip()

RULES_TABLE_NAME = os.environ.get("RULES_TABLE_NAME", "MonitoringRules")
ALERTS_TABLE_NAME = os.environ.get("ALERTS_TABLE_NAME", "DeviceEvents")
DEVICES_TABLE_NAME = os.environ.get("DEVICES_TABLE_NAME", "Devices")
INVITES_TABLE_NAME = os.environ.get("INVITES_TABLE_NAME", "FamilyInvites")
FAMILY_USERS_TABLE_NAME = os.environ.get("FAMILY_USERS_TABLE_NAME", "FamilyUsers")
RESIDENTS_TABLE_NAME = os.environ.get("RESIDENTS_TABLE_NAME", "Residents")
STAFF_TABLE_NAME = os.environ.get("STAFF_TABLE_NAME", "StaffMembers")


def _build_local_dynamodb_resource():
    endpoint = DYNAMODB_URL or "http://localhost:8000"
    return boto3.resource(
        "dynamodb",
        endpoint_url=endpoint,
        region_name="us-east-1",
        aws_access_key_id="local",
        aws_secret_access_key="local",
    )


def _build_aws_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)


local_dynamodb = _build_local_dynamodb_resource()
aws_dynamodb = _build_aws_dynamodb_resource()


if USE_AWS_DYNAMODB:
    # Full AWS mode: all tables from AWS DynamoDB.
    table_rules = aws_dynamodb.Table(RULES_TABLE_NAME)
    table_events = aws_dynamodb.Table(ALERTS_TABLE_NAME)
    table_devices = aws_dynamodb.Table(DEVICES_TABLE_NAME)
    table_invites = aws_dynamodb.Table(INVITES_TABLE_NAME)
    table_family_users = aws_dynamodb.Table(FAMILY_USERS_TABLE_NAME)
    table_residents = aws_dynamodb.Table(RESIDENTS_TABLE_NAME)
    table_staff_members = aws_dynamodb.Table(STAFF_TABLE_NAME)
elif USE_AWS_ALERTS_TABLE:
    # Hybrid mode: everything local except alerts table in AWS.
    table_rules = local_dynamodb.Table(RULES_TABLE_NAME)
    table_events = aws_dynamodb.Table(ALERTS_TABLE_NAME)
    table_devices = local_dynamodb.Table(DEVICES_TABLE_NAME)
    table_invites = local_dynamodb.Table(INVITES_TABLE_NAME)
    table_family_users = local_dynamodb.Table(FAMILY_USERS_TABLE_NAME)
    table_residents = local_dynamodb.Table(RESIDENTS_TABLE_NAME)
    table_staff_members = local_dynamodb.Table(STAFF_TABLE_NAME)
else:
    # Local mode.
    table_rules = local_dynamodb.Table(RULES_TABLE_NAME)
    table_events = local_dynamodb.Table(ALERTS_TABLE_NAME)
    table_devices = local_dynamodb.Table(DEVICES_TABLE_NAME)
    table_invites = local_dynamodb.Table(INVITES_TABLE_NAME)
    table_family_users = local_dynamodb.Table(FAMILY_USERS_TABLE_NAME)
    table_residents = local_dynamodb.Table(RESIDENTS_TABLE_NAME)
    table_staff_members = local_dynamodb.Table(STAFF_TABLE_NAME)


def init_db():
    # In full AWS mode we do not auto-create tables.
    if USE_AWS_DYNAMODB:
        print("USE_AWS_DYNAMODB=true: skipping local table auto-creation.")
        return

    # In hybrid mode we still auto-create local tables, except alerts.
    local_tables_to_create = {
        RULES_TABLE_NAME,
        DEVICES_TABLE_NAME,
        INVITES_TABLE_NAME,
        FAMILY_USERS_TABLE_NAME,
        RESIDENTS_TABLE_NAME,
        STAFF_TABLE_NAME,
    }
    if not USE_AWS_ALERTS_TABLE:
        local_tables_to_create.add(ALERTS_TABLE_NAME)

    for t_name in local_tables_to_create:
        try:
            local_dynamodb.create_table(
                TableName=t_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )
            print(f"Table created: {t_name}")
        except Exception:
            pass
