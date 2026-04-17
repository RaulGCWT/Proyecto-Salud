from datetime import datetime, timezone
import uuid


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def upsert_item(table, payload):
    item = dict(payload or {})
    item['id'] = item.get('id') or str(uuid.uuid4())
    table.put_item(Item=item)
    return item

