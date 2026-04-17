from src.lambda_handlers.common import parse_body, response
from src.services.invites import (
    INVITE_ACCEPTED,
    INVITE_CANCELLED,
    INVITE_EXPIRED,
    INVITE_PENDING,
    change_invitation_state,
    create_invitation,
    get_invitation_by_id,
    get_invitation_by_token,
    list_invitations,
    register_family_user_from_invitation,
)


def get_invites(event, context):
    return response(200, list_invitations())


def create_invite(event, context):
    body = parse_body(event)
    if not body.get("email") or not body.get("name"):
        return response(400, {"error": "Invite name and email are required"})
    return response(201, create_invitation(body))


def update_invite_state(event, context):
    invite_id = (event.get("pathParameters") or {}).get("invite_id")
    if not invite_id:
        return response(400, {"error": "invite_id is required"})

    payload = parse_body(event)
    new_state = str(payload.get("state") or "").upper()
    if new_state not in [INVITE_PENDING, INVITE_CANCELLED]:
        return response(400, {"error": "Unsupported invitation state"})

    invitation = get_invitation_by_id(invite_id)
    if not invitation:
        return response(404, {"error": "Invitation not found"})

    current_state = invitation.get("state")
    if current_state == INVITE_ACCEPTED:
        return response(409, {"error": "Accepted invitations cannot be modified"})
    if current_state == INVITE_EXPIRED and new_state != INVITE_PENDING:
        return response(409, {"error": "Expired invitations can only be re-opened"})

    return response(200, change_invitation_state(invitation, new_state))


def verify_invite(event, context):
    token = (event.get("queryStringParameters") or {}).get("token")
    if not token:
        return response(400, {"error": "Token is required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return response(404, {"error": "Invitation not found"})

    return response(200, invitation)


def accept_invite(event, context):
    body = parse_body(event)
    token = body.get("token")
    if not token:
        return response(400, {"error": "Token is required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return response(404, {"error": "Invitation not found"})
    if invitation.get("state") == INVITE_ACCEPTED:
        return response(200, invitation)
    if invitation.get("state") != INVITE_PENDING:
        return response(409, {"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"})

    return response(200, change_invitation_state(invitation, INVITE_ACCEPTED))


def register_invite(event, context):
    body = parse_body(event)
    token = body.get("token")
    password = body.get("password")
    name = body.get("name")

    if not token or not password or not name:
        return response(400, {"error": "Token, name and password are required"})

    invitation = get_invitation_by_token(token)
    if not invitation:
        return response(404, {"error": "Invitation not found"})
    if invitation.get("state") == INVITE_ACCEPTED:
        return response(409, {"error": "Invitation already used"})
    if invitation.get("state") != INVITE_PENDING:
        return response(409, {"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"})

    user = register_family_user_from_invitation(invitation, name, password)
    return response(201, {
        "status": "registered",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
    })
