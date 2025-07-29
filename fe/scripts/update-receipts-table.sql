-- Update existing receipts table with proper defaults and RLS
ALTER TABLE public.receipts 
  ALTER COLUMN created_at SET DEFAULT NOW(),
  ALTER COLUMN modified_at SET DEFAULT NOW();

-- Add updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update modified_at
DROP TRIGGER IF EXISTS update_receipts_modified_at ON public.receipts;
CREATE TRIGGER update_receipts_modified_at
    BEFORE UPDATE ON public.receipts
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- Enable Row Level Security
ALTER TABLE public.receipts ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own receipts" ON public.receipts;
DROP POLICY IF EXISTS "Users can insert their own receipts" ON public.receipts;
DROP POLICY IF EXISTS "Users can update their own receipts" ON public.receipts;
DROP POLICY IF EXISTS "Users can delete their own receipts" ON public.receipts;

-- Create RLS policies for receipts
CREATE POLICY "Users can view their own receipts" ON public.receipts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own receipts" ON public.receipts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own receipts" ON public.receipts
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own receipts" ON public.receipts
  FOR DELETE USING (auth.uid() = user_id);

-- Create purchase_items table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.purchase_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  receipt_id UUID REFERENCES public.receipts(id) ON DELETE CASCADE,
  category TEXT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add trigger for purchase_items modified_at
DROP TRIGGER IF EXISTS update_purchase_items_modified_at ON public.purchase_items;
CREATE TRIGGER update_purchase_items_modified_at
    BEFORE UPDATE ON public.purchase_items
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- Enable RLS for purchase_items
ALTER TABLE public.purchase_items ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view purchase items for their receipts" ON public.purchase_items;
DROP POLICY IF EXISTS "Users can insert purchase items for their receipts" ON public.purchase_items;
DROP POLICY IF EXISTS "Users can update purchase items for their receipts" ON public.purchase_items;
DROP POLICY IF EXISTS "Users can delete purchase items for their receipts" ON public.purchase_items;

-- Create RLS policies for purchase_items
CREATE POLICY "Users can view purchase items for their receipts" ON public.purchase_items
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.receipts 
      WHERE public.receipts.id = public.purchase_items.receipt_id 
      AND public.receipts.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert purchase items for their receipts" ON public.purchase_items
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.receipts 
      WHERE public.receipts.id = public.purchase_items.receipt_id 
      AND public.receipts.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update purchase items for their receipts" ON public.purchase_items
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.receipts 
      WHERE public.receipts.id = public.purchase_items.receipt_id 
      AND public.receipts.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete purchase items for their receipts" ON public.purchase_items
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.receipts 
      WHERE public.receipts.id = public.purchase_items.receipt_id 
      AND public.receipts.user_id = auth.uid()
    )
  );
