"""Acquire the prepared run's images, bridge and volume on one guarded peer.

No public real-daemon selector, startup execution or runtime readiness. The private
handoff is a trusted immediate nonblocking constructor; arbitrary Python cannot be
preempted. Owner tool probes remain outside the five-second daemon phase.
"""
import time

import daemon_images
import dev
import networks
import startup
import volumes

SECONDS = 5


def acquire(target_path, run_id, *, _socket_path='/var/run/docker.sock', _handoff=None):
    """Return joint selected descriptors only after all custody postchecks pass."""
    with daemon_images.qualified_evidence(target_path, run_id) as (target, plan, evidence):
        deadline = time.monotonic() + SECONDS
        def current():
            evidence()
            if time.monotonic() >= deadline:
                dev.refuse('docker', 'docker_timeout')
        with dev.DockerSession(_socket_path=_socket_path, deadline=deadline) as session:
            current()
            dev.docker_prerequisite(_session=session)
            current()
            images = daemon_images.observe_session(session, plan, current)
            network = networks.acquire_session(target, run_id, session, current)
            volume_result = volumes.acquire_session(target, run_id, session, current)
            # Observe the entire joint set again after both mutation phases.
            if daemon_images.observe_session(session, plan, current) != images:
                daemon_images.fail('image_identity_mismatch')
            network_id = network['Id']
            for reference in [network_id, networks.create_input(target, run_id)['Name'], network_id]:
                current()
                status, actual = session.exchange('GET', networks.PREFIX + reference)
                if status == 404:
                    networks.fail('network_replaced')
                if status != 200:
                    networks.fail('network_inspection_failed')
                latest = networks.descriptor(actual, target, run_id)
                if latest['Id'] != network_id:
                    networks.fail('network_replaced')
            current()
            status, actual = session.exchange('GET', volumes.PREFIX + volume_result['volume']['Name'])
            if status == 404:
                volumes.fail('volume_changed')
            if status != 200:
                volumes.fail('volume_inspection_failed')
            if startup.volume_descriptor(actual, target, run_id) != volume_result['volume']:
                volumes.fail('volume_changed')
            volumes.observe_unused(session, volume_result['volume']['Name'], current)
            current()
            # Observe currently available EOF/unsolicited bytes at the handoff boundary.
            session.idle()
            session.budget()
            result = {'network': latest, 'images': images, **volume_result}
            if _handoff is not None:
                result = _handoff(target, result)
            current()
            session.idle()
            session.budget()
        # Exiting qualified_evidence repeats owner probes and all anchored checks.
    return result


def invocation(target_path, run_id, executable, work, *, _socket_path='/var/run/docker.sock'):
    """Construct fresh-start argv leaving volume creation to the CLI; never execute."""
    with daemon_images.qualified_evidence(target_path, run_id) as (target, plan, evidence):
        startup.check_workdir(work, target, run_id)
        deadline = time.monotonic() + SECONDS
        def current():
            evidence()
            if time.monotonic() >= deadline:
                dev.refuse('docker', 'docker_timeout')
        with dev.DockerSession(_socket_path=_socket_path, deadline=deadline) as session:
            current()
            dev.docker_prerequisite(_session=session)
            current()
            images = daemon_images.observe_session(session, plan, current)
            volumes.require_absent(target, run_id, session, current)
            network = networks.acquire_session(target, run_id, session, current)
            if daemon_images.observe_session(session, plan, current) != images:
                daemon_images.fail('image_identity_mismatch')
            network_id = network['Id']
            for reference in [network_id, networks.create_input(target, run_id)['Name'], network_id]:
                current()
                status, actual = session.exchange('GET', networks.PREFIX + reference)
                if status == 404:
                    networks.fail('network_replaced')
                if status != 200:
                    networks.fail('network_inspection_failed')
                latest = networks.descriptor(actual, target, run_id)
                if latest['Id'] != network_id:
                    networks.fail('network_replaced')
            volumes.require_absent(target, run_id, session, current)
            current()
            session.idle()
            session.budget()
            result = startup.invocation(executable, work, target, run_id, latest)
            current()
            session.idle()
            session.budget()
    return result
