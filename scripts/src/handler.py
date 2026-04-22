from src.database import USE_AWS_DYNAMODB, init_db
from src.lambda_handlers.devices import get_devices, save_device, update_device
from src.lambda_handlers.events import clear_events, delete_event, get_events, update_event_status
from src.lambda_handlers.invites import accept_invite, create_invite, get_invites, register_invite, update_invite_state, verify_invite
from src.lambda_handlers.rules import create_rule, delete_rule, get_rules, update_rule
from src.lambda_handlers.users import get_family_users, get_residents, get_staff_members, save_resident, save_staff_member, update_family_user


if not USE_AWS_DYNAMODB:
    # En local y con serverless-offline creamos las tablas una sola vez por cold start.
    init_db()
