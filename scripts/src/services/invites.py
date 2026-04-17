import secrets
import uuid
from datetime import datetime, timezone, timedelta

from werkzeug.security import generate_password_hash

from src.database import table_invites, table_family_users
from src.services.common import utc_now_iso

INVITE_PENDING = 'PENDING'
INVITE_ACCEPTED = 'ACCEPTED'
INVITE_EXPIRED = 'EXPIRED'
INVITE_CANCELLED = 'CANCELLED'
INVITE_REGISTERED = 'REGISTERED'
INVITE_VALID_DAYS = 7


def parse_iso_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None


def normalize_invitation_state(value):
    return str(value or '').strip().upper()


def get_invitation_state_change_error(invitation, new_state):
    normalized_new_state = normalize_invitation_state(new_state)
    current_state = normalize_invitation_state((invitation or {}).get('state'))

    if normalized_new_state not in {INVITE_PENDING, INVITE_CANCELLED}:
        return {"error": "Unsupported invitation state", "status_code": 400}
    if current_state == INVITE_ACCEPTED:
        return {"error": "Accepted invitations cannot be modified", "status_code": 409}
    if current_state == INVITE_EXPIRED and normalized_new_state != INVITE_PENDING:
        return {"error": "Expired invitations can only be re-opened", "status_code": 409}
    return None


def get_invitation_access_error(invitation):
    current_state = normalize_invitation_state((invitation or {}).get('state'))
    if current_state == INVITE_ACCEPTED:
        return {"error": "Invitation already used", "status_code": 409}
    if current_state != INVITE_PENDING:
        readable_state = current_state.lower() if current_state else 'invalid'
        return {"error": f"Invitation is {readable_state}", "status_code": 409}
    return None


def append_invite_history(invitation, status, changed_at=None):
    timestamp = changed_at or utc_now_iso()
    history = list(invitation.get('history') or [])
    if not history or history[-1].get('status') != status:
        history.append({'status': status, 'date': timestamp})
    invitation['history'] = history


def build_accept_url(token):
    return f"http://localhost:3000/accept-invite?token={token}"


def sync_invitation_status(invitation, persist=True):
    if not invitation:
        return None

    current_state = normalize_invitation_state(invitation.get('state')) or INVITE_PENDING
    expires_at = parse_iso_datetime(invitation.get('expiresAt'))
    now = datetime.now(timezone.utc)

    if current_state == INVITE_PENDING and expires_at and expires_at <= now:
        invitation['state'] = INVITE_EXPIRED
        append_invite_history(invitation, INVITE_EXPIRED, expires_at.isoformat())
        if persist:
            table_invites.put_item(Item=invitation)

    return invitation


def serialize_invitation(invitation, persist=True):
    synced = sync_invitation_status(dict(invitation or {}), persist=persist)
    if not synced:
        return None
    synced['acceptUrl'] = build_accept_url(synced.get('token'))
    return synced


def get_invitation_by_token(token, persist=True):
    items = table_invites.scan().get('Items', [])
    invitation = next((item for item in items if item.get('token') == token), None)
    return serialize_invitation(invitation, persist=persist) if invitation else None


def get_invitation_by_id(invite_id, persist=True):
    response = table_invites.get_item(Key={'id': invite_id})
    invitation = response.get('Item')
    return serialize_invitation(invitation, persist=persist) if invitation else None


def list_invitations():
    response = table_invites.scan()
    return [serialize_invitation(item) for item in response.get('Items', [])]


def create_invitation(payload):
    invite = dict(payload or {})
    invite_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(24)
    created_at = utc_now_iso()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=INVITE_VALID_DAYS)).isoformat()
    invitation = {
        'id': invite_id,
        'token': token,
        'email': invite.get('email'),
        'name': invite.get('name'),
        'relationship': invite.get('relationship', ''),
        'residentId': invite.get('residentId'),
        'patientName': invite.get('patientName', 'Unassigned'),
        'deviceId': invite.get('deviceId', ''),
        'state': INVITE_PENDING,
        'createdAt': created_at,
        'expiresAt': expires_at,
        'acceptedAt': None,
        'cancelledAt': None,
        'history': [{'status': INVITE_PENDING, 'date': created_at}]
    }
    table_invites.put_item(Item=invitation)
    return serialize_invitation(invitation, persist=False)


def change_invitation_state(invitation, new_state):
    normalized_new_state = normalize_invitation_state(new_state)
    changed_at = utc_now_iso()
    invitation['state'] = normalized_new_state
    if normalized_new_state == INVITE_PENDING:
        invitation['cancelledAt'] = None
        invitation['expiresAt'] = (datetime.now(timezone.utc) + timedelta(days=INVITE_VALID_DAYS)).isoformat()
    else:
        invitation['cancelledAt'] = changed_at
    append_invite_history(invitation, normalized_new_state, changed_at)
    table_invites.put_item(Item=invitation)
    return serialize_invitation(invitation, persist=False)


def register_family_user_from_invitation(invitation, name, password):
    user = {
        'id': str(uuid.uuid4()),
        'email': invitation.get('email'),
        'name': name,
        'passwordHash': generate_password_hash(password),
        'role': 'family',
        'state': 'Active',
        'residentId': invitation.get('residentId'),
        'relationship': invitation.get('relationship', ''),
        'patientName': invitation.get('patientName', 'Unassigned'),
        'deviceId': invitation.get('deviceId', ''),
        'deviceIdOverride': '',
        'invitationId': invitation.get('id'),
        'createdAt': utc_now_iso()
    }
    table_family_users.put_item(Item=user)

    accepted_at = utc_now_iso()
    invitation['name'] = name
    invitation['state'] = INVITE_ACCEPTED
    invitation['acceptedAt'] = accepted_at
    append_invite_history(invitation, INVITE_REGISTERED, accepted_at)
    append_invite_history(invitation, INVITE_ACCEPTED, accepted_at)
    table_invites.put_item(Item=invitation)
    return user
