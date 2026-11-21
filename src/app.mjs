import { buildBriefing, answerQuestion, findDuplicates } from './intelligence.mjs';
import { drawNeighbourhood } from './neighbourhood.mjs';

const main = document.querySelector('#main');
const dialog = document.querySelector('#dialog');
const content = document.querySelector('#dialog-content');
const notice = document.querySelector('#notice');
let state, briefing, busy = false, inboxFilter = 'pending', planFilter = 'All', weekOffset = 0;
let conversation = [], timer, returnFocus, dirty = false, discard = false;
const pages = { briefing: 'Briefing', plan: 'Family plan', inbox: 'Inbox', ask: 'Ask Relay' };
const shapes = {
  sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M19 5l-1.5 1.5m-11 11L5 19"/>',
  stack:'<path d="m3 8 9-5 9 5-9 5zM3 12l9 5 9-5M3 16l9 5 9-5"/>',
  arrow:'<path d="M4 12h15m-6-6 6 6-6 6"/>', right:'<path d="m9 5 7 7-7 7"/>',
  plus:'<path d="M12 5v14M5 12h14"/>', calendar:'<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v4m10-4v4M3 10h18"/>',
  inbox:'<path d="M3 14 6 5h12l3 9v5H3zM3 14h5l2 3h4l2-3h5"/>',
  message:'<path d="M3 5h18v13H9l-5 4v-4H3Z"/>', mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
  user:'<circle cx="12" cy="8" r="3.2"/><path d="M5 21v-2a7 7 0 0 1 14 0v2"/>',
  check:'<path d="m4 12 5 5L20 6"/>', x:'<path d="m5 5 14 14m0-14L5 19"/>',
  spark:'<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
  edit:'<path d="M4 20l5-1 11-11-4-4L5 15zm9-13 4 4"/>',
  back:'<path d="m14 5-7 7 7 7"/>', log:'<path d="M3 12a9 9 0 1 0 2-6L2 9m0-5v5h5M12 7v5l4 2"/>'
};
function icon(name){return '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.7">'+shapes[name]+'</svg>';}
function esc(value=''){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function dateKey(d){return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');}
const now = ()=>new Date();
function dateLabel(date,opts={weekday:'short',month:'short',day:'numeric'}){return date?new Date(date+'T12:00:00').toLocaleDateString('en-US',opts):'Date open';}
function timeLabel(time){if(!time)return 'Time open';const [h,m]=time.split(':').map(Number);return (h%12||12)+':'+String(m).padStart(2,'0')+' '+(h>=12?'PM':'AM');}
function page(){return Object.hasOwn(pages,location.hash.slice(1))?location.hash.slice(1):'briefing';}
function button(action,label,cls='btn',ico='',id=''){return '<button type="button" class="'+cls+'" data-action="'+action+'" data-id="'+esc(id)+'">'+(ico?icon(ico):'')+label+'</button>';}
function toPage(key,label){return '<a class="textlink" href="#'+key+'">'+label+icon('arrow')+'</a>';}
function notify(text){clearTimeout(timer);notice.textContent=text;notice.classList.add('show');timer=setTimeout(()=>notice.classList.remove('show'),3500);}
async function api(path,payload) {
  const res=await fetch('/api/'+path,payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!res.ok){const info=await res.json().catch(()=>({}));throw new Error(info.error || 'Relay could not save this. Please try again.');}
  return res.json();
}
function empty(title,copy){return '<div class="empty"><h3>'+title+'</h3><p>'+copy+'</p></div>';}
function openPanel(title,body){
  if(!dialog.open){returnFocus=document.activeElement;dialog.showModal();}
  dirty=false;discard=false;
  content.innerHTML='<div class="dialog-top"><h2 id="dialog-title" tabindex="-1">'+esc(title)+'</h2>'+button('close',icon('x'),'iconbtn closebtn')+'</div>'+body;
  content.querySelector('.closebtn').setAttribute('aria-label','Close dialog');
  (content.querySelector('[autofocus]')||content.querySelector('h2')).focus();
}
function closePanel(){
  if(busy)return;
  if(dirty&&!discard){
    if(!content.querySelector('.discard'))content.insertAdjacentHTML('beforeend','<div class="discard" role="alert">Discard your unsaved edits? '+button('keep','Keep editing','small')+button('discard','Discard edits','small')+'</div>');
    content.querySelector('[data-action="keep"]').focus();return;
  }
  dialog.close();if(returnFocus?.isConnected)returnFocus.focus();else main.focus();
}
dialog.addEventListener('cancel',e=>{e.preventDefault();closePanel();});
dialog.addEventListener('input',()=>{dirty=true;});
function planRow(p){
  const owner=p.person?icon('user')+esc(p.person):'Person unspecified';
  return '<button class="plan-row" data-action="detail" data-id="'+esc(p.id)+'"><span class="date-tile"><small>'+esc(dateLabel(p.date,{month:'short'}))+'</small><strong>'+(p.date?esc(p.date.slice(-2)):'—')+'</strong></span><span class="row-text"><strong>'+esc(p.title)+'</strong><span>'+esc(dateLabel(p.date,{weekday:'long'}))+' <i>·</i> '+esc(timeLabel(p.time))+'</span></span><span class="owner">'+owner+'</span>'+icon('right')+'</button>';
}
function sourceRow(s){
  return '<button class="source-row" data-action="source" data-id="'+esc(s.id)+'"><span class="source-icon '+(s.target?'change':'')+'">'+icon(s.target?'log':'mail')+'</span><span class="row-text"><small>'+esc(s.status==='pending'?(s.target?'Proposed change':'New suggestion'):s.status)+'</small><strong>'+esc(s.title||'Untitled information')+'</strong></span>'+icon('right')+'</button>';
}
function titleBlock(kicker,title,desc,act=''){return '<div class="pagehead"><div><p class="page-meta">'+kicker+'</p><h1>'+title+'</h1><p>'+desc+'</p></div>'+act+'</div>';}
function weekBounds(){
  const first=now(); first.setDate(first.getDate()+weekOffset*7);
  const last=new Date(first);last.setDate(last.getDate()+6);
  return [dateKey(first),dateKey(last)];
}
function weekStrip(){const [a,b]=weekBounds();return '<div class="weekbar"><span>'+icon('calendar')+dateLabel(a,{month:'short',day:'numeric'})+' – '+dateLabel(b,{month:'short',day:'numeric'})+'</span><div><button class="iconbtn" aria-label="Previous seven days" data-action="previous">'+icon('back')+'</button><button class="iconbtn" aria-label="Next seven days" data-action="next">'+icon('right')+'</button></div></div>';}
function taskRow(task){const plan=state.plans.find(p=>p.id===task.plan);return '<div class="task-row '+(task.status==='done'?'is-done':'')+'"><button class="task-check" data-action="toggle-task" data-id="'+esc(task.id)+'" aria-label="Mark '+esc(task.title)+' as '+(task.status==='done'?'open':'done')+'">'+(task.status==='done'?icon('check'):'')+'</button><div><strong>'+esc(task.title)+'</strong><small>'+(plan?esc(plan.title)+' · ':'')+esc(task.person||'Household')+'</small></div></div>';}
function tasksFor(planId=''){return (state.tasks||[]).filter(task=>!planId||task.plan===planId);}
function home(){
 const [start,end]=weekBounds(),review=briefing.review.length,rows=sortedPlans().filter(p=>p.date>=start&&p.date<=end),today=briefing.today.length,actions=briefing.openTasks.length;
 const urgent=review?review+' source '+(review===1?'needs':'need')+' a decision.':actions?actions+' follow-through '+(actions===1?'action is':'actions are')+' open.':'No unresolved household signals.';
 const items=review?briefing.review.slice(0,3).map(sourceRow).join(''):empty('Inbox clear','New information waits here for a decision.');
 const taskItems=actions?briefing.openTasks.slice(0,4).map(taskRow).join(''):empty('Nothing to follow through','Add a practical action from any plan detail.');
 return '<section class="ledger-head"><div><p class="date-stamp">'+esc(now().toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'}))+'</p><h1>Keep the household moving.</h1><p>'+esc(urgent)+'</p></div>'+button('intake','Capture a notice','btn primary','plus')+'</section>'+
 '<section class="signal-strip"><div><span>Review queue</span><strong>'+review+'</strong></div><div><span>Today</span><strong>'+today+'</strong></div><div><span>Open actions</span><strong>'+actions+'</strong></div><a href="#ask">Ask Relay '+icon('arrow')+'</a></section>'+
 '<div class="ledger-grid"><section class="ledger-column"><div class="column-title"><h2>In motion</h2>'+toPage('plan','Full plan')+'</div>'+weekStrip()+'<div class="sheet">'+(rows.length?rows.map(planRow).join(''):empty('A clear week','Approved plans in the next seven days appear here.'))+'</div></section>'+
 '<section class="ledger-column right-rail"><div class="column-title"><h2>Requires a decision</h2>'+toPage('inbox','Inbox')+'</div><div class="review-sheet">'+items+'</div><div class="column-title follow-title"><h2>Follow-through</h2></div><div class="task-list">'+taskItems+'</div></section></div>'+signals();
}
function signals(){
  const conflicts=briefing.conflicts.map(c=>'<div class="signal"><strong>Schedule overlap</strong><p>'+esc(c.person)+' has two plans at '+esc(timeLabel(c.time))+' on '+esc(dateLabel(c.date))+'.</p>'+c.plans.map(p=>button('detail',esc(p.title),'small','',p.id)).join('')+'</div>');
  const changes=briefing.changes.slice(0,3).map(c=>'<div class="signal"><strong>Updated plan</strong><p>'+esc(c.plan.title)+'</p>'+button('detail','See history','small','log',c.plan.id)+'</div>');
  return conflicts.length||changes.length?'<section class="signals"><h2>Changes &amp; overlaps</h2>'+[...conflicts,...changes].join('')+'</section>':'';
}
function sortedPlans(){return [...state.plans].sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')||a.time.localeCompare(b.time)||a.title.localeCompare(b.title));}
function plans(){
  const rows=sortedPlans().filter(p=>planFilter==='All'||p.person===planFilter);
  return titleBlock('HOUSEHOLD SCHEDULE','Family plan','Approved plans, their sources, and what changed.',button('intake','Add information','btn primary','plus'))+
  '<div class="filters" aria-label="Filter by person">'+['All',...state.members].map(p=>'<button data-action="plan-filter" data-id="'+esc(p)+'" aria-pressed="'+(planFilter===p)+'">'+esc(p==='All'?'Everyone':p)+'</button>').join('')+'</div><div class="sheet">'+(rows.length?rows.map(planRow).join(''):empty('No plans here yet','Approve a suggestion in the inbox to add it to the family plan.'))+'</div>'+signals();
}
function inbox(){
  const rows=state.sources.filter(s=>s.status===inboxFilter);
  return titleBlock('FAMILY INFORMATION','Inbox','Compare each suggestion with its source before it joins the plan.',button('intake','Add information','btn primary','plus'))+
  '<div class="filters">'+['pending','approved','rejected'].map(s=>'<button data-action="inbox-filter" data-id="'+s+'" aria-pressed="'+(s===inboxFilter)+'">'+({pending:'Needs review',approved:'Approved',rejected:'Rejected'}[s])+' <b>'+state.sources.filter(x=>x.status===s).length+'</b></button>').join('')+'</div><div class="review-sheet">'+(rows.length?rows.map(sourceRow).join(''):empty('Nothing here yet','Information with this review status appears here.'))+'</div>';
}
function ask(){
 const prompts=['What is on today?','What changed?','Any conflicts?','What needs review?'];
 return titleBlock('HOUSEHOLD CONTEXT','Ask Relay','Look up reviewed plans, changes, and information still awaiting review.')+
 '<section class="ask-panel"><div class="askintro"><span class="ask-mark">'+icon('spark')+'</span><h2>What would you like to know?</h2><p>Relay uses rule-based lookups in this household’s records.</p></div><div class="prompts">'+prompts.map(p=>button('prompt',esc(p),'small','',p)).join('')+'</div><div id="answers" role="log">'+conversation.map(a=>'<article><span class="eyebrow">YOUR QUESTION</span><h3>'+esc(a.question)+'</h3><p>'+esc(a.text)+'</p><div class="citations">'+a.planIds.map(id=>state.plans.find(p=>p.id===id)).filter(Boolean).map(p=>button('detail',esc(p.title),'small','calendar',p.id)).join('')+a.sourceIds.map(id=>state.sources.find(s=>s.id===id)).filter(Boolean).map(s=>button('source','Source · '+esc(s.title),'small','mail',s.id)).join('')+'</div></article>').join('')+'</div><form id="ask-form" novalidate><label for="question">Ask about your family plan</label><div class="ask-input"><input id="question" name="question" maxlength="500" placeholder="What changed this week?" required><button class="btn primary">Ask '+icon('arrow')+'</button></div><p class="error" role="alert"></p></form></section>';
}
function render(){
 const key=page();document.title='Relay · '+pages[key];
 document.querySelectorAll('nav a').forEach(a=>{if(a.hash==='#'+key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 briefing=buildBriefing(state,dateKey(now()));
 document.querySelector('#nav-count').textContent=briefing.review.length||'';
 main.innerHTML=({briefing:home,plan:plans,inbox,ask}[key])();const landscape=document.querySelector('#landscape');if(landscape)drawNeighbourhood(landscape);
}
function original(s){return '<div class="original"><div class="eyebrow">'+icon('mail')+' ORIGINAL WORDING</div><blockquote>'+esc(s?.text||'Source unavailable.')+'</blockquote></div>';}
function field(label,name,type,value='',required=false){return '<label>'+label+'<input type="'+type+'" name="'+name+'" value="'+esc(value)+'" '+(required?'required':'')+(type==='text'?' maxlength="160"':'')+'></label>';}
function options(values,value,blank){return '<option value="">'+blank+'</option>'+values.map(([id,label])=>'<option value="'+esc(id)+'"'+(id===value?' selected':'')+'>'+esc(label)+'</option>').join('');}
function intake(){
 openPanel('Add information','<p>Paste a message, email, or notice. Use fictional information in this sample workspace.</p><form id="intake" novalidate>'+field('Short title (optional)','title','text')+'<label>Original wording<textarea name="text" rows="6" maxlength="12000" required autofocus placeholder="Paste the notice as you received it…"></textarea></label><p class="hint">Relay preserves this wording as a suggestion. Add the plan details when you review it.</p><p class="error" role="alert"></p><div class="actions"><button class="btn primary">Create suggestion '+icon('arrow')+'</button></div></form>');
}
function review(id){
 const s=state.sources.find(x=>x.id===id);if(!s)return;
 if(s.status!=='pending'){openPanel(s.title||'Reviewed source','<p class="badge">'+esc(s.status)+'</p>'+original(s));return;}
 const target=state.plans.find(p=>p.id===s.target);
 const dup=findDuplicates(state,s).filter(o=>o.id!==s.id);
 const missing=briefing.uncertainties.find(u=>u.sourceId===s.id)?.fields||[];
 const current=target?'<div class="comparison"><strong>Currently confirmed</strong><p>'+esc([target.title,dateLabel(target.date),timeLabel(target.time),target.person].filter(Boolean).join(' · '))+'</p></div>':'';
 openPanel('Review information',original(s)+current+(dup.length?'<p class="warning">Similar wording already exists in the inbox. Check for a duplicate before approving.</p>':'')+
 '<form id="review" data-id="'+esc(id)+'" novalidate><div class="form-head"><h3>Suggested plan</h3><span class="badge">Awaiting approval</span></div>'+(missing.length?'<p class="hint">Check these details against the source: '+esc(missing.join(', '))+'.</p>':'')+
 field('Plan title','title','text',s.title,true)+'<div class="two">'+field('Date','date','date',s.date)+field('Time','time','time',s.time)+'</div><label>Affected person<select name="person">'+options(state.members.map(p=>[p,p]),s.person,'Unspecified')+'</select></label><label>Apply this suggestion to<select name="target">'+options(state.plans.map(p=>[p.id,p.title]),s.target,'A new plan')+'</select></label><p class="error" role="alert"></p><div class="actions">'+button('reject','Reject suggestion','btn secondary','',id)+'<button class="btn primary">'+icon('check')+'Approve plan</button></div></form>');
}
function detail(id){
 const p=state.plans.find(x=>x.id===id);if(!p)return;
 const source=state.sources.find(x=>x.id===p.sourceId);
 const planTasks=tasksFor(id), openTasks=planTasks.filter(task=>task.status==='open');
 openPanel(p.title,'<div class="detailmeta"><span>'+icon('calendar')+esc(dateLabel(p.date))+'</span><span>'+icon('clock')+esc(timeLabel(p.time))+'</span><span>'+icon('user')+esc(p.person||'Person unspecified')+'</span></div>'+original(source)+'<section class="follow-panel"><div class="dialog-section"><h3>Follow-through</h3><span>'+openTasks.length+' open</span></div><div class="task-list">'+(planTasks.length?planTasks.map(taskRow).join(''):empty('No actions yet','Record the small practical action that makes this plan happen.'))+'</div><form id="task" data-plan="'+esc(id)+'" novalidate><label>Action<input name="title" maxlength="160" required placeholder="e.g. Pack shin guards"></label><label>Who will handle it?<select name="person">'+options(state.members.map(person=>[person,person]),p.person,'Household')+'</select></label><p class="error" role="alert"></p><div class="actions"><button class="btn secondary">Add action</button></div></form></section><h3>Plan history</h3><ol class="history">'+[p,...[...(p.history||[])].reverse()].map((v,i)=>'<li><span class="history-state">'+(i?'Earlier version':'Current version')+'</span><strong>'+esc(v.title)+'</strong><p>'+esc([dateLabel(v.date),timeLabel(v.time),v.person].filter(Boolean).join(' · '))+'</p>'+(i?button('source','Read original wording','small','mail',v.sourceId):'')+'</li>').join('')+'</ol>');
}
function household(){openPanel('Household','<p>This sample workspace uses fictional family information. Its records are stored on this computer’s Relay server.</p><h3>Family members</h3><div class="members">'+state.members.map(p=>'<span>'+icon('user')+esc(p)+'</span>').join('')+'</div><h3>Household data</h3><div class="data-actions"><a class="btn secondary" href="/api/export" download="relay-household.json">Export household data</a>'+button('reset-confirm','Delete household data','btn danger')+'</div>');}
function askQuestion(q){
 if(!q.trim())return;
 const result=answerQuestion(state,q.trim(),dateKey(now()));
 conversation.push({...result,question:q.trim()});render();
 const last=document.querySelector('#answers article:last-child');if(last){last.tabIndex=-1;last.focus();}
}
function showError(err){const node=content.querySelector('.error')||main.querySelector('.error');if(node)node.textContent=err.message;else notify(err.message);}
async function save(path,data,after){
 if(busy)return;busy=true;dialog.setAttribute('aria-busy','true');content.querySelectorAll('button,input,textarea,select').forEach(e=>e.disabled=true);
 try{state=await api(path,data);dirty=false;busy=false;dialog.close();render();after();}
 catch(err){showError(err);}
 finally{busy=false;dialog.removeAttribute('aria-busy');content.querySelectorAll('button,input,textarea,select').forEach(e=>e.disabled=false);}
}
document.addEventListener('submit',async e=>{
 const f=e.target;e.preventDefault();if(busy)return;
 const data=Object.fromEntries(new FormData(f));
 const required=[...f.querySelectorAll('[required]')].find(el=>!el.value.trim());
 if(required){const err=f.querySelector('.error');err.textContent='Enter '+(required.name==='text'?'the original wording':required.name==='title'?'a plan title':'a question')+' to continue.';err.id=f.id+'-error';required.setAttribute('aria-invalid','true');required.setAttribute('aria-describedby',err.id);required.focus();return;}
 if(f.id==='ask-form')return askQuestion(data.question);
 if(f.id==='intake'){
  const originalIds=new Set(state.sources.map(s=>s.id));
  await save('intake',data,()=>{inboxFilter='pending';const s=state.sources.find(x=>!originalIds.has(x.id));location.hash='inbox';if(s)review(s.id);notify('Suggestion ready to review.');});
 }
 if(f.id==='review'){
  const target=state.plans.find(p=>p.id===data.target);
  await save('review',{...data,id:f.dataset.id,decision:'approve',...(target?{expectedSourceId:target.sourceId}:{})},()=>{main.focus();notify('Approved and saved to the family plan.');});
 }
 if(f.id==='task')await save('tasks',{action:'create',title:data.title,person:data.person,plan:f.dataset.plan},()=>{main.focus();notify('Follow-through action added.');});
});
document.addEventListener('click',async e=>{
 const el=e.target.closest('[data-action]');if(!el||busy)return;
 const id=el.dataset.id;
 switch(el.dataset.action){
 case 'retry':return start();
 case 'intake':return intake();
 case 'household':return household();
 case 'detail':return detail(id);
 case 'source':return review(id);
 case 'close':return closePanel();
 case 'discard':discard=true;return closePanel();
 case 'keep':content.querySelector('.discard')?.remove();content.querySelector('input,textarea,select')?.focus();return;
 case 'plan-filter':planFilter=id;render();break;
 case 'inbox-filter':inboxFilter=id;render();break;
 case 'next':weekOffset++;render();break;
 case 'previous':weekOffset--;render();break;
 case 'prompt':return askQuestion(id);
 case 'toggle-task':return save('tasks',{action:'toggle',id},()=>{main.focus();notify('Follow-through updated.');});
 case 'reject':return save('review',{id,decision:'reject'},()=>{main.focus();notify('Suggestion rejected.');});
 case 'reset-confirm':return openPanel('Delete household data?','<p>This permanently removes this workspace’s plans, original sources, and change history. Export a copy first if you need one.</p><p class="error" role="alert"></p><div class="actions"><button class="btn secondary" data-action="household" autofocus>Keep data</button>'+button('reset','Delete data','btn danger')+'</div>');
 case 'reset':return save('reset',{},()=>{conversation=[];weekOffset=0;planFilter='All';inboxFilter='pending';location.hash='briefing';render();main.focus();notify('Household data deleted.');});
 }
 if(!el.isConnected)Array.from(main.querySelectorAll('[data-action]')).find(x=>x.dataset.action===el.dataset.action&&x.dataset.id===el.dataset.id)?.focus({preventScroll:true});
});
window.addEventListener('hashchange',()=>{if(!state)return;render();if(!dialog.open){main.focus({preventScroll:true});window.scrollTo(0,0);}});
async function start(){try{state=await api('state');render();}catch{main.innerHTML=empty('Briefing unavailable','Check the connection to the Relay server and try again.')+button('retry','Try again','btn primary');}}
start();

