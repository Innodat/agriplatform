// Fixed-root native test code synchronization only; never connects or prepares a DB.
import {fileURLToPath} from 'node:url';
import {syncKdgNativeDatabase} from '../src/kdg-database-pattern.ts';
try {
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw Error('arguments_invalid');
 syncKdgNativeDatabase(fileURLToPath(new URL('../../../',import.meta.url)),process.argv[2]==='--check');
 console.log('KDG native database test parity verified.');
} catch(error) {
 console.error(error instanceof Error&&/^(scaffold_[a-z_]+|database_pattern_(?:invalid|drift)|arguments_invalid)$/.test(error.message)?error.message:'database_pattern_failed');
 process.exitCode=1;
}
