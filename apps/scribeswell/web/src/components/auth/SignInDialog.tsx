/** Standalone account entry. Session evidence remains owned by Supabase Auth. */
import { useEffect, useRef, useState, type FormEvent } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export type AccountMode = 'signin' | 'signup';
interface SignInDialogProps { onClose: () => void; initialMode: AccountMode }

export function SignInDialog({onClose, initialMode}: SignInDialogProps) {
  const {signIn, signUp} = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pending, setPending] = useState(false);
  const generation = useRef(0);
  const submitting = useRef(false);
  const dialog = useRef<HTMLDivElement>(null);
  const emailInput = useRef<HTMLInputElement>(null);
  const trigger = useRef(document.activeElement as HTMLElement | null);
  const title = mode === 'signup' ? 'Create account' : 'Sign in';

  useEffect(() => {
    emailInput.current?.focus();
    // Inert every sibling along the modal's ancestor path, including header
    // controls and other body surfaces, without inverting an existing inert state.
    const background: Array<{node: HTMLElement; inert: boolean}> = [];
    let branch: HTMLElement | null = dialog.current;
    while (branch?.parentElement) {
      for (const sibling of Array.from(branch.parentElement.children)) {
        if (sibling !== branch && sibling instanceof HTMLElement) {
          background.push({node: sibling, inert: sibling.inert}); sibling.inert = true;
        }
      }
      branch = branch.parentElement;
      if (branch === document.body) break;
    }
    // Disabling the active submit button can move focus to body. Escape and
    // keyboard containment must continue to work while a request is pending.
    function outsideKeys(event: KeyboardEvent) {
      if (event.key === 'Escape') {event.preventDefault(); event.stopPropagation(); onClose(); return;}
      if (dialog.current?.contains(document.activeElement)) return;
      if (event.key === 'Tab') {event.preventDefault(); dialog.current?.querySelector<HTMLButtonElement>('button')?.focus();}
    }
    window.addEventListener('keydown', outsideKeys);
    return () => {
      window.removeEventListener('keydown', outsideKeys);
      generation.current++;
      for (const {node, inert} of background) node.inert = inert;
      if (trigger.current?.isConnected) trigger.current.focus({preventScroll: true});
    };
  }, []);

  useEffect(() => { if (!pending) emailInput.current?.focus(); else dialog.current?.querySelector<HTMLButtonElement>('button')?.focus(); }, [mode, pending]);

  function switchMode() {
    generation.current++;
    submitting.current = false;
    setLoading(false); setPassword(''); setError(null); setPending(false);
    setMode(previous => previous === 'signin' ? 'signup' : 'signin');
    emailInput.current?.focus();
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    const request = ++generation.current;
    setLoading(true); setError(null);
    const result = mode === 'signup' ? await signUp(email, password) : await signIn(email, password);
    if (request !== generation.current) return;
    submitting.current = false; setLoading(false);
    if (result.error) { setError(result.error); return; }
    setPassword('');
    if ('status' in result && result.status === 'confirmation-pending') setPending(true);
    else onClose();
  }
  return <div ref={dialog} className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" role="dialog" aria-modal="true" aria-labelledby="signin-title" onKeyDown={event => {
    if (event.key === 'Escape') {event.preventDefault(); event.stopPropagation(); onClose();}
    if (event.key === 'Tab') {
      const controls = Array.from(dialog.current?.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled])') ?? []);
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {event.preventDefault(); last?.focus();}
      else if (!event.shiftKey && document.activeElement === last) {event.preventDefault(); first?.focus();}
    }
  }}>
    <div className="bg-white rounded-xl shadow-xl w-full max-w-sm max-h-full overflow-y-auto p-6">
      <div className="flex items-center justify-between mb-4 gap-3">
        <h2 id="signin-title" className="text-lg font-semibold text-stone-800">{pending ? 'Check your email' : title}</h2>
        <button onClick={onClose} className="text-stone-500 p-1" aria-label={mode === 'signup' ? 'Close create account dialog' : 'Close sign in dialog'}><X className="w-5 h-5" /></button>
      </div>
      {pending ? <div className="space-y-4">
        <p role="status" className="text-sm text-stone-700">If this address can be registered, check your email for a confirmation link. If you already have an account, sign in. You can continue reading while you wait.</p>
        <button className="underline" onClick={switchMode}>Sign in</button>
        <button className="ml-4 underline" onClick={onClose}>Continue reading</button>
      </div> : <>
        <form aria-busy={loading} onSubmit={event => void submit(event)} className="space-y-4">
          <div><label htmlFor="email" className="block text-sm font-medium text-stone-700 mb-1">Email</label><input ref={emailInput} id="email" type="email" autoComplete="email" required value={email} onChange={event => setEmail(event.target.value)} className="w-full border border-stone-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500" /></div>
          <div><label htmlFor="password" className="block text-sm font-medium text-stone-700 mb-1">Password</label><input id="password" type="password" autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} required value={password} onChange={event => setPassword(event.target.value)} className="w-full border border-stone-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500" /></div>
          {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
          <button type="submit" disabled={loading} className="w-full bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-medium py-2 rounded-md text-sm">{loading ? (mode === 'signup' ? 'Requesting account…' : 'Signing in…') : title}</button>
        </form>
        {loading && <p role="status" className="mt-2 text-sm text-stone-600">{mode === 'signup' ? 'Requesting account…' : 'Signing in…'}</p>}
        <button className="mt-4 text-sm underline" onClick={switchMode}>{mode === 'signup' ? 'Sign in' : 'Create account'}</button>
        <p className="mt-4 text-xs text-stone-500 text-center">The reader works without an account.</p>
      </>}
    </div>
  </div>;
}
