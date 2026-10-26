// Explicit source synchronization only; no database or browser activation.
import {fileURLToPath} from 'node:url';
import {syncKdgOffline} from '../src/kdg-offline-pattern.ts';
try{
 if(process.argv.length!==3||!['--check','--write'].includes(process.argv[2]))throw Error('arguments_invalid');
 syncKdgOffline(fileURLToPath(new URL('../../../',import.meta.url)),process.argv[2]==='--check');console.log('KDG IndexedDB primitive code/test parity verified.');
}catch(error){console.error(error instanceof Error&&/^(scaffold_[a-z_]+|offline_pattern_(?:invalid|drift)|arguments_invalid)$/.test(error.message)?error.message:'offline_pattern_failed');process.exitCode=1;}
