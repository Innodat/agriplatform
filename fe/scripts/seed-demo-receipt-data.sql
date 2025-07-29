-- Insert demo receipts for the current user
-- This will use the actual database structure once we know it
DO $$
DECLARE
    current_user_id UUID;
    receipt_1 UUID;
    receipt_2 UUID;
    receipt_3 UUID;
    receipt_4 UUID;
    receipt_5 UUID;
BEGIN
    -- Get current authenticated user
    current_user_id := auth.uid();
    
    -- If no authenticated user, use a placeholder (for demo purposes)
    IF current_user_id IS NULL THEN
        current_user_id := '00000000-0000-0000-0000-000000000000';
    END IF;

    -- Insert demo receipts and capture their IDs
    INSERT INTO public.receipt (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_1;
    
    INSERT INTO public.receipt (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_2;
    
    INSERT INTO public.receipt (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_3;
    
    INSERT INTO public.receipt (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE - INTERVAL '12 days') RETURNING id INTO receipt_4;
    
    INSERT INTO public.receipt (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE - INTERVAL '12 days') RETURNING id INTO receipt_5;

    -- Insert purchase items for each receipt
    -- Note: We'll need to adjust these based on the actual purchase table structure
    INSERT INTO public.purchase (receipt_id, amount, description) VALUES
        (receipt_1, 300.00, 'Office supplies - Stationary'),
        (receipt_2, 650.00, 'Personal care items - Toiletries'),
        (receipt_3, 320.00, 'Lunch items - Food'),
        (receipt_4, 1700.00, 'Grocery shopping - Food'),
        (receipt_4, 70.00, 'Soap and shampoo - Toiletries'),
        (receipt_5, 640.00, 'Children toys - Toys'),
        (receipt_5, 4450.00, 'Bulk office supplies - Stationary');

END $$;
