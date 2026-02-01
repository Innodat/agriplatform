select * from finance.receipt where id = 11;
select om.org_id, om.user_id, p.id, p.role, p.permission
from identity.role_permissions p
join identity.member_role mr on p.role = mr.role
join identity.org_member om on mr.member_id = om.id
where om.user_id = '5d4ff1be-50af-44cb-b3ba-9419c4cb1da8' and p.role = 'employee' and p.permission in ('finance.receipt.update', 'finance.receipt.delete');

select * from identity.org_member where user_id = '5d4ff1be-50af-44cb-b3ba-9419c4cb1da8';
select * from identity.member_role;