"""Retain ENV image, bridge and volume custody on one bounded owner peer.

Default startup controls stay synthetic. The explicit pinned-CLI PostgreSQL proof
extends this owner through disposable execution, observed shutdown and cleanup;
full environment admission remains gated. Owner tool probes remain outside the
five-second acquisition phase, and no public daemon endpoint selector is exposed.
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
        try:
            self._current()
            if self._fixture is not None:
                startup.check_fixture_custody(*self._fixture, self.target, self.run_id,
                                              listener_identity=self._listener_identity)
        except dev.Refusal as error:
            if error.code != 'docker_timeout':
                self.ownership_lost = True
            raise

    def check(self):
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
                if type(members) is not dict or set(members) - {self.container_id}:
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
        self.deadline = self.session.deadline = time.monotonic() + 15
        if startup.lifecycle.shutdown_state(self.owned()) != started:
            startup.fail('execution_instance_changed')
        status, _ = self.session.exchange('POST', '/v1.48/containers/' + self.container_id + '/stop?t=5')
        if status != 204:
            startup.fail('execution_stop_failed')
        startup.lifecycle.shutdown_state(self.owned(), started)

    def recreate(self, started):
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
        self.phase = 9
        self.start_attempted = False
        self.container_create(*self._create_operands, _replacement=True)
        self.container_copy(['cp', '-', self.container_id + ':/'], startup.lifecycle.public_archive())
        self.container_start(['start', self.container_id])

    def finish_execution(self):
        if self.phase != 5:
            startup.fail('invalid_owner_handoff')
        # Consume finish before any mutation; SQL/lifecycle helpers require phase5.
        if getattr(self, '_finish_attempted', False):
            startup.fail('invalid_owner_handoff')
        self._finish_attempted = True
        started = self.healthy_instance()
        if self.persistence:
            self.persistence_sql('write', started)
            self.persistence_sql('schemas', started)
        self.stop_instance(started)
        if self.persistence:
            self.recreate(started)
            started = self.healthy_instance()
            self.persistence_sql('verify', started)
            self.persistence_sql('schemas', started)
            self.stop_instance(started)
            self.persistence_verified = True
        self.phase = 6
        self.cleanup_execution(clean=True, started=started)

    def cleanup_execution(self, *, clean=False, started=None):
        """Consume one cleanup budget; never replay a mutation or recover lost ownership."""
        if self.cleanup_attempted:
            startup.fail('execution_cleanup_unresolved')
        self.cleanup_attempted = True
        self.deadline = self.session.deadline = time.monotonic() + 10
        if self.container_id is None or self.ownership_lost or self.session.closed or self.phase == 8:
            startup.fail('execution_cleanup_unresolved')
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
