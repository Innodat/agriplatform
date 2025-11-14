-- static_data.sql: Static data inserts for currency, expense_category, and expense_type tables



-- Currency
INSERT INTO finance.currency (id, symbol, name, is_active, created_timestamp, created_user_id, modified_timestamp, modified_user_id)
VALUES
    (1, 'K', 'Zambian Kwatchas', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (2, 'R', 'South African Rands', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (3, '$', 'United States Dollars', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (4, 'P', 'Botswana Pula', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (5, 'N', 'Namibian Dollars', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1);

-- Expense Category
INSERT INTO finance.expense_category (id, name, description, is_active, created_timestamp, created_user_id, modified_timestamp, modified_user_id)
VALUES
    (1, 'AH', 'Ahavah School', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (2, 'VH', 'Vehicles', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (3, 'FL', 'Fuel', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (4, 'L1', 'Liseli Farm 1', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (5, 'L2', 'Liseli Farm 2', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (6, 'L3', 'Liseli Farm 3', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (7, 'Other', 'Other', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1);

-- Expense Type
INSERT INTO finance.expense_type (id, expense_category_id, name, description, is_active, created_timestamp, created_user_id, modified_timestamp, modified_user_id)
VALUES
    -- Ahavah School
    (1, 1, 'Feeding Program', 'Feeding Program', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (2, 1, 'Teachers', 'Teachers', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (3, 1, 'Maintenance', 'Maintenance', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (4, 1, 'Stationery & Books', 'Stationery & Books', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (5, 1, 'Toys', 'Toys', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (6, 1, 'Uniforms', 'Uniforms', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (7, 1, 'Medical Supplies', 'Medical Supplies', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (8, 1, 'Other', 'Other', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    -- Vehicles
    (9, 2, 'ADJ5370ZM', 'ADJ5370ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (10, 2, 'AJE4009ZM', 'AJE4009ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (11, 2, 'BAC6391ZM', 'BAC6391ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (12, 2, 'BAR8114ZM', 'BAR8114ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (13, 2, 'ADJ9078ZM', 'ADJ9078ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (14, 2, 'AUB2798ZM', 'AUB2798ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (15, 2, 'AJE2623ZM', 'AJE2623ZM', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    -- Fuel
    (16, 3, 'L1 - Diesel', 'L1 - Diesel', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (17, 3, 'L1 - Petrol', 'L1 - Petrol', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (18, 3, 'L2 - Diesel', 'L2 - Diesel', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (19, 3, 'L2 - Petrol', 'L2 - Petrol', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    -- L1
    (20, 4, 'Base Camp', 'Base Camp', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (21, 4, 'Workshop', 'Workshop', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (22, 4, 'Community', 'Community', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (23, 4, 'Maintenance', 'Maintenance', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (24, 4, 'Irrigation', 'Irrigation', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (25, 4, 'Farm', 'Farm', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (26, 4, 'Other', 'Other', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    -- L2
    (27, 5, 'Farm', 'Farm', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (28, 5, 'Irrigation', 'Irrigation', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (29, 5, 'Maintenance', 'Maintenance', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (30, 5, 'Workshop', 'Workshop', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    (31, 5, 'Other', 'Other', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1),
    -- L3
    (32, 6, 'Other', 'Other', TRUE, CURRENT_TIMESTAMP, 1, CURRENT_TIMESTAMP, 1);


SELECT setval('finance.expense_category_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.expense_category));
SELECT setval('finance.currency_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.currency));
SELECT setval('finance.expense_type_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.expense_type));