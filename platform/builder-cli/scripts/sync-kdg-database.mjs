// Explicit fixed-root code/test synchronization, never database execution.
import {fileURLToPath} from 'node:url';
import {syncKdgDatabase} from '../src/kdg-database-pattern.ts';
try{
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw Error('arguments_invalid');
 syncKdgDatabase(fileURLToPath(new URL('../../../',import.meta.url)),process.argv[2]==='--check');console.log('KDG database candidate code/test parity verified.');
}catch(error){console.error(error instanceof Error&&/^(scaffold_[a-z_]+|database_pattern_(?:invalid|drift)|arguments_invalid)$/.test(error.message)?error.message:'database_pattern_failed');process.exitCode=1;}
