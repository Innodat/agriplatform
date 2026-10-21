"""One isolated Identity worker and compact safe operator transport."""
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import sys
from uuid import UUID

# -I keeps ambient Python paths out; select only the repository owner modules.
OWNER = Path(__file__).resolve().parent
sys.path.insert(0, str(OWNER))
import identity_operator as adapter
import access_operator
import access_operator_input
from identity_operator_input import parse_command, EnsureAccountActorCommand, RegisterSystemCommand, RetireMembershipCommand, JoinMembershipCommand, CommandValidationError
from identity_operator_target import load_target, TargetError, ROOT
import dev
import images

CODES = frozenset(('command_invalid', 'command_unsupported', 'identity_operator_input_invalid',
    'identity_operator_target_invalid', 'access_operator_input_invalid', 'operation_unavailable', 'operation_verification_unavailable',
    'operation_busy', 'access_denied', 'operation_conflict', 'connection_busy', 'isolation_unsupported'))


def _uuid(value):
    if type(value) is not str or str(UUID(value)) != value.lower() or not UUID(value).int:
        raise ValueError()
    return str(UUID(value))


def _receipt(value, operation_id, command='actor.register_system'):
    if type(value) is not dict or set(value) != {'operation_id','status','result','command_version','result_version','committed_at'}:
        raise ValueError()
    if value['operation_id'] != operation_id or value['status'] != 'committed':
        raise ValueError()
    if type(value['command_version']) is not int or value['command_version'] != 1 or type(value['result_version']) is not int or value['result_version'] != 1:
        raise ValueError()
    instant = datetime.fromisoformat(value['committed_at'])
    if instant.tzinfo is None or instant.utcoffset() != timezone.utc.utcoffset(instant):
        raise ValueError()
    result = value['result']
    if type(result) is not dict or set(result) != {'command','target','disposition','revision','event_id'} or result['command'] != command:
        raise ValueError()
    # Reuse the protected adapter's typed stored-result validator.
    (access_operator if command in ('application.register','permission.register','entry_permission.register','application.set_enabled') else adapter)._receipt(({k:v for k,v in result.items() if k != 'command'}, 1, 1, instant), operation_id, command)
    return value


def validate_response(raw, operation_id, command='actor.register_system', expected_target=None):
    value = dev.decode(raw)
    if type(value) is dict and set(value) == {'operation_id','status'} and value == {'operation_id':operation_id,'status':'unresolved'}:
        return value
    if type(value) is dict and set(value) == {'operation_id','code'} and value['operation_id'] == operation_id and type(value['code']) is str and value['code'] in CODES:
        return value
    receipt = _receipt(value, operation_id, command)
    if expected_target is not None and any(receipt['result']['target'].get(k) != v for k,v in expected_target.items()):
        raise ValueError()
    return receipt


def _connection(target):
    from sqlalchemy import create_engine
    from sqlalchemy.engine import URL
    from sqlalchemy.pool import NullPool
    return create_engine(URL.create('postgresql+psycopg', username=getattr(target,'owner_id','identity')+'_operator', password=target.password,
        host='127.0.0.1', port=target.port, database=target.database), poolclass=NullPool,
        isolation_level='READ COMMITTED', hide_parameters=True,
        connect_args=dict(connect_timeout=3, sslmode='disable', gssencmode='disable',
            passfile='/dev/null', application_name=getattr(target,'owner_id','identity')+'_operator',
            options='-c statement_timeout=5000 -c lock_timeout=2000'))


def verify_session(connection, target):
    from sqlalchemy import text
    row = connection.execute(text('SELECT session_user,current_user,current_database(), '
        'r.rolcanlogin,r.rolsuper,r.rolcreatedb,r.rolcreaterole,r.rolreplication,r.rolbypassrls,r.rolinherit, '
        'EXISTS(SELECT 1 FROM pg_catalog.pg_auth_members m WHERE m.member=r.oid) '
        'FROM pg_catalog.pg_roles r WHERE r.rolname=session_user')).one()
    login = getattr(target,'owner_id','identity')+'_operator'
    if tuple(row) != (login,login,target.database,True,False,False,False,False,False,False,False):
        raise adapter.OperatorError('access_denied')
    connection.rollback()


def worker(request):
    if len(request) == 5:
        return access_worker(request)
    # Revalidate both transport and filesystem before constructing a connection.
    action, path, value, operation_id = request
    operation_id = _uuid(operation_id)
    command_name = 'actor.register_system'
    context = {}
    if action == 'execute':
        body = value.encode('utf-8')
        command = parse_command(body)
        if not isinstance(command, (EnsureAccountActorCommand, RegisterSystemCommand, RetireMembershipCommand, JoinMembershipCommand)) or _uuid(command.operation_id) != operation_id:
            raise ValueError()
        command_name = command.command
    elif action == 'outcome' and type(value) is dict and set(value) == {'command','org_id','account_id'} and value['command'] in ('membership.retire','membership.join'):
        context = {'command':value['command'],'org_id':_uuid(value['org_id']),'account_id':_uuid(value['account_id'])}
        command_name = value['command']
    elif action == 'outcome' and type(value) is dict and set(value) == {'command','account_id'} and value['command'] == 'account_actor.ensure':
        context = {'command':value['command'],'account_id':_uuid(value['account_id'])}
        command_name = value['command']
    elif action != 'outcome' or value is not None:
        raise ValueError()
    target = load_target(path)
    engine = _connection(target)
    try:
        with engine.connect() as connection:
            verify_session(connection, target)
            receipt = adapter.execute(connection, body) if action == 'execute' else adapter.outcome(connection, operation_id, **context)
        if receipt is None:
            return dict(operation_id=operation_id,status='unresolved')
        result = asdict(receipt)
        result['committed_at'] = receipt.committed_at.astimezone(timezone.utc).isoformat()
        return _receipt(result, operation_id, command_name)
    finally:
        engine.dispose()


class WorkerInterrupted(Exception):
    """Distinct from InterruptedError, which selectors may treat as a syscall retry."""


def _interrupt(signum, frame):
    raise WorkerInterrupted()


def dispatch(request):
    previous = {}
    try:
        for name in (signal.SIGINT, signal.SIGTERM):
            previous[name] = signal.signal(name, _interrupt)
        return images.bounded_command([sys.executable,'-I','-B',str(Path(__file__).resolve()),'_worker'],
            ROOT, {'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},12,8192,
            input_data=json.dumps(request,ensure_ascii=False).encode())
    finally:
        for name, handler in previous.items():
            signal.signal(name, handler)


def _identity_main(argv=None):
    operation_id = None
    result = {'code':'command_invalid'}
    status = 2
    try:
        parser = dev.Parser(add_help=False,allow_abbrev=False)
        parser.add_argument('action',choices=['execute','outcome'])
        parser.add_argument('--owner',required=True,choices=['identity'])
        parser.add_argument('--target',required=True)
        parser.add_argument('--command-file')
        parser.add_argument('--command')
        parser.add_argument('--operation-id')
        parser.add_argument('--org-id')
        parser.add_argument('--account-id')
        actual_argv = sys.argv[1:] if argv is None else argv
        flags = [item for item in actual_argv if item.startswith('--')]
        if len(flags) != len(set(flags)) or any('=' in item for item in flags):
            raise ValueError()
        args = parser.parse_args(actual_argv)
        if args.action == 'execute':
            if args.command_file is None or args.command is not None or args.operation_id is not None or args.org_id is not None or args.account_id is not None:
                raise ValueError()
            body = dev.read(Path(__import__('os').path.abspath(args.command_file)))
            command = parse_command(body)
            operation_id = _uuid(command.operation_id)
            if not isinstance(command,(EnsureAccountActorCommand,RegisterSystemCommand,RetireMembershipCommand,JoinMembershipCommand)):
                raise adapter.OperatorError('command_unsupported',operation_id)
            command_name = command.command
            value = body.decode('utf-8')
        else:
            if args.command_file is not None or args.command not in ('actor.register_system','account_actor.ensure','membership.retire','membership.join'):
                raise ValueError()
            operation_id = _uuid(args.operation_id)
            command_name = args.command
            if args.command in ('membership.retire','membership.join'):
                value = dict(command=args.command,org_id=_uuid(args.org_id),account_id=_uuid(args.account_id))
            elif args.command == 'account_actor.ensure':
                if args.org_id is not None:
                    raise ValueError()
                value = dict(command=args.command,account_id=_uuid(args.account_id))
            else:
                if args.org_id is not None or args.account_id is not None:
                    raise ValueError()
                value = None
        expected_target = None
        if command_name in ('membership.retire','membership.join'):
            expected_target = ({'org_id':str(UUID(command.scope.org_id)), 'account_id':str(UUID(command.payload.account_id)),
                **({'membership_id':command.payload.membership_id} if command_name == 'membership.retire' else {})} if args.action == 'execute' else
                {'org_id':value['org_id'],'account_id':value['account_id']})
        if command_name == 'account_actor.ensure':
            expected_target = ({k:str(UUID(getattr(command.payload,k))) for k in ('account_id','actor_id')}
                if args.action == 'execute' else {'account_id':value['account_id']})
        target = load_target(args.target)
        request = [args.action,str(target.path),value,operation_id]
        try:
            result = validate_response(dispatch(request),operation_id,command_name,expected_target)
        except (Exception, KeyboardInterrupt):
            result = dict(code='operation_unavailable',operation_id=operation_id)
        status = 0 if result.get('status') == 'committed' else 2
    except (TargetError,CommandValidationError,access_operator_input.CommandValidationError,adapter.OperatorError) as error:
        result = {'code':error.code if error.code in CODES else 'operation_unavailable'}
        if operation_id is not None:
            result['operation_id'] = operation_id
    except (Exception,KeyboardInterrupt):
        result = {'code':'command_invalid'}
        if operation_id is not None:
            result['operation_id'] = operation_id
    print(json.dumps(result,separators=(',',':'),sort_keys=True))
    return status


def access_worker(request):
    action,path,value,operation_id,owner = request
    if owner != 'access':
        raise ValueError()
    operation_id = _uuid(operation_id)
    if action == 'execute':
        body = value.encode('utf-8')
        command = access_operator_input.parse_command(body)
        if not isinstance(command,(access_operator_input.RegisterApplicationCommand,access_operator_input.RegisterPermissionCommand,access_operator_input.RegisterEntryPermissionCommand,access_operator_input.SetApplicationEnabledCommand)) or _uuid(command.operation_id) != operation_id:
            raise ValueError()
        context = None
    elif action == 'outcome' and type(value) is dict and value.get('command') in ('application.register','permission.register','entry_permission.register','application.set_enabled') and set(value) == ({'command','app_id','permission'} if value['command'] in ('permission.register','entry_permission.register') else {'command','app_id'}):
        if type(value['app_id']) is not str or access_operator_input._APP_ID.fullmatch(value['app_id']) is None:
            raise ValueError()
        if value['command'] in ('permission.register','entry_permission.register') and not access_operator.valid_permission(value['permission']):
            raise ValueError()
        context = value
    else:
        raise ValueError()
    target = load_target(path,owner='access')
    engine = _connection(target)
    try:
        with engine.connect() as connection:
            verify_session(connection,target)
            receipt = access_operator.execute(connection,body) if action == 'execute' else access_operator.outcome(connection,operation_id,**context)
        if receipt is None:
            return dict(operation_id=operation_id,status='unresolved')
        result = asdict(receipt)
        result['committed_at'] = receipt.committed_at.astimezone(timezone.utc).isoformat()
        return _receipt(result,operation_id,command.command if action == 'execute' else context['command'])
    finally:
        engine.dispose()


def _access_main(argv):
    operation_id = None
    result = {'code':'command_invalid'}
    try:
        parser = dev.Parser(add_help=False,allow_abbrev=False)
        parser.add_argument('action',choices=['execute','outcome'])
        parser.add_argument('--owner',required=True,choices=['access'])
        parser.add_argument('--target',required=True)
        parser.add_argument('--command-file')
        parser.add_argument('--command')
        parser.add_argument('--operation-id')
        parser.add_argument('--app-id')
        parser.add_argument('--permission')
        flags = [item.split('=',1)[0] if item.startswith('--permission=') else item for item in argv if item.startswith('--')]
        if len(flags) != len(set(flags)) or any('=' in item for item in flags):
            raise ValueError()
        args = parser.parse_args(argv)
        if args.action == 'execute':
            if args.command_file is None or any(v is not None for v in (args.command,args.operation_id,args.app_id,args.permission)):
                raise ValueError()
            body = dev.read(Path(os.path.abspath(args.command_file)))
            command = access_operator_input.parse_command(body)
            operation_id = _uuid(command.operation_id)
            if not isinstance(command,(access_operator_input.RegisterApplicationCommand,access_operator_input.RegisterPermissionCommand,access_operator_input.RegisterEntryPermissionCommand,access_operator_input.SetApplicationEnabledCommand)):
                raise adapter.OperatorError('command_unsupported',operation_id)
            value = body.decode('utf-8')
            expected = {'app_id':command.payload.app_id}
            if command.command in ('permission.register','entry_permission.register'):expected['permission']=command.payload.permission
            command_name=command.command
        else:
            if args.command_file is not None or args.command not in ('application.register','permission.register','entry_permission.register','application.set_enabled') or type(args.app_id) is not str or access_operator_input._APP_ID.fullmatch(args.app_id) is None:
                raise ValueError()
            if (not access_operator.valid_permission(args.permission) if args.command in ('permission.register','entry_permission.register') else args.permission is not None):
                raise ValueError()
            operation_id = _uuid(args.operation_id)
            command_name=args.command
            value = dict(command=args.command,app_id=args.app_id)
            if args.command in ('permission.register','entry_permission.register'):value['permission']=args.permission
            expected = {k:v for k,v in value.items() if k != 'command'}
        target = load_target(args.target,owner='access')
        request = [args.action,str(target.path),value,operation_id,'access']
        try:
            result = validate_response(dispatch(request),operation_id,command_name,expected)
        except (Exception,KeyboardInterrupt):
            result = dict(code='operation_unavailable',operation_id=operation_id)
    except (TargetError,access_operator_input.CommandValidationError,adapter.OperatorError) as error:
        result = {'code':error.code if error.code in CODES else 'operation_unavailable'}
        if operation_id is not None:
            result['operation_id'] = operation_id
    except (Exception,KeyboardInterrupt):
        result = {'code':'command_invalid'}
        if operation_id is not None:
            result['operation_id'] = operation_id
    print(json.dumps(result,separators=(',',':'),sort_keys=True))
    return 0 if result.get('status') == 'committed' else 2


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    return _access_main(argv) if '--owner' in argv and argv[argv.index('--owner')+1:argv.index('--owner')+2] == ['access'] else _identity_main(argv)


def worker_main():
    operation_id = None
    os.environ.clear()  # No ambient libpq service, password, endpoint or config discovery.
    try:
        raw = sys.stdin.buffer.read(131073)
        if len(raw) > 131072:
            raise ValueError()
        request = dev.decode(raw)
        if type(request) is not list or len(request) not in (4,5):
            raise ValueError()
        operation_id = _uuid(request[3])
        result = worker(request)
    except (TargetError,CommandValidationError,access_operator_input.CommandValidationError,adapter.OperatorError) as error:
        result = dict(code=error.code if error.code in CODES else 'operation_unavailable',operation_id=operation_id)
    except Exception:
        result = dict(code='operation_unavailable',operation_id=operation_id)
    print(json.dumps(result,separators=(',',':'),sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(worker_main() if sys.argv[1:] == ['_worker'] else main())
