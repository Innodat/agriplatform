#!/usr/bin/env node
import {generateClient} from './generate.mjs';
try {
 const args=process.argv.slice(2),options={};
 while(args.length){const flag=args.shift();if(flag==='--check'&&!Object.hasOwn(options,'check'))options.check=true;
 else if((flag==='--schema'||flag==='--output')&&!Object.hasOwn(options,flag.slice(2))&&args.length&&!args[0].startsWith('--'))options[flag.slice(2)]=args.shift();
 else throw new Error('api_client_arguments_invalid');}
 if(!options.schema||!options.output)throw new Error('api_client_arguments_invalid');
 generateClient(options);process.stdout.write(options.check?'api_client_current\n':'api_client_generated\n');
}catch(error){const identifier=error instanceof Error&&/^(api_client|scaffold)_[a-z_]+$/.test(error.message)?error.message:'api_client_failed';process.stderr.write(identifier+'\n');process.exitCode=1;}
