import { useState } from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import { Check } from 'lucide-react';
import { z } from 'zod';
import { createClient } from '@supabase/supabase-js';

export const inputSchema = z.object({ count: z.number().int().min(0) });
export function createLocalAuthClient(fetch: typeof globalThis.fetch) {
  return createClient('http://127.0.0.1:55481', 'synthetic-public-key', {
    auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
    global: { fetch },
  });
}

export function Fixture() {
  const [count, setCount] = useState(0);
  return <main className="p-4"><Routes>
    <Route path="/" element={<>
      <h1>ENV synthetic compatibility fixture</h1>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <output role="status">Count {count}</output><Check aria-hidden="true" />
      <Link to="/details">Details</Link>
    </>} />
    <Route path="/details" element={<h1>Synthetic details</h1>} />
  </Routes></main>;
}
