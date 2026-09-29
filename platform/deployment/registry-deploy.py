"""Temporary GHCR credentials; cancellation drains the release lock owner safely."""
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile


class Control:
    def __init__(self): self.cancelled = False
    def stop(self, signum, frame): self.cancelled = True


def deploy(actor, token, command, control=None):
    control = control or Control()
    if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}(?:\[bot\])?', actor)
            or not re.fullmatch(r'[A-Za-z0-9_.-]{1,4096}', token) or not command):
        raise ValueError('invalid registry inputs')
    if os.geteuid() != 0:
        raise ValueError('root wrapper required')
    env = os.environ.copy()
    for name in ('GITHUB_TOKEN', 'REGISTRY_TOKEN', 'REGISTRY_ACTOR', 'DOCKER_AUTH_CONFIG'):
        env.pop(name, None)
    with tempfile.TemporaryDirectory(prefix='agriplatform-registry-', dir='/run') as directory:
        os.chmod(directory, 0o700)
        env['DOCKER_CONFIG'] = directory
        if control.cancelled: raise RuntimeError('cancelled')
        # The private DOCKER_CONFIG intentionally excludes per-user CLI plugins.
        # Require a system-wide Compose installation before accepting credentials.
        version = subprocess.run(['docker', 'compose', 'version', '--short'], env=env,
                                 check=True, timeout=10, start_new_session=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout
        match = re.fullmatch(rb'v?(\d+)\.(\d+)\.(\d+)', version.strip())
        if not match or tuple(map(int, match.groups())) < (2, 30, 0):
            raise ValueError('system-wide Compose >=2.30.0 required')
        if control.cancelled: raise RuntimeError('cancelled')
        subprocess.run(['docker', 'login', 'ghcr.io', '--username', actor, '--password-stdin'],
                       input=(token+'\n').encode(), env=env, check=True, timeout=45,
                       start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if control.cancelled: raise RuntimeError('cancelled')
        # Detach the coordinator from SSH's process group. TERM/HUP/INT mark this
        # invocation cancelled but must not release its flock while a separately
        # supervised Docker migration still runs. Its own per-stage deadlines drain
        # it; preserve credentials through its final possible pull, then clean up.
        process = subprocess.Popen(command, env=env, start_new_session=True,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        result = process.wait()
        if result or control.cancelled:
            raise RuntimeError('deployment failed or cancelled')


def main():
    control = Control()
    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, control.stop)
    try:
        actor = sys.stdin.readline(128).rstrip('\n')
        token = sys.stdin.readline(4098).rstrip('\n')
        deploy(actor, token, [sys.executable, str(Path(__file__).with_name('host-release.py')),
                              *sys.argv[1:]], control)
    except Exception:
        raise SystemExit('Registry authentication or deployment failed; drained invocation credentials removed') from None


if __name__ == '__main__': main()
