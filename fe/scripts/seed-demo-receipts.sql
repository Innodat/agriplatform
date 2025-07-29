-- Insert demo receipts for the current user
-- Note: Replace the user_id with actual authenticated user ID when running
DO $$
DECLARE
    current_user_id UUID;
    receipt_1 UUID;
    receipt_2 UUID;
    receipt_3 UUID;
    receipt_4 UUID;
    receipt_5 UUID;
BEGIN
    -- Get current authenticated user (this will work when run from authenticated context)
    current_user_id := auth.uid();
    
    -- If no authenticated user, use a placeholder (for demo purposes)
    IF current_user_id IS NULL THEN
        current_user_id := '00000000-0000-0000-0000-000000000000';
    END IF;

    -- Insert demo receipts and capture their IDs
    INSERT INTO public.receipts (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_1;
    
    INSERT INTO public.receipts (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_2;
    
    INSERT INTO public.receipts (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE) RETURNING id INTO receipt_3;
    
    INSERT INTO public.receipts (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE - INTERVAL '12 days') RETURNING id INTO receipt_4;
    
    INSERT INTO public.receipts (user_id, captured_date) VALUES
        (current_user_id, CURRENT_DATE - INTERVAL '12 days') RETURNING id INTO receipt_5;

    -- Insert purchase items for each receipt
    INSERT INTO public.purchase_items (receipt_id, category, amount, description) VALUES
        (receipt_1, 'Stationary', 300.00, 'Office supplies'),
        (receipt_2, 'Toiletries', 650.00, 'Personal care items'),
        (receipt_3, 'Food', 320.00, 'Lunch items'),
        (receipt_4, 'Food', 1700.00, 'Grocery shopping'),
        (receipt_4, 'Toiletries', 70.00, 'Soap and shampoo'),
        (receipt_5, 'Toys', 640.00, 'Children toys'),
        (receipt_5, 'Stationary', 4450.00, 'Bulk office supplies');

END $$;
