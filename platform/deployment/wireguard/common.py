"""Strict WireGuard inputs and bounded, secret-safe command execution."""
import base64
import ipaddress
import re
import subprocess


class SafeError(Exception):
    """Only fixed, non-secret operator diagnostics may reach the CLI."""


def key(value):
    try:
        raw = base64.b64decode(value, validate=True)
        if len(raw) != 32 or not any(raw) or base64.b64encode(raw).decode() != value:
            raise ValueError
    except (ValueError, TypeError):
        raise SafeError('Invalid WireGuard key') from None
    return value


def private_address(value):
    try:
        address = ipaddress.IPv4Interface(value)
        private = any(address.ip in ipaddress.IPv4Network(cidr) for cidr in
                      ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))
        if address.network.prefixlen != 32 or not private or str(address) != value:
            raise ValueError
    except (ValueError, TypeError):
        raise SafeError('Require a canonical private IPv4 /32 address') from None
    return str(address.ip)


def identity(value):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', value):
        raise SafeError('Invalid peer identity')
    return value


def validate_inputs(env):
    names = ('WG_CLIENT_PRIVATE_KEY', 'WG_SERVER_PUBLIC_KEY', 'WG_ENDPOINT',
             'WG_SERVER_ADDRESS', 'WG_CLIENT_ADDRESS', 'DEPLOY_HOST', 'DEPLOY_USER',
             'SSH_PRIVATE_KEY', 'SSH_KNOWN_HOSTS')
    if any(not env.get(name) for name in names):
        raise SafeError('Missing private deployment inputs')
    values = {name: env[name] for name in names}
    key(values['WG_CLIENT_PRIVATE_KEY']); key(values['WG_SERVER_PUBLIC_KEY'])
    server = private_address(values['WG_SERVER_ADDRESS'])
    client = private_address(values['WG_CLIENT_ADDRESS'])
    subnet = ipaddress.IPv4Network(server + '/24', strict=False)
    addresses = (ipaddress.IPv4Address(server), ipaddress.IPv4Address(client))
    if any(address not in subnet or address in (subnet.network_address, subnet.broadcast_address) for address in addresses):
        raise SafeError('Private deployment addresses must be usable in the same server subnet')
    if server == client or values['DEPLOY_HOST'] != server:
        raise SafeError('Private deployment address mismatch')
    try:
        host, port = values['WG_ENDPOINT'].split(':')
        address = ipaddress.IPv4Address(host)
        if port != '51820' or not address.is_global or address.is_multicast or str(address) != host:
            raise ValueError
    except ValueError:
        raise SafeError('Require a public IPv4 endpoint on UDP51820') from None
    if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', values['DEPLOY_USER']):
        raise SafeError('Invalid deployment account')
    return values


def command(argv, *, input=None, allow_failure=False):
    try:
        result = subprocess.run(argv, input=input, text=True, capture_output=True,
                                timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise SafeError('WireGuard command unavailable or timed out') from None
    if result.returncode and not allow_failure:
        raise SafeError('WireGuard command failed')
    return result
