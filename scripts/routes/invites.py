from flask import Blueprint, jsonify, request

from services.invites import (
    get_invitation_access_error,
    get_invitation_state_change_error,
    change_invitation_state,
    create_invitation,
    get_invitation_by_id,
    get_invitation_by_token,
    list_invitations,
    register_family_user_from_invitation,
)

invites_bp = Blueprint('invites', __name__)


@invites_bp.route('/invites', methods=['GET', 'POST'])
def handle_invites():
    if request.method == 'POST':
        invite = dict(request.json or {})
        if not invite.get('email') or not invite.get('name'):
            return jsonify({"error": "Invite name and email are required"}), 400
        return jsonify(create_invitation(invite)), 201

    return jsonify(list_invitations()), 200


@invites_bp.route('/invites/<invite_id>/state', methods=['PUT'])
def update_invite_state(invite_id):
    payload = dict(request.json or {})
    invitation = get_invitation_by_id(invite_id)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    new_state = payload.get('state')
    state_error = get_invitation_state_change_error(invitation, new_state)
    if state_error:
        return jsonify({"error": state_error["error"]}), state_error["status_code"]

    return jsonify(change_invitation_state(invitation, new_state)), 200


@invites_bp.route('/invites/verify', methods=['GET'])
def verify_invite():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    invitation = get_invitation_by_token(token)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    return jsonify(invitation), 200


@invites_bp.route('/invites/accept', methods=['POST'])
def accept_invite():
    token = (request.json or {}).get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    invitation = get_invitation_by_token(token)
    if not invitation:
        return jsonify({"error": "Invitation not found"}), 404

    access_error = get_invitation_access_error(invitation)
    if access_error:
        return jsonify({"error": access_error["error"]}), access_error["status_code"]

    return jsonify(change_invitation_state(invitation, 'ACCEPTED')), 200


@invites_bp.route('/invites/register', methods=['POST'])
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

    access_error = get_invitation_access_error(invitation)
    if access_error:
        return jsonify({"error": access_error["error"]}), access_error["status_code"]

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
