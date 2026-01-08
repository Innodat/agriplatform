CREATE OR REPLACE FUNCTION finance.create_receipt_with_purchases(
  p_supplier      text,
  p_receipt_date  date,
  p_currency_id   bigint,
  p_reimbursable  boolean,
  p_items         jsonb
)
RETURNS TABLE (
  receipt_id bigint,
  receipt    jsonb,
  purchases  jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''  -- 🔒 lock search_path; fully qualify below
AS $fn$
DECLARE
  v_user uuid := auth.uid();
  v_org_id uuid := identity.current_org_id();
  v_receipt_id bigint;
BEGIN
  IF v_user IS NULL THEN
    RAISE EXCEPTION 'Not authenticated';
  END IF;

  IF v_org_id IS NULL THEN
    RAISE EXCEPTION 'Organization context required';
  END IF;

  IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
    RAISE EXCEPTION 'items must be a non-empty JSON array';
  END IF;

  INSERT INTO finance.receipt (org_id, supplier, receipt_date, created_by, created_at, updated_at)
  VALUES (v_org_id, p_supplier, p_receipt_date, v_user, now(), now())
  RETURNING id INTO v_receipt_id;

  WITH ins AS (
    INSERT INTO finance.purchase (
      expense_type_id,
      other_category,
      currency_id,
      user_id,
      amount,
      is_active,
      reimbursable,
      receipt_id,
      created_by,
      updated_by,
      created_at,
      updated_at
    )
    SELECT
      i.expense_type_id,
      i.other_category,
      COALESCE(i.currency_id, p_currency_id),
      i.user_id,
      i.amount,
      true,
      COALESCE(i.reimbursable, p_reimbursable),
      v_receipt_id,
      v_user,
      v_user,
      now(),
      now()
    FROM jsonb_to_recordset(p_items) AS i(
      expense_type_id bigint,
      amount          numeric,
      other_category  text,
      currency_id     bigint,
      reimbursable    boolean,
      user_id         uuid
    )
    RETURNING *
  ),
  r AS (
    SELECT jsonb_build_object(
      'id', rec.id,
      'supplier', rec.supplier,
      'content_id', rec.content_id,
      'is_active', rec.is_active,
      'created_by', rec.created_by,
      'updated_by', rec.updated_by,
      'created_at', rec.created_at,
      'updated_at', rec.updated_at,
      'receipt_date', rec.receipt_date
    ) AS j
    FROM finance.receipt rec
    WHERE rec.id = v_receipt_id
  ),
  p AS (
    SELECT jsonb_agg(to_jsonb(ins.*)) AS j
    FROM ins
  )
  SELECT v_receipt_id, r.j, COALESCE(p.j, '[]'::jsonb)
  INTO receipt_id, receipt, purchases
  FROM r, p;

  RETURN NEXT;
END;
$fn$;

-- Ensure schema is exposed in Supabase API settings (Studio -> API -> Exposed Schemas)
GRANT USAGE ON SCHEMA finance TO authenticated, anon;

GRANT EXECUTE ON FUNCTION finance.create_receipt_with_purchases(
  text, date, bigint, boolean, jsonb
) TO authenticated;
