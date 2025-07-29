-- Enable Row Level Security for receipt table
ALTER TABLE public.receipt ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own receipts" ON public.receipt;
DROP POLICY IF EXISTS "Users can insert their own receipts" ON public.receipt;
DROP POLICY IF EXISTS "Users can update their own receipts" ON public.receipt;
DROP POLICY IF EXISTS "Users can delete their own receipts" ON public.receipt;

-- Create RLS policies for receipt table
CREATE POLICY "Users can view their own receipts" ON public.receipt
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own receipts" ON public.receipt
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own receipts" ON public.receipt
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own receipts" ON public.receipt
  FOR DELETE USING (auth.uid() = user_id);

-- Enable RLS for purchase table
ALTER TABLE public.purchase ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view purchase items for their receipts" ON public.purchase;
DROP POLICY IF EXISTS "Users can insert purchase items for their receipts" ON public.purchase;
DROP POLICY IF EXISTS "Users can update purchase items for their receipts" ON public.purchase;
DROP POLICY IF EXISTS "Users can delete purchase items for their receipts" ON public.purchase;

-- Create RLS policies for purchase table
CREATE POLICY "Users can view purchase items for their receipts" ON public.purchase
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.receipt 
      WHERE public.receipt.id = public.purchase.receipt_id 
      AND public.receipt.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert purchase items for their receipts" ON public.purchase
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.receipt 
      WHERE public.receipt.id = public.purchase.receipt_id 
      AND public.receipt.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update purchase items for their receipts" ON public.purchase
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.receipt 
      WHERE public.receipt.id = public.purchase.receipt_id 
      AND public.receipt.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete purchase items for their receipts" ON public.purchase
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.receipt 
      WHERE public.receipt.id = public.purchase.receipt_id 
      AND public.receipt.user_id = auth.uid()
    )
  );

-- Add trigger function for modified_at if it doesn't exist
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for both tables if they don't exist
DROP TRIGGER IF EXISTS update_receipt_modified_at ON public.receipt;
CREATE TRIGGER update_receipt_modified_at
    BEFORE UPDATE ON public.receipt
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

DROP TRIGGER IF EXISTS update_purchase_modified_at ON public.purchase;
CREATE TRIGGER update_purchase_modified_at
    BEFORE UPDATE ON public.purchase
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();
