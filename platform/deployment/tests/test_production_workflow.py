"""Acceptance contracts for one production environment and fail-stop sequencing."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[3]
class ProductionWorkflow(unittest.TestCase):
 def test_only_production_trigger_and_main_guard(self):
  workflows=ROOT/'.github/workflows'
  self.assertFalse((workflows/'staging.yml').exists())
  text=(workflows/'production.yml').read_text()
  self.assertRegex(text,r'push:\s+branches: \[main\]')
  self.assertIn('workflow_dispatch:',text)
  self.assertIn("if: github.ref == 'refs/heads/main'",text)
  self.assertIn('environment: production',text)
  self.assertIn('RELEASE_SHA: ${{ github.sha }}',text)
  self.assertIn('cancel-in-progress: false',text)
  self.assertNotIn('verify-promotion.py',text)
  self.assertNotIn('needs.verify',text)
 def test_all_gates_precede_live_mutations(self):
  text=(ROOT/'.github/workflows/production.yml').read_text()
  ordered=['check-ci-inputs.py','release.py check','install-frontends.py','build-release.mjs','playwright.release.config.cjs','gateway_smoke.py','ci-build.py','container_smoke.py','ci-deploy.sh','publish-frontend.py','record-production.py']
  positions=[text.rindex(item) if item=='record-production.py' else text.index(item) for item in ordered]
  self.assertEqual(positions,sorted(positions))
  self.assertNotIn('continue-on-error:',text)
  self.assertNotIn('--alias=staging',text)
  self.assertIn('packages: write',text)
  self.assertIn('if: always()',text)
  self.assertIn('platform/deployment/public-release/',text)
  self.assertIn('            netlify.toml',text)
  self.assertLess(text.index('record-production.py --preflight'),text.index('ci-deploy.sh'))
  self.assertIn('apps/pts/web/node_modules/.bin/playwright install --with-deps chromium',text)
 def test_initial_size_and_environment(self):
  text=(ROOT/'platform/deployment/terraform/example.tfvars').read_text()
  self.assertRegex(text,r'environment\s*= "production"')
  self.assertRegex(text,r'server_type\s*= "cpx12"')

 def test_frontend_filter_preserves_backend_gates_and_evidence(self):
  text=(ROOT/'.github/workflows/production.yml').read_text()
  self.assertIn('fetch-depth: 0',text)
  self.assertIn('force_frontend_build:',text)
  self.assertIn('record-production.py --select',text)
  self.assertIn('record-production.py --retained',text)
  self.assertIn('            frontend-plan.json',text)
  steps=re.split(r'      - ',text)
  for command in ['install-frontends.py','build-release.mjs','playwright.release.config.cjs','publish-frontend.py']:
   step=next(step for step in steps if command in step)
   self.assertIn("if: steps.frontend.outputs.build == 'true'",step)
  for command in ['gateway_smoke.py','ci-build.py','container_smoke.py','ci-deploy.sh']:
   step=next(step for step in steps if command in step)
   self.assertNotIn('if:',step)
  self.assertLess(text.index('record-production.py --select'),text.index('install-frontends.py'))
