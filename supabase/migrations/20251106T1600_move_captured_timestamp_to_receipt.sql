-- Migration: Move captured_timestamp from purchase to receipt table and rename to captured_at
-- Date: 2025-11-06

-- Add captured_at column to receipt table
ALTER TABLE finance.receipt 
ADD COLUMN IF NOT EXISTS captured_at TIMESTAMP;

-- Migrate data: Set receipt.captured_at to the earliest purchase.captured_timestamp for each receipt
UPDATE finance.receipt r
SET captured_at = (
  SELECT MIN(p.captured_timestamp)
  FROM finance.purchase p
  WHERE p.receipt_id = r.id
)
WHERE r.captured_at IS NULL;

-- Set default for new receipts
ALTER TABLE finance.receipt 
ALTER COLUMN captured_at SET DEFAULT CURRENT_TIMESTAMP;

-- Drop captured_timestamp from purchase table
ALTER TABLE finance.purchase 
DROP COLUMN IF EXISTS captured_timestamp;

-- Add comment
COMMENT ON COLUMN finance.receipt.captured_at IS 'Timestamp when the receipt was captured/created';
