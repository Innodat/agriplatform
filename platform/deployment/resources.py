"""Acquire the prepared run's images, bridge and volume on one guarded peer.

No public real-daemon selector, startup execution or runtime readiness. The private
handoff is a trusted immediate nonblocking constructor; arbitrary Python cannot be
preempted. Owner tool probes remain outside the five-second daemon phase.
"""
from contextlib import contextmanager
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


@contextmanager
def fresh_session(target_path, run_id, executable, work, *, _socket_path='/var/run/docker.sock', _executable_custody=None):
    """Retain fresh custody across a bounded consumer; constructors stay immediate."""
    if _executable_custody is not None:
        _executable_custody.check()
    with daemon_images.qualified_evidence(target_path, run_id) as (target, plan, evidence):
        startup.check_workdir(work, target, run_id)
        deadline = time.monotonic() + SECONDS
        def current():
            evidence()
            if _executable_custody is not None:
                _executable_custody.check()
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
            command = startup.invocation(executable, work, target, run_id, latest)
            guard = FreshGuard(target, run_id, session, current, deadline, plan, images, latest, command)
            guard.check()
            yield guard
            if guard.volume is not None:
                guard.joint()
            guard.check()


class FreshGuard:
    """One sequential fresh operation on the retained owner session, never a reservation."""
    def __init__(self, target, run_id, session, current, deadline, plan, images, network, command):
        self.target, self.run_id, self.session = target, run_id, session
        self._current, self.deadline, self.plan = current, deadline, plan
        self.images, self.network, self.command = images, network, command
        self.volume, self.phase = None, 0
        self._fixture, self._listener_identity = None, None

    def bind_fixture(self, work, work_fd, sources, fixture_hash, wrappers):
        """Bind only the closed startup fixture's concrete private custody fields."""
        if self._fixture is not None or self.phase != 0:
            startup.fail('invalid_owner_handoff')
        self._fixture = (work, work_fd, dict(sources), fixture_hash, dict(wrappers))
        self.current()

    def bind_listener(self, identity):
        if self._fixture is None or self._listener_identity is not None:
            startup.fail('invalid_owner_handoff')
        self._listener_identity = identity
        self.current()

    def current(self):
        self._current()
        if self._fixture is not None:
            startup.check_fixture_custody(*self._fixture, self.target, self.run_id,
                                          listener_identity=self._listener_identity)

    def check(self):
        self.current()
        self.session.idle()
        self.session.budget()

    def remaining(self):
        self.check()
        return self.deadline - time.monotonic()

    def joint(self):
        self.check()
        if daemon_images.observe_session(self.session, self.plan, self.current) != self.images:
            daemon_images.fail('image_identity_mismatch')
        network_id = self.network['Id']
        for reference in [network_id, networks.create_input(self.target, self.run_id)['Name'], network_id]:
            self.current()
            status, actual = self.session.exchange('GET', networks.PREFIX + reference)
            if status == 404:
                networks.fail('network_replaced')
            if status != 200:
                networks.fail('network_inspection_failed')
            if networks.descriptor(actual, self.target, self.run_id) != self.network:
                networks.fail('network_replaced')
        if self.volume is not None:
            self.current()
            status, actual = self.session.exchange('GET', volumes.PREFIX + self.volume['Name'])
            if status == 404:
                volumes.fail('volume_changed')
            if status != 200:
                volumes.fail('volume_inspection_failed')
            if startup.volume_descriptor(actual, self.target, self.run_id) != self.volume:
                volumes.fail('volume_changed')
            volumes.observe_unused(self.session, self.volume['Name'], self.current)
        self.check()

    def probe(self):
        if self.phase != 0:
            startup.fail('invalid_owner_handoff')
        self.check()
        volumes.require_absent(self.target, self.run_id, self.session, self.current)
        self.check()
        self.phase = 1

    def create(self):
        if self.phase != 1:
            startup.fail('invalid_owner_handoff')
        # Consume before any uncertain mutation so this context cannot replay it.
        self.phase = -1
        self.joint()
        result = volumes.create_fresh_session(self.target, self.run_id, self.session, self.current)
        self.volume = result['volume']
        self.joint()
        self.phase = 2


def invocation(target_path, run_id, executable, work, *, _socket_path='/var/run/docker.sock'):
    """Immediate construction only; fresh execution uses the retained context."""
    with fresh_session(target_path, run_id, executable, work, _socket_path=_socket_path) as guard:
        result = guard.command
    return result
