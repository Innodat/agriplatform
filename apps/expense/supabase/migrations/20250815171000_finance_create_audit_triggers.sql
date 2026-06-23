-- Finance schema
create trigger audit_finance_purchase
before insert or update on finance.purchase
for each row execute function identity.set_audit_fields();

create trigger audit_finance_receipt
before insert or update on finance.receipt
for each row execute function identity.set_audit_fields();

create trigger audit_expense_category
before insert or update on finance.expense_category
for each row execute function identity.set_audit_fields();

create trigger audit_expense_type
before insert or update on finance.expense_type
for each row execute function identity.set_audit_fields();

create trigger audit_currency
before insert or update on finance.currency
for each row execute function identity.set_audit_fields();

