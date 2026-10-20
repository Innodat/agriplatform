"""Retain ENV image, bridge and volume custody on one bounded owner peer.

Default startup controls stay synthetic. The explicit pinned-CLI PostgreSQL proof
extends this owner through disposable execution, observed shutdown and cleanup;
full environment admission remains gated. Owner tool probes remain outside the
five-second acquisition phase, and no public daemon endpoint selector is exposed.
"""
from contextlib import contextmanager
import time
import os
import ctypes
import secrets

import daemon_images
import images
import create_profile
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
            with dev._owner_observation('acquisition', 'custody', lambda: deadline):
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
            with dev._owner_observation('fresh', 'custody', lambda: session.deadline):
                evidence()
                if _executable_custody is not None:
                    _executable_custody.check()
                if time.monotonic() >= session.deadline:
                    dev.refuse('docker', 'docker_timeout')
        with dev.DockerSession(_socket_path=_socket_path, deadline=deadline) as session:
            current()
            dev.docker_prerequisite(_session=session)
            current()
            images = daemon_images.observe_session(session, plan, current)
            volumes.require_absent(target, run_id, session, current)
            created_networks = []
            network = networks.acquire_session(target, run_id, session, current, _created=created_networks)
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
            guard.network_created = latest['Id'] in created_networks
            guard.check()
            yield guard
            if guard.volume is not None and not guard.cleaned:
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
        self.execution = False
        self.execution_started = False
        self.start_attempted = False
        self.container_id = self.execution_input = None
        self.network_created = False
        self.effective_config = None
        self.ownership_lost = self.cleaned = False
        self.cleanup_attempted = False
        self.persistence = self.persistence_verified = False
        self.exec_attempts = set()
        self.exec_ids = set()
        self.stopped_instances = set()
        self._create_operands = None
        self.old_container_id = None
        self.initialized_cli = False
        self.auth_boundary = self.auth_job_refused = self.auth_terminal_attempted = False
        self.auth_migration = False
        self.auth_catalog = self.auth_catalog_precondition_verified = self.auth_catalog_verified = False
        self.api_default_privileges_request_refused = False
        self.api_default_privileges = self.api_default_privileges_attempted = self.api_default_privileges_verified = False
        self.post_auth_setup_tail = self.post_auth_setup_tail_attempted = False
        self._tail_completed = self.owner_post_auth_setup_tail_verified = False
        self._tail_custody = None
        self.kong_boundary = self.kong_boundary_attempted = self._kong_boundary_completed = False
        self.owner_kong_boundary_verified = False
        self.kong_execution = self.kong_create_attempted = self.kong_creation_uncertain = False
        self.kong_copy_attempted = self.kong_start_attempted = self.kong_stop_attempted = False
        self.kong_delete_attempted = self.kong_healthy_verified = self.kong_shutdown_verified = False
        self.kong_disposed = self.owner_kong_execution_verified = False
        self.kong_id = self.kong_fixture = self.kong_started_at = None
        self.gotrue_boundary_attempted = self._gotrue_boundary_completed = False
        self.auth_job_created_id = None
        self._shutdown_deadline = None
        self.auth_catalog_attempts = set()
        self.cli_db_backend = self.cli_db_backend_present_verified = self.cli_db_backend_departure_verified = False
        self.cli_db_backend_attempts = set()
        self.auth_job_id = self.auth_job_input = self.auth_job_effective = None
        self.auth_job_dispatched = self.auth_job_exit_verified = self.auth_job_disposed = False
        self.auth_job_create_attempted = self.auth_job_start_attempted = self.auth_job_delete_attempted = False
        self.auth_cli_terminated = False
        self.auth_job_creation_uncertain = False
        self.auth_job_started_at = None
        self.auth_job_finished_at = None
        self.poststart_identity = None
        self.poststart_healthy = False
        self._second_fixture = self._second_listener_identity = None

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

    def bind_second_fixture(self, work, work_fd, sources, fixture_hash, wrappers):
        if not self.initialized_cli or self.phase != 10 or self._second_fixture is not None:
            startup.fail('invalid_owner_handoff')
        if self._fixture is None or work == self._fixture[0]:
            startup.fail('invalid_owner_handoff')
        self._second_fixture = (work, work_fd, dict(sources), fixture_hash, dict(wrappers))
        self.current()

    def bind_second_listener(self, identity):
        if self._second_fixture is None or self._second_listener_identity is not None:
            startup.fail('invalid_owner_handoff')
        self._second_listener_identity = identity
        self.current()

    def current(self):
        try:
            self._current()
            if self._fixture is not None:
                startup.check_fixture_custody(*self._fixture, self.target, self.run_id,
                                              listener_identity=self._listener_identity, owner_tail=self._tail_custody)
            if self._second_fixture is not None:
                startup.check_fixture_custody(*self._second_fixture, self.target, self.run_id,
                                              listener_identity=self._second_listener_identity)
        except dev.Refusal as error:
            if error.code != 'docker_timeout':
                self.ownership_lost = True
            raise
        except (OSError, ValueError, KeyError, TypeError):
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')

    def check(self):
        with dev._owner_observation('guard', 'budget', lambda: self.session.deadline):
            self.current()
            self.session.idle()
            self.session.budget()

    def remaining(self):
        self.check()
        return self.deadline - time.monotonic()

    def joint(self):
        if self.ownership_lost:
            startup.fail('execution_ownership_changed')
        try:
            return self._joint()
        except dev.Refusal as error:
            if self.execution and error.code != 'docker_timeout':
                self.ownership_lost = True
            raise

    def _joint(self):
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
            if self.execution and self.container_id is not None:
                members = actual.get('Containers') if type(actual) is dict else None
                if type(members) is not dict or set(members) - {self.container_id, self.auth_job_id, self.kong_id}:
                    startup.fail('execution_ownership_changed')
                actual = dict(actual, Containers={})
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
            if self.execution and self.container_id is not None:
                self.references()
            else:
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


    def enable_execution(self):
        if self.execution or self.phase not in (0, 2):
            startup.fail('invalid_owner_handoff')
        self.execution = True

    def enable_persistence(self):
        if not self.execution or self.persistence or self.execution_started or self.phase not in (0, 2):
            startup.fail('invalid_owner_handoff')
        self.persistence = True

    def enable_initialized_cli(self):
        if not self.persistence or self.initialized_cli or self.execution_started:
            startup.fail('invalid_owner_handoff')
        self.initialized_cli = True

    def enable_auth_boundary(self):
        if not self.execution or self.auth_boundary or self.persistence or self.execution_started:
            startup.fail('invalid_owner_handoff')
        self.auth_boundary = True

    def enable_kong_execution(self):
        self.enable_kong_boundary()
        self.kong_execution = True

    def enable_kong_boundary(self):
        self.enable_post_auth_setup_tail()
        self.kong_boundary = True

    def enable_post_auth_setup_tail(self):
        self.enable_api_default_privileges()
        self.post_auth_setup_tail = True

    def enable_api_default_privileges(self):
        self.enable_cli_db_backend()
        self.api_default_privileges = True

    def enable_cli_db_backend(self):
        self.enable_auth_catalog()
        self.cli_db_backend = True

    def enable_auth_catalog(self):
        self.enable_auth_migration()
        self.auth_catalog = True

    def enable_auth_migration(self):
        self.enable_auth_boundary()
        self.auth_migration = True

    def poststart_health(self):
        if not self.auth_boundary or self.phase != 5 or self.auth_terminal_attempted:
            startup.fail('invalid_owner_handoff')
        row = self.owned()
        started = startup.lifecycle.shutdown_state(row)
        if self.poststart_identity is not None and started != self.poststart_identity:
            startup.fail('execution_instance_changed')
        self.poststart_identity = started
        observed_health = row['State'].get('Health')
        if type(observed_health) is not dict:
            startup.fail('execution_invalid_health')
        health = observed_health.get('Status')
        if health not in ('starting', 'unhealthy', 'healthy'):
            startup.fail('execution_invalid_health')
        self.poststart_healthy = health == 'healthy'
        # Selected current fields only; exclude logs, errors, PID and timestamps.
        return {'Status': row['State']['Status'], 'Running': row['State']['Running'],
                'Health': {'Status': health}}

    def refuse_auth_job(self, args, environment, fixture):
        import create_profile
        if (not self.auth_boundary or self.phase != 5 or self.auth_terminal_attempted
                or not self.poststart_healthy):
            startup.fail('invalid_owner_handoff')
        self.auth_terminal_attempted = True
        create_profile.validate_auth_job(args, fixture, environment)
        # The job can follow only the same currently healthy owned instance.
        row = self.owned()
        if startup.lifecycle.shutdown_state(row) != self.poststart_identity:
            startup.fail('execution_instance_changed')
        observed_health = row['State'].get('Health')
        if type(observed_health) is not dict or observed_health.get('Status') != 'healthy':
            startup.fail('execution_invalid_health')
        self.auth_job_refused = True

    def admit_auth_job(self, args, environment, fixture):
        import create_profile
        if not self.auth_migration:
            startup.fail('invalid_owner_handoff')
        # Same single-use admission and current healthy PG identity as refusal.
        self.refuse_auth_job(args, environment, fixture)
        self.auth_job_refused = False
        self.auth_job_input = create_profile.auth_execution_request(args, fixture, environment)

    def auth_pg_current(self):
        row = self.owned()
        if startup.lifecycle.shutdown_state(row) != self.poststart_identity:
            startup.fail('execution_instance_changed')
        health = row['State'].get('Health')
        if type(health) is not dict or health.get('Status') != 'healthy':
            startup.fail('execution_invalid_health')

    def auth_job_owned(self):
        import create_profile
        if self.ownership_lost or self.auth_job_id is None:
            startup.fail('execution_ownership_changed')
        try:
            self.auth_pg_current()
            self.current()
            status, row = self.session.exchange('GET', '/v1.48/containers/' + self.auth_job_id + '/json')
            body = self.auth_job_input['body']
            config = row.get('Config', {}) if type(row) is dict else {}
            host = row.get('HostConfig', {}) if type(row) is dict else {}
            net = row.get('NetworkSettings', {}).get('Networks', {}) if type(row) is dict else {}
            state = row.get('State', {}) if type(row) is dict else {}
            if (status != 200 or row.get('Id') != self.auth_job_id
                    or row.get('Name') != '/supabase_auth_migrate_' + self.auth_job_project
                    or row.get('Image') != self.images[body['Image']]['Id']
                    or any(not create_profile._exact_tree(config.get(k), v) for k, v in self.auth_job_effective.items() if k != 'ArgsEscaped')
                    or any(config.get(k, False) is not False for k in ('ArgsEscaped', 'Tty', 'OpenStdin', 'StdinOnce', 'AttachStdin', 'AttachStdout', 'AttachStderr'))
                    or row.get('Path') != 'gotrue' or not create_profile._exact_tree(row.get('Args'), ['migrate'])
                    or any(config.get(k) not in (None, {}, []) for k in ('Entrypoint', 'Volumes', 'ExposedPorts', 'Healthcheck', 'OnBuild', 'Shell'))
                    or row.get('Mounts') != []
                    or any(not create_profile._exact_tree(host.get(k), v) for k, v in body['HostConfig'].items())
                    or any(host.get(k) not in (None, [], {}) for k in ('Binds', 'Mounts', 'Tmpfs', 'VolumesFrom', 'PortBindings', 'CapAdd', 'Devices', 'DeviceRequests', 'SecurityOpt', 'Links'))
                    or any(host.get(k, '') != '' for k in ('PidMode', 'UTSMode', 'UsernsMode'))
                    or host.get('IpcMode') not in ('private', '')
                    or set(net) != {self.network['Name']}
                    or net[self.network['Name']].get('NetworkID') not in
                        ((self.network['Id'], '') if state.get('Status') == 'created' and not self.auth_job_start_attempted else (self.network['Id'],))
                    or row.get('Platform') != 'linux'
                    or type(row.get('RestartCount')) is not int or row['RestartCount'] != 0
                    or type(state) is not dict or type(state.get('Running')) is not bool
                    or type(state.get('Pid')) is not int or type(state.get('ExitCode')) is not int
                    or state.get('OOMKilled') is not False or state.get('Dead') is not False or state.get('Error') != ''
                    or state.get('Paused') is not False or state.get('Restarting') is not False
                    or state.get('Status') not in ('created', 'running', 'exited')
                    or state['Running'] != (state['Status'] == 'running')
                    or (state['Pid'] > 0) != state['Running'] or state['Pid'] < 0):
                startup.fail('execution_ownership_changed')
            if state['Status'] in ('created', 'running') and state['ExitCode'] != 0:
                startup.fail('execution_invalid_job')
            if state['Status'] == 'created':
                if (state.get('StartedAt') != '0001-01-01T00:00:00Z'
                        or state.get('FinishedAt') != '0001-01-01T00:00:00Z' or self.auth_job_started_at is not None):
                    startup.fail('execution_invalid_job')
            else:
                started = state.get('StartedAt')
                instant = startup.lifecycle.shutdown_timestamp(started)
                if self.auth_job_started_at is not None and started != self.auth_job_started_at:
                    startup.fail('execution_invalid_job')
                self.auth_job_started_at = started
                if state['Status'] == 'exited':
                    finished = state.get('FinishedAt')
                    if (startup.lifecycle.shutdown_timestamp(finished) <= instant
                            or (self.auth_job_finished_at is not None and finished != self.auth_job_finished_at)):
                        self.auth_job_exit_verified = False
                        startup.fail('execution_invalid_job')
                    self.auth_job_finished_at = finished
                elif state.get('FinishedAt') != '0001-01-01T00:00:00Z':
                    startup.fail('execution_invalid_job')
            self.check()
            return row
        except dev.Refusal as error:
            if error.code != 'docker_timeout':
                self.ownership_lost = True
            raise
        except (KeyError, TypeError, AttributeError):
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')

    def execute_auth_job(self):
        import create_profile
        import re
        if (not self.auth_migration or not self.auth_cli_terminated or self.auth_job_input is None
                or self.auth_job_create_attempted or self.phase != 5
                or (self.auth_catalog and not self.auth_catalog_precondition_verified)
                or (self.cli_db_backend and not self.cli_db_backend_departure_verified)):
            startup.fail('invalid_owner_handoff')
        self.auth_job_create_attempted = True
        self.auth_pg_current()
        request = self.auth_job_input
        self.auth_job_project = request['body']['Labels']['com.supabase.cli.project']
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/supabase_auth_migrate_' + self.auth_job_project + '/json')
        if status != 404:
            startup.fail('execution_existing_container')
        self.auth_pg_current()
        status, image = self.session.exchange('GET', '/v1.48/images/' + request['body']['Image'] + '/json')
        if status != 200 or type(image) is not dict or image.get('Id') != self.images[request['body']['Image']]['Id']:
            startup.fail('execution_image_changed')
        create_profile.validate_auth_image_config(image.get('Config'))
        self.auth_job_effective = {**create_profile.AUTH_IMAGE_CONFIG,
                'Image': request['body']['Image'], 'Cmd': ['gotrue', 'migrate'], 'ArgsEscaped': False,
                'Env': request['body']['Env'] + create_profile.AUTH_IMAGE_CONFIG['Env'],
                'Labels': request['body']['Labels']}
        self.auth_pg_current()
        self.auth_job_creation_uncertain = True
        status, response = self.session.exchange(request['method'], request['path'], request['body'])
        if (status != 201 or type(response) is not dict or set(response) != {'Id', 'Warnings'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])
                or response['Id'] == self.container_id or response['Warnings'] not in (None, [])):
            # Unknown creation must not permit deleting bridge/storage underneath it.
            self.ownership_lost = True
            startup.fail('execution_uncertain_creation')
        self.auth_job_created_id = self.auth_job_id = response['Id']
        self.auth_job_creation_uncertain = False
        row = self.auth_job_owned()
        if row['State']['Status'] != 'created' or row['State']['ExitCode'] != 0:
            startup.fail('execution_invalid_job')
        self.auth_pg_current()
        self.auth_job_start_attempted = True
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.auth_job_id + '/start')
        if status != 204:
            startup.fail('execution_start_failed')
        self.auth_job_dispatched = True
        while True:
            row = self.auth_job_owned()
            state = row['State']
            if state['Status'] == 'exited':
                if state['ExitCode'] != 0:
                    startup.fail('execution_auth_job_failed')
                self.auth_job_exit_verified = True
                break
            if state['Status'] != 'running':
                startup.fail('execution_invalid_job')
            time.sleep(min(.1, max(0, self.remaining())))
        self.remove_auth_job(clean=True)

    def remove_auth_job(self, *, clean=False):
        if self.auth_job_delete_attempted or self.auth_job_id is None:
            startup.fail('execution_cleanup_unresolved')
        row = self.auth_job_owned()
        if clean and (not self.auth_job_exit_verified or row['State']['Status'] != 'exited' or row['State']['ExitCode'] != 0):
            startup.fail('execution_cleanup_unresolved')
        self.current()
        self.auth_job_delete_attempted = True
        status, _ = self.session.exchange('DELETE', '/v1.48/containers/' + self.auth_job_id + '?force=' + ('false' if clean else 'true'))
        if status != 204:
            startup.fail('execution_cleanup_unresolved')
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/' + self.auth_job_id + '/json')
        if status != 404:
            startup.fail('execution_cleanup_unresolved')
        self.auth_job_id = None
        self.auth_job_disposed = True
        self.auth_pg_current()

    def initialized_probe(self):
        if not self.initialized_cli or self.phase != 10:
            startup.fail('invalid_owner_handoff')
        self.phase = -1
        self.joint()
        self.phase = 11

    def initialized_ensure(self):
        if not self.initialized_cli or self.phase != 11:
            startup.fail('invalid_owner_handoff')
        self.phase = -1
        self.joint()
        self.phase = 9

    def references(self):
        path = ('/v1.48/containers/json?all=true&filters=%7B%22volume%22%3A%5B%22'
                + self.volume['Name'] + '%22%5D%7D')
        self.current()
        status, rows = self.session.exchange('GET', path)
        if (status != 200 or type(rows) is not list or len(rows) != 1
                or type(rows[0]) is not dict or rows[0].get('Id') != self.container_id):
            startup.fail('execution_ownership_changed')

    def owned(self):
        """Every identity/configuration mismatch permanently revokes cleanup authority."""
        import create_profile
        if self.ownership_lost or self.container_id is None:
            startup.fail('execution_ownership_changed')
        try:
            self.joint()
            self.current()
            status, row = self.session.exchange('GET', '/v1.48/containers/' + self.container_id + '/json')
            body = self.execution_input['body']
            host = row.get('HostConfig', {}) if type(row) is dict else {}
            config = row.get('Config', {}) if type(row) is dict else {}
            mounts = row.get('Mounts') if type(row) is dict else None
            expected_mount = self.volume['Name']
            state = row.get('State', {}) if type(row) is dict else {}
            pending_attachment = (not self.start_attempted and type(state) is dict
                    and state.get('Status') == 'created' and state.get('Running') is False
                    and type(state.get('Pid')) is int and state['Pid'] == 0
                    and state.get('Dead') is False and state.get('OOMKilled') is False
                    and state.get('Error') == '' and type(state.get('ExitCode')) is int and state['ExitCode'] == 0
                    and state.get('StartedAt') == '0001-01-01T00:00:00Z'
                    and state.get('FinishedAt') == '0001-01-01T00:00:00Z'
                    and type(row.get('RestartCount')) is int and row['RestartCount'] == 0)
            if (status != 200 or row.get('Id') != self.container_id
                    or row.get('Name') != '/' + expected_mount
                    or row.get('Image') != self.images[body['Image']]['Id']
                    or any(not create_profile._exact_tree(config.get(k), self.effective_config[k]) for k in ['Image', 'Entrypoint', 'Cmd', 'Labels'])
                    or sorted(config.get('Env', [])) != sorted(self.effective_config['Env'])
                    or any(not create_profile._exact_tree(config.get('Healthcheck', {}).get(k), v) for k, v in body['Healthcheck'].items())
                    or any(k not in body['Healthcheck'] and (k not in ('StartPeriod', 'StartInterval') or v != 0) for k, v in config.get('Healthcheck', {}).items())
                    or any(not create_profile._exact_tree(host.get(k), v) for k, v in body['HostConfig'].items())
                    or host.get('Tmpfs') not in (None, {}) or host.get('VolumesFrom') not in (None, [])
                    or type(mounts) is not list or len(mounts) != 1
                    or mounts[0].get('Type') != 'volume' or mounts[0].get('Name') != expected_mount
                    or mounts[0].get('Destination') != '/var/lib/postgresql/data' or mounts[0].get('RW') is not True
                    or set(row.get('NetworkSettings', {}).get('Networks', {})) != {self.network['Name']}
                    or type(row['NetworkSettings']['Networks'][self.network['Name']].get('Aliases')) is not list
                    or not {'db', 'db.supabase.internal'} <= set(row['NetworkSettings']['Networks'][self.network['Name']]['Aliases'])
                    or row['NetworkSettings']['Networks'][self.network['Name']].get('NetworkID') not in
                        ((self.network['Id'], '') if pending_attachment else (self.network['Id'],))
                    or any(host.get(k) not in (None, [], {}) for k in ['CapAdd', 'Devices', 'DeviceRequests', 'VolumesFrom', 'SecurityOpt'])
                    or host.get('PidMode', '') != '' or host.get('UTSMode', '') != ''):
                startup.fail('execution_ownership_changed')
            self.check()
            return row
        except dev.Refusal as error:
            if error.code != 'docker_timeout':
                self.ownership_lost = True
            raise
        except (ValueError, KeyError, TypeError, AttributeError):
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')

    def container_create(self, args, fixture, environment, *, _replacement=False):
        import create_profile
        import re
        if not self.execution or self.phase != (9 if _replacement else 2):
            startup.fail('invalid_owner_handoff')
        create_profile.validate(args, fixture, environment)
        selected = dict(fixture, postgres_image=fixture['selection_plan'][fixture['postgres_image']])
        operands = list(args)
        operands[create_profile.validate(args, fixture, environment)] = selected['postgres_image']
        request = create_profile.disposable_execution_request(operands, selected, environment)
        self.check()
        if self.execution_started != _replacement:
            startup.fail('invalid_owner_handoff')
        if not _replacement:
            self.execution_started = True
            self._create_operands = (list(args), dict(fixture), dict(environment))
            self.deadline = self.session.deadline = time.monotonic() + 120
        self.phase = -1
        self.joint()
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/supabase_db_' + fixture['project'] + '/json')
        if status != 404:
            startup.fail('execution_existing_container')
        self.current()
        status, image = self.session.exchange('GET', '/v1.48/images/' + selected['postgres_image'] + '/json')
        if (status != 200 or image.get('Id') != self.images[selected['postgres_image']]['Id']
                or set(image.get('Config', {}).get('Volumes') or {}) - {'/var/lib/postgresql/data'}):
            startup.fail('execution_image_changed')
        inherited = image.get('Config', {})
        image_env = inherited.get('Env') or []
        image_labels = inherited.get('Labels') or {}
        if (type(image_env) is not list or any(type(v) is not str or '=' not in v for v in image_env)
                or type(image_labels) is not dict):
            startup.fail('execution_image_changed')
        public_names = set(create_profile.CONTAINER_ENV)
        self.effective_config = {**request['body'],
            'Env': [v for v in image_env if v.split('=', 1)[0] not in public_names] + request['body']['Env'],
            'Labels': {**image_labels, **request['body']['Labels']}}
        self.current()
        with dev.free_ports({'database': fixture['database_port']}):
            self.check()
        status, response = self.session.exchange(request['method'], request['path'], request['body'])
        if (status != 201 or type(response) is not dict or set(response) != {'Id', 'Warnings'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])
                or response['Warnings'] not in (None, [])):
            startup.fail('execution_uncertain_creation')
        if _replacement and response['Id'] == self.old_container_id:
            self.ownership_lost = True
            startup.fail('execution_uncertain_creation')
        self.container_id, self.execution_input = response['Id'], request
        self.owned()
        self.phase = 3
        return self.container_id

    def created(self):
        row = self.owned()
        state = row.get('State')
        if type(state) is not dict or state.get('Status') != 'created' or state.get('Running') is not False:
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')
        return row

    def container_copy(self, args, archive):
        if not self.execution or self.phase != 3 or args != ['cp', '-', self.container_id + ':/']:
            startup.fail('invalid_owner_handoff')
        startup.lifecycle.validate_archive(archive)
        self.phase = -1
        self.created()
        status, _ = self.session.exchange('PUT', '/v1.48/containers/' + self.container_id + '/archive?path=%2F', archive)
        if status != 200:
            startup.fail('execution_copy_failed')
        self.created()
        self.phase = 4

    def container_start(self, args):
        if not self.execution or self.phase != 4 or args != ['start', self.container_id]:
            startup.fail('invalid_owner_handoff')
        self.phase = -1
        self.created()
        self.start_attempted = True
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/start')
        if status != 204:
            startup.fail('execution_start_failed')
        if self.auth_boundary:
            self.poststart_identity = startup.lifecycle.shutdown_state(self.owned())
        self.phase = 5

    def persistence_sql(self, mode, started):
        import re
        if not self.persistence or self.phase != 5 or (self.old_container_id is None and mode not in ('write', 'schemas')) or (self.old_container_id is not None and mode not in ('verify', 'schemas')):
            startup.fail('invalid_owner_handoff')
        expected = ('write', 'schemas', 'verify', 'schemas')
        if len(self.exec_attempts) >= len(expected) or mode != expected[len(self.exec_attempts)]:
            startup.fail('invalid_owner_handoff')
        key = (self.container_id, mode)
        if key in self.exec_attempts:
            startup.fail('invalid_owner_handoff')
        self.exec_attempts.add(key)
        body = startup.lifecycle.persistence_exec(self.run_id, mode)
        def stable():
            if startup.lifecycle.shutdown_state(self.owned()) != started:
                startup.fail('execution_instance_changed')
        stable()
        status, response = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/exec', body)
        if (status != 201 or type(response) is not dict or set(response) != {'Id'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])):
            startup.fail('execution_uncertain_exec')
        ident = response['Id']
        if ident in self.exec_ids:
            startup.fail('execution_invalid_exec')
        self.exec_ids.add(ident)
        def inspect_exec():
            stable()
            status, row = self.session.exchange('GET', '/v1.48/exec/' + ident + '/json')
            config = row.get('ProcessConfig') if type(row) is dict else None
            if (status != 200 or type(row) is not dict or row.get('ID') != ident
                    or row.get('ContainerID') != self.container_id or type(row.get('Running')) is not bool
                    or 'ExitCode' not in row or (row['ExitCode'] is not None and type(row['ExitCode']) is not int)
                    or type(row.get('Pid')) is not int or row['Pid'] < 0
                    or type(config) is not dict or config.get('entrypoint') != body['Cmd'][0]
                    or config.get('arguments') != body['Cmd'][1:] or config.get('privileged') is not False
                    or config.get('tty') is not False or config.get('user') != 'postgres'):
                startup.fail('execution_invalid_exec')
            return row
        row = inspect_exec()
        if row['Running'] is not False or row['Pid'] != 0 or row['ExitCode'] is not None:
            startup.fail('execution_invalid_exec')
        stable()
        status, _ = self.session.exchange('POST', '/v1.48/exec/' + ident + '/start', {'Detach': True, 'Tty': False})
        if status != 200:
            startup.fail('execution_uncertain_exec')
        while True:
            row = inspect_exec()
            if row['Running'] is False:
                if type(row['ExitCode']) is not int:
                    startup.fail('execution_invalid_exec')
                if row['ExitCode'] != 0:
                    startup.fail('execution_sql_failed')
                break
            time.sleep(min(.1, max(0, self.remaining())))
        stable()

    def cli_db_backend_sql(self, mode, process=None):
        import re
        if (getattr(self, '_finish_attempted', False) or not self.cli_db_backend or not self.auth_catalog or self.phase != 5
                or self.auth_job_input is None or not self.auth_terminal_attempted
                or mode not in ('present', 'departed') or mode in self.cli_db_backend_attempts
                or self.auth_job_create_attempted or self.auth_catalog_attempts
                or (mode == 'present' and (self.auth_cli_terminated or process is None
                    or self.cli_db_backend_attempts or process.poll() is not None))
                or (mode == 'departed' and (not self.auth_cli_terminated
                    or not self.cli_db_backend_present_verified))):
            startup.fail('invalid_owner_handoff')
        self.cli_db_backend_attempts.add(mode)
        body = startup.lifecycle.cli_db_backend_exec(mode)
        def stable():
            self.auth_pg_current()
            if mode == 'present' and (self.auth_cli_terminated or process.poll() is not None):
                startup.fail('invalid_owner_handoff')
        stable()
        status, response = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/exec', body)
        if (status != 201 or type(response) is not dict or set(response) != {'Id'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])):
            startup.fail('execution_uncertain_exec')
        ident = response['Id']
        if ident in self.exec_ids:
            startup.fail('execution_invalid_exec')
        self.exec_ids.add(ident)
        stable()
        def inspect_exec():
            stable()
            status, row = self.session.exchange('GET', '/v1.48/exec/' + ident + '/json')
            stable()
            config = row.get('ProcessConfig') if type(row) is dict else None
            if (status != 200 or type(row) is not dict or row.get('ID') != ident
                    or row.get('ContainerID') != self.container_id or type(row.get('Running')) is not bool
                    or 'ExitCode' not in row or (row['ExitCode'] is not None and type(row['ExitCode']) is not int)
                    or type(row.get('Pid')) is not int or row['Pid'] < 0
                    or type(config) is not dict or config.get('entrypoint') != body['Cmd'][0]
                    or config.get('arguments') != body['Cmd'][1:] or config.get('privileged') is not False
                    or config.get('tty') is not False or config.get('user') != 'postgres'):
                startup.fail('execution_invalid_exec')
            return row
        row = inspect_exec()
        if row['Running'] is not False or row['Pid'] != 0 or row['ExitCode'] is not None:
            startup.fail('execution_invalid_exec')
        stable()
        status, _ = self.session.exchange('POST', '/v1.48/exec/' + ident + '/start', {'Detach': True, 'Tty': False})
        stable()
        if status != 200:
            startup.fail('execution_uncertain_exec')
        while True:
            row = inspect_exec()
            if row['Running'] and row['ExitCode'] is not None:
                startup.fail('execution_invalid_exec')
            if row['Running'] is False:
                if type(row['ExitCode']) is not int or row['Pid'] <= 0:
                    startup.fail('execution_invalid_exec')
                if row['ExitCode'] != 0:
                    startup.fail('execution_sql_failed')
                break
            time.sleep(min(.1, max(0, self.remaining())))
        stable()

        if mode == 'present':
            self.cli_db_backend_present_verified = True
        else:
            self.cli_db_backend_departure_verified = True

    def _auth_owned_sql(self, body, stable):
        import re
        if getattr(self, '_finish_attempted', False):
            startup.fail('invalid_owner_handoff')
        stable()
        status, response = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/exec', body)
        if (status != 201 or type(response) is not dict or set(response) != {'Id'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])):
            startup.fail('execution_uncertain_exec')
        stable()
        ident = response['Id']
        if ident in self.exec_ids:
            startup.fail('execution_invalid_exec')
        self.exec_ids.add(ident)
        def inspect_exec():
            stable()
            status, row = self.session.exchange('GET', '/v1.48/exec/' + ident + '/json')
            stable()
            config = row.get('ProcessConfig') if type(row) is dict else None
            if (status != 200 or type(row) is not dict or row.get('ID') != ident
                    or row.get('ContainerID') != self.container_id or type(row.get('Running')) is not bool
                    or 'ExitCode' not in row or (row['ExitCode'] is not None and type(row['ExitCode']) is not int)
                    or type(row.get('Pid')) is not int or row['Pid'] < 0
                    or type(config) is not dict or config.get('entrypoint') != body['Cmd'][0]
                    or config.get('arguments') != body['Cmd'][1:] or config.get('privileged') is not False
                    or config.get('tty') is not False or config.get('user') != 'postgres'):
                startup.fail('execution_invalid_exec')
            return row
        row = inspect_exec()
        if row['Running'] is not False or row['Pid'] != 0 or row['ExitCode'] is not None:
            startup.fail('execution_invalid_exec')
        stable()
        status, _ = self.session.exchange('POST', '/v1.48/exec/' + ident + '/start', {'Detach': True, 'Tty': False})
        stable()
        if status != 200:
            startup.fail('execution_uncertain_exec')
        while True:
            row = inspect_exec()
            if row['Running'] and row['ExitCode'] is not None:
                startup.fail('execution_invalid_exec')
            if row['Running'] is False:
                if type(row['ExitCode']) is not int or row['Pid'] <= 0:
                    startup.fail('execution_invalid_exec')
                if row['ExitCode'] != 0:
                    startup.fail('execution_sql_failed')
                break
            time.sleep(min(.1, max(0, self.remaining())))
        stable()

    def complete_post_auth_setup_tail(self):
        if self.post_auth_setup_tail_attempted or getattr(self, '_finish_attempted', False):
            startup.fail('invalid_owner_handoff')
        # Failed prerequisite checks also consume this invocation; no repaired replay.
        self.post_auth_setup_tail_attempted = True
        if (not self.post_auth_setup_tail or self.phase != 5 or self._fixture is None
                or not self.api_default_privileges or not self.api_default_privileges_verified
                or not self.auth_cli_terminated or not self.cli_db_backend or not self.auth_catalog
                or not self.cli_db_backend_present_verified
                or not self.cli_db_backend_departure_verified or not self.auth_catalog_precondition_verified
                or not self.auth_catalog_verified or not self.api_default_privileges_request_refused
                or not self.auth_job_exit_verified or not self.auth_job_disposed):
            startup.fail('invalid_owner_handoff')
        self.check()
        self.auth_pg_current()
        work = self._fixture[0]
        mutated = False
        try:
            # Bind both mutation parents before the final closed-fixture check.
            with dev.directory(work / 'supabase') as parent, dev.directory(work / 'tmp') as temporary:
                dev.check_private(parent)
                dev.check_private(temporary)
                parent_info, tmp_info = os.fstat(parent), os.fstat(temporary)
                parent_identity = (parent_info.st_dev, parent_info.st_ino)
                tmp_identity = (tmp_info.st_dev, tmp_info.st_ino)
                self.check()
                try:
                    for name, identity in (('supabase', parent_identity), ('tmp', tmp_identity)):
                        with dev.directory(work / name) as current_parent:
                            info = os.fstat(current_parent)
                            if (info.st_dev, info.st_ino) != identity:
                                startup.fail('fixture_changed')
                except (dev.Refusal, OSError):
                    self.ownership_lost = True
                    raise
                # Construct privately, retain its identity, then publish without
                # replacing even an empty destination. Never adopt canonical mkdir.
                mutated = True
                staged = '.owner-tail-' + secrets.token_hex(16)
                os.mkdir(staged, 0o700, dir_fd=temporary)
                branch = os.open(staged, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=temporary)
                try:
                    dev.check_private(branch)
                    if os.listdir(branch):
                        startup.fail('fixture_changed')
                    fd = os.open('_current_branch', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o644, dir_fd=branch)
                    with os.fdopen(fd, 'wb') as stream:
                        os.fchmod(stream.fileno(), 0o644)
                        stream.write(b'main')
                        stream.flush()
                        os.fsync(stream.fileno())
                        custody = tuple((info.st_dev, info.st_ino) for info in
                                        (parent_info, os.fstat(branch), os.fstat(stream.fileno())))
                    os.fsync(branch)
                    self.check()
                    for name, identity in (('supabase', parent_identity), ('tmp', tmp_identity)):
                        with dev.directory(work / name) as current_parent:
                            info = os.fstat(current_parent)
                            if (info.st_dev, info.st_ino) != identity:
                                startup.fail('fixture_changed')
                    # This owner already depends on Linux process/Unix-socket
                    # primitives. RENAME_NOREPLACE is required for directory
                    # publication; ordinary rename would overwrite an empty rival.
                    publish = ctypes.CDLL(None, use_errno=True).renameat2
                    publish.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
                    publish.restype = ctypes.c_int
                    if publish(temporary, os.fsencode(staged), parent, b'.branches', 1) != 0:
                        error = ctypes.get_errno()
                        raise OSError(error, 'owner tail publication failed')
                    self._tail_custody = custody
                finally:
                    os.close(branch)
                self.check()
                self.auth_pg_current()
                self.check()
                with dev.directory(work / 'tmp') as current_tmp:
                    info = os.fstat(current_tmp)
                    if (info.st_dev, info.st_ino) != tmp_identity:
                        startup.fail('fixture_changed')
        except BaseException:
            if mutated:
                self.ownership_lost = True
            raise
        self._tail_completed = True

    def verify_kong_boundary(self):
        # Consume before *all* prerequisite checks, including failed attempts.
        if self.kong_boundary_attempted:
            startup.fail('invalid_owner_handoff')
        self.kong_boundary_attempted = True
        if (not self.kong_boundary or not self.post_auth_setup_tail or not self._tail_completed
                or self.phase != 5 or self._fixture is None or self._tail_custody is None
                or getattr(self, '_finish_attempted', False)
                or not self.api_default_privileges_verified or not self.auth_cli_terminated
                or not self.cli_db_backend_present_verified or not self.cli_db_backend_departure_verified
                or not self.auth_catalog_precondition_verified or not self.auth_catalog_verified
                or not self.api_default_privileges_request_refused
                or not self.auth_job_exit_verified or not self.auth_job_disposed):
            startup.fail('invalid_owner_handoff')
        self.check()
        self.auth_pg_current()
        pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
        pin = next(item for item in pins['images'] if item['id'] == 'kong')
        repository = 'public.ecr.aws/' + pin['repository']
        selected = [ref for ref in self.images if ref.startswith(repository + '@sha256:')]
        if len(selected) != 1 or self.plan.get(selected[0]) != self.images[selected[0]]['Id']:
            startup.fail('invalid_owner_handoff')
        fixture = {'project': dev.project_identity(self.target, self.run_id),
                   'workdir': str(self._fixture[0]), 'network': self.network,
                   'selection_plan': {repository + ':' + pin['tag']: selected[0]},
                   'image_observations': self.images}
        self.check()
        status, image = self.session.exchange('GET', '/v1.48/images/' + selected[0] + '/json')
        if (status != 200 or type(image) is not dict
                or image.get('Id') != self.images[selected[0]]['Id']
                or image.get('Os') != 'linux' or image.get('Architecture') != 'amd64'
                or image.get('Variant', '') != ''):
            startup.fail('execution_image_changed')
        create_profile.validate_kong_image_config(image.get('Config'))
        args = create_profile.kong_request(fixture)
        environment = dict(create_profile.KONG_ENV)
        request = create_profile.kong_execution_request(fixture)
        files = create_profile.kong_transfer_files(fixture)
        create_profile.validate_kong_intent(args, environment, request, files, fixture)
        disposable = create_profile.kong_disposable_execution_request(args, environment, request, files, fixture)
        create_profile.validate_kong_disposable_execution_request(disposable, fixture)
        archive = startup.lifecycle.kong_archive(files, fixture)
        startup.lifecycle.validate_kong_archive(archive, fixture)
        self.check()
        self.auth_pg_current()
        # Classifier only: never exchange, dispatch, create, copy or start Kong.
        for candidate in (request, disposable):
            try:
                dev._docker_request(candidate['method'], candidate['path'], candidate['body'], True)
            except dev.Refusal as error:
                if (error.stage, error.code) != ('docker', 'docker_request_invalid'):
                    raise
            else:
                startup.fail('invalid_owner_handoff')
        self.check()
        self.auth_pg_current()
        self.check()
        self._kong_boundary_completed = True

    def verify_gotrue_service_boundary(self):
        """Single-use internal refusal proof; no GoTrue execution or public fact."""
        import copy
        if self.gotrue_boundary_attempted:
            startup.fail('invalid_owner_handoff')
        self.gotrue_boundary_attempted = True
        if (not self.execution or not self.kong_execution or not self._kong_boundary_completed
                or not self._tail_completed or self._tail_custody is None
                or self.phase != 5 or self._fixture is None
                or getattr(self, '_finish_attempted', False) or self.cleaned or self.ownership_lost
                or not self.kong_healthy_verified or self.kong_started_at is None or self.kong_id is None
                or self.kong_stop_attempted or self.kong_shutdown_verified or self.kong_disposed
                or not self.auth_cli_terminated or not self.api_default_privileges_verified
                or not self.auth_job_exit_verified or not self.auth_job_disposed
                or not self.cli_db_backend_present_verified or not self.cli_db_backend_departure_verified
                or not self.auth_catalog_precondition_verified or not self.auth_catalog_verified
                or not self.api_default_privileges_request_refused):
            startup.fail('invalid_owner_handoff')

        def current_services():
            self.check()
            self.auth_pg_current()
            row = self.kong_owned()
            if (row['State']['Status'] != 'running'
                    or startup.lifecycle.shutdown_state(row) != self.kong_started_at
                    or type(row['State'].get('Health')) is not dict
                    or row['State']['Health'].get('Status') != 'healthy'):
                startup.fail('execution_invalid_health')
            self.check()

        current_services()
        pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
        pin = next(item for item in pins['images'] if item['id'] == 'gotrue')
        repository = 'public.ecr.aws/' + pin['repository']
        selected = [ref for ref in self.images if ref.startswith(repository + '@sha256:')]
        if len(selected) != 1 or self.plan.get(selected[0]) != self.images[selected[0]]['Id']:
            startup.fail('invalid_owner_handoff')
        selected = selected[0]
        descriptor = copy.deepcopy(self.images[selected])
        status, image = self.session.exchange('GET', '/v1.48/images/' + selected + '/json')
        if (status != 200 or type(image) is not dict or image.get('Id') != descriptor['Id']
                or image.get('Os') != 'linux' or image.get('Architecture') != 'amd64'
                or image.get('Variant', '') != ''):
            startup.fail('execution_image_changed')
        create_profile.validate_auth_image_config(image.get('Config'))
        fixture = {'target_id': self.target['target_id'],
                   'project': dev.project_identity(self.target, self.run_id),
                   'workdir': str(self._fixture[0]), 'network': copy.deepcopy(self.network),
                   'origins': copy.deepcopy(self.target['origins']),
                   'callback_urls': copy.deepcopy(self.target['callback_urls']),
                   'selection_plan': {repository + ':' + pin['tag']: selected},
                   'image_observations': {selected: copy.deepcopy(descriptor)}}
        original = copy.deepcopy(fixture)
        args = create_profile.gotrue_service_request(fixture)
        environment = create_profile.gotrue_service_environment(fixture)
        request = create_profile.gotrue_service_execution_request(fixture)
        create_profile.validate_gotrue_service_intent(args, environment, request, fixture)
        if not create_profile._exact_tree(fixture, original):
            startup.fail('invalid_owner_handoff')
        current_services()
        try:
            dev._docker_request(request['method'], request['path'], request['body'], True)
        except dev.Refusal as error:
            if (error.stage, error.code) != ('docker', 'docker_request_invalid'):
                raise
        else:
            startup.fail('invalid_owner_handoff')
        current_services()
        if (not create_profile._exact_tree(self.images.get(selected), descriptor)
                or self.plan.get(selected) != descriptor['Id']
                or [ref for ref in self.images if ref.startswith(repository + '@sha256:')] != [selected]):
            startup.fail('execution_image_changed')
        self._gotrue_boundary_completed = True

    def execute_kong(self):
        """One retained-owner lifecycle, within the original PG execution budget."""
        import re
        if self.kong_create_attempted:
            startup.fail('invalid_owner_handoff')
        self.kong_create_attempted = True
        if (not self.kong_execution or not self._kong_boundary_completed or not self._tail_completed
                or self.phase != 5 or self._fixture is None or self._tail_custody is None
                or getattr(self, '_finish_attempted', False) or not self.auth_cli_terminated
                or not self.api_default_privileges_verified or not self.auth_job_exit_verified
                or not self.auth_job_disposed or not self.cli_db_backend_present_verified
                or not self.cli_db_backend_departure_verified or not self.auth_catalog_verified
                or not self.auth_catalog_precondition_verified or not self.api_default_privileges_request_refused):
            startup.fail('invalid_owner_handoff')
        self.auth_pg_current()
        pins = images.load_pins(dev.read(dev.ROOT / images.PINS))
        pin = next(item for item in pins['images'] if item['id'] == 'kong')
        repository = 'public.ecr.aws/' + pin['repository']
        selected = [ref for ref in self.images if ref.startswith(repository + '@sha256:')]
        if len(selected) != 1 or self.plan.get(selected[0]) != self.images[selected[0]]['Id']:
            startup.fail('invalid_owner_handoff')
        fixture = {'project': dev.project_identity(self.target, self.run_id),
                   'workdir': str(self._fixture[0]), 'network': self.network,
                   'selection_plan': {repository + ':' + pin['tag']: selected[0]},
                   'image_observations': self.images}
        self.kong_fixture = fixture
        status, image = self.session.exchange('GET', '/v1.48/images/' + selected[0] + '/json')
        if (status != 200 or type(image) is not dict or image.get('Id') != self.images[selected[0]]['Id']
                or image.get('Os') != 'linux' or image.get('Architecture') != 'amd64'
                or image.get('Variant', '') != ''):
            startup.fail('execution_image_changed')
        create_profile.validate_kong_image_config(image.get('Config'))
        args, environment = create_profile.kong_request(fixture), dict(create_profile.KONG_ENV)
        source, files = create_profile.kong_execution_request(fixture), create_profile.kong_transfer_files(fixture)
        request = create_profile.kong_disposable_execution_request(args, environment, source, files, fixture)
        create_profile.validate_kong_disposable_execution_request(request, fixture)
        archive = startup.lifecycle.kong_archive(files, fixture)
        startup.lifecycle.validate_kong_archive(archive, fixture)
        self.auth_pg_current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/supabase_kong_disposable_' + fixture['project'] + '/json',
                                           _kong_fixture=fixture)
        if status != 404:
            self.kong_creation_uncertain = True
            startup.fail('execution_existing_container')
        self.auth_pg_current()
        with dev.free_ports({'api': 55481}):
            self.check()
        self.kong_creation_uncertain = True
        status, response = self.session.exchange(request['method'], request['path'], request['body'], _kong_fixture=fixture)
        if (status != 201 or type(response) is not dict or set(response) != {'Id', 'Warnings'}
                or type(response['Id']) is not str or not re.fullmatch('[0-9a-f]{64}', response['Id'])
                or response['Id'] in {self.container_id, self.old_container_id, self.auth_job_created_id}
                or response['Warnings'] not in (None, [])):
            startup.fail('execution_uncertain_creation')
        self.kong_id = response['Id']
        self.kong_creation_uncertain = False
        self.kong_created()
        self.kong_copy_attempted = True
        status, _ = self.session.exchange('PUT', '/v1.48/containers/' + self.kong_id + '/archive?path=%2F', archive)
        if status != 200:
            startup.fail('execution_copy_failed')
        self.kong_created()
        self.kong_start_attempted = True
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.kong_id + '/start')
        if status != 204:
            startup.fail('execution_start_failed')
        while True:
            row = self.kong_owned()
            current = startup.lifecycle.shutdown_state(row)
            if self.kong_started_at is not None and current != self.kong_started_at:
                startup.fail('execution_instance_changed')
            self.kong_started_at = current
            health = row['State'].get('Health')
            if type(health) is not dict or health.get('Status') not in ('starting', 'healthy'):
                startup.fail('execution_invalid_health')
            if health['Status'] == 'healthy':
                break
            time.sleep(min(.1, max(0, self.remaining())))
        self.auth_pg_current()
        self.check()
        self.kong_healthy_verified = True

    def kong_owned(self):
        if self.ownership_lost or self.kong_id is None or self.kong_creation_uncertain:
            startup.fail('execution_ownership_changed')
        try:
            if self.container_id not in self.stopped_instances:
                self.auth_pg_current()
            else:
                pg = self.owned()
                if pg['State'].get('Running') is True:
                    if startup.lifecycle.shutdown_state(pg) != self.poststart_identity:
                        startup.fail('execution_instance_changed')
                else:
                    startup.lifecycle.shutdown_state(pg, self.poststart_identity)
            self.current()
            status, row = self.session.exchange('GET', '/v1.48/containers/' + self.kong_id + '/json')
            if status != 200 or type(row) is not dict:
                startup.fail('execution_ownership_changed')
            create_profile.validate_kong_container(row, self.kong_id, self.kong_fixture,
                                                  started=self.kong_started_at is not None)
            state = row['State']
            if state['Status'] == 'created':
                if (self.kong_started_at is not None or state['ExitCode'] != 0
                        or state.get('StartedAt') != '0001-01-01T00:00:00Z'
                        or state.get('FinishedAt') != '0001-01-01T00:00:00Z'):
                    startup.fail('execution_instance_changed')
            else:
                started = state.get('StartedAt')
                instant = startup.lifecycle.shutdown_timestamp(started)
                if self.kong_started_at is not None and started != self.kong_started_at:
                    startup.fail('execution_instance_changed')
                if state['Status'] == 'running':
                    if state['ExitCode'] != 0 or state.get('FinishedAt') != '0001-01-01T00:00:00Z':
                        startup.fail('execution_instance_changed')
                elif startup.lifecycle.shutdown_timestamp(state.get('FinishedAt')) <= instant:
                    startup.fail('execution_instance_changed')
            self.check()
            return row
        except dev.Refusal as error:
            if error.code != 'docker_timeout':
                self.ownership_lost = True
            raise
        except (KeyError, TypeError, ValueError, AttributeError):
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')

    def kong_created(self):
        row = self.kong_owned()
        if row['State']['Status'] != 'created':
            self.ownership_lost = True
            startup.fail('execution_ownership_changed')
        return row

    def stop_kong(self):
        if self.kong_stop_attempted:
            startup.fail('invalid_owner_handoff')
        self.kong_stop_attempted = True
        if not self.kong_healthy_verified or self.kong_started_at is None:
            startup.fail('invalid_owner_handoff')
        row = self.kong_owned()
        if startup.lifecycle.shutdown_state(row) != self.kong_started_at:
            startup.fail('execution_instance_changed')
        if row['State'].get('Health', {}).get('Status') != 'healthy':
            startup.fail('execution_invalid_health')
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.kong_id + '/stop?t=5')
        if status != 204:
            startup.fail('execution_stop_failed')
        startup.lifecycle.shutdown_state(self.kong_owned(), self.kong_started_at)
        self.kong_shutdown_verified = True

    def remove_kong(self, *, clean=False):
        if self.kong_delete_attempted or self.kong_id is None:
            startup.fail('execution_cleanup_unresolved')
        self.kong_delete_attempted = True
        row = self.kong_owned()
        if clean:
            if not self.kong_shutdown_verified:
                startup.fail('execution_cleanup_unresolved')
            startup.lifecycle.shutdown_state(row, self.kong_started_at)
        status, _ = self.session.exchange('DELETE', '/v1.48/containers/' + self.kong_id + '?force=' + ('false' if clean else 'true'))
        if status != 204:
            startup.fail('execution_cleanup_unresolved')
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/' + self.kong_id + '/json')
        if status != 404:
            startup.fail('execution_cleanup_unresolved')
        self.kong_id = None
        self.kong_disposed = True
        self.joint()

    def api_default_privileges_sql(self):
        if (not self.api_default_privileges or self.api_default_privileges_attempted
                or getattr(self, '_finish_attempted', False) or self.phase != 5
                or not self.cli_db_backend or not self.cli_db_backend_present_verified
                or not self.cli_db_backend_departure_verified or not self.auth_cli_terminated
                or not self.auth_catalog or not self.auth_catalog_precondition_verified
                or not self.auth_catalog_verified or not self.api_default_privileges_request_refused
                or not self.auth_job_exit_verified or not self.auth_job_disposed):
            startup.fail('invalid_owner_handoff')
        self.api_default_privileges_attempted = True
        for mode in ('apply', 'verify'):
            body = startup.lifecycle.api_default_privileges_bounded_exec(mode)
            import create_profile
            if not create_profile._exact_tree(body, startup.lifecycle._api_default_privileges_profile_bounded(mode)):
                startup.fail('invalid_owner_handoff')
            self._auth_owned_sql(body, self.auth_pg_current)
        self.auth_pg_current()
        self.api_default_privileges_verified = True

    def auth_catalog_sql(self, mode):
        if (getattr(self, '_finish_attempted', False) or not self.auth_catalog or not self.auth_cli_terminated or self.phase != 5
                or (self.cli_db_backend and not self.cli_db_backend_departure_verified)
                or mode not in ('pre', 'post') or mode in self.auth_catalog_attempts
                or (mode == 'pre' and (self.auth_catalog_attempts or self.auth_job_create_attempted))
                or (mode == 'post' and (not self.auth_catalog_precondition_verified
                    or not self.auth_job_exit_verified or not self.auth_job_disposed))):
            startup.fail('invalid_owner_handoff')
        self.auth_catalog_attempts.add(mode)
        body = startup.lifecycle.auth_catalog_exec(mode)
        def stable():
            self.auth_pg_current()
        self._auth_owned_sql(body, stable)
        if mode == 'post':
            # Construct the next source-derived setup request, but never exchange it.
            # Treat accidental allowlist expansion as failure, not execution authority.
            request = startup.lifecycle.api_default_privileges_exec()
            if not startup.lifecycle.valid_api_default_privileges_exec(request):
                startup.fail('invalid_owner_handoff')
            try:
                dev._docker_request('POST', '/v1.48/containers/' + self.container_id + '/exec', request, True)
            except dev.Refusal as error:
                if (error.stage, error.code) != ('docker', 'docker_request_invalid'):
                    raise
            else:
                startup.fail('invalid_owner_handoff')
        stable()

        if mode == 'pre':
            self.auth_catalog_precondition_verified = True
        else:
            self.api_default_privileges_request_refused = True
            self.auth_catalog_verified = True

    def healthy_instance(self):
        started = None
        while True:
            row = self.owned()
            current = startup.lifecycle.shutdown_state(row)
            if started is not None and current != started:
                startup.fail('execution_instance_changed')
            started = current
            health = row.get('State', {}).get('Health', {}).get('Status')
            if health == 'healthy':
                return started
            if health not in ('starting', 'unhealthy'):
                startup.fail('execution_invalid_health')
            time.sleep(min(.1, max(0, self.remaining())))

    def stop_instance(self, started):
        if self.phase != 5 or self.container_id in self.stopped_instances:
            startup.fail('invalid_owner_handoff')
        self.stopped_instances.add(self.container_id)
        self.check()
        if not self.kong_execution:
            self.deadline = self.session.deadline = time.monotonic() + 15
        elif self._shutdown_deadline is None or self.deadline != self._shutdown_deadline:
            startup.fail('invalid_owner_handoff')
        if startup.lifecycle.shutdown_state(self.owned()) != started:
            startup.fail('execution_instance_changed')
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/stop?t=5')
        if status != 204:
            startup.fail('execution_stop_failed')
        startup.lifecycle.shutdown_state(self.owned(), started)

    def remove_first(self, started):
        if (not self.persistence or self.phase != 5 or self.old_container_id is not None
                or self.container_id not in self.stopped_instances):
            startup.fail('invalid_owner_handoff')
        # Intermediate removal never consumes final disposal authority/budget.
        self.phase = 8
        startup.lifecycle.shutdown_state(self.owned(), started)
        old = self.container_id
        status, _ = self.session.exchange('DELETE', '/v1.48/containers/' + old + '?force=false')
        if status != 204:
            startup.fail('execution_cleanup_unresolved')
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/' + old + '/json')
        if status != 404:
            startup.fail('execution_cleanup_unresolved')
        self.old_container_id, self.container_id = old, None
        self.joint()  # Unused unchanged owned volume and empty bridge, before budget transition.
        self.check()
        self.deadline = self.session.deadline = time.monotonic() + 120
        self.start_attempted = False
        self.phase = 10 if self.initialized_cli else 9

    def recreate(self, started):
        if self.initialized_cli:
            startup.fail('invalid_owner_handoff')
        self.remove_first(started)
        self.container_create(*self._create_operands, _replacement=True)
        self.container_copy(['cp', '-', self.container_id + ':/'], startup.lifecycle.public_archive())
        self.container_start(['start', self.container_id])

    def prepare_initialized_cli(self):
        if not self.initialized_cli or self.old_container_id is not None or self.phase != 5:
            startup.fail('invalid_owner_handoff')
        if getattr(self, '_initialized_prepare_attempted', False):
            startup.fail('invalid_owner_handoff')
        self._initialized_prepare_attempted = True
        started = self.healthy_instance()
        self.persistence_sql('write', started)
        self.persistence_sql('schemas', started)
        self.stop_instance(started)
        self.remove_first(started)

    def finish_execution(self):
        # Every finish attempt is terminal, including a failed prerequisite.
        if getattr(self, '_finish_attempted', False):
            startup.fail('invalid_owner_handoff')
        self._finish_attempted = True
        if self.phase != 5:
            startup.fail('invalid_owner_handoff')
        if self.auth_boundary and not (self.auth_job_refused or (self.auth_migration and self.auth_job_exit_verified and self.auth_job_disposed)):
            startup.fail('invalid_owner_handoff')
        if self.cli_db_backend and not self.cli_db_backend_departure_verified:
            startup.fail('invalid_owner_handoff')
        if self.auth_catalog and not (self.auth_catalog_verified and self.api_default_privileges_request_refused):
            startup.fail('invalid_owner_handoff')
        if self.api_default_privileges and not self.api_default_privileges_verified:
            startup.fail('invalid_owner_handoff')
        if self.kong_boundary and not self._kong_boundary_completed:
            startup.fail('invalid_owner_handoff')
        if self.kong_execution and not self.kong_healthy_verified:
            startup.fail('invalid_owner_handoff')
        if self.post_auth_setup_tail and not self._tail_completed:
            startup.fail('invalid_owner_handoff')
        started = self.healthy_instance()
        if self.auth_boundary and started != self.poststart_identity:
            startup.fail('execution_instance_changed')
        if self.initialized_cli and self.old_container_id is None:
            startup.fail('invalid_owner_handoff')
        if self.persistence and not self.initialized_cli:
            self.persistence_sql('write', started)
            self.persistence_sql('schemas', started)
        if self.kong_execution:
            self.check()
            self._shutdown_deadline = time.monotonic() + 15
            self.deadline = self.session.deadline = self._shutdown_deadline
            self.stop_kong()
        if not self.initialized_cli:
            self.stop_instance(started)
        if self.persistence:
            if not self.initialized_cli:
                self.recreate(started)
            started = self.healthy_instance()
            self.persistence_sql('verify', started)
            self.persistence_sql('schemas', started)
            self.stop_instance(started)
            self.persistence_verified = True
        self.phase = 6
        self.cleanup_execution(clean=True, started=started)
        if self.post_auth_setup_tail:
            self.current()
            self.owner_post_auth_setup_tail_verified = True
        if self.kong_boundary:
            self.current()
            self.owner_kong_boundary_verified = True
        if self.kong_execution:
            self.current()
            if not (self.kong_disposed and self.kong_shutdown_verified and self.cleaned):
                startup.fail('execution_cleanup_unresolved')
            self.owner_kong_execution_verified = True

    def cleanup_execution(self, *, clean=False, started=None):
        """Consume one cleanup budget; never replay a mutation or recover lost ownership."""
        if self.cleanup_attempted:
            startup.fail('execution_cleanup_unresolved')
        self.cleanup_attempted = True
        self.deadline = self.session.deadline = time.monotonic() + 10
        if self.container_id is None or self.ownership_lost or self.session.closed or self.phase == 8 or self.auth_job_creation_uncertain or self.kong_creation_uncertain:
            startup.fail('execution_cleanup_unresolved')
        if self.kong_id is not None:
            self.remove_kong(clean=clean)
        if self.auth_job_id is not None:
            self.remove_auth_job()
        row = self.owned()
        if clean:
            startup.lifecycle.shutdown_state(row, started)
        status, _ = self.session.exchange('DELETE', '/v1.48/containers/' + self.container_id + '?force=' + ('false' if clean else 'true'))
        if status != 204:
            startup.fail('execution_cleanup_unresolved')
        self.current()
        status, _ = self.session.exchange('GET', '/v1.48/containers/' + self.container_id + '/json')
        if status != 404:
            startup.fail('execution_cleanup_unresolved')
        self.container_id = None
        self.joint()
        status, _ = self.session.exchange('DELETE', volumes.PREFIX + self.volume['Name'])
        if status != 204:
            startup.fail('execution_cleanup_unresolved')
        status, _ = self.session.exchange('GET', volumes.PREFIX + self.volume['Name'])
        if status != 404:
            startup.fail('execution_cleanup_unresolved')
        self.volume = None
        self.joint()
        if self.network_created:
            status, _ = self.session.exchange('DELETE', networks.PREFIX + self.network['Id'])
            if status != 204:
                startup.fail('execution_cleanup_unresolved')
            status, _ = self.session.exchange('GET', networks.PREFIX + self.network['Id'])
            if status != 404:
                startup.fail('execution_cleanup_unresolved')
        self.cleaned = True
        self.phase = 7


def invocation(target_path, run_id, executable, work, *, _socket_path='/var/run/docker.sock'):
    """Immediate construction only; fresh execution uses the retained context."""
    with fresh_session(target_path, run_id, executable, work, _socket_path=_socket_path) as guard:
        result = guard.command
    return result
