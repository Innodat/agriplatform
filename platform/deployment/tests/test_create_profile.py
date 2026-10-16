"""Independent complete PG17 requests, adversarial profile and input custody proof."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import startup
import create_profile
from create_profile_fixtures import (expected_request, expected_environment, expected_execution_request, boundary_fixture,
                                     target_fixture, test_plan, test_observations, RUN, SYNTHETIC_CLI_SOURCE)


def profile_rejection():
    return {'kind': 'rejected', 'reason': 'unsafe_create', 'command': ['create', 'other'],
            'flags': ['--entrypoint', '--label', '--name', '--network', '-e', '-p', '-v']}


class CompleteCreateProfile(unittest.TestCase):
    def setUp(self):
        self.f = boundary_fixture()
        self.args, self.env = expected_request(self.f), expected_environment(self.f)

    def test_refused_create_proves_closed_execution_request(self):
        events = []
        code, _, _ = startup.fixture_command('docker', self.args, self.f, events, environment=self.env)
        self.assertEqual(code, 125)
        self.assertTrue(events[0]['facts']['create_request_proven'])

    def selected_inputs(self):
        f = copy.deepcopy(self.f)
        f['postgres_image'] = f['selection_plan'][f['postgres_image']]
        return expected_request(f), f, self.env.copy()

    def test_review_host_port_requires_exact_valid_integer(self):
        for port in [True, False, 0, -1, 65536, 'nonnumeric', '55482', 55482.0]:
            args, f, env = self.selected_inputs()
            f['database_port'] = port
            with self.subTest(port=port), self.assertRaises(dev.Refusal):
                create_profile.execution_request(expected_request(f), f, env)

    def test_review_unconstructed_facts_have_no_request_attestation(self):
        self.assertNotIn('create_request_proven', startup.selected_facts(self.f))
        self.assertNotIn('create_request_proven', startup.create_facts(self.args, self.f, environment=self.env))

    def test_review_nested_inherited_environment_custody(self):
        for seam in ['transform', 'constructor']:
            args, env, fixture = copy.deepcopy((self.args, self.env, self.f))
            env['UNRELATED'] = {'values': ['original']}
            transform = startup.immutable_first_create
            constructor = create_profile.execution_request
            def corrupt_transform(argv, f, plan, *, environment):
                result = transform(argv, f, plan, environment=environment)
                environment['UNRELATED']['values'].append('changed')
                return result
            def corrupt_constructor(argv, f, inherited):
                result = constructor(argv, f, inherited)
                inherited['UNRELATED']['values'].append('changed')
                env['UNRELATED']['values'].append('changed')
                return result
            events = []
            target, name, effect = ((startup, 'immutable_first_create', corrupt_transform) if seam == 'transform'
                                    else (create_profile, 'execution_request', corrupt_constructor))
            with self.subTest(seam=seam), patch.object(target, name, side_effect=effect):
                with self.assertRaises(dev.Refusal):
                    startup.fixture_command('docker', args, fixture, events, environment=env)
                self.assertEqual(events, [])

    def test_review_corrupt_request_control_requires_valid_construction_baseline(self):
        for failure in ['constructor', 'validator']:
            def execute(command, work, env, timeout, limit):
                f = startup.decode_fixture(work / 'fixture.json')
                events = ([{'kind': 'container_inspect'}]
                          + [{'kind': 'image_inspect', 'image_index': i,
                              'descriptor': f['image_observations'][f['selection_plan'][tag]]}
                             for i, tag in enumerate(f['images'])]
                          + [{'kind': 'volume_inspect'}, {'kind': 'network_inspect'},
                             {'kind': 'existing_volume_create_refused'}])
                (work / 'events.json').write_text(json.dumps(events))
                function = 'execution_request' if failure == 'constructor' else 'validate_execution_request'
                with patch.object(create_profile, function, side_effect=dev.Refusal('startup', 'unsafe_create')):
                    startup.fixture_main('docker', expected_request(f), work,
                                         environment=expected_environment(f), profile_control='invalid-create-request')
                raise dev.Refusal('images_cli', 'command_refused')
            with self.subTest(failure=failure), patch.object(startup.images, 'bounded_command', side_effect=execute):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/unused'), target_fixture(), RUN, control='invalid-create-request',
                                            selection_plan=test_plan(), image_observations=test_observations())
            self.assertEqual(caught.exception.code, 'boundary_not_proven')

    def test_execution_request_independent_full_oracle_and_detachment(self):
        args, f, env = self.selected_inputs()
        before = copy.deepcopy((args, f, env))
        env['UNRELATED'] = 'sensitive-canary'
        with patch.dict(os.environ, {'AMBIENT_SECRET': 'sensitive-canary'}):
            actual = create_profile.execution_request(args, f, env)
        self.assertEqual(actual, expected_execution_request(f))
        self.assertNotIn('sensitive-canary', json.dumps(actual))
        env.pop('UNRELATED')
        self.assertEqual((args, f, env), before)
        actual['body']['Env'].clear()
        actual['body']['NetworkingConfig']['EndpointsConfig'].clear()
        self.assertEqual(create_profile.execution_request(args, f, env), expected_execution_request(f))
        self.assertEqual((args, f, env), before)

    def test_every_execution_node_rejects_missing_extra_value_and_primitive_type(self):
        args, f, env = self.selected_inputs()
        expected = expected_execution_request(f)
        paths = []
        def visit(value, path=()):
            paths.append(path)
            if type(value) is dict:
                for key, item in value.items(): visit(item, path + (key,))
            elif type(value) is list:
                for key, item in enumerate(value): visit(item, path + (key,))
        visit(expected)
        for path in paths:
            node = expected
            for key in path: node = node[key]
            replacements = [None, True, 0.0, 'sensitive-canary', [], {}]
            if type(node) is int: replacements += [float(node), bool(node)]
            if type(node) is dict: replacements += [dict(node, unexpected=True)]
            if type(node) is list: replacements += [node + ['sensitive-canary'], tuple(node)]
            for replacement in replacements:
                if type(replacement) is type(node) and replacement == node: continue
                changed = copy.deepcopy(expected)
                if not path: changed = replacement
                else:
                    parent = changed
                    for key in path[:-1]: parent = parent[key]
                    parent[path[-1]] = replacement
                with self.subTest(path=path, replacement=type(replacement)), self.assertRaises(dev.Refusal):
                    create_profile.validate_execution_request(changed, args, f, env)
            if path:
                changed = copy.deepcopy(expected)
                parent = changed
                for key in path[:-1]: parent = parent[key]
                del parent[path[-1]]
                with self.subTest(missing=path), self.assertRaises(dev.Refusal):
                    create_profile.validate_execution_request(changed, args, f, env)

    def test_boundary_rejects_constructor_corruption_and_custody_mutations(self):
        original = create_profile.execution_request
        for mutation in ['body', 'args', 'env', 'fixture', 'fixture-type', 'caller-args', 'caller-env', 'caller-fixture']:
            args, env, f = copy.deepcopy((self.args, self.env, self.f))
            def corrupt(argv, fixture, inherited):
                actual = original(argv, fixture, inherited)
                if mutation == 'body': actual['body']['HostConfig']['RestartPolicy']['MaximumRetryCount'] = False
                if mutation == 'args': argv[-1] = 'sensitive-canary'
                if mutation == 'env': inherited['JWT_EXP'] = '1'
                if mutation == 'fixture': fixture['network']['Id'] = 'foreign'
                if mutation == 'fixture-type': fixture['network']['Internal'] = 0
                if mutation == 'caller-args': args[-1] = 'sensitive-canary'
                if mutation == 'caller-env': env['JWT_EXP'] = '1'
                if mutation == 'caller-fixture': f['network']['Id'] = 'foreign'
                return actual
            events = []
            with self.subTest(mutation=mutation), patch.object(create_profile, 'execution_request', side_effect=corrupt):
                with self.assertRaises(dev.Refusal):
                    startup.fixture_command('docker', args, f, events, environment=env)
            self.assertEqual(events, [])

    def test_request_dispatch_refused_before_socket_access(self):
        args, f, env = self.selected_inputs()
        actual = create_profile.execution_request(args, f, env)
        with patch.object(dev.socket, 'socket') as socket, self.assertRaises(dev.Refusal) as caught:
            dev.docker_exchange(actual['method'], actual['path'], actual['body'])
        self.assertEqual(caught.exception.code, 'docker_request_invalid')
        socket.assert_not_called()

    def test_execution_requires_selected_pinned_postgres_child(self):
        for image in [self.f['postgres_image'], 'foreign/postgres@sha256:' + '1' * 64,
                      'public.ecr.aws/supabase/postgres@sha256:' + '1' * 64,
                      'public.ecr.aws/supabase/postgres@sha256:bad',
                      next(value for value in test_plan().values() if '/gotrue@' in value)]:
            f = dict(self.f, postgres_image=image)
            with self.subTest(image=image), self.assertRaises(dev.Refusal):
                create_profile.execution_request(expected_request(f), f, self.env)

    def test_coherently_changed_network_is_refused_before_construction(self):
        for key, value in [('Labels', {}), ('Options', {}), ('Name', 'foreign'), ('Containers', {'foreign': {}})]:
            f = copy.deepcopy(self.f)
            f['network'][key] = value
            with self.subTest(key=key), patch.object(create_profile, 'execution_request') as constructor:
                with self.assertRaises(dev.Refusal):
                    startup.fixture_command('docker', expected_request(f), f, [], environment=self.env)
                constructor.assert_not_called()

    def rejected(self, args=None, env=None):
        events = []
        with self.assertRaises(dev.Refusal) as caught:
            startup.fixture_command('docker', self.args if args is None else args, self.f, events,
                                    environment=self.env if env is None else env)
        self.assertIn(caught.exception.code, ['unsafe_create', 'unexpected_container_command'])
        self.assertEqual(events, [])
        self.assertNotIn('sensitive-canary', str(caught.exception))

    def test_list_and_tuple_create_are_equivalent(self):
        records = []
        for args in [self.args, tuple(self.args)]:
            events = []
            result = startup.fixture_command('docker', args, self.f, events, environment=self.env)
            records.append((result, events))
        self.assertEqual(records[0], records[1])

    def test_validator_malformed_inputs_and_resource_limits(self):
        for args in [None, {}, 'create', b'create', iter(self.args), [None], [1], [True],
                     ['create'] * 257, ['x' * 65537]]:
            with self.subTest(kind=type(args).__name__), patch.object(create_profile, 'request') as request:
                with self.assertRaises(dev.Refusal):
                    create_profile.validate(args, self.f, self.env)
                request.assert_not_called()
        for env in [None, [], (), 'sensitive-canary', {'JWT_SECRET': None},
                    {**self.env, 'JWT_EXP': 3600}, {**self.env, 'POSTGRES_HOST': b'/var/run/postgresql'}]:
            with self.subTest(kind=type(env).__name__), self.assertRaises(dev.Refusal):
                create_profile.validate(self.args, self.f, env)
        # Boundary sizes reach profile comparison; exceeding either bound refuses
        # before consulting authority or returning any selected facts.
        for args in [['x'] * 256, ['x' * 65536]]:
            with patch.object(create_profile, 'request', return_value=self.args) as request:
                with self.assertRaises(dev.Refusal):
                    create_profile.validate(args, self.f, self.env)
                request.assert_called_once_with(self.f)

    def test_controls_reject_invalid_original_profile_before_injection(self):
        for baseline in ['args[-1] += "sensitive-canary"',
                         'os.environ["JWT_SECRET"] = "sensitive-canary"',
                         'os.environ["DOCKER_TLS"] = "sensitive-canary"']:
            with tempfile.TemporaryDirectory() as directory:
                executable = Path(directory) / 'synthetic-cli'
                source = SYNTHETIC_CLI_SOURCE.replace('commands = ', baseline + '\ncommands = ', 1)
                executable.write_text('#!' + sys.executable + '\n' + source)
                executable.chmod(0o700)
                for control in ['invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request']:
                    with self.subTest(baseline=baseline, control=control), self.assertRaises(dev.Refusal) as caught:
                        startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                                selection_plan=test_plan(), image_observations=test_observations())
                    self.assertEqual(caught.exception.code, 'boundary_not_proven')
                    self.assertNotIn('sensitive-canary', str(caught.exception))

    def test_negative_controls_require_exact_prerequisite_sequence(self):
        for mutation in ['missing', 'duplicate', 'reordered', 'earlier-positive']:
            def execute(command, work, env, timeout, limit):
                f = startup.decode_fixture(work / 'fixture.json')
                events = ([{'kind': 'container_inspect'}]
                          + [{'kind': 'image_inspect', 'image_index': i,
                              'descriptor': f['image_observations'][f['selection_plan'][tag]]}
                             for i, tag in enumerate(f['images'])]
                          + [{'kind': 'volume_inspect'}, {'kind': 'network_inspect'},
                             {'kind': 'existing_volume_create_refused'}])
                if mutation == 'missing': events.pop(5)
                if mutation == 'duplicate': events.insert(5, events[5])
                if mutation == 'reordered': events[5], events[6] = events[6], events[5]
                if mutation == 'earlier-positive': events.append({'kind': 'postgres_create', 'facts': {}})
                (work / 'events.json').write_text(json.dumps(events + [profile_rejection()]))
                raise dev.Refusal('images_cli', 'command_refused')
            with self.subTest(mutation=mutation), patch.object(startup.images, 'bounded_command', side_effect=execute):
                with self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(Path('/unused'), target_fixture(), RUN, control='invalid-create-script',
                                            selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, 'boundary_not_proven')

    def test_public_source_fixture_digest_and_unchanged_input(self):
        self.assertEqual(hashlib.sha256(self.args[-1].encode()).hexdigest(),
                         '6f995b129657d28b15a97a1c8a957a7c0015a9865880747c25ad00e3b6d7dd86')
        before = copy.deepcopy((self.args, self.env, self.f))
        events = []
        result = startup.fixture_command('docker', self.args, self.f, events, environment=self.env)
        self.assertEqual(result[0], 125)
        self.assertEqual(before, (self.args, self.env, self.f))
        self.assertTrue(events[0]['facts']['complete_create_profile_proven'])

    def test_every_operand_change_deletion_duplicate_and_reordering_refused(self):
        for i in range(len(self.args)):
            for variant in [self.args[:i] + ['sensitive-canary'] + self.args[i+1:],
                            self.args[:i] + self.args[i+1:],
                            self.args[:i] + [self.args[i]] + self.args[i:]]:
                with self.subTest(index=i):
                    self.rejected(variant)
        for i in range(1, len(self.args)-4, 2):
            changed = self.args.copy()
            changed[i:i+4] = changed[i+2:i+4] + changed[i:i+2]
            if changed != self.args:
                self.rejected(changed)
        for script in [self.args[-1]+'\nsensitive-canary', self.args[-1].replace('/etc/postgresql', '/sensitive-canary'),
                       self.args[-1].replace('$JWT_SECRET', 'sensitive-canary'), 'sensitive-canary']:
            self.rejected(self.args[:-1]+[script])

    def test_environment_missing_changed_routing_inline_and_extra_names(self):
        for key in self.env:
            missing = dict(self.env)
            missing.pop(key)
            self.rejected(env=missing)
            self.rejected(env={**self.env, key: 'sensitive-canary'})
        for key in ['DOCKER_CONTEXT', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH', 'DOCKER_API_VERSION',
                    'DOCKER_TLS', 'DOCKER_DEFAULT_PLATFORM', 'DOCKER_CUSTOM_HEADERS']:
            for value in ['', 'sensitive-canary']:
                self.rejected(env={**self.env, key: value})
        for name in ['EXTRA', 'POSTGRES_PASSWORD=sensitive-canary']:
            self.rejected(self.args[:3]+['-e', name]+self.args[3:])
        events = []
        startup.fixture_command('docker', self.args, self.f, events,
                                environment={**self.env, 'UNRELATED': 'sensitive-canary'})
        self.assertNotIn('sensitive-canary', json.dumps(events))
        with self.assertRaises(dev.Refusal):
            startup.fixture_command('docker', self.args, self.f, [])

    def test_environment_or_arguments_mutation_during_transform_refused(self):
        original = startup.immutable_first_create
        for mutation in ['env-copy', 'env-caller', 'args-copy', 'args-caller', 'fixture', 'result']:
            args, env, fixture = copy.deepcopy((self.args, self.env, self.f))
            def corrupt(argv, f, plan, *, environment):
                selected = original(argv, f, plan, environment=environment)
                if mutation == 'env-copy': environment['JWT_SECRET'] = 'sensitive-canary'
                if mutation == 'env-caller': env['JWT_SECRET'] = 'sensitive-canary'
                if mutation == 'args-copy': argv[-1] = 'sensitive-canary'
                if mutation == 'args-caller': args[-1] = 'sensitive-canary'
                if mutation == 'fixture': f['database_port'] = 1
                if mutation == 'result': selected[-1] = 'sensitive-canary'
                return selected
            events = []
            with self.subTest(mutation=mutation), patch.object(startup, 'immutable_first_create', side_effect=corrupt):
                with self.assertRaises(dev.Refusal):
                    startup.fixture_command('docker', args, fixture, events, environment=env)
            self.assertEqual(events, [])
            if mutation not in ['env-caller', 'args-caller']:
                self.assertEqual((args, env, fixture), (self.args, self.env, self.f))

    def test_public_profile_controls_reach_same_process_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / 'synthetic-cli'
            executable.write_text('#!' + sys.executable + '\n' + SYNTHETIC_CLI_SOURCE)
            executable.chmod(0o700)
            for control in ['invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request']:
                with self.subTest(control=control), self.assertRaises(dev.Refusal) as caught:
                    startup.synthetic_probe(executable, target_fixture(), RUN, control=control,
                                            selection_plan=test_plan(), image_observations=test_observations())
                self.assertEqual(caught.exception.code, 'expected_create_profile_rejected')

    def test_real_wrapper_forwards_environment_and_safely_rejects_canaries(self):
        for mutation in ['none', 'env', 'script', 'routing']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                target = target_fixture()
                network = startup.fixture_network(target, RUN)
                startup.initialize_workdir(work, target, RUN)
                startup.install_fixture(work, target, RUN, network, guard_parent=False,
                                        selection_plan=test_plan(), image_observations=test_observations())
                f = startup.decode_fixture(work/'fixture.json')
                args, env = expected_request(f), expected_environment(f)
                if mutation == 'env': env['JWT_SECRET'] = 'sensitive-canary'
                if mutation == 'script': args[-1] += 'sensitive-canary'
                if mutation == 'routing': env['DOCKER_CONTEXT'] = 'sensitive-canary'
                result = subprocess.run([str(work/'bin/docker'), *args], env=env, capture_output=True, text=True)
                events = startup.decode_fixture(work/'events.json')
                self.assertEqual(result.returncode, 125)
                self.assertNotIn('sensitive-canary', result.stdout + result.stderr + json.dumps(events))
                if mutation == 'none':
                    self.assertEqual(events, [{'kind': 'postgres_create', 'facts': {
                        'image': test_plan()[f['postgres_image']], 'name': 'supabase_db_' + f['project'],
                        'network': network['Id'], 'publish': '55482:5432',
                        'database_volume': 'supabase_db_' + f['project'], 'host_bind_mounts': False,
                        'create_refused': True, 'complete_create_profile_proven': True,
                        'original_image': f['postgres_image'], 'immutable_selection_proven': True,
                        'create_request_proven': True}}])
                else:
                    self.assertEqual(events, [profile_rejection()])


if __name__ == '__main__':
    unittest.main()
