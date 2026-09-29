"""Publish the assembled static artifact outside monorepo project discovery."""
import argparse
import os
import signal
from pathlib import Path
import shutil
import subprocess
import tempfile


def run_publisher(command, work, output, timeout=600):
    process = subprocess.Popen(command, cwd=work, stdout=output, start_new_session=True)
    try:
        result = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # npx starts children; end the entire publication group before cleanup.
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
        raise
    if result:
        raise subprocess.CalledProcessError(result, command)


def publish(root=Path.cwd(), output_name='netlify-deploy.json'):
    root = root.resolve()
    artifact = root / 'platform/deployment/public-release'
    if not (artifact / 'release-identity.json').is_file():
        raise ValueError('Missing verified frontend artifact')
    # Preserve the original config and relative publish path, without workspace
    # manifests that make Netlify select one silo instead of the assembled site.
    with tempfile.TemporaryDirectory(prefix='boabab-publication-', dir='/tmp') as directory:
        work = Path(directory)
        shutil.copytree(artifact, work / 'platform/deployment/public-release')
        shutil.copyfile(root / 'netlify.toml', work / 'netlify.toml')
        with (root / output_name).open('xb') as output:
            run_publisher(
                ['npx', '--yes', 'netlify-cli@23.6.0', 'deploy',
                 '--dir=platform/deployment/public-release', '--prod', '--no-build', '--json'],
                work, output,
            )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='netlify-deploy.json')
    publish(output_name=parser.parse_args().output)
