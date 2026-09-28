#!/usr/bin/env python3
"""Ephemeral Linux CI tunnel, with ownership-checked cleanup and SSH preflight."""
import argparse
import json
import os
from pathlib import Path
import secrets
import stat
import sys
from common import SafeError, command, private_address, validate_inputs

STATE = Path('/run/agriplatform-ci-wireguard')
INTERFACE = 'ap-ci-wg'


def configuration(values):
    return (f"[Interface]\nPrivateKey = {values['WG_CLIENT_PRIVATE_KEY']}\n\n"
            f"[Peer]\nPublicKey = {values['WG_SERVER_PUBLIC_KEY']}\n"
            f"Endpoint = {values['WG_ENDPOINT']}\n"
            f"AllowedIPs = {values['WG_SERVER_ADDRESS']}\nPersistentKeepalive = 25\n")


def write_private(path, text):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as output:
        output.write(text)


def protected_state(state):
    info = state.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
        raise SafeError('Unsafe runner state directory')


def teardown(state=STATE):
    if not state.exists() and not state.is_symlink():
        return
    protected_state(state)
    marker = (state / 'owner').read_text()
    if len(marker) != 32 or any(c not in '0123456789abcdef' for c in marker):
        raise SafeError('Invalid runner ownership marker')
    try:
        result = command(['ip', '-json', 'link', 'show'], allow_failure=False)
        try:
            links = json.loads(result.stdout)
            matches = [item for item in links if item.get('ifname') == INTERFACE]
        except (ValueError, TypeError, AttributeError):
            raise SafeError('Cannot verify runner interface ownership') from None
        if matches:
            if len(matches) != 1 or matches[0].get('ifalias') != 'agriplatform-' + marker:
                raise SafeError('Refusing to remove an unowned interface')
            try:
                command(['ip', 'link', 'delete', 'dev', INTERFACE])
            except SafeError:
                # Only an ownership-verified interface reaches this fallback.
                # Both actions are attempted even when one fails; cleanup stays
                # incomplete until a later attempt actually deletes the interface.
                try:
                    command(['ip', 'link', 'set', 'dev', INTERFACE, 'down'])
                except SafeError:
                    pass
                try:
                    route = (state / 'route').read_text()
                    private_address(route)
                    command(['ip', 'route', 'del', route, 'dev', INTERFACE])
                except (SafeError, OSError):
                    pass
                raise SafeError('Runner cleanup incomplete; interface deletion must be retried') from None
    finally:
        # Remove our secret files even if interface deletion fails; retain ownership
        # evidence for an always-run retry. Never recursively delete unknown files.
        for name in ('tunnel.conf', 'ssh_key', 'known_hosts'):
            (state / name).unlink(missing_ok=True)
    (state / 'route').unlink(missing_ok=True)
    (state / 'owner').unlink()
    state.rmdir()


def setup(env, state=STATE):
    values = validate_inputs(env)  # Validate everything before creating any state.
    state.mkdir(mode=0o700)  # Existing state requires explicit cleanup, never overwrite.
    write_private(state / 'owner', secrets.token_hex(16))
    try:
        write_private(state / 'route', values['WG_SERVER_ADDRESS'])
        write_private(state / 'tunnel.conf', configuration(values))
        write_private(state / 'ssh_key', values['SSH_PRIVATE_KEY'] + '\n')
        write_private(state / 'known_hosts', values['SSH_KNOWN_HOSTS'] + '\n')
        marker = (state / 'owner').read_text()
        command(['ip', 'link', 'add', 'name', INTERFACE, 'alias', 'agriplatform-' + marker, 'type', 'wireguard'])
        command(['wg', 'setconf', INTERFACE, str(state / 'tunnel.conf')])
        command(['ip', 'address', 'add', values['WG_CLIENT_ADDRESS'], 'dev', INTERFACE])
        command(['ip', 'link', 'set', 'dev', INTERFACE, 'mtu', '1200'])
        command(['ip', 'link', 'set', 'dev', INTERFACE, 'up'])
        command(['ip', 'route', 'add', values['WG_SERVER_ADDRESS'], 'dev', INTERFACE])
        # Authentication and host verification complete before ci-deploy can mutate the host.
        command(['ssh', '-i', str(state / 'ssh_key'), '-o', 'IdentitiesOnly=yes',
                 '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                 '-o', 'GlobalKnownHostsFile=/dev/null', '-o', 'UserKnownHostsFile=' + str(state / 'known_hosts'),
                 '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=2',
                 values['DEPLOY_USER'] + '@' + values['DEPLOY_HOST'], 'true'])
    except BaseException:
        try:
            teardown(state)
        except (SafeError, OSError):
            raise SafeError('Runner setup failed; cleanup requires retry') from None
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('validate', 'setup', 'teardown'))
    args = parser.parse_args()
    try:
        if args.action == 'validate':
            validate_inputs(os.environ)
        else:
            if os.geteuid() != 0:
                raise SafeError('Runner setup and teardown require root')
            if args.action == 'setup':
                setup(os.environ)
            else:
                teardown()
    except SafeError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print('Private deployment ' + args.action + ' failed; check inputs, ownership and connectivity', file=sys.stderr)
        return 1
    print('Private deployment ' + args.action + ' succeeded (values suppressed)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
