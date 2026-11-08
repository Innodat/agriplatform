// UI doubles still run over the consumer's required same-site HTTPS transport.
// This disposable certificate is local test infrastructure, never release input.
import {mkdtempSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {createServer} from 'vite';

const directory=mkdtempSync(join(tmpdir(),'pts-ui-tls-'));
let server;
let closing=false;
async function stop(){
 if(closing)return;closing=true;
 try{if(server)await server.close();}finally{rmSync(directory,{recursive:true,force:true});}
}
try{
 const key=join(directory,'key.pem'),cert=join(directory,'cert.pem');
 execFileSync('openssl',['req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,DNS:files.localhost','-keyout',key,'-out',cert],{stdio:'ignore'});
 server=await createServer({server:{host:'127.0.0.1',port:5181,strictPort:true,https:{key:readFileSync(key),cert:readFileSync(cert)}}});
 for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>void stop().then(()=>process.exit(0)));
 await server.listen();server.printUrls();
}catch(error){await stop();throw error;}
