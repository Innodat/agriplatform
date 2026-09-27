// Only used by the isolated shared-session browser suite; no collection/database access.
const http=require('node:http');
const requests=[];
http.createServer((req,res)=>{
 const path=new URL(req.url,'http://localhost').pathname;res.setHeader('Content-Type','application/json');
 if(path==='/health')return res.end('{}');
 if(path==='/requests')return res.end(JSON.stringify(requests));
 requests.push(path);
 if(path==='/api/bible/books/Gen')return res.end(JSON.stringify({id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1,chapters:[{id:1,chapter_num:1}]}));
 if(path==='/api/bible/books')return res.end(JSON.stringify({data:[{id:1,osis_id:'Gen',name_en:'Genesis',name_he:'בראשית',testament:'OT',book_order:1}],total:1}));
 if(path==='/api/bible/books/Gen/chapters/1/verses')return res.end(JSON.stringify({data:[{id:1,verse_num:1,book_id:1,chapter_num:1,words:[{id:1,position:1,surface_he:'בְּרֵאשִׁית',display_he:'בְּרֵאשִׁית',lemma_strong:null,morph_code:null}]}],total:1}));
 res.statusCode=404;res.end('{}');
}).listen(5185,'127.0.0.1');
