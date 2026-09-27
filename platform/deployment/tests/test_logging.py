import ast
import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
class Logging(unittest.TestCase):
 def test_reader_exception_log_does_not_include_upstream_error_or_url(self):
  source=Path(__file__).resolve().parents[3]/'apps/scribeswell/backend/main.py'
  function=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='unhandled_exception_handler')
  function.decorator_list=[]
  for arg in function.args.args:arg.annotation=None
  namespace={'logging':logging,'__name__':'release-log-test','JSONResponse':lambda **kwargs:kwargs}
  exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
  with self.assertLogs('release-log-test',level='ERROR') as logs:
   asyncio.run(namespace['unhandled_exception_handler'](SimpleNamespace(url=SimpleNamespace(path='/private-token')),RuntimeError('secret-signed-url')))
  self.assertNotIn('secret-signed-url',str(logs.output));self.assertNotIn('private-token',str(logs.output))
