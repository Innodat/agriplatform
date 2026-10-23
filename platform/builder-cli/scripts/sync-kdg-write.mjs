// Explicit fixed-root source synchronization. Never connects to a database.
import {fileURLToPath} from 'node:url';
import {syncKdgWrite} from '../src/kdg-write-pattern.ts';
try{
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw Error('arguments_invalid');
 syncKdgWrite(fileURLToPath(new URL('../../../',import.meta.url)),process.argv[2]==='--check');console.log('KDG write context code/test parity verified.');
}catch(error){console.error(error instanceof Error&&/^(scaffold_[a-z_]+|write_pattern_(?:invalid|drift)|arguments_invalid)$/.test(error.message)?error.message:'write_pattern_failed');process.exitCode=1;}
