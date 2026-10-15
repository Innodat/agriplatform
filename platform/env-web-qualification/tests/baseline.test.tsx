import { afterEach, expect, test } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { Fixture, createLocalAuthClient, inputSchema } from '../src/Fixture';

afterEach(cleanup);

test('React DOM interaction and routing render the synthetic result', async () => {
  render(<MemoryRouter initialEntries={['/']}><Fixture /></MemoryRouter>);
  await userEvent.click(screen.getByRole('button', { name: 'Increment' }));
  expect(screen.getByRole('status').textContent).toBe('Count 1');
  await userEvent.click(screen.getByRole('link', { name: 'Details' }));
  expect(screen.getByRole('heading').textContent).toBe('Synthetic details');
});

test('Zod rejects invalid input with typed diagnostic', () => {
  const result = inputSchema.safeParse({ count: -1 });
  expect(result.success).toBe(false);
  if (!result.success) expect(result.error.issues[0]?.code).toBe('too_small');
  expect(inputSchema.parse({ count: 1 })).toEqual({ count: 1 });
});

test('Supabase Auth initializes locally without any external request', async () => {
  let requests = 0;
  const client = createLocalAuthClient(async () => { requests++; throw new Error('network forbidden'); });
  expect(await client.auth.getSession()).toEqual({ data: { session: null }, error: null });
  expect(requests).toBe(0);
  expect(await client.auth.signOut({ scope: 'local' })).toEqual({ error: null });
  expect(requests).toBe(0);
});
