import {createRequire} from 'node:module';
import {readFileSync,realpathSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const fail=()=>{throw new Error('api_client_tool_invalid');};
export function qualifyTool(owner=import.meta.url){
 try{
  const require=createRequire(owner),metadata=require.resolve('@hey-api/openapi-ts/package.json');
  const pkg=JSON.parse(readFileSync(metadata,'utf8'));
  // Resolve from the build-tool owner, not the hoisted upstream tool: apps retain TS7.
  const compilerMetadata=require.resolve('typescript/package.json');
  const ts=JSON.parse(readFileSync(compilerMetadata,'utf8'));
  if(pkg.name!=='@hey-api/openapi-ts'||pkg.version!=='0.99.0'||ts.name!=='typescript'||ts.version!=='6.0.3')fail();
  const toolRoot=realpathSync(dirname(metadata)),compilerRoot=realpathSync(dirname(compilerMetadata));
  const compiler=realpathSync(require.resolve('typescript'));
  if(!compiler.startsWith(compilerRoot+'/'))fail();
  // The package bin launches this actual upstream CLI in a second process; select
  // its pinned entry directly so --import is confined to this bounded CLI child.
  const cli=realpathSync(resolve(toolRoot,'dist/run.mjs'));
  if(!cli.startsWith(toolRoot+'/'))fail();
  return {toolRoot,compilerURL:pathToFileURL(compiler).href,cli};
 }catch{fail();}
}
export function compatibilityResolution(specifier,parentURL,qualified){
 if(specifier!=='typescript'||!parentURL?.startsWith('file:'))return null;
 const parent=fileURLToPath(parentURL);
 return parent.startsWith(qualified.toolRoot+'/')?qualified.compilerURL:null;
}
