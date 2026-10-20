// Loaded only in the upstream CLI child, never an app/compiler process.
import {registerHooks} from 'node:module';
import {compatibilityResolution,qualifyTool} from './tooling.mjs';
const qualified=qualifyTool();
registerHooks({resolve(specifier,context,nextResolve){
 const url=compatibilityResolution(specifier,context.parentURL,qualified);
 return url?{url,shortCircuit:true}:nextResolve(specifier,context);
}});
