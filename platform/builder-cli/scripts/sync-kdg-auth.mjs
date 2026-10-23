// Scoped owning generator; use --check in CI or --write to update unedited managed files.
import {fileURLToPath} from 'node:url';
import {checkKdgAuthPattern,syncKdgAuthPattern} from '../src/kdg-auth-pattern.ts';
const root=fileURLToPath(new URL('../../../',import.meta.url));
try{
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw new Error('arguments_invalid');
 (process.argv[2]==='--check'?checkKdgAuthPattern:syncKdgAuthPattern)(root);
 process.stdout.write('KDG Auth template and generated-test parity verified.\n');
}catch(error){process.stderr.write((error instanceof Error&&/^(scaffold_[a-z_]+|kdg_auth_(?:template_drift|manifest_invalid)|arguments_invalid)$/.test(error.message)?error.message:'auth_pattern_failed')+'\n');process.exitCode=1;}
