import { spawn } from 'child_process'
import { platform } from 'os'
import { z } from 'zod'
import { resolve } from 'path'
import { existsSync } from 'fs'

// CLI arg validation
const ArgsSchema = z.object({
  input: z.string().min(1).default('./src/index.css'),
  output: z.string().min(1).default('./dist/output.css'),
  watch: z.boolean().optional(),
  minify: z.boolean().optional(),
  init: z.boolean().optional(),
  postcss: z.boolean().optional(),
})

const rawArgs = process.argv.slice(2)
const flags: Record<string, any> = {}
rawArgs.forEach((arg, i) => {
  if (arg === '-i') flags.input = rawArgs[i + 1]
  if (arg === '-o') flags.output = rawArgs[i + 1]
  if (arg === '--watch') flags.watch = true
  if (arg === '--minify') flags.minify = true
  if (arg === 'init') flags.init = true
  if (arg === '-p') flags.postcss = true
})

const parsed = ArgsSchema.safeParse(flags)
if (!parsed.success) {
  console.error('❌ Invalid args:', parsed.error.format())
  process.exit(1)
}

// Approval gate stub
console.log('✅ Tailwind args approved:', parsed.data)

const tailwindPath = resolve(
  __dirname, '..', '..', '..',
  'frontend', 'node_modules', 'tailwindcss', 'lib', 'cli.js'
)

if (!existsSync(tailwindPath)) {
  console.error(`❌ Tailwind CLI not found at ${tailwindPath}`)
  process.exit(1)
}

const cliArgs = parsed.data.init
  ? ['init', parsed.data.postcss ? '-p' : '']
  : ['-i', parsed.data.input, '-o', parsed.data.output]
if (parsed.data.watch) cliArgs.push('--watch')
if (parsed.data.minify) cliArgs.push('--minify')

spawn('node', [tailwindPath, ...cliArgs.filter(Boolean)], {
  stdio: 'inherit',
  shell: platform() === 'win32'
})