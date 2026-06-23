
create trigger audit_log_finance_purchase
after insert or update or delete on finance.purchase
for each row execute function identity.log_audit();

create trigger audit_log_finance_receipt
after insert or update or delete on finance.receipt
for each row execute function identity.log_audit();

create trigger audit_log_expense_category
after insert or update or delete on finance.expense_category
for each row execute function identity.log_audit();

create trigger audit_log_expense_type
after insert or update or delete on finance.expense_type
for each row execute function identity.log_audit();

create trigger audit_log_currency
after insert or update or delete on finance.currency
for each row execute function identity.log_audit();
