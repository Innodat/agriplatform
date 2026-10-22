import type {EntryContext} from '../src/entry';

function readonlyContract(context: EntryContext) {
  // @ts-expect-error Entry evidence is immutable, including nested scopes.
  context.authorization_scope.org_id = 'replacement';
  // @ts-expect-error Entry evidence is immutable, including nested scopes.
  context.resource_scope.account_id = 'replacement';
}
void readonlyContract;
