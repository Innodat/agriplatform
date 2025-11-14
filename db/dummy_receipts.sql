-- Dummy data for receipts and purchases
-- 5 receipts, 2 for today

-- Receipts
INSERT INTO finance.receipt (id, is_active, created_timestamp, created_user_id, modified_user_id, modified_timestamp)
VALUES
  (1, TRUE, CURRENT_TIMESTAMP, 'system', 'system', CURRENT_TIMESTAMP),
  (2, TRUE, CURRENT_TIMESTAMP, 'system', 'system', CURRENT_TIMESTAMP),
  (3, TRUE, CURRENT_DATE - INTERVAL '2 days', 'system', 'system', CURRENT_DATE - INTERVAL '2 days'),
  (4, TRUE, CURRENT_DATE - INTERVAL '5 days', 'system', 'system', CURRENT_DATE - INTERVAL '5 days'),
  (5, TRUE, CURRENT_DATE - INTERVAL '10 days', 'system', 'system', CURRENT_DATE - INTERVAL '10 days'),
  (6, TRUE, CURRENT_DATE - INTERVAL '11 days', 'system', 'system', CURRENT_DATE - INTERVAL '11 days'),
  (7, TRUE, CURRENT_DATE - INTERVAL '12 days', 'system', 'system', CURRENT_DATE - INTERVAL '12 days'),
  (8, TRUE, CURRENT_DATE - INTERVAL '13 days', 'system', 'system', CURRENT_DATE - INTERVAL '13 days'),
  (9, TRUE, CURRENT_DATE - INTERVAL '14 days', 'system', 'system', CURRENT_DATE - INTERVAL '14 days'),
  (10, TRUE, CURRENT_DATE - INTERVAL '15 days', 'system', 'system', CURRENT_DATE - INTERVAL '15 days'),
  (11, TRUE, CURRENT_DATE - INTERVAL '16 days', 'system', 'system', CURRENT_DATE - INTERVAL '16 days'),
  (12, TRUE, CURRENT_DATE - INTERVAL '17 days', 'system', 'system', CURRENT_DATE - INTERVAL '17 days'),
  (13, TRUE, CURRENT_DATE - INTERVAL '18 days', 'system', 'system', CURRENT_DATE - INTERVAL '18 days'),
  (14, TRUE, CURRENT_DATE - INTERVAL '19 days', 'system', 'system', CURRENT_DATE - INTERVAL '19 days'),
  (15, TRUE, CURRENT_DATE - INTERVAL '20 days', 'system', 'system', CURRENT_DATE - INTERVAL '20 days'),
  (16, TRUE, CURRENT_DATE - INTERVAL '21 days', 'system', 'system', CURRENT_DATE - INTERVAL '21 days'),
  (17, TRUE, CURRENT_DATE - INTERVAL '22 days', 'system', 'system', CURRENT_DATE - INTERVAL '22 days'),
  (18, TRUE, CURRENT_DATE - INTERVAL '23 days', 'system', 'system', CURRENT_DATE - INTERVAL '23 days'),
  (19, TRUE, CURRENT_DATE - INTERVAL '24 days', 'system', 'system', CURRENT_DATE - INTERVAL '24 days'),
  (20, TRUE, CURRENT_DATE - INTERVAL '25 days', 'system', 'system', CURRENT_DATE - INTERVAL '25 days'),
  (21, TRUE, CURRENT_DATE - INTERVAL '26 days', 'system', 'system', CURRENT_DATE - INTERVAL '26 days'),
  (22, TRUE, CURRENT_DATE - INTERVAL '27 days', 'system', 'system', CURRENT_DATE - INTERVAL '27 days'),
  (23, TRUE, CURRENT_DATE - INTERVAL '28 days', 'system', 'system', CURRENT_DATE - INTERVAL '28 days'),
  (24, TRUE, CURRENT_DATE - INTERVAL '29 days', 'system', 'system', CURRENT_DATE - INTERVAL '29 days'),
  (25, TRUE, CURRENT_DATE - INTERVAL '30 days', 'system', 'system', CURRENT_DATE - INTERVAL '30 days');

-- Purchases (linked to receipts above)
INSERT INTO finance.purchase (receipt_id, expense_type_id, other_category, currency_id, user_id, amount, reimbursable, captured_timestamp, is_active, created_timestamp, created_user_id, modified_user_id, modified_timestamp)
VALUES
  (1, 1, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 150.00, TRUE, CURRENT_TIMESTAMP, TRUE, CURRENT_TIMESTAMP, 'system', 'system', CURRENT_TIMESTAMP),
  (1, 2, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 75.50, FALSE, CURRENT_TIMESTAMP, TRUE, CURRENT_TIMESTAMP, 'system', 'system', CURRENT_TIMESTAMP),
  (2, 3, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 200.00, TRUE, CURRENT_TIMESTAMP, TRUE, CURRENT_TIMESTAMP, 'system', 'system', CURRENT_TIMESTAMP),
  (3, 4, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 50.00, FALSE, CURRENT_DATE - INTERVAL '2 days', TRUE, CURRENT_DATE - INTERVAL '2 days', 'system', 'system', CURRENT_DATE - INTERVAL '2 days'),
  (4, 5, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 300.00, TRUE, CURRENT_DATE - INTERVAL '5 days', TRUE, CURRENT_DATE - INTERVAL '5 days', 'system', 'system', CURRENT_DATE - INTERVAL '5 days'),
  (5, 6, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 120.00, FALSE, CURRENT_DATE - INTERVAL '10 days', TRUE, CURRENT_DATE - INTERVAL '10 days', 'system', 'system', CURRENT_DATE - INTERVAL '10 days'),
  (6, 1, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 180.00, TRUE, CURRENT_DATE - INTERVAL '11 days', TRUE, CURRENT_DATE - INTERVAL '11 days', 'system', 'system', CURRENT_DATE - INTERVAL '11 days'),
  (7, 2, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 90.00, FALSE, CURRENT_DATE - INTERVAL '12 days', TRUE, CURRENT_DATE - INTERVAL '12 days', 'system', 'system', CURRENT_DATE - INTERVAL '12 days'),
  (8, 3, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 210.00, TRUE, CURRENT_DATE - INTERVAL '13 days', TRUE, CURRENT_DATE - INTERVAL '13 days', 'system', 'system', CURRENT_DATE - INTERVAL '13 days'),
  (9, 4, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 60.00, FALSE, CURRENT_DATE - INTERVAL '14 days', TRUE, CURRENT_DATE - INTERVAL '14 days', 'system', 'system', CURRENT_DATE - INTERVAL '14 days'),
  (10, 5, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 320.00, TRUE, CURRENT_DATE - INTERVAL '15 days', TRUE, CURRENT_DATE - INTERVAL '15 days', 'system', 'system', CURRENT_DATE - INTERVAL '15 days'),
  (11, 6, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 130.00, FALSE, CURRENT_DATE - INTERVAL '16 days', TRUE, CURRENT_DATE - INTERVAL '16 days', 'system', 'system', CURRENT_DATE - INTERVAL '16 days'),
  (12, 1, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 170.00, TRUE, CURRENT_DATE - INTERVAL '17 days', TRUE, CURRENT_DATE - INTERVAL '17 days', 'system', 'system', CURRENT_DATE - INTERVAL '17 days'),
  (13, 2, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 95.00, FALSE, CURRENT_DATE - INTERVAL '18 days', TRUE, CURRENT_DATE - INTERVAL '18 days', 'system', 'system', CURRENT_DATE - INTERVAL '18 days'),
  (14, 3, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 220.00, TRUE, CURRENT_DATE - INTERVAL '19 days', TRUE, CURRENT_DATE - INTERVAL '19 days', 'system', 'system', CURRENT_DATE - INTERVAL '19 days'),
  (15, 4, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 70.00, FALSE, CURRENT_DATE - INTERVAL '20 days', TRUE, CURRENT_DATE - INTERVAL '20 days', 'system', 'system', CURRENT_DATE - INTERVAL '20 days'),
  (16, 5, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 340.00, TRUE, CURRENT_DATE - INTERVAL '21 days', TRUE, CURRENT_DATE - INTERVAL '21 days', 'system', 'system', CURRENT_DATE - INTERVAL '21 days'),
  (17, 6, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 140.00, FALSE, CURRENT_DATE - INTERVAL '22 days', TRUE, CURRENT_DATE - INTERVAL '22 days', 'system', 'system', CURRENT_DATE - INTERVAL '22 days'),
  (18, 1, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 160.00, TRUE, CURRENT_DATE - INTERVAL '23 days', TRUE, CURRENT_DATE - INTERVAL '23 days', 'system', 'system', CURRENT_DATE - INTERVAL '23 days'),
  (19, 2, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 85.00, FALSE, CURRENT_DATE - INTERVAL '24 days', TRUE, CURRENT_DATE - INTERVAL '24 days', 'system', 'system', CURRENT_DATE - INTERVAL '24 days'),
  (20, 3, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 230.00, TRUE, CURRENT_DATE - INTERVAL '25 days', TRUE, CURRENT_DATE - INTERVAL '25 days', 'system', 'system', CURRENT_DATE - INTERVAL '25 days'),
  (21, 4, NULL, 2, '7c838a24-6ecc-4755-b585-39954bfd83d4', 80.00, FALSE, CURRENT_DATE - INTERVAL '26 days', TRUE, CURRENT_DATE - INTERVAL '26 days', 'system', 'system', CURRENT_DATE - INTERVAL '26 days'),
  (22, 5, NULL, 3, '7c838a24-6ecc-4755-b585-39954bfd83d4', 360.00, TRUE, CURRENT_DATE - INTERVAL '27 days', TRUE, CURRENT_DATE - INTERVAL '27 days', 'system', 'system', CURRENT_DATE - INTERVAL '27 days'),
  (23, 6, NULL, 4, '7c838a24-6ecc-4755-b585-39954bfd83d4', 150.00, FALSE, CURRENT_DATE - INTERVAL '28 days', TRUE, CURRENT_DATE - INTERVAL '28 days', 'system', 'system', CURRENT_DATE - INTERVAL '28 days'),
  (24, 1, NULL, 5, '7c838a24-6ecc-4755-b585-39954bfd83d4', 190.00, TRUE, CURRENT_DATE - INTERVAL '29 days', TRUE, CURRENT_DATE - INTERVAL '29 days', 'system', 'system', CURRENT_DATE - INTERVAL '29 days'),
  (25, 2, NULL, 1, '7c838a24-6ecc-4755-b585-39954bfd83d4', 105.00, FALSE, CURRENT_DATE - INTERVAL '30 days', TRUE, CURRENT_DATE - INTERVAL '30 days', 'system', 'system', CURRENT_DATE - INTERVAL '30 days');

SELECT setval('finance.invoice_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.receipt));
SELECT setval('finance.purchase_id_seq', (SELECT COALESCE(MAX(id), 1) FROM finance.purchase));
