// Scoped build-time synchronization; no output override or forced adoption.
import {fileURLToPath} from 'node:url';
import {syncKdgLocalHost} from '../src/kdg-local-host-pattern.ts';
try{
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw Error('arguments_invalid');
 syncKdgLocalHost(fileURLToPath(new URL('../../../',import.meta.url)),process.argv[2]==='--check');console.log('KDG local host code/test parity verified.');
}catch(error){console.error(error instanceof Error&&/^(scaffold_[a-z_]+|local_host_pattern_(?:invalid|drift)|arguments_invalid)$/.test(error.message)?error.message:'local_host_pattern_failed');process.exitCode=1;}
