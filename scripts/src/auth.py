import os
from functools import lru_cache

import jwt
import requests
from flask import jsonify, request
from jwt import PyJWKClient


DEFAULT_AUTHENTICATED_PERMISSIONS = {'profile:view'}
GROUP_PERMISSIONS = {
    'members': {
        'dashboard:view',
        'devices:view',
        'devices:edit',
        'alerts:view',
        'alerts:clear',
        'rules:view',
        'rules:manage',
        'profile:view',
        'user:create-records',
    },
    'technician': {
        'dashboard:view',
        'devices:view',
        'devices:edit',
        'alerts:view',
        'rules:view',
        'rules:manage',
        'profile:view',
        'user:create-records',
    },
    'clinician': {
        'dashboard:view',
        'alerts:view',
        'profile:view',
    },
    'admin': {
        'dashboard:view',
        'devices:view',
        'alerts:view',
        'rules:manage',
        'profile:view',
        'user:create-records',
    },
}

OWNER_SCOPED_ROLES = {'family', 'resident'}
STAFF_ROLES = {'admin', 'technician', 'clinician', 'members'}
RULE_ASSIGNMENT_ROLES = {'admin', 'technician', 'members'}

AUTH_ISSUER = os.getenv('AUTH_ISSUER', '').strip()
AUTH_JWKS_URL = os.getenv('AUTH_JWKS_URL', '').strip()
AUTH_AUDIENCE = os.getenv('AUTH_AUDIENCE', '').strip()


class AuthError(Exception):
    """Error controlado para problemas de autenticacion."""


def normalize_group_name(group):
    return str(group or '').strip().lower()


def get_primary_group(groups=None):
    if not isinstance(groups, list) or not groups:
        return ''
    return normalize_group_name(groups[0])


def parse_device_ids(device_ids):
    if not device_ids:
        return []

    if isinstance(device_ids, list):
        raw_items = device_ids
    else:
        raw_items = str(device_ids).split(',')

    return [
        str(item).strip()
        for item in raw_items
        if str(item).strip()
    ]


def get_groups_from_claims(claims=None):
    claims = claims or {}
    groups = claims.get('cognito:groups')

    if isinstance(groups, list):
        return [normalize_group_name(group) for group in groups if normalize_group_name(group)]

    if isinstance(groups, str):
        return [normalize_group_name(group) for group in groups.split(',') if normalize_group_name(group)]

    return []


def resolve_permissions_from_groups(groups=None):
    groups = groups or []
    resolved = set(DEFAULT_AUTHENTICATED_PERMISSIONS)

    for group in groups:
        normalized_group = normalize_group_name(group)
        permissions = GROUP_PERMISSIONS.get(normalized_group, set())
        resolved.update(permissions)

    # Algunas acciones implican visualizar la pantalla completa.
    if 'rules:manage' in resolved:
        resolved.add('rules:view')
    if 'devices:edit' in resolved:
        resolved.add('devices:view')
    if 'alerts:clear' in resolved:
        resolved.add('alerts:view')
    if 'user:create-records' in resolved:
        resolved.add('user:administration')

    return resolved


def build_user_context(claims=None):
    claims = claims or {}
    groups = get_groups_from_claims(claims)
    primary_group = get_primary_group(groups)
    role = normalize_group_name(
        claims.get('custom:role')
        or claims.get('role')
        or primary_group
    )

    return {
        'sub': str(claims.get('sub') or '').strip(),
        'email': str(claims.get('email') or '').strip(),
        'name': str(
            claims.get('name')
            or claims.get('preferred_username')
            or claims.get('given_name')
            or claims.get('email')
            or 'Usuario'
        ).strip(),
        'groups': groups,
        'primaryGroup': primary_group,
        'role': role,
        'tenantKey': str(claims.get('custom:tenant_key') or '').strip(),
        'residenceId': str(claims.get('custom:residence_id') or '').strip(),
        'area': str(claims.get('custom:area') or '').strip(),
        'residentId': str(claims.get('custom:resident_id') or '').strip(),
        'deviceIds': parse_device_ids(claims.get('custom:device_ids')),
        'permissions': resolve_permissions_from_groups(groups),
    }


def get_record_owner_id(user_context=None):
    user_context = user_context or {}
    return str(
        user_context.get('email')
        or user_context.get('tenantKey')
        or user_context.get('sub')
        or ''
    ).strip()


def get_scoped_owner_id(user_context=None):
    user_context = user_context or {}
    role = normalize_group_name(
        user_context.get('role')
        or user_context.get('primaryGroup')
    )

    if role not in OWNER_SCOPED_ROLES:
        return ''

    return get_record_owner_id(user_context)


def is_staff_role(user_context=None):
    user_context = user_context or {}
    role = normalize_group_name(
        user_context.get('role')
        or user_context.get('primaryGroup')
    )
    return role in STAFF_ROLES


def can_assign_rules(user_context=None):
    user_context = user_context or {}
    role = normalize_group_name(
        user_context.get('role')
        or user_context.get('primaryGroup')
    )
    return role in RULE_ASSIGNMENT_ROLES


def has_permission(user_context=None, permission=''):
    user_context = user_context or {}
    permissions = user_context.get('permissions') or set()
    return str(permission or '').strip() in permissions


def is_device_allowed_for_user(device=None, user_context=None):
    device = device or {}
    user_context = user_context or {}

    if is_staff_role(user_context):
        return True

    allowed_device_ids = {
        str(device_id).strip().lower()
        for device_id in (user_context.get('deviceIds') or [])
        if str(device_id).strip()
    }

    if not allowed_device_ids:
        return False

    candidate_values = {
        str(device.get('deviceId') or '').strip().lower(),
        str(device.get('id') or '').strip().lower(),
        str(device.get('mac') or '').strip().lower(),
    }
    return bool(candidate_values & allowed_device_ids)


def _resolve_jwks_url(issuer=''):
    if AUTH_JWKS_URL:
        return AUTH_JWKS_URL

    issuer = str(issuer or '').strip().rstrip('/')
    if not issuer:
        return ''

    discovery_url = f'{issuer}/.well-known/openid-configuration'
    response = requests.get(discovery_url, timeout=5)
    response.raise_for_status()
    payload = response.json()
    return str(payload.get('jwks_uri') or '').strip()


@lru_cache(maxsize=32)
def _get_jwk_client(jwks_url):
    if not jwks_url:
        raise AuthError('JWKS URL is not configured')
    return PyJWKClient(jwks_url)


def decode_verified_token(token):
    if not token:
        raise AuthError('Token is required')

    try:
        unverified_claims = jwt.decode(
            token,
            options={'verify_signature': False, 'verify_aud': False}
        )
    except jwt.PyJWTError as error:
        raise AuthError('Invalid token format') from error

    issuer = str(unverified_claims.get('iss') or AUTH_ISSUER or '').strip()
    if not issuer:
        raise AuthError('Token issuer is missing')

    try:
        jwks_url = _resolve_jwks_url(issuer)
        if not jwks_url:
            raise AuthError('JWKS endpoint is not available')

        signing_key = _get_jwk_client(jwks_url).get_signing_key_from_jwt(token)
        decode_options = {'verify_aud': bool(AUTH_AUDIENCE)}
        decode_kwargs = {
            'key': signing_key.key,
            'algorithms': [jwt.get_unverified_header(token).get('alg', 'RS256')],
            'issuer': issuer,
            'options': decode_options,
        }

        if AUTH_AUDIENCE:
            decode_kwargs['audience'] = AUTH_AUDIENCE

        return jwt.decode(token, **decode_kwargs)
    except jwt.ExpiredSignatureError as error:
        raise AuthError('Token has expired') from error
    except jwt.PyJWTError as error:
        raise AuthError('Token verification failed') from error
    except requests.RequestException as error:
        raise AuthError('Unable to retrieve signing keys') from error
    except OSError as error:
        raise AuthError('Unable to retrieve signing keys') from error


def get_bearer_token_from_request():
    auth_header = str(request.headers.get('Authorization') or '').strip()
    if not auth_header.lower().startswith('bearer '):
        raise AuthError('Authorization header is required')
    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        raise AuthError('Bearer token is required')
    return token


def require_user_context(required_permission=None):
    try:
        token = get_bearer_token_from_request()
        claims = decode_verified_token(token)
        user_context = build_user_context(claims)

        if required_permission and not has_permission(user_context, required_permission):
            return None, (jsonify({'error': 'Insufficient permissions'}), 403)

        return user_context, None
    except AuthError as error:
        return None, (jsonify({'error': str(error)}), 401)
