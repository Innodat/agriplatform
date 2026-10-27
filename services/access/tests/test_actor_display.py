"""Synthetic Identity owner HTTP acceptance; no native retention/privilege claim."""
import sys
import asyncio
import json
import time
from uuid import UUID
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from actor_display_http import create_app, ActorDisplayPolicy, ACTIVE, PREVIOUS, ORG as ORG_SETTING
from actor_display_contract import ActorDisplayResponse, ActorDisplayRequest

ORG = '33333333-3333-4333-8333-333333333333'
ACTOR = '44444444-4444-4444-8444-444444444444'
KEY = 'synthetic-actor-display-key-only-0001'
PATH = '/v2/identity/actor-displays'


def config(**extra):
    return {ACTIVE: KEY, ORG_SETTING: ORG, **extra}


class Projection:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else [{'actor_id': UUID(ACTOR), 'display_name': 'Retained actor'}]
        self.calls = []

    async def __call__(self, actor_ids, deadline):
        self.calls.append((actor_ids, deadline))
        return self.rows


def owner_app():
    return create_app(config(), Projection())


async def post_async(app, body=None, *, headers=None, content=None, path=PATH):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://owner') as client:
        return await client.post(path, json=body if content is None else None, content=content,
                                 headers={'X-Service-Key': KEY, 'Content-Type': 'application/json'} if headers is None else headers)


def post(app, body=None, **kwargs):
    return asyncio.run(post_async(app, {'org_id': ORG, 'actor_ids': [ACTOR]} if body is None else body, **kwargs))


def assert_error(response, status):
    assert response.status_code == status, response.text
    assert response.headers['cache-control'] == 'private, no-store'
    assert response.json() == {'error_id': {403: 'service_access_denied', 422: 'validation_failed', 503: 'identity.actor_display_unavailable'}[status],
                               'error': 'Request could not be completed', 'details': {}}
    assert len(response.content) <= 1024


def test_retained_labels_http_acceptance():
    async def post():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=owner_app()), base_url='http://owner') as client:
            return await client.post(PATH, json={'org_id': ORG, 'actor_ids': [ACTOR]}, headers={'X-Service-Key': KEY})
    response = asyncio.run(post())
    assert response.status_code == 200, response.text
    assert response.json() == {'org_id': ORG, 'labels': [
        {'actor_id': ACTOR, 'status': 'resolved', 'display_name': 'Retained actor'},
    ]}
    assert response.headers['cache-control'] == 'private, no-store'


def ids(count):
    return [str(UUID(int=i + 1)) for i in range(count)]


def test_retained_lifecycle_rename_and_order_are_identity_only():
    # Synthetic labels simulate lifecycle, not a claim about actual Auth retention.
    selected = ids(6)
    names = ['Retained account', 'Removed account', 'System', 'Migrate', 'Registered service']
    projection = Projection([{'actor_id': UUID(actor), 'display_name': name} for actor, name in reversed(list(zip(selected, names)))])
    app = create_app(config(), projection)
    body = {'org_id': ORG, 'actor_ids': selected}
    before = post(app, body)
    assert before.status_code == 200
    assert [row['actor_id'] for row in before.json()['labels']] == selected
    assert [row.get('display_name') for row in before.json()['labels']] == names + [None]
    assert before.json()['labels'][-1] == {'actor_id': selected[-1], 'status': 'unavailable'}
    projection.rows[-1]['display_name'] = 'Renamed account'
    after = post(app, body)
    assert [row['actor_id'] for row in after.json()['labels']] == selected
    assert after.json()['labels'][0]['display_name'] == 'Renamed account'
    assert projection.calls[0][0] == tuple(UUID(actor) for actor in selected)
    assert isinstance(projection.calls[0][1], float)


@pytest.mark.parametrize('headers', [
    {}, {'Authorization': 'Bearer end-user'}, {'X-Service-Key': 'wrong-service'},
    [('X-Service-Key', KEY), ('X-Service-Key', KEY)],
    {'X-Service-Key': KEY, 'Authorization': ''}, {'X-Service-Key': KEY, 'Authorization': 'Bearer user'},
])
def test_header_denials_before_body_or_projection(headers):
    projection = Projection()
    assert_error(post(create_app(config(), projection), headers=headers, content=b'bad private payload'), 403)
    assert not projection.calls


def test_disabled_and_header_denials_do_not_read_input():
    async def execute(configuration, headers):
        reads = []
        async def receive():
            reads.append(True)
            raise AssertionError('body read')
        sent = []
        async def send(message):
            sent.append(message)
        scope = {'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1', 'method': 'POST',
                 'scheme': 'http', 'path': PATH, 'raw_path': PATH.encode(), 'query_string': b'',
                 'root_path': '', 'headers': headers, 'client': ('test', 1), 'server': ('owner', 80)}
        projection = Projection()
        await create_app(configuration, projection)(scope, receive, send)
        assert sent[0]['status'] == 403 and not reads and not projection.calls
        assert (b'cache-control', b'private, no-store') in sent[0]['headers']
    asyncio.run(execute({}, [(b'x-service-key', KEY.encode())]))
    asyncio.run(execute(config(), [(b'x-service-key', KEY.encode()), (b'authorization', b'')]))


@pytest.mark.parametrize('configuration', [
    {ACTIVE: KEY}, {ORG_SETTING: ORG}, {PREVIOUS: KEY}, config(**{ACTIVE: ''}),
    config(**{PREVIOUS: ''}), config(**{PREVIOUS: KEY}), config(**{ACTIVE: 'short'}),
    config(**{ACTIVE: 'x' * 257}), config(**{ACTIVE: 'a' * 31 + ' '}), config(**{ACTIVE: 'é' * 32}),
    config(**{ORG_SETTING: '00000000-0000-0000-0000-000000000000'}),
    config(**{ORG_SETTING: '{' + ORG + '}'}), config(**{'OTHER_SERVICE_KEY': KEY}),
    config(**{PREVIOUS: 'previous-synthetic-key-for-tests-0001', 'ACCESS_SERVICE_KEY': 'previous-synthetic-key-for-tests-0001'}),
])
def test_configuration_invalid_is_safe(configuration, caplog):
    with pytest.raises(RuntimeError, match='^actor_display_configuration_invalid$') as failure:
        ActorDisplayPolicy(configuration)
    assert KEY not in str(failure.value) and KEY not in caplog.text


def test_policy_redaction_rotation_same_org_and_no_ambient_config(monkeypatch):
    previous = 'previous-synthetic-key-for-tests-0001'
    policy = ActorDisplayPolicy(config(**{PREVIOUS: previous}))
    assert KEY not in repr(policy) and previous not in repr(policy) and ORG not in repr(policy)
    projection = Projection()
    app = create_app(config(**{PREVIOUS: previous}), projection)
    for key in (KEY, previous):
        assert post(app, headers={'X-Service-Key': key, 'Content-Type': 'application/json'}).status_code == 200
        assert_error(post(app, {'org_id': ACTOR, 'actor_ids': [ACTOR]}, headers={'X-Service-Key': key, 'Content-Type': 'application/json'}), 403)
    assert len(projection.calls) == 2
    monkeypatch.setenv(ACTIVE, KEY)
    monkeypatch.setenv(ORG_SETTING, ORG)
    assert_error(post(create_app({}, Projection())), 403)
    assert_error(post(create_app(config(), Projection()), headers={'X-Service-Key': previous}), 403)


@pytest.mark.parametrize('body', [
    {}, [], None, {'org_id': ORG, 'actor_ids': []}, {'org_id': ORG, 'actor_ids': ids(204)},
    {'org_id': ORG, 'actor_ids': [ACTOR, ACTOR]}, {'org_id': ORG, 'actor_ids': ids(2)[::-1]},
    {'org_id': ORG, 'actor_ids': [ACTOR], 'account_id': ACTOR},
    {'org_id': ORG, 'actor_ids': [1]}, {'org_id': ORG, 'actor_ids': [ACTOR.replace('-', '')]},
    {'org_id': ORG, 'actor_ids': ['aaaaaaaa-AAAA-4aaa-8aaa-aaaaaaaaaaaa']},
    {'org_id': ORG, 'actor_ids': ['00000000-0000-0000-0000-000000000000']},
    {'org_id': '00000000-0000-0000-0000-000000000000', 'actor_ids': [ACTOR]},
    {'org_id': 1, 'actor_ids': [ACTOR]},
])
def test_closed_request_rejects_before_projection(body):
    projection = Projection()
    # Explicit encoding preserves null instead of the helper's default body.
    assert_error(post(create_app(config(), projection), content=json.dumps(body).encode()), 422)
    assert not projection.calls


@pytest.mark.parametrize('raw', [
    b'{', b'\xff', b'{"org_id":"' + ORG.encode() + b'","org_id":"' + ORG.encode() + b'","actor_ids":[]}',
    b'{"org_id":NaN,"actor_ids":[]}', b'[]', b'null',
    json.dumps({'org_id': ORG, 'actor_ids': [ACTOR]}).encode() + b' ' * 16384,
])
def test_json_encoding_and_size_rejects_before_projection(raw):
    projection = Projection()
    assert_error(post(create_app(config(), projection), content=raw), 422)
    assert not projection.calls


def test_content_type_query_and_streamed_actual_bytes():
    projection = Projection()
    app = create_app(config(), projection)
    assert_error(post(app, headers={'X-Service-Key': KEY, 'Content-Type': 'text/plain'}), 422)
    assert_error(post(app, path=PATH + '?actor_id=' + ACTOR), 422)
    async def stream():
        yield b' ' * 8192
        yield b' ' * 8193
        raise AssertionError('must stop at streamed excess')
    assert_error(asyncio.run(post_async(app, content=stream(), headers={'X-Service-Key': KEY, 'Content-Type': 'application/json', 'Content-Length': '1'})), 422)
    assert not projection.calls
    raw = json.dumps({'org_id': ORG, 'actor_ids': [ACTOR]}).encode()
    assert post(app, content=raw + b' ' * (16384 - len(raw))).status_code == 200
    assert post(app, {'org_id': ORG, 'actor_ids': ids(203)}).status_code == 503  # foreign injected row
    assert post(create_app(config(), Projection([])), {'org_id': ORG, 'actor_ids': ids(203)}).status_code == 200


@pytest.mark.parametrize('rows', [
    [{'actor_id': UUID(ORG), 'display_name': 'foreign'}],
    [{'actor_id': UUID(ACTOR), 'display_name': 'one'}] * 2,
    [{'actor_id': UUID(ACTOR), 'display_name': 'one', 'account_id': ACTOR}],
    [{'actor_id': UUID(ACTOR)}], [{'actor_id': ACTOR, 'display_name': 'wrong native type'}],
    [{'actor_id': UUID(int=0), 'display_name': 'zero'}], None, 'malformed',
])
def test_projection_integrity_never_becomes_absence(rows):
    projection = Projection()
    projection.rows = rows
    assert_error(post(create_app(config(), projection)), 503)


@pytest.mark.parametrize('name', ['', '  \u00a0', 'x' * 257, '\x00', 'name\n', '\x7f', '\x85', '\ud800', 1, None])
def test_invalid_stored_name_fails_entire_batch(name):
    assert_error(post(create_app(config(), Projection([{'actor_id': UUID(ACTOR), 'display_name': name}]))), 503)


@pytest.mark.parametrize('name', ['é', 'A <script>& text', '😀' * 256, 'x' * 256])
def test_valid_scalar_name_is_preserved_without_normalizing(name):
    response = post(create_app(config(), Projection([{'actor_id': UUID(ACTOR), 'display_name': name}])))
    assert response.status_code == 200
    assert response.json()['labels'][0]['display_name'] == name


def test_lazy_reader_iteration_is_bounded_and_closed():
    seen = []
    closed = []
    def rows():
        try:
            for _ in range(1000):
                seen.append(True)
                yield {'actor_id': UUID(ACTOR), 'display_name': 'private'}
        finally:
            closed.append(True)
    assert_error(post(create_app(config(), Projection(rows()))), 503)
    assert len(seen) == 2 and closed == [True]


def test_unknown_mapping_is_not_inferred_from_same_uuid_or_current_facts():
    projection = Projection([])  # No account/person/member/eligibility input exists.
    response = post(create_app(config(), projection))
    assert response.json()['labels'] == [{'actor_id': ACTOR, 'status': 'unavailable'}]
    assert projection.calls[0][0] == (UUID(ACTOR),)


def test_exception_and_logs_are_safe(caplog):
    async def broken(*args):
        raise RuntimeError('secret key private name body ' + KEY)
    response = post(create_app(config(), broken))
    assert_error(response, 503)
    assert KEY not in response.text + caplog.text and 'private name' not in caplog.text


@pytest.mark.parametrize('mode', ['caller', 'repeated', 'timeout', 'deadline'])
def test_cleanup_exception_never_reaches_asyncio_diagnostics(mode, monkeypatch, caplog):
    import actor_display_http
    monkeypatch.setattr(actor_display_http, 'OPERATION_SECONDS', .25)
    monkeypatch.setattr(actor_display_http, 'UNWIND_RESERVE_SECONDS', .06)

    async def execute():
        started, cleaning, finished = asyncio.Event(), asyncio.Event(), asyncio.Event()
        diagnostics, owned = [], []
        marker = 'synthetic-private-cleanup-exception'
        loop = asyncio.get_running_loop()
        previous = loop.get_exception_handler()
        loop.set_exception_handler(lambda _, context: diagnostics.append(context))

        async def reader(selected, deadline):
            owned.append(asyncio.current_task())
            started.set()
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cleaning.set()
                try:
                    await asyncio.sleep(10 if mode == 'deadline' else .02)
                finally:
                    finished.set()
                raise RuntimeError(marker)

        # The deadline case fails cleanup on the second, original-deadline cancel.
        async def deadline_reader(selected, deadline):
            try:
                return await reader(selected, deadline)
            except asyncio.CancelledError:
                raise RuntimeError(marker)

        app = create_app(config(), deadline_reader if mode == 'deadline' else reader)
        try:
            task = asyncio.create_task(post_async(app, {'org_id': ORG, 'actor_ids': [ACTOR]}))
            await started.wait()
            if mode in ('caller', 'repeated'):
                task.cancel()
                await cleaning.wait()
                if mode == 'repeated':
                    task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
            else:
                assert_error(await task, 503)
            assert finished.is_set() and owned[0].done()
            # Give shield's deferred diagnostic callback a chance to execute.
            await asyncio.sleep(0)
            await asyncio.sleep(0)
            assert len(diagnostics) == 0
            assert marker not in caplog.text
            if not owned[0].cancelled():
                assert marker not in repr(owned[0])
                assert marker not in repr(owned[0].result())
        finally:
            loop.set_exception_handler(previous)

    asyncio.run(execute())


def test_slow_input_and_reader_use_one_original_deadline(monkeypatch):
    import actor_display_http
    monkeypatch.setattr(actor_display_http, 'OPERATION_SECONDS', .15)
    monkeypatch.setattr(actor_display_http, 'UNWIND_RESERVE_SECONDS', .02)
    async def execute():
        observed = []
        async def stream():
            await asyncio.sleep(.07)
            yield json.dumps({'org_id': ORG, 'actor_ids': [ACTOR]}).encode()
        async def reader(selected, deadline):
            observed.append(deadline)
            try:
                await asyncio.sleep(.1)
            finally:
                await asyncio.sleep(.005)
                observed.append('unwound')
            return []
        started = time.monotonic()
        response = await post_async(create_app(config(), reader), content=stream())
        elapsed = time.monotonic() - started
        assert_error(response, 503)
        assert .12 <= elapsed < .2 and observed[-1] == 'unwound'
        assert .14 < observed[0] - started < .17
    asyncio.run(execute())


def test_slow_input_never_invokes_projection(monkeypatch):
    import actor_display_http
    monkeypatch.setattr(actor_display_http, 'OPERATION_SECONDS', .1)
    monkeypatch.setattr(actor_display_http, 'UNWIND_RESERVE_SECONDS', .01)
    async def stream():
        await asyncio.sleep(.2)
        yield b'{}'
    projection = Projection()
    assert_error(asyncio.run(post_async(create_app(config(), projection), content=stream())), 503)
    assert not projection.calls


def test_cancellation_propagates_after_owned_reader_cleanup():
    async def execute():
        started, finished = asyncio.Event(), asyncio.Event()
        async def reader(selected, deadline):
            try:
                started.set()
                await asyncio.sleep(10)
            finally:
                await asyncio.sleep(.01)
                finished.set()
        task = asyncio.create_task(post_async(create_app(config(), reader), {'org_id': ORG, 'actor_ids': [ACTOR]}))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert finished.is_set()
    asyncio.run(execute())


def test_repeated_cancellation_waits_for_owned_cleanup_even_if_reader_returns():
    async def execute():
        started, cleaning, finished = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def reader(selected, deadline):
            started.set()
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cleaning.set()
                await asyncio.sleep(.02)
                finished.set()
                return []  # Swallowing cancellation must never publish a 200.
        task = asyncio.create_task(post_async(create_app(config(), reader), {'org_id': ORG, 'actor_ids': [ACTOR]}))
        await started.wait()
        task.cancel()
        await cleaning.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert finished.is_set()
    asyncio.run(execute())


def test_reader_cleanup_exhausting_reserve_is_cancelled_at_original_deadline(monkeypatch):
    import actor_display_http
    monkeypatch.setattr(actor_display_http, 'OPERATION_SECONDS', .2)
    monkeypatch.setattr(actor_display_http, 'UNWIND_RESERVE_SECONDS', .06)

    async def execute():
        owned = []
        cancellations = []
        terminated = asyncio.Event()
        response_started = []

        async def reader(selected, deadline):
            owned.append((asyncio.current_task(), deadline))
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancellations.append(time.monotonic())
                try:
                    await asyncio.sleep(1)  # Cleanup deliberately exceeds its reserve.
                except asyncio.CancelledError:
                    cancellations.append(time.monotonic())
                    raise
            finally:
                terminated.set()

        app = create_app(config(), reader)

        async def observed_app(scope, receive, send):
            async def observed_send(message):
                if message['type'] == 'http.response.start':
                    assert terminated.is_set() and owned[0][0].done()
                    response_started.append(time.monotonic())
                await send(message)
            await app(scope, receive, observed_send)

        started = time.monotonic()
        response = await post_async(observed_app, {'org_id': ORG, 'actor_ids': [ACTOR]})
        assert_error(response, 503)
        task, deadline = owned[0]
        assert task.cancelled() and len(cancellations) == 2
        assert cancellations[0] < deadline <= cancellations[1]
        assert cancellations[1] - cancellations[0] >= .04
        # Only scheduler/response overhead is allowed beyond the original timer;
        # the one-second cleanup cannot receive a new execution budget.
        assert deadline <= response_started[0] < deadline + .05
        assert time.monotonic() - started < .25

    asyncio.run(execute())


def test_default_three_second_budget_and_bounded_unwind():
    import actor_display_http
    assert actor_display_http.OPERATION_SECONDS == 3.0
    async def execute():
        finished = []
        async def reader(selected, deadline):
            try:
                await asyncio.sleep(10)
            finally:
                await asyncio.sleep(.01)
                finished.append(True)
        started = time.monotonic()
        response = await post_async(create_app(config(), reader), {'org_id': ORG, 'actor_ids': [ACTOR]})
        assert_error(response, 503)
        assert 2.8 <= time.monotonic() - started < 3.15
        assert finished == [True]
    asyncio.run(execute())


def test_serialization_shares_original_deadline(monkeypatch):
    import actor_display_http
    original = actor_display_http.JSONResponse
    def serialize(content, *args, **kwargs):
        response = original(content, *args, **kwargs)
        if 'labels' in content:
            time.sleep(.03)
        return response
    monkeypatch.setattr(actor_display_http, 'OPERATION_SECONDS', .02)
    monkeypatch.setattr(actor_display_http, 'UNWIND_RESERVE_SECONDS', .001)
    monkeypatch.setattr(actor_display_http, 'JSONResponse', serialize)
    assert_error(post(create_app(config(), Projection())), 503)


def test_escaped_response_byte_bound_has_no_partial_output():
    # U+2028 is legal plain text. JSONResponse uses UTF-8, so use 4-byte scalars.
    selected = ids(203)
    projection = Projection([{'actor_id': UUID(actor), 'display_name': '😀' * 256} for actor in selected])
    assert post(create_app(config(), projection), {'org_id': ORG, 'actor_ids': selected}).status_code == 200
    # The normal encoder fits every legal bounded row; exercise the defensive
    # actual-byte check with an oversized serializer result, without changing it.
    import actor_display_http
    original = actor_display_http.JSONResponse
    def oversized(content, *args, **kwargs):
        response = original(content, *args, **kwargs)
        if 'labels' in content:
            response.body += b' ' * (256 * 1024)
        return response
    try:
        actor_display_http.JSONResponse = oversized
        assert_error(post(create_app(config(), Projection())), 503)
    finally:
        actor_display_http.JSONResponse = original


def test_wire_models_are_closed_discriminated_unions():
    success = {'org_id': ORG, 'labels': [{'actor_id': ACTOR, 'status': 'unavailable'}]}
    ActorDisplayResponse.model_validate(success)
    for label in (
        {'actor_id': ACTOR, 'status': 'unavailable', 'display_name': 'forbidden'},
        {'actor_id': ACTOR, 'status': 'resolved'},
        {'actor_id': ACTOR, 'status': 'unknown'},
    ):
        with pytest.raises(ValueError):
            ActorDisplayResponse.model_validate({'org_id': ORG, 'labels': [label]})


def test_isolated_schema_covers_exact_operation_security_and_all_envelopes():
    schema = owner_app().openapi()
    assert set(schema['paths']) == {PATH}
    operation = schema['paths'][PATH]['post']
    assert operation['security'] == [{'KdgActorDisplayKey': []}]
    assert schema['components']['securitySchemes']['KdgActorDisplayKey'] == {'type': 'apiKey', 'in': 'header', 'name': 'X-Service-Key'}
    assert set(operation['responses']) == {'200', '403', '422', '503'}
    request = operation['requestBody']['content']['application/json']['schema']
    assert request['additionalProperties'] is False and request['required'] == ['org_id', 'actor_ids']
    for model in schema['components']['schemas'].values():
        assert model['additionalProperties'] is False
    assert schema['components']['schemas']['ActorDisplayResponse']['properties']['labels']['items']['discriminator']['propertyName'] == 'status'
