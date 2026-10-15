import { defineConfig } from 'vitest/config';
// The retained workspace graph resolves Vitest's own Vite dependency separately.
// Keep build plugins on the fixture's exact Vite8 identity in vite.config.ts.
export default defineConfig({ test: { environment: 'jsdom' }, esbuild: { jsx: 'automatic' } });
