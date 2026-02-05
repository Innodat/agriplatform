-- Dummy data for receipts and purchases
-- 5 receipts, 2 for today
-- NOTE: Updated to use deleted_at instead of is_active (removed obsolete columns)

-- Receipts
INSERT INTO finance.receipt (id, created_at, created_by, updated_at, updated_by)
VALUES
  (1, CURRENT_TIMESTAMP, 'system', CURRENT_TIMESTAMP, 'system'),
  (2, CURRENT_TIMESTAMP, 'system', CURRENT_TIMESTAMP, 'system'),
  (3, CURRENT_DATE - INTERVAL '2 days', 'system', CURRENT_DATE - INTERVAL '2 days', 'system'),
  (4, CURRENT_DATE - INTERVAL '5 days', 'system', CURRENT_DATE - INTERVAL '5 days', 'system'),
  (5, CURRENT_DATE - INTERVAL '10 days', 'system', CURRENT_DATE - INTERVAL '10 days', 'system'),
  (6, CURRENT_DATE - INTERVAL '11 days', 'system', CURRENT_DATE - INTERVAL '11 days', 'system'),
  (7, CURRENT_DATE - INTERVAL '12 days', 'system', CURRENT_DATE - INTERVAL '12 days', 'system'),
  (8, CURRENT_DATE - INTERVAL '13 days', 'system', CURRENT_DATE - INTERVAL '13 days', 'system'),
  (9, CURRENT_DATE - INTERVAL '14 days', 'system', CURRENT_DATE - INTERVAL '14 days', 'system'),
  (10, CURRENT_DATE - INTERVAL '15 days', 'system', CURRENT_DATE - INTERVAL '15 days', 'system'),
  (11, CURRENT_DATE - INTERVAL '16 days', 'system', CURRENT_DATE - INTERVAL '16 days', 'system'),
  (12, CURRENT_DATE - INTERVAL '17 days', 'system', CURRENT_DATE - INTERVAL '17 days', 'system'),
  (13, CURRENT_DATE - INTERVAL '18 days', 'system', CURRENT_DATE - INTERVAL '18 days', 'system'),
  (14, CURRENT_DATE - INTERVAL '19 days', 'system', CURRENT_DATE - INTERVAL '19 days', 'system'),
  (15, CURRENT_DATE - INTERVAL '20 days', 'system', CURRENT_DATE - INTERVAL '20 days', 'system'),
  (16, CURRENT_DATE - INTERVAL '21 days', 'system', CURRENT_DATE - INTERVAL '21 days', 'system'),
  (17, CURRENT_DATE - INTERVAL '22 days', 'system', CURRENT_DATE - INTERVAL '22 days', 'system'),
  (18, CURRENT_DATE - INTERVAL '23 days', 'system', CURRENT_DATE - INTERVAL '23 days', 'system'),
  (19, CURRENT_DATE - INTERVAL '24 days', 'system', CURRENT_DATE - INTERVAL '24 days', 'system'),
  (20, CURRENT_DATE - INTERVAL '25 days', 'system', CURRENT_DATE - INTERVAL '25 days', 'system'),
  (21, CURRENT_DATE - INTERVAL '26 days', 'system', CURRENT_DATE - INTERVAL '26 days', 'system'),
  (22, CURRENT_DATE - INTERVAL '27 days', 'system', CURRENT_DATE - INTERVAL '27 days', 'system'),
  (23, CURRENT_DATE - INTERVAL '28 days', 'system', CURRENT_DATE - INTERVAL '28 days', 'system'),
  (24, CURRENT_DATE - INTERVAL '29 days', 'system', CURRENT_DATE - INTERVAL '29 days', 'system'),
  (25, CURRENT_DATE - INTERVAL '30 days', 'system', CURRENT_DATE - INTERVAL '30 days', 'system');

-- Purchases (linked to receipts above)
INSERT INTO finance.purchase (receipt_id, expense_type_id, other_category, currency_id, user_id, amount, reimbursable, created_at, created_by, updated_at, updated_by)
VALUES
  (1, 1, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 150.00, TRUE, CURRENT_TIMESTAMP, 'system', CURRENT_TIMESTAMP, 'system'),
  (1, 2, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 75.50, FALSE, CURRENT_TIMESTAMP, 'system', CURRENT_TIMESTAMP, 'system'),
  (2, 3, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 200.00, TRUE, CURRENT_TIMESTAMP, 'system', CURRENT_TIMESTAMP, 'system'),
  (3, 4, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 50.00, FALSE, CURRENT_DATE - INTERVAL '2 days', 'system', CURRENT_DATE - INTERVAL '2 days', 'system'),
  (4, 5, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 300.00, TRUE, CURRENT_DATE - INTERVAL '5 days', 'system', CURRENT_DATE - INTERVAL '5 days', 'system'),
  (5, 6, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 120.00, FALSE, CURRENT_DATE - INTERVAL '10 days', 'system', CURRENT_DATE - INTERVAL '10 days', 'system'),
  (6, 1, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 180.00, TRUE, CURRENT_DATE - INTERVAL '11 days', 'system', CURRENT_DATE - INTERVAL '11 days', 'system'),
  (7, 2, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 90.00, FALSE, CURRENT_DATE - INTERVAL '12 days', 'system', CURRENT_DATE - INTERVAL '12 days', 'system'),
  (8, 3, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 210.00, TRUE, CURRENT_DATE - INTERVAL '13 days', 'system', CURRENT_DATE - INTERVAL '13 days', 'system'),
  (9, 4, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 60.00, FALSE, CURRENT_DATE - INTERVAL '14 days', 'system', CURRENT_DATE - INTERVAL '14 days', 'system'),
  (10, 5, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 320.00, TRUE, CURRENT_DATE - INTERVAL '15 days', 'system', CURRENT_DATE - INTERVAL '15 days', 'system'),
  (11, 6, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 130.00, FALSE, CURRENT_DATE - INTERVAL '16 days', 'system', CURRENT_DATE - INTERVAL '16 days', 'system'),
  (12, 1, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 170.00, TRUE, CURRENT_DATE - INTERVAL '17 days', 'system', CURRENT_DATE - INTERVAL '17 days', 'system'),
  (13, 2, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 95.00, FALSE, CURRENT_DATE - INTERVAL '18 days', 'system', CURRENT_DATE - INTERVAL '18 days', 'system'),
  (14, 3, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 220.00, TRUE, CURRENT_DATE - INTERVAL '19 days', 'system', CURRENT_DATE - INTERVAL '19 days', 'system'),
  (15, 4, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 70.00, FALSE, CURRENT_DATE - INTERVAL '20 days', 'system', CURRENT_DATE - INTERVAL '20 days', 'system'),
  (16, 5, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 340.00, TRUE, CURRENT_DATE - INTERVAL '21 days', 'system', CURRENT_DATE - INTERVAL '21 days', 'system'),
  (17, 6, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 140.00, FALSE, CURRENT_DATE - INTERVAL '22 days', 'system', CURRENT_DATE - INTERVAL '22 days', 'system'),
  (18, 1, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 160.00, TRUE, CURRENT_DATE - INTERVAL '23 days', 'system', CURRENT_DATE - INTERVAL '23 days', 'system'),
  (19, 2, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 85.00, FALSE, CURRENT_DATE - INTERVAL '24 days', 'system', CURRENT_DATE - INTERVAL '24 days', 'system'),
  (20, 3, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 230.00, TRUE, CURRENT_DATE - INTERVAL '25 days', 'system', CURRENT_DATE - INTERVAL '25 days', 'system'),
  (21, 4, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 80.00, FALSE, CURRENT_DATE - INTERVAL '26 days', 'system', CURRENT_DATE - INTERVAL '26 days', 'system'),
  (22, 5, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 360.00, TRUE, CURRENT_DATE - INTERVAL '27 days', 'system', CURRENT_DATE - INTERVAL '27 days', 'system'),
  (23, 6, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 150.00, FALSE, CURRENT_DATE - INTERVAL '28 days', 'system', CURRENT_DATE - INTERVAL '28 days', 'system'),
  (24, 1, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 190.00, TRUE, CURRENT_DATE - INTERVAL '29 days', 'system', CURRENT_DATE - INTERVAL '29 days', 'system'),
  (25, 2, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 105.00, FALSE, CURRENT_DATE - INTERVAL '30 days', 'system', CURRENT_DATE - INTERVAL '30 days', 'system');

SELECT setval('finance.invoice_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.receipt));
SELECT setval('finance.purchase_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.purchase));