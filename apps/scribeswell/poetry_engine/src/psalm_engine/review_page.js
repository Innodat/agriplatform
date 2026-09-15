/* Portable review state. No server, external scripts, or automatic approval. */
class PtsReviewState {
  constructor(packet, hash) {
    this.packet = packet; this.hash = hash; this.reviewer = '';
    this.values = Object.fromEntries(packet.items.map(i => [i.id, {
      id:i.id, item_sha256:i.item_sha256, status:'pending', reviewer:'',
      category:i.category, kind:i.kind, summary:i.summary,
      alternatives:[...i.alternatives], notes:''
    }]));
  }
  edit(id, key, value) {
    if (!['category','kind','summary','alternatives','notes'].includes(key)) throw Error('Unknown field');
    this.values[id][key] = value; this.values[id].status = 'pending'; this.values[id].reviewer = '';
  }
  decide(id, status) {
    if (!['pending','approved','rejected','disputed','context'].includes(status)) throw Error('Unknown decision');
    const d = {...this.values[id], status, reviewer:status==='pending'?'':this.reviewer.trim()};
    this.validate(d, status !== 'pending'); this.values[id] = d;
  }
  validate(d, final=false) {
    const item=this.packet.items.find(i=>i.id===d.id);
    if(!item || d.item_sha256!==item.item_sha256) throw Error('The reviewed item has changed.');
    if(!['pending','approved','rejected','disputed','context'].includes(d.status) ||
       !['analysis','principle'].includes(d.kind)) throw Error('Invalid review fields.');
    if(!['reviewer','category','summary','notes'].every(k=>typeof d[k]==='string') ||
       !Array.isArray(d.alternatives) || !d.alternatives.every(a=>typeof a==='string')) throw Error('Invalid review text.');
    if(final && (!d.reviewer.trim() || !d.category.trim() || !d.summary.trim()))
      throw Error('Enter your reviewer identifier, category and a substantive claim.');
    if(final && ['rejected','disputed'].includes(d.status) && !d.notes.trim())
      throw Error('Explain the rejection or disagreement in your review notes.');
  }
  work() { return {format:'pts-review-work-1',packet_sha256:this.hash,reviewer:this.reviewer,items:Object.values(this.values)}; }
  restore(work) {
    if(work.format!=='pts-review-work-1' || work.packet_sha256!==this.hash) throw Error('This work belongs to a different or changed packet.');
    if(typeof work.reviewer!=='string' || !Array.isArray(work.items) ||
       work.items.length!==this.packet.items.length || new Set(work.items.map(i=>i.id)).size!==work.items.length)
      throw Error('Incomplete or duplicate review items.');
    const next={};
    for(const d of work.items){this.validate(d,d.status!=='pending');next[d.id]=structuredClone(d);}
    this.values=next;this.reviewer=work.reviewer;
  }
  decisions() {
    const rows=Object.values(this.values).filter(d=>d.status!=='pending');
    if(!rows.length) throw Error('No decisions yet. Save work to keep unfinished edits.');
    rows.forEach(d=>this.validate(d,true));
    return {format:'pts-review-decisions-1',packet_sha256:this.hash,decisions:structuredClone(rows)};
  }
}
globalThis.PtsReviewState=PtsReviewState;
if(typeof document!=='undefined') {
  const {packet,packet_sha256}=JSON.parse(document.getElementById('review-data').textContent);
  const state=new PtsReviewState(packet,packet_sha256);
  const $=id=>document.getElementById(id);
  let selected=packet.items[0].id, dirty=false;
  const fileUri=path=>'file://'+path.split('/').map(encodeURIComponent).join('/');
  function message(text,error=false){$('message').textContent=text;$('message').className=error?'error':'';}
  function download(value,suffix){
    const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=packet.source.dataset.replace('.pdf','')+suffix;
    a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function filtered(){const q=$('search').value.toLowerCase(),f=$('filter').value;
    return packet.items.filter(i=>(f==='all'||state.values[i.id].status===f)&&
      [i.title,...i.references,state.values[i.id].summary,state.values[i.id].category].join(' ').toLowerCase().includes(q));}
  function nav(){
    $('item-list').replaceChildren();
    for(const i of filtered()){
      const b=document.createElement('button');b.className='item-link';b.setAttribute('aria-current',String(i.id===selected));
      const label=document.createElement('small');const dot=document.createElement('span');dot.className='dot '+state.values[i.id].status;
      label.append(dot,document.createTextNode(i.references.join(' · ')));const title=document.createElement('strong');title.textContent=i.title;
      b.append(label,title);b.onclick=()=>{selected=i.id;render();};$('item-list').append(b);
    }
    const counts=Object.values(state.values);$('progress').textContent=`${counts.filter(d=>d.status==='approved').length} approved · ${counts.filter(d=>d.status==='pending').length} pending · ${counts.length} items`;
  }
  function showPage(page){
    const img=packet.page_images[String(page)];$('source-label').textContent='PDF page '+page;
    $('source-page').value=String(page);$('source-image').src=fileUri(img.uri);
    $('source-image').alt=`${packet.source.dataset}, Appendix page ${page}`;
    $('source-image').style.width=(img.panels*100)+'%';$('source-image').style.marginLeft=(-img.position*100)+'%';
    $('open-image').href=fileUri(img.uri);$('open-pdf').href=fileUri(packet.source.uri)+'#page='+page;
  }
  function render(){
    nav();const visible=filtered();if(!visible.some(i=>i.id===selected)) selected=visible[0]?.id;
    $('empty').hidden=!!selected;$('editor-content').hidden=!selected;if(!selected)return;
    nav();const i=packet.items.find(i=>i.id===selected),d=state.values[selected];
    $('item-title').textContent=i.title;$('references').textContent=i.references.join(' · ');
    $('item-status').textContent=d.status+(d.reviewer?' · '+d.reviewer:'');
    for(const key of ['summary','category','kind','notes','status'])$(key).value=d[key];
    $('alternatives').value=d.alternatives.join('\n');$('category-label').textContent=packet.categories[d.category]||'Custom category';
    $('evidence').replaceChildren();const pages=[...new Set(i.support.map(id=>packet.units[id].page))];
    $('source-page').replaceChildren(...pages.map(p=>{const o=document.createElement('option');o.value=p;o.textContent='Page '+p;return o;}));
    for(const id of i.support){const unit=packet.units[id];const details=document.createElement('details');details.className='evidence';details.open=true;
      const summary=document.createElement('summary');summary.textContent=`${unit.label} · page ${unit.page}`;
      const button=document.createElement('button');button.textContent='View source';button.onclick=e=>{e.preventDefault();showPage(unit.page);};
      summary.append(button);const text=document.createElement('p');text.textContent=unit.text;details.append(summary,text);$('evidence').append(details);}
    $('coverage').textContent=`${packet.items.length} proposed observations; ${packet.coverage.length} original fragments accounted for. Supporting footnotes are joined across extraction breaks.`;
    showPage(pages[0]);
  }
  function changed(key){if(!selected)return;state.edit(selected,key,key==='alternatives'?$(key).value.split('\n').map(s=>s.trim()).filter(Boolean):$(key).value);
    dirty=true;$('status').value='pending';$('item-status').textContent='pending';nav();if(key==='category')$('category-label').textContent=packet.categories[$('category').value]||'Custom category';}
  function decide(status){if(!selected)return;state.decide(selected,status);dirty=true;message('Decision recorded locally. Save work or export decisions to keep it.');render();}
  function next(afterId=selected){const all=packet.items,at=all.findIndex(i=>i.id===afterId);const order=[...all.slice(at+1),...all.slice(0,at+1)];
    const n=order.find(i=>state.values[i.id].status==='pending');if(n){$('filter').value='all';$('search').value='';selected=n.id;render();}else message('No pending items remain. Export your decisions.');}
  $('guide-title').textContent=packet.source.dataset.replace('.pdf','').replace('psalms-','Psalm ');
  for(const [value,label] of Object.entries(packet.categories)){const o=document.createElement('option');o.value=value;o.label=label;$('categories').append(o);}
  for(const key of ['summary','category','notes','alternatives'])$(key).oninput=()=>changed(key);
  $('kind').onchange=()=>changed('kind');$('reviewer').oninput=()=>{state.reviewer=$('reviewer').value;dirty=true;};
  $('status').onchange=()=>{try{decide($('status').value);}catch(e){message(e.message,true);$('status').value=state.values[selected].status;}};
  $('approve').onclick=()=>{try{const previous=selected;decide('approved');next(previous);}catch(e){message(e.message,true);}};
  $('next').onclick=()=>next();$('source-page').onchange=()=>showPage(Number($('source-page').value));
  $('zoom').oninput=()=>{$('zoom-frame').style.width=$('zoom').value+'%';$('zoom-value').textContent=$('zoom').value+'%';};
  $('search').oninput=render;$('filter').onchange=render;
  $('save').onclick=()=>{download(state.work(),'.review-work.json');dirty=false;message('Work file downloaded. Keep it to resume this review.');};
  $('load').onclick=()=>$('load-file').click();$('load-file').onchange=async()=>{try{const file=$('load-file').files[0];if(!file)return;
    if(dirty&&!confirm('Replace current unsaved edits with the selected work file?'))return;
    state.restore(JSON.parse(await file.text()));$('reviewer').value=state.reviewer;dirty=false;render();message('Saved work restored.');
  }catch(e){message(e.message,true);}finally{$('load-file').value='';}};
  $('export').onclick=()=>{try{download(state.decisions(),'.decisions.json');message('Decisions exported. Save work too if you have unfinished edits.');}catch(e){message(e.message,true);}};
  window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});render();
}
