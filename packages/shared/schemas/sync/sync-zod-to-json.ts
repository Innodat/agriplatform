import { writeFileSync, mkdirSync } from 'fs'
import { resolve } from 'path'
import { zodToJsonSchema } from 'zod-to-json-schema'
import * as schemas from '../zod'

const outputDir = resolve(__dirname, '..', 'pydantic')
mkdirSync(outputDir, { recursive: true })

Object.entries(schemas).forEach(([name, schema]) => {
  const jsonSchema = zodToJsonSchema(schema, name)
  const filePath = resolve(outputDir, `${name}.json`)
  writeFileSync(filePath, JSON.stringify(jsonSchema, null, 2))
  console.log(`✅ Synced ${name} → ${filePath}`)
})
