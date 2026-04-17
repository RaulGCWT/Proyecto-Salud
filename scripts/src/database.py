import os
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def _read_bool_env(name, default=False):
    value = os.environ.get(name, str(default)).strip().lower()
    return value == "true"


def _read_str_env(name, default):
    value = os.environ.get(name, default)
    value = str(value).strip()
    return value or default


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

DYNAMODB_URL = _read_str_env("DYNAMODB_URL", "http://localhost:8000")
AWS_REGION = _read_str_env("AWS_REGION", "eu-west-1")
USE_AWS_DYNAMODB = _read_bool_env("USE_AWS_DYNAMODB", False)
USE_AWS_ALERTS_TABLE = _read_bool_env("USE_AWS_ALERTS_TABLE", False)

RULES_TABLE_NAME = _read_str_env("RULES_TABLE_NAME", "MonitoringRules")
ALERTS_TABLE_NAME = _read_str_env("ALERTS_TABLE_NAME", "DeviceEvents")
DEVICES_TABLE_NAME = _read_str_env("DEVICES_TABLE_NAME", "Devices")
INVITES_TABLE_NAME = _read_str_env("INVITES_TABLE_NAME", "FamilyInvites")
FAMILY_USERS_TABLE_NAME = _read_str_env("FAMILY_USERS_TABLE_NAME", "FamilyUsers")
RESIDENTS_TABLE_NAME = _read_str_env("RESIDENTS_TABLE_NAME", "Residents")
STAFF_TABLE_NAME = _read_str_env("STAFF_TABLE_NAME", "StaffMembers")

TABLE_NAMES = {
    "rules": RULES_TABLE_NAME,
    "events": ALERTS_TABLE_NAME,
    "devices": DEVICES_TABLE_NAME,
    "invites": INVITES_TABLE_NAME,
    "family_users": FAMILY_USERS_TABLE_NAME,
    "residents": RESIDENTS_TABLE_NAME,
    "staff_members": STAFF_TABLE_NAME,
}


# ---------------------------------------------------------------------------
# DynamoDB resources
# ---------------------------------------------------------------------------

def _build_local_dynamodb_resource():
    # Local mode uses a deterministic endpoint so the rest of the code can stay simple.
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


def _resolve_table_resource(table_name, use_aws=False):
    resource = aws_dynamodb if use_aws else local_dynamodb
    return resource.Table(table_name)


def _resolve_table_sources():
    # Full AWS mode: all tables come from AWS DynamoDB.
    if USE_AWS_DYNAMODB:
        return {
            "rules": _resolve_table_resource(TABLE_NAMES["rules"], use_aws=True),
            "events": _resolve_table_resource(TABLE_NAMES["events"], use_aws=True),
            "devices": _resolve_table_resource(TABLE_NAMES["devices"], use_aws=True),
            "invites": _resolve_table_resource(TABLE_NAMES["invites"], use_aws=True),
            "family_users": _resolve_table_resource(TABLE_NAMES["family_users"], use_aws=True),
            "residents": _resolve_table_resource(TABLE_NAMES["residents"], use_aws=True),
            "staff_members": _resolve_table_resource(TABLE_NAMES["staff_members"], use_aws=True),
        }

    # Hybrid mode: only alerts live in AWS, the rest stays local.
    if USE_AWS_ALERTS_TABLE:
        return {
            "rules": _resolve_table_resource(TABLE_NAMES["rules"]),
            "events": _resolve_table_resource(TABLE_NAMES["events"], use_aws=True),
            "devices": _resolve_table_resource(TABLE_NAMES["devices"]),
            "invites": _resolve_table_resource(TABLE_NAMES["invites"]),
            "family_users": _resolve_table_resource(TABLE_NAMES["family_users"]),
            "residents": _resolve_table_resource(TABLE_NAMES["residents"]),
            "staff_members": _resolve_table_resource(TABLE_NAMES["staff_members"]),
        }

    # Local mode: everything uses the local DynamoDB instance.
    return {
        "rules": _resolve_table_resource(TABLE_NAMES["rules"]),
        "events": _resolve_table_resource(TABLE_NAMES["events"]),
        "devices": _resolve_table_resource(TABLE_NAMES["devices"]),
        "invites": _resolve_table_resource(TABLE_NAMES["invites"]),
        "family_users": _resolve_table_resource(TABLE_NAMES["family_users"]),
        "residents": _resolve_table_resource(TABLE_NAMES["residents"]),
        "staff_members": _resolve_table_resource(TABLE_NAMES["staff_members"]),
    }


_resolved_tables = _resolve_table_sources()

table_rules = _resolved_tables["rules"]
table_events = _resolved_tables["events"]
table_devices = _resolved_tables["devices"]
table_invites = _resolved_tables["invites"]
table_family_users = _resolved_tables["family_users"]
table_residents = _resolved_tables["residents"]
table_staff_members = _resolved_tables["staff_members"]


def _create_table_if_missing(table_name):
    # We only auto-create tables in local mode, so a missing table should be fixed here.
    try:
        local_dynamodb.meta.client.describe_table(TableName=table_name)
        return
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")
        if error_code != "ResourceNotFoundException":
            raise

    local_dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    print(f"Table created: {table_name}")


def init_db():
    # In full AWS mode we do not auto-create local tables.
    if USE_AWS_DYNAMODB:
        print("USE_AWS_DYNAMODB=true: skipping local table auto-creation.")
        return

    # In hybrid mode we still auto-create local tables, except alerts.
    local_tables_to_create = {
        TABLE_NAMES["rules"],
        TABLE_NAMES["devices"],
        TABLE_NAMES["invites"],
        TABLE_NAMES["family_users"],
        TABLE_NAMES["residents"],
        TABLE_NAMES["staff_members"],
    }
    if not USE_AWS_ALERTS_TABLE:
        local_tables_to_create.add(TABLE_NAMES["events"])

    for table_name in sorted(local_tables_to_create):
        _create_table_if_missing(table_name)
