-- Static data inserts for currency, expense_category, and expense_type tables

-- Ensure default org exists
INSERT INTO identity.org (name, slug, created_by, updated_by)
VALUES (
  'Liseli',
  'liseli',
  '11111111-1111-1111-1111-111111111111'::uuid,
  '11111111-1111-1111-1111-111111111111'::uuid
)
ON CONFLICT (slug) DO UPDATE
  SET name = EXCLUDED.name,
      updated_at = now(),
      updated_by = EXCLUDED.updated_by;

-- Currency
INSERT INTO finance.currency (id, symbol, name, org_id, is_active, created_at, created_by, updated_at, updated_by)
VALUES
  (1, 'K', 'Zambian Kwatchas', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (2, 'R', 'South African Rands', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (3, '$', 'United States Dollars', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (4, 'P', 'Botswana Pula', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (5, 'N', 'Namibian Dollars', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid)
ON CONFLICT (org_id, id) DO UPDATE
  SET symbol = EXCLUDED.symbol,
      name = EXCLUDED.name,
      is_active = EXCLUDED.is_active,
      updated_at = EXCLUDED.updated_at,
      updated_by = EXCLUDED.updated_by;

-- Expense Category
INSERT INTO finance.expense_category (id, name, description, org_id, is_active, created_at, created_by, updated_at, updated_by)
VALUES
  (1, 'AH', 'Ahavah School', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (2, 'VH', 'Vehicles', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (3, 'FL', 'Fuel', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (4, 'L1', 'Liseli Farm 1', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (5, 'L2', 'Liseli Farm 2', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (6, 'L3', 'Liseli Farm 3', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (7, 'Other', 'Other', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid)
ON CONFLICT (org_id, id) DO UPDATE
  SET name = EXCLUDED.name,
      description = EXCLUDED.description,
      is_active = EXCLUDED.is_active,
      updated_at = EXCLUDED.updated_at,
      updated_by = EXCLUDED.updated_by;

-- Expense Type
INSERT INTO finance.expense_type (id, expense_category_id, name, description, org_id, is_active, created_at, created_by, updated_at, updated_by)
VALUES
  -- Ahavah School
  (1, 1, 'Feeding Program', 'Feeding Program', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (2, 1, 'Teachers', 'Teachers', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (3, 1, 'Maintenance', 'Maintenance', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (4, 1, 'Stationery & Books', 'Stationery & Books', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (5, 1, 'Toys', 'Toys', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (6, 1, 'Uniforms', 'Uniforms', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (7, 1, 'Medical Supplies', 'Medical Supplies', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (8, 1, 'Other', 'Other', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),

  -- Vehicles
  (9, 2, 'ADJ5370ZM', 'ADJ5370ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (10, 2, 'AJE4009ZM', 'AJE4009ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (11, 2, 'BAC6391ZM', 'BAC6391ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (12, 2, 'BAR8114ZM', 'BAR8114ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (13, 2, 'ADJ9078ZM', 'ADJ9078ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (14, 2, 'AUB2798ZM', 'AUB2798ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (15, 2, 'AJE2623ZM', 'AJE2623ZM', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),

  -- Fuel
  (16, 3, 'L1 - Diesel', 'L1 - Diesel', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (17, 3, 'L1 - Petrol', 'L1 - Petrol', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (18, 3, 'L2 - Diesel', 'L2 - Diesel', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (19, 3, 'L2 - Petrol', 'L2 - Petrol', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),

  -- L1
  (20, 4, 'Base Camp', 'Base Camp', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (21, 4, 'Workshop', 'Workshop', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (22, 4, 'Community', 'Community', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (23, 4, 'Maintenance', 'Maintenance', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (24, 4, 'Irrigation', 'Irrigation', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (25, 4, 'Farm', 'Farm', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (26, 4, 'Other', 'Other', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),

  -- L2
  (27, 5, 'Farm', 'Farm', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (28, 5, 'Irrigation', 'Irrigation', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (29, 5, 'Maintenance', 'Maintenance', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (30, 5, 'Workshop', 'Workshop', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),
  (31, 5, 'Other', 'Other', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid),

  -- L3
  (32, 6, 'Other', 'Other', (select id from identity.org where slug = 'liseli'), TRUE, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid, CURRENT_TIMESTAMP, '11111111-1111-1111-1111-111111111111'::uuid)
ON CONFLICT (org_id, id) DO UPDATE
  SET expense_category_id = EXCLUDED.expense_category_id,
      name = EXCLUDED.name,
      description = EXCLUDED.description,
      is_active = EXCLUDED.is_active,
      updated_at = EXCLUDED.updated_at,
      updated_by = EXCLUDED.updated_by;
