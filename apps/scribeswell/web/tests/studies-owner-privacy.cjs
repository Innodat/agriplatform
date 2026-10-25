// No payload/URL values leave this observer; qualification fails on unreadable
// non-bodyless responses rather than silently excluding another origin/type.
function credentialInspection(sentinels){
 let leaked=false,incomplete=false;const pending=[];
 const check=value=>{const text=Buffer.isBuffer(value)?value.toString('latin1'):String(value??'');if(sentinels.some(key=>text.includes(key)||text.includes(encodeURIComponent(key))))leaked=true;};
 const inspectPage=page=>page.on('websocket',socket=>{check(socket.url());socket.on('framesent',event=>check(event.payload));socket.on('framereceived',event=>check(event.payload));});
 return {
  inspect(context){
   context.on('request',request=>{check(request.url());for(const value of Object.values(request.headers()))check(value);check(request.postData());});
   context.on('response',response=>{
    check(response.url());for(const value of Object.values(response.headers()))check(value);
    if(![101,204,205,304].includes(response.status()))pending.push(response.body().then(check).catch(()=>{if(![301,302,303,307,308].includes(response.status()))incomplete=true;}));
   });
   context.on('page',inspectPage);for(const page of context.pages())inspectPage(page);
  },
  async settle(){let count;do{count=pending.length;await Promise.all(pending);}while(count!==pending.length);if(leaked||incomplete)throw Error('Service credential inspection failed');return {leaked:false,complete:true};},
 };
}
module.exports={credentialInspection};
