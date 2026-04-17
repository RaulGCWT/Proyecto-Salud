from src.database import table_devices
from src.lambda_handlers.common import get_owner_id, parse_body, response


def get_devices(event, context):
    items = table_devices.scan().get("Items", [])
    owner_id = get_owner_id(event)
    role = str((event.get("headers") or {}).get("x-role") or (event.get("headers") or {}).get("X-Role") or "").strip().lower()
    residence_id = str((event.get("headers") or {}).get("x-residence-id") or (event.get("headers") or {}).get("X-Residence-Id") or "").strip()
    area = str((event.get("headers") or {}).get("x-area") or (event.get("headers") or {}).get("X-Area") or "").strip().lower()
    resident_id = str((event.get("headers") or {}).get("x-resident-id") or (event.get("headers") or {}).get("X-Resident-Id") or "").strip()
    device_ids_header = str((event.get("headers") or {}).get("x-device-ids") or (event.get("headers") or {}).get("X-Device-Ids") or "").strip()

    staff_roles = {"admin", "technician", "clinician", "members"}
    if role in staff_roles or not any([owner_id, residence_id, area, resident_id, device_ids_header]):
        return response(200, items)

    allowed_device_ids = {
        device_id.strip().lower()
        for device_id in device_ids_header.split(",")
        if device_id.strip()
    }

    filtered_items = []
    for item in items:
        item_device_id = str(item.get("deviceId") or item.get("id") or item.get("mac") or "").strip().lower()
        item_residence_id = str(item.get("residenceId") or "").strip()
        item_area = str(item.get("area") or "").strip().lower()
        item_resident_id = str(item.get("residentId") or "").strip()

        if owner_id and str(item.get("ownerId") or "") == str(owner_id):
            filtered_items.append(item)
            continue

        if residence_id and item_residence_id == residence_id:
            filtered_items.append(item)
            continue

        if area and item_area == area:
            filtered_items.append(item)
            continue

        if resident_id and item_resident_id == resident_id:
            filtered_items.append(item)
            continue

        if allowed_device_ids and item_device_id in allowed_device_ids:
            filtered_items.append(item)

    return response(200, filtered_items)


def save_device(event, context):
    body = parse_body(event)
    headers = event.get("headers") or {}
    device_id = str((body.get("mac") or body.get("id") or "").strip().lower())
    if not device_id:
        return response(400, {"error": "Device id is required"})

    owner_id = body.get("ownerId") or headers.get("x-owner-id") or headers.get("X-Owner-Id") or ""
    tenant_key = body.get("tenantKey") or headers.get("x-tenant-key") or headers.get("X-Tenant-Key") or ""
    residence_id = body.get("residenceId") or headers.get("x-residence-id") or headers.get("X-Residence-Id") or ""
    area = body.get("area") or headers.get("x-area") or headers.get("X-Area") or ""
    resident_id = body.get("residentId") or headers.get("x-resident-id") or headers.get("X-Resident-Id") or ""

    device = {
        "id": device_id,
        "mac": device_id,
        "name": body.get("name") or f"Bed-{device_id[-5:]}",
        "type": body.get("type") or "Standard",
        "ownerId": owner_id,
        "tenantKey": tenant_key,
        "residenceId": residence_id,
        "area": area,
        "residentId": resident_id,
    }

    table_devices.put_item(Item=device)
    return response(201, device)


def update_device(event, context):
    device_id = (event.get("pathParameters") or {}).get("device_id")
    if not device_id:
        return response(400, {"error": "device_id is required"})

    body = parse_body(event)
    headers = event.get("headers") or {}
    current_id = str(device_id).strip().lower()
    name = (body.get("name") or "").strip()
    if not name:
        return response(400, {"error": "Device name is required"})

    owner_id = body.get("ownerId") or headers.get("x-owner-id") or headers.get("X-Owner-Id") or ""
    tenant_key = body.get("tenantKey") or headers.get("x-tenant-key") or headers.get("X-Tenant-Key") or ""
    residence_id = body.get("residenceId") or headers.get("x-residence-id") or headers.get("X-Residence-Id") or ""
    area = body.get("area") or headers.get("x-area") or headers.get("X-Area") or ""
    resident_id = body.get("residentId") or headers.get("x-resident-id") or headers.get("X-Resident-Id") or ""

    response_data = table_devices.update_item(
        Key={"id": current_id},
        UpdateExpression="SET #n = :n, #t = :t, #m = :m, #owner = :owner, #tenant = :tenant, #residence = :residence, #area = :area, #resident = :resident",
        ExpressionAttributeNames={
            "#n": "name",
            "#t": "type",
            "#m": "mac",
            "#owner": "ownerId",
            "#tenant": "tenantKey",
            "#residence": "residenceId",
            "#area": "area",
            "#resident": "residentId",
        },
        ExpressionAttributeValues={
            ":n": name,
            ":t": body.get("type") or "Standard",
            ":m": current_id,
            ":owner": owner_id,
            ":tenant": tenant_key,
            ":residence": residence_id,
            ":area": area,
            ":resident": resident_id,
        },
        ReturnValues="ALL_NEW",
    )

    return response(200, response_data.get("Attributes", {"id": current_id}))
