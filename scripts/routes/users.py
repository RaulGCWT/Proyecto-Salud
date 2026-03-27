from flask import Blueprint, jsonify, request

from database import table_family_users, table_invites, table_residents, table_staff_members
from services.common import upsert_item
from services.invites import (
    INVITE_ACCEPTED,
    INVITE_CANCELLED,
    INVITE_EXPIRED,
    INVITE_PENDING,
    create_invitation,
    get_invitation_by_id,
    get_invitation_by_token,
    list_invitations,
    change_invitation_state,
    register_family_user_from_invitation,
)

users_bp = Blueprint('users', __name__)


@users_bp.route('/staff-members', methods=['GET', 'POST'])
def handle_staff_members():
    if request.method == 'POST':
        staff_member = upsert_item(table_staff_members, request.json)
        return jsonify(staff_member), 201

    response = table_staff_members.scan()
    return jsonify(response.get('Items', [])), 200


@users_bp.route('/residents', methods=['GET', 'POST'])
def handle_residents():
    if request.method == 'POST':
        resident = upsert_item(table_residents, request.json)
        return jsonify(resident), 201

    response = table_residents.scan()
    return jsonify(response.get('Items', [])), 200


@users_bp.route('/invites', methods=['GET', 'POST'])
def handle_invites():
    if request.method == 'POST':
        invite = dict(request.json or {})
        if not invite.get('email') or not invite.get('name'):
            return jsonify({"error": "Invite name and email are required"}), 400
        return jsonify(create_invitation(invite)), 201

    return jsonify(list_invitations()), 200


@users_bp.route('/invites/<invite_id>/state', methods=['PUT'])
def update_invite_state(invite_id):
    payload = dict(request.json or {})
    new_state = str(payload.get('state') or '').upper()
    if new_state not in [INVITE_PENDING, INVITE_CANCELLED]:
        return jsonify({"error": "Unsupported invitation state"}), 400

    invitation = get_invitation_by_id(invite_id)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    current_state = invitation.get('state')
    if current_state == INVITE_ACCEPTED:
        return jsonify({"error": "Accepted invitations cannot be modified"}), 409
    if current_state == INVITE_EXPIRED and new_state != INVITE_PENDING:
        return jsonify({"error": "Expired invitations can only be re-opened"}), 409

    return jsonify(change_invitation_state(invitation, new_state)), 200


@users_bp.route('/invites/verify', methods=['GET'])
def verify_invite():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    invitation = get_invitation_by_token(token)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    return jsonify(invitation), 200


@users_bp.route('/invites/accept', methods=['POST'])
def accept_invite():
    token = (request.json or {}).get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    invitation = get_invitation_by_token(token)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404
    if invitation.get('state') == INVITE_ACCEPTED:
        return jsonify(invitation), 200
    if invitation.get('state') != INVITE_PENDING:
        return jsonify({"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"}), 409

    return jsonify(change_invitation_state(invitation, INVITE_ACCEPTED)), 200


@users_bp.route('/invites/register', methods=['POST'])
def register_from_invite():
    payload = dict(request.json or {})
    token = payload.get('token')
    password = payload.get('password')
    name = payload.get('name')

    if not token or not password or not name:
        return jsonify({"error": "Token, name and password are required"}), 400

    invitation = get_invitation_by_token(token)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404
    if invitation.get('state') == INVITE_ACCEPTED:
        return jsonify({"error": "Invitation already used"}), 409
    if invitation.get('state') != INVITE_PENDING:
        return jsonify({"error": f"Invitation is {invitation.get('state', 'invalid').lower()}"}), 409

    user = register_family_user_from_invitation(invitation, name, password)
    return jsonify({
        "status": "registered",
        "user": {
            "id": user['id'],
            "email": user['email'],
            "name": user['name'],
            "role": user['role']
        }
    }), 201


@users_bp.route('/family-users', methods=['GET'])
def get_family_users():
    response = table_family_users.scan()
    return jsonify(response.get('Items', [])), 200


@users_bp.route('/family-users/<family_user_id>', methods=['PUT'])
def update_family_user(family_user_id):
    payload = dict(request.json or {})
    items = table_family_users.scan().get('Items', [])
    family_user = next((item for item in items if item.get('id') == family_user_id), None)

    if not family_user:
        return jsonify({"error": "Family user not found"}), 404

    updated_user = {
        **family_user,
        **payload,
        'id': family_user_id
    }
    table_family_users.put_item(Item=updated_user)
    return jsonify(updated_user), 200
