#!/usr/bin/env python3
"""Manage named server peers in one protected config; no private key generation."""
import argparse
from contextlib import contextmanager
import fcntl
import ipaddress
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
from common import SafeError, command, identity, key, private_address

MARKER = '# agriplatform-peer: '


def fields(block, allowed):
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line in ('[Interface]', '[Peer]'):
            continue
        if '=' not in line:
            raise SafeError('Malformed WireGuard config')
        name, value = (part.strip() for part in line.split('=', 1))
        if name not in allowed or name in result:
            raise SafeError('Unsupported or repeated WireGuard field')
        result[name] = value
    return result


def parse(text):
    chunks = re.split(r'(?m)^# agriplatform-peer: ', text)
    interface = chunks[0]
    if interface.count('[Interface]') != 1 or '[Peer]' in interface:
        raise SafeError('Require one interface and a registered identity for every peer')
    settings = fields(interface, {'PrivateKey', 'Address', 'ListenPort', 'MTU'})
    if not {'PrivateKey', 'Address', 'ListenPort'} <= settings.keys() or settings['ListenPort'] != '51820':
        raise SafeError('Require the documented server interface configuration')
    key(settings['PrivateKey'])
    try:
        server_interface = ipaddress.IPv4Interface(settings['Address'])
        private_address(str(server_interface.ip) + '/32')
        if server_interface.network.prefixlen != 24 or str(server_interface) != settings['Address']:
            raise ValueError
        if server_interface.ip in (server_interface.network.network_address, server_interface.network.broadcast_address):
            raise ValueError
    except ValueError:
        raise SafeError('Require a canonical private server IPv4 /24 address') from None
    server = str(server_interface.ip)
    if 'MTU' in settings and (not settings['MTU'].isdigit() or not 1200 <= int(settings['MTU']) <= 1420):
        raise SafeError('Invalid WireGuard MTU')
    registry = {}
    addresses, keys = {server}, set()
    for chunk in chunks[1:]:
        name, separator, body = chunk.partition('\n')
        identity(name)
        if not separator or body.count('[Peer]') != 1 or '[Interface]' in body:
            raise SafeError('Malformed registered peer')
        settings = fields(body, {'PublicKey', 'AllowedIPs'})
        if set(settings) != {'PublicKey', 'AllowedIPs'}:
            raise SafeError('Require a key and one private address for every peer')
        public_key = key(settings['PublicKey'])
        address = private_address(settings['AllowedIPs'])
        peer_ip = ipaddress.IPv4Address(address)
        if peer_ip not in server_interface.network or peer_ip in (server_interface.network.network_address, server_interface.network.broadcast_address):
            raise SafeError('Peer address must be a usable address in the server subnet')
        if name in registry or address in addresses or public_key in keys:
            raise SafeError('Conflicting peer registry')
        addresses.add(address); keys.add(public_key)
        registry[name] = (settings['AllowedIPs'], public_key, MARKER + chunk)
    return interface, registry


def update(text, action, name, address=None, public_key=None):
    identity(name)
    interface, registry = parse(text)
    if action == 'add':
        private_address(address); key(public_key)
        if name in registry:
            if registry[name][:2] != (address, public_key):
                raise SafeError('Peer identity already has different credentials')
            return text
        block = f'{MARKER}{name}\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = {address}\n'
        result = text + ('\n' if text.endswith('\n') else '\n\n') + block
        parse(result)  # Validate address/key uniqueness before any write.
        return result
    if action != 'remove':
        raise SafeError('Unsupported peer operation')
    if name not in registry:
        return text
    return interface + ''.join(entry[2] for peer, entry in registry.items() if peer != name)


def stripped(text):
    """Native wg syncconf input; deliberately no wg-quick hooks or SaveConfig."""
    return '\n'.join(line for line in text.splitlines()
                     if not re.match(r'^\s*(Address|MTU)\s*=', line)) + '\n'


def protected(path, directory=False):
    info = path.lstat()
    kind = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    mode = 0o700 if directory else 0o600
    if not kind or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != mode:
        raise SafeError('Require root-owned protected WireGuard files and directory')


def atomic_write(path, text):
    fd, temporary = tempfile.mkstemp(prefix='.agriplatform-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        Path(temporary).unlink(missing_ok=True)


def sync(interface, text, directory):
    fd, temporary = tempfile.mkstemp(prefix='.sync-', dir=directory)
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(stripped(text))
        command(['wg', 'syncconf', interface, temporary])
    finally:
        Path(temporary).unlink(missing_ok=True)


@contextmanager
def locked(path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        protected(path)
        deadline = time.monotonic() + 5
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise SafeError('Peer registry is busy') from None
                time.sleep(0.05)
        yield
    finally:
        os.close(fd)


def apply(config, action, name, address=None, public_key=None):
    if not re.fullmatch(r'[a-zA-Z0-9_=+.-]{1,15}', config.stem) or config.suffix != '.conf':
        raise SafeError('Invalid WireGuard config name')
    protected(config.parent, directory=True)
    with locked(config.with_suffix('.lock')):
        protected(config)
        old = config.read_text()
        new = update(old, action, name, address, public_key)
        # Verify active interface before persistent mutation; never start or stop it.
        command(['wg', 'show', config.stem, 'listen-port'])
        changed = new != old
        try:
            if changed:
                atomic_write(config, new)
            sync(config.stem, new, config.parent)
        except (SafeError, OSError):
            if changed:
                try:
                    atomic_write(config, old)
                except OSError:
                    raise SafeError('Peer update failed; saved and live configuration require console recovery') from None
            try:
                sync(config.stem, old, config.parent)
            except (SafeError, OSError):
                raise SafeError('Peer update failed; saved config restored but live recovery is required') from None
            raise SafeError('Peer update failed; previous configuration restored') from None
        return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path('/etc/wireguard/wg0.conf'))
    actions = parser.add_subparsers(dest='action', required=True)
    add = actions.add_parser('add')
    add.add_argument('identity'); add.add_argument('--address', required=True)
    add.add_argument('--public-key', required=True)
    remove = actions.add_parser('remove'); remove.add_argument('identity')
    args = parser.parse_args()
    try:
        if os.geteuid() != 0:
            raise SafeError('Peer management requires root')
        apply(args.config, args.action, args.identity, getattr(args, 'address', None), getattr(args, 'public_key', None))
    except SafeError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError):
        print('Peer operation failed; inspect protected files through the console', file=sys.stderr)
        return 1
    print('Peer operation synchronized (keys suppressed)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
