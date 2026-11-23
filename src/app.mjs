import { buildBriefing, answerQuestion, findDuplicates, describeChanges } from './intelligence.mjs';

const main = document.querySelector('#main');
const dialog = document.querySelector('#dialog');
const content = document.querySelector('#dialog-content');
const notice = document.querySelector('#notice');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
const arrivalEase = 'cubic-bezier(.16, 1, .3, 1)';
function settle(element, {x=0,y=0,duration=220}={}){
 if(!element||reduceMotion.matches||!element.animate)return;
 element.getAnimations().filter(animation=>animation.id==='relay-settle').forEach(animation=>animation.cancel());
 const motion=element.animate([{opacity:.68,transform:`translate(${x}px,${y}px)`},{opacity:1,transform:'none'}],
  {duration,easing:arrivalEase});
 motion.id='relay-settle';
}
let state, briefing, busy = false, inboxFilter = 'pending', planFilter = '', weekOffset = 0;
let conversation = [], timer, returnFocus, dirty = false, discard = false;
let signInEmail = '';
let accountMode = false;
let familyMode = false;
let incomingInvite = /^#invite=([A-Za-z0-9_-]{32})$/.exec(location.hash)?.[1] || '';
if(incomingInvite)history.replaceState(history.state,'',location.pathname+location.search+'#briefing');
let pendingReconciliation;
let selectedDay='';
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
function notify(text){
 clearTimeout(timer);
 notice.textContent=text;
 notice.classList.add('show');
 if(/approved|updated|applied/i.test(text)){
  const mark=document.createElement('span');
  mark.className='receipt-mark';
  mark.setAttribute('aria-hidden','true');
  mark.innerHTML=icon('check');
  notice.prepend(mark);
 }
 timer=setTimeout(()=>notice.classList.remove('show'),3500);
}
async function api(path,payload) {
  const res=await fetch('/api/'+path,payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  if(!res.ok){
    const info=await res.json().catch(()=>({}));
    throw Object.assign(new Error(info.error || 'Relay could not save this. Please try again.'), {code:info.code});
  }
  return res.json();
}
function empty(title,copy){return '<div class="empty"><h3>'+title+'</h3><p>'+copy+'</p></div>';}
function openPanel(title,body){
  if(!dialog.open){returnFocus=document.activeElement;dialog.showModal();}
  dirty=false;discard=false;
  pendingReconciliation=undefined;
  content.innerHTML='<div class="dialog-top"><h2 id="dialog-title" tabindex="-1">'+esc(title)+'</h2>'+button('close',icon('x'),'iconbtn closebtn')+'</div>'+body;
  content.querySelector('.closebtn').setAttribute('aria-label','Close dialog');
  (content.querySelector('[autofocus]')||content.querySelector('h2')).focus();
  settle(content.querySelector('.dialog-top'),{y:5,duration:200});
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
  const person=p.person?personMark(p.person):'<span class="person-mark mark-open" aria-hidden="true">'+icon('user')+'</span>';
  return '<button class="plan-row" data-action="detail" data-id="'+esc(p.id)+'">'+person+'<span class="row-text"><strong>'+esc(p.title)+'</strong><span>'+esc(p.person||'Person unspecified')+'</span></span><span class="schedule-time">'+esc(timeLabel(p.time))+'</span>'+icon('right')+'</button>';
}
function personMark(name){
 const tone=(Array.from(name.toLowerCase()).reduce((value,char)=>(value*31+char.codePointAt(0))%997,0)+name.length)%4;
 const initials=name.trim().split(/\s+/u).slice(0,2).map(word=>Array.from(word)[0]).join('');
 return '<span aria-hidden="true" class="person-mark tone-'+tone+'">'+esc(initials)+'</span>';
}
function householdPeople(){
 const names=state.members.slice(0,5);
 if(!names.length)return state.access?.viewer.role==='member'
  ?button('household','Open household','people-empty')
  :button('household','Add people to your plans','people-empty','plus');
 return names.map(name=>button('person-plan',personMark(name)+'<span>'+esc(name)+'</span>','person-link','',name)).join('')+
 (state.members.length>5?button('household','See everyone','people-empty'):'');
}
function sourceRow(s){
  return '<button class="source-row" data-action="source" data-id="'+esc(s.id)+'"><span class="source-icon '+(s.target?'change':'')+'">'+icon(s.target?'log':'mail')+'</span><span class="row-text"><small>'+esc(s.status==='pending'?(s.target?'Proposed change':'New suggestion'):s.status)+'</small><strong>'+esc(s.title||'Untitled information')+'</strong></span>'+icon('right')+'</button>';
}
function titleBlock(title,desc,act=''){return '<div class="pagehead"><div><h1>'+title+'</h1><p>'+desc+'</p></div>'+act+'</div>';}
function weekBounds(){
  const first=now(); first.setDate(first.getDate()+weekOffset*7);
  const last=new Date(first);last.setDate(last.getDate()+6);
  return [dateKey(first),dateKey(last)];
}
function weekStrip(){const [a,b]=weekBounds();return '<div class="weekbar"><span>'+icon('calendar')+dateLabel(a,{month:'short',day:'numeric'})+' – '+dateLabel(b,{month:'short',day:'numeric'})+'</span><div><button class="iconbtn" aria-label="Previous seven days" data-action="previous">'+icon('back')+'</button><button class="iconbtn" aria-label="Next seven days" data-action="next">'+icon('right')+'</button></div></div>';}
function weekCalendar(rows,start){
 const today=dateKey(now());
 const days=Array.from({length:7},(_,offset)=>{
  const day=new Date(start+'T12:00:00');
  day.setDate(day.getDate()+offset);
  const date=dateKey(day), count=rows.filter(plan=>plan.date===date).length;
  const label=dateLabel(date,{weekday:'long',month:'long',day:'numeric'})+', '+count+' '+(count===1?'plan':'plans');
  return '<button type="button" data-action="calendar-day" data-id="'+date+'" aria-pressed="'+(selectedDay===date)+'" aria-label="'+esc(label)+'"'+(date===today?' aria-current="date"':'')+'><span>'+esc(dateLabel(date,{weekday:'short'}))+'</span><strong>'+day.getDate()+'</strong><span class="day-mark">'+(count||'&nbsp;')+'</span></button>';
 });
 return '<div class="week-calendar" aria-label="Filter the schedule by date">'+days.join('')+'</div>';
}
function taskRow(task){const plan=state.plans.find(p=>p.id===task.plan);return '<div class="task-row '+(task.status==='done'?'is-done':'')+'"><button class="task-check" data-action="toggle-task" data-id="'+esc(task.id)+'" aria-label="Mark '+esc(task.title)+' as '+(task.status==='done'?'open':'done')+'">'+(task.status==='done'?icon('check'):'')+'</button><div><strong>'+esc(task.title)+'</strong><small>'+(plan?esc(plan.title)+' · ':'')+esc(task.person||'Household')+'</small></div></div>';}
function tasksFor(planId=''){return (state.tasks||[]).filter(task=>!planId||task.plan===planId);}
function home(){
 const [start,end]=weekBounds(),review=briefing.review.length,rows=sortedPlans().filter(p=>p.date>=start&&p.date<=end),actions=briefing.openTasks.length;
 const today=dateKey(now());
 const todayCount=briefing.today.length;
 const urgent=todayCount?todayCount+' '+(todayCount===1?'plan':'plans')+' today.':'No plans scheduled today.';
 const items=review?briefing.review.slice(0,3).map(sourceRow).join(''):empty('Inbox clear','New information waits here for a decision.');
 const taskItems=actions?briefing.openTasks.slice(0,4).map(taskRow).join(''):empty('Nothing to follow through','Add a practical action from any plan detail.');
 const groups=[...new Set(rows.map(plan=>plan.date))].filter(date=>!selectedDay||date===selectedDay);
 const agenda=groups.map(date=>'<section class="agenda-day"><h3>'+esc(date===today?'Today':dateLabel(date))+'</h3>'+rows.filter(plan=>plan.date===date).map(planRow).join('')+'</section>').join('');
 const preparation=[...briefing.today,...briefing.upcoming].filter(plan=>plan.date>=start&&plan.date<=end&&(plan.preparation||plan.instructions)).slice(0,3);
 const prep=preparation.map(plan=>button('detail','<strong>'+esc(plan.title)+'</strong><span>'+esc(plan.preparation||plan.instructions)+'</span>','prep-note','',plan.id)).join('');
 return '<section class="home-arrival"><div class="home-greeting"><p class="arrival-date">'+esc(now().toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric'}))+'</p><h1>Family briefing</h1><p>'+esc(urgent)+'</p>'+button('intake','Add information','btn primary','plus')+'</div>'+
 '<section class="home-people"><h2>People in your plans</h2><div class="people-line">'+householdPeople()+'</div></section></section>'+
 '<div class="ledger-grid"><section class="ledger-column calendar-room"><div class="column-title"><h2>On the calendar</h2>'+toPage('plan','Full plan')+'</div>'+weekStrip()+weekCalendar(rows,start)+'<div class="sheet" aria-label="Scheduled plans">'+(agenda||empty('No scheduled plans',selectedDay?'Choose another date or select this day again to show the week.':'Approve a dated suggestion to see it in the schedule.'))+'</div></section>'+
 '<aside class="ledger-column right-rail"><div class="column-title"><h2>Needs review</h2>'+toPage('inbox','Inbox')+'</div><div class="review-sheet">'+items+'</div>'+
 (prep?'<section class="preparation-board"><h2>Get ready</h2>'+prep+'</section>':'')+
 '<div class="column-title follow-title"><h2>Follow-through</h2></div><div class="task-list">'+taskItems+'</div></aside></div>'+signals();
}
function signals(){
  const conflicts=briefing.conflicts.map(c=>'<div class="signal"><strong>Schedule overlap</strong><p>'+esc(c.person)+' has two plans at '+esc(timeLabel(c.time))+' on '+esc(dateLabel(c.date))+'.</p>'+c.plans.map(p=>button('detail',esc(p.title),'small','',p.id)).join('')+'</div>');
  const changes=briefing.changes.slice(0,3).map(c=>'<div class="signal"><strong>'+esc(c.plan.title)+'</strong><p>'+c.fields.map(({field})=>esc(detailLabels[field])).join(', ')+' changed</p>'+button('detail','See history','small','log',c.plan.id)+'</div>');
  return conflicts.length||changes.length?'<section class="signals"><h2>Changes &amp; overlaps</h2>'+[...conflicts,...changes].join('')+'</section>':'';
}
function sortedPlans(){return [...state.plans].sort((a,b)=>(a.date||'9999').localeCompare(b.date||'9999')||a.time.localeCompare(b.time)||a.title.localeCompare(b.title));}
function plans(){
  const rows=sortedPlans().filter(p=>!planFilter||p.person===planFilter);
  const groups=[...new Set(rows.map(plan=>plan.date))];
  const timeline=groups.map(date=>'<section class="agenda-day"><h2>'+esc(date?dateLabel(date,{weekday:'long',month:'long',day:'numeric',year:'numeric'}):'Date to be confirmed')+'</h2>'+rows.filter(plan=>plan.date===date).map(planRow).join('')+'</section>').join('');
  return titleBlock('Family plan','Approved plans, their sources, and what changed.',button('intake','Add information','btn primary','plus'))+
  '<div class="filters people-filter" role="group" aria-label="Filter by person">'+['',...state.members].map(p=>'<button data-action="plan-filter" data-id="'+esc(p)+'" aria-pressed="'+(planFilter===p)+'">'+(p?personMark(p):'')+esc(p||'Everyone')+'</button>').join('')+'</div><div class="sheet plan-timeline">'+(timeline||empty('No plans here yet',planFilter?'No approved plans list this person.':'Approve a suggestion in the inbox to add it to the family plan.'))+'</div>'+signals();
}
function inbox(){
  const rows=state.sources.filter(s=>s.status===inboxFilter);
  return titleBlock('Inbox','Compare each suggestion with its source before it joins the plan.',button('intake','Add information','btn primary','plus'))+
  '<div class="filters">'+['pending','approved','rejected'].map(s=>'<button data-action="inbox-filter" data-id="'+s+'" aria-pressed="'+(s===inboxFilter)+'">'+({pending:'Needs review',approved:'Approved',rejected:'Rejected'}[s])+' <b>'+state.sources.filter(x=>x.status===s).length+'</b></button>').join('')+'</div><div class="review-sheet">'+(rows.length?rows.map(sourceRow).join(''):empty('Nothing here yet','Information with this review status appears here.'))+'</div>';
}
function ask(){
 const prompts=['What is happening this week?','What should we prepare?','What changed?','Any conflicts?','What needs review?'];
 return titleBlock('Ask Relay','Look up reviewed plans, changes, and information still awaiting review.')+
 '<section class="ask-panel"><div class="askintro"><h2>Saved household records</h2><p>Relay uses rule-based lookups. Each answer points back to a plan or source.</p></div><div class="ask-work"><div class="prompts">'+prompts.map(p=>button('prompt',esc(p),'small','',p)).join('')+'</div><div id="answers" role="log">'+conversation.map(a=>'<article><span class="eyebrow">YOUR QUESTION</span><h3>'+esc(a.question)+'</h3><p>'+esc(a.text)+'</p><div class="citations">'+a.planIds.map(id=>state.plans.find(p=>p.id===id)).filter(Boolean).map(p=>button('detail',esc(p.title),'small','calendar',p.id)).join('')+a.sourceIds.map(id=>state.sources.find(s=>s.id===id)).filter(Boolean).map(s=>button('source','Source · '+esc(s.title),'small','mail',s.id)).join('')+'</div></article>').join('')+'</div><form id="ask-form" novalidate><label for="question">Ask about your family plan</label><div class="ask-input"><input id="question" name="question" maxlength="500" placeholder="What changed?" required><button class="btn primary">Ask '+icon('arrow')+'</button></div><p class="error" role="alert"></p></form></div></section>';
}
function render(movement){
 const key=page();document.title='Relay · '+pages[key];
 document.querySelectorAll('nav a').forEach(a=>{if(a.hash==='#'+key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
 briefing=buildBriefing(state,dateKey(now()));
 document.querySelector('#nav-count').textContent=briefing.review.length||'';
 main.innerHTML=({briefing:home,plan:plans,inbox,ask}[key])();
 if(movement==='route')settle(main.firstElementChild,{y:8,duration:260});
 if(movement==='day')settle(main.querySelector('.calendar-room .sheet'),{y:4});
 if(movement==='previous'||movement==='next'){
  const direction=movement==='next'?1:-1;
  for(const target of ['.week-calendar','.calendar-room .sheet'])settle(main.querySelector(target),{x:direction*12});
 }
 if(movement==='filter')settle(main.querySelector('.plan-timeline, .review-sheet'),{y:4});
}
const detailLabels = {title:'Plan title', date:'Date', time:'Time', person:'Affected person', preparation:'What to bring', instructions:'Instructions',location:'Location',responsibility:'Responsible person',deadline:'Deadline'};
const logisticalFields=['location','responsibility','deadline','preparation','instructions'];
function evidence(s){
 const statuses = {suggested:'Found in source', conflicting:'Conflicting values', invalid:'Check this value', needs_date:'Confirm the date first'};
 const lines = Object.entries(s.extraction||{}).map(([key,report]) =>
  '<li><strong>'+esc(detailLabels[key])+'</strong><span>'+esc(statuses[report.status])+'</span>'+
  report.evidence.map(item=>'<p>Line '+item.line+' · '+esc(item.value||'Empty')+'</p>').join('')+'</li>');
 const flagged=Object.values(s.extraction||{}).filter(item=>item.status!=='suggested').length;
 const label=flagged?' · '+flagged+' to check':'';
 return lines.length?'<details class="evidence" '+(matchMedia('(min-width:761px)').matches?'open':'')+'><summary>What Relay found'+label+'</summary><ul>'+lines.join('')+'</ul></details>':'';
}
function logistics(plan){
 const keys=logisticalFields.filter(key=>plan[key]);
 return keys.length?'<dl class="logistics">'+keys.map(key=>'<div><dt>'+detailLabels[key]+'</dt><dd>'+esc(key==='deadline'?dateLabel(plan[key]):plan[key])+'</dd></div>').join('')+'</dl>':'';
}
function compare(plan){
 return plan?'<strong>Currently confirmed</strong><p>'+esc([plan.title,dateLabel(plan.date),timeLabel(plan.time),plan.person].filter(Boolean).join(' · '))+'</p>'+logistics(plan):'';
}
function original(s){return '<div class="original"><div class="eyebrow">'+icon('mail')+' ORIGINAL WORDING</div><blockquote>'+esc(s?.text||'Source unavailable.')+'</blockquote></div>';}
function field(label,name,type,value='',required=false){return '<label>'+label+'<input type="'+type+'" name="'+name+'" value="'+esc(value)+'" '+(required?'required':'')+(type==='text'?' maxlength="160"':'')+'></label>';}
function options(values,value,blank){return '<option value="">'+blank+'</option>'+values.map(([id,label])=>'<option value="'+esc(id)+'"'+(id===value?' selected':'')+'>'+esc(label)+'</option>').join('');}
function intake(){
 openPanel('Add information','<p>Paste a message, email, or notice, then check the suggestion before approving it.</p><form id="intake" novalidate>'+field('Short title (optional)','title','text')+'<label>Original wording<textarea name="text" rows="6" maxlength="12000" required autofocus placeholder="Paste the message as you received it…"></textarea></label><p class="hint">Relay reads recognized lines such as When, Where, For, and Please bring. Enter unclear details during review.</p><p class="error" role="alert"></p><div class="actions"><button class="btn primary">Create suggestion '+icon('arrow')+'</button></div></form>');
}
function review(id){
 const s=state.sources.find(x=>x.id===id);if(!s)return;
 if(s.status!=='pending'){openPanel(s.title||'Reviewed source','<p class="badge">'+esc(s.status)+'</p>'+original(s));return;}
 const target=state.plans.find(p=>p.id===s.target);
 const dup=findDuplicates(state,s).filter(o=>o.id!==s.id);
 const missing=briefing.uncertainties.find(u=>u.sourceId===s.id)?.fields||[];
 openPanel('Review information','<div class="review-workspace"><div class="review-source">'+original(s)+evidence(s)+'</div><div class="review-decision">'+(dup.length?'<p class="warning">This wording already exists in the inbox. Check for a duplicate before approving.</p>':'')+
 '<form id="review" data-id="'+esc(id)+'" novalidate><div class="form-head"><h3>Suggested plan</h3><span class="badge">Awaiting approval</span></div>'+
 (Object.keys(s.extraction||{}).length?'':'<p class="hint">Relay couldn’t extract structured details. Use the original wording to fill in what you know.</p>')+
 (missing.length?'<p class="hint">Check these details against the source: '+esc(missing.join(', '))+'.</p>':'')+
 '<label>Apply this suggestion to<select name="target">'+options(state.plans.map(p=>[p.id,p.title]),s.target,'A new plan')+'</select></label>'+
 '<div class="comparison" aria-live="polite">'+compare(target)+'</div><div id="reconciliation"></div>'+
 field('Plan title','title','text',s.title,true)+'<div class="two">'+field('Date','date','date',s.date)+field('Time','time','time',s.time)+'</div><label>Affected person<select name="person">'+options(state.members.map(p=>[p,p]),s.person,'Unspecified')+'</select></label>'+
 '<details class="review-logistics" '+(s.location||s.responsibility||s.deadline?'open':'')+'><summary>Location, responsibility and deadline</summary>'+
 field('Location','location','text',s.location)+
 '<div class="two"><label>Responsible person<select name="responsibility">'+options(state.members.map(name=>[name,name]),s.responsibility,'Unassigned')+'</select></label>'+
 field('Deadline','deadline','date',s.deadline)+'</div></details>'+
 ['preparation','instructions'].map(key=>'<label>'+detailLabels[key]+'<textarea name="'+key+'" rows="2" maxlength="480">'+esc(s[key])+'</textarea></label>').join('')+
 '<p class="error" role="alert"></p><div class="actions">'+button('reject','Reject suggestion','btn secondary','',id)+'<button class="btn primary">'+icon('check')+'Approve plan</button></div></form></div></div>');
 const form=content.querySelector('#review');
 const inherited=new Map();
 const edited=new Set();
 form.addEventListener('input', event=>{
  if(event.target.name in detailLabels)edited.add(event.target.name);
 });
 const fillOmittedFields=plan=>{
  for(const key of ['date','time','person',...logisticalFields]){
   const control=form.elements[key];
   if(edited.has(key)||s[key]||s.extraction?.[key])continue;
   if(!control.value||control.value===inherited.get(key)){
    control.value=plan?.[key]||'';
    inherited.set(key,control.value);
   }
  }
 };
 fillOmittedFields(target);
 form.elements.target.addEventListener('change', event=>{
  if(pendingReconciliation){
   event.target.value=pendingReconciliation.target;
   return;
  }
  const plan=state.plans.find(item=>item.id===event.target.value);
  fillOmittedFields(plan);
  form.querySelector('.comparison').innerHTML=compare(plan);
 });
}
async function showReconciliation(form, base, draft) {
 const next=await api('state');
 const current=next.plans.find(plan=>plan.id===draft.target);
 const draftSource=next.sources.find(source=>source.id===draft.id);
 const box=form.querySelector('#reconciliation');
 form.querySelector('.comparison').hidden=true;
 state=next;
 render();
 pendingReconciliation={target:draft.target,current,fields:[]};
 if(!current||draftSource?.status!=='pending'){
  box.innerHTML='<p>This suggestion is no longer open for approval. Your draft is still below for reference.</p>';
 }else{
  const changes=base?describeChanges(base,current):[];
  pendingReconciliation.fields=changes.map(change=>change.field);
  const source=next.sources.find(item=>item.id===current.sourceId);
  const show=value=>esc(value||'Unspecified');
  box.innerHTML='<h3 tabindex="-1">The family plan changed</h3><p>Another review was approved while you worked. Your edits are still here. Choose which values to carry forward before approving.</p>'+
   (changes.length?changes.map(({field,before,after})=>'<div class="revision-field"><h4>'+esc(detailLabels[field])+'</h4><dl><div><dt>When you opened it</dt><dd>'+show(before)+'</dd></div><div><dt>Now confirmed</dt><dd>'+show(after)+'</dd></div><div><dt>Your draft</dt><dd>'+show(draft[field])+'</dd></div></dl><label>Choose '+esc(detailLabels[field].toLowerCase())+'<select data-reconcile="'+field+'"><option value="">Choose a value</option><option value="current">Use confirmed value</option><option value="draft">Keep my draft</option></select></label></div>').join(''):'<p>The approved source changed. The plan details match what you saw before.</p>')+
   (source?'<details><summary>Read the newly approved source</summary>'+original(source)+'</details>':'')+
   button('reconcile','Apply choices to draft','btn secondary');
 }
 box.tabIndex=-1;
 const heading=box.querySelector('h3')||box;
 heading.scrollIntoView({block:'center'});
 heading.focus({preventScroll:true});
 settle(box,{y:5});
}
function reconcileDraft(){
 const form=content.querySelector('#review');
 const recovery=pendingReconciliation;
 if(!form||!recovery?.current)return;
 const controls=[...form.querySelectorAll('[data-reconcile]')];
 const missing=controls.find(control=>!control.value);
 if(missing){showError(new Error('Choose a value for each changed field.'));missing.focus();return;}
 for(const control of controls){
  if(control.value==='current'){
   const field=control.dataset.reconcile;
   form.elements[field].value=recovery.current[field]||'';
  }
 }
 form.querySelector('.comparison').innerHTML=compare(recovery.current);
 form.querySelector('.comparison').hidden=false;
 form.querySelector('#reconciliation').replaceChildren();
 pendingReconciliation=undefined;
 form.querySelector('.error').textContent='';
 form.elements.title.focus();
 notify('Choices applied. Check and approve the draft.');
}
function detail(id){
 const p=state.plans.find(x=>x.id===id);if(!p)return;
 const source=state.sources.find(x=>x.id===p.sourceId);
 const planTasks=tasksFor(id), openTasks=planTasks.filter(task=>task.status==='open');
 openPanel(p.title,'<div class="detailmeta"><span>'+icon('calendar')+esc(dateLabel(p.date))+'</span><span>'+icon('clock')+esc(timeLabel(p.time))+'</span><span>'+icon('user')+esc(p.person||'Person unspecified')+'</span></div>'+logistics(p)+original(source)+'<section class="follow-panel"><div class="dialog-section"><h3>Follow-through</h3><span>'+openTasks.length+' open</span></div><div class="task-list">'+(planTasks.length?planTasks.map(taskRow).join(''):empty('No actions yet','Record the small practical action that makes this plan happen.'))+'</div><form id="task" data-plan="'+esc(id)+'" novalidate><label>Action<input name="title" maxlength="160" required placeholder="e.g. Pack shin guards"></label><label>Who will handle it?<select name="person">'+options(state.members.map(person=>[person,person]),p.person,'Household')+'</select></label><p class="error" role="alert"></p><div class="actions"><button class="btn secondary">Add action</button></div></form></section><h3>Plan history</h3><ol class="history">'+[p,...[...(p.history||[])].reverse()].map((v,i)=>'<li><span class="history-state">'+(i?'Earlier version':'Current version')+'</span><strong>'+esc(v.title)+'</strong><p>'+esc([dateLabel(v.date),timeLabel(v.time),v.person].filter(Boolean).join(' · '))+'</p>'+logistics(v)+(i?button('source','Read original wording','small','mail',v.sourceId):'')+'</li>').join('')+'</ol>');
}
function household(){
 if(!state)return;
 const members=state.members.map(name=>'<li>'+personMark(name)+esc(name)+'</li>').join('');
 const role=state.access?.viewer.role||'';
 openPanel('Household','<p>'+esc(accountMode?'Your household is shared with the people you invite.':'Your workspace is stored on this computer.')+'</p><h3>People in your plans</h3>'+
 (members?'<ul class="members">'+members+'</ul>':'<p class="hint">Add a name to identify who a message or plan concerns.</p>')+
 (role==='owner'||role==='admin'?'<form id="member" novalidate><label>Name<input name="name" maxlength="80" required></label><p class="error" role="alert"></p><div class="actions"><button class="btn secondary">Add family member</button></div></form>':'')+
 '<div class="data-actions">'+button('access','Household access','btn secondary')+
 (role==='owner'?'<a class="btn secondary" href="/api/export" download="relay-household.json">Export household data</a>'+button('reset-confirm','Delete household data','btn danger'):'')+
 (accountMode?button('account-signout','Sign out','btn secondary'):'')+'</div>');
}
const roleLabels={owner:'Owner',admin:'Administrator',member:'Adult member'};
function invitationDetails(code){
 const link=familyMode?location.origin+'/#invite='+encodeURIComponent(code):'';
 return '<div class="invite-code"><label>One-time invitation code<input readonly value="'+esc(code)+'"></label>'+
 (link?'<label>Invitation link<input id="invite-link" readonly value="'+esc(link)+'"></label>'+
 button('copy-invite','Copy invitation link','btn secondary'):'')+
 '<p>Share privately. The invitation works on one browser and expires in 24 hours.</p></div>';
}
function accessPanel(code=''){
 const access=state.access;
 if(!access)return;
 const {viewer,people,invites}=access;
 const manager=viewer.role==='owner'||viewer.role==='admin';
 const rows=people.map(person=>'<li><div><strong>'+esc(person.name)+'</strong><span>'+roleLabels[person.role]+(person.id===viewer.id?' · You':'')+'</span></div>'+
  (viewer.role==='owner'&&person.role!=='owner'?'<div class="access-actions">'+button('access-role',person.role==='admin'?'Make adult member':'Make administrator','small','',person.id)+button('access-remove','Remove access','small','',person.id)+'</div>':'')+'</li>').join('');
 openPanel('Household access','<p>Adults with access can read the household plan and review incoming information.</p><ul class="access-list">'+rows+'</ul>'+
 (code?invitationDetails(code):'')+
 (manager?'<h3>Invite an adult</h3><form id="invite" novalidate><label>Name<input name="name" maxlength="80" required></label><p class="error" role="alert"></p><div class="actions"><button class="btn primary">Create invitation</button></div></form>'+
  (invites.length?'<h3>Pending invitations</h3><ul class="access-list">'+invites.map(invite=>'<li><strong>'+esc(invite.name)+'</strong>'+button('revoke-invite','Revoke invitation','small','',invite.id)+'</li>').join('')+'</ul>':''):'')+
 (viewer.role==='owner'&&!familyMode?button('join','Join another household','btn secondary'):''));
}
function joinPanel(){
 openPanel('Join a household','<p>Enter the private code from a household owner or administrator. If this browser already has household records, use a fresh browser profile.</p><form id="join" novalidate><label>Invitation code<input name="code" maxlength="80" required autocomplete="off"></label><p class="error" role="alert"></p><div class="actions"><button class="btn primary">Join household</button></div></form>');
}
function removeAccess(id){
 const person=state.access.people.find(item=>item.id===id);
 if(!person)return;
 openPanel('Remove household access?', '<p>'+esc(person.name)+' will no longer be able to open or change this household’s records.</p><p class="error" role="alert"></p><div class="actions"><button class="btn secondary" data-action="access" autofocus>Keep access</button>'+button('confirm-remove','Remove access','btn danger','',id)+'</div>');
}
function askQuestion(q){
 if(!q.trim())return;
 const result=answerQuestion(state,q.trim(),dateKey(now()));
 conversation.push({...result,question:q.trim()});render();
 const last=document.querySelector('#answers article:last-child');if(last){last.tabIndex=-1;last.focus();}
}
function showError(err){const node=content.querySelector('.error')||main.querySelector('.error');if(node)node.textContent=err.message;else notify(err.message);}
async function save(path,data,after,onError){
 if(busy)return;busy=true;dialog.setAttribute('aria-busy','true');content.querySelectorAll('button,input,textarea,select').forEach(e=>e.disabled=true);
 try{state=await api(path,data);dirty=false;busy=false;dialog.close();render();after();}
 catch(err){
  try{
   if(err.code==='sign_in_required'||err.code==='family_sign_in_required'||err.code==='access_removed'&&familyMode){showSignIn();return;}
   if(onError&&await onError(err))return;
   showError(err);
  }
  catch{showError(new Error('The plan changed. Your draft is still here. Try again to load the latest version.'));}
 }
 finally{busy=false;dialog.removeAttribute('aria-busy');content.querySelectorAll('button,input,textarea,select').forEach(e=>e.disabled=false);}
}
function showSignIn(stage=familyMode?'family':'email'){
 state=undefined;
 conversation=[];
 document.title='Sign in · Relay';
 document.querySelector('#nav-count').textContent='';
 document.querySelectorAll('nav [aria-current]').forEach(link=>link.removeAttribute('aria-current'));
 if(dialog.open)dialog.close();
 const code=stage==='code';
 const family=stage==='family';
 main.innerHTML='<section class="account-entry"><h1>Sign in to Relay</h1><p>'+
  (family?(incomingInvite?'Your invitation is ready. Join to see your family’s plans.':'Enter your owner key or a private invitation from your household.'):code?'Enter the code sent to '+esc(signInEmail)+'.':'Use your email to open your household.')+
  '</p><form id="account-form" data-stage="'+stage+'"><label>'+
  (family?'Private code<input name="code" type="password" autocomplete="off" maxlength="80" required value="'+esc(incomingInvite)+'">'
       :code?'Email code<input name="code" inputmode="numeric" autocomplete="one-time-code" maxlength="8" required>'
       :'Email<input name="email" type="email" autocomplete="email" maxlength="254" required value="'+esc(signInEmail)+'">')+
  '</label><p class="error" role="alert"></p><div class="actions">'+
  (code?button('account-email','Change email','btn secondary'):'')+
  '<button class="btn primary">'+(family&&incomingInvite?'Join household':family||code?'Sign in':'Send code')+'</button></div></form></section>';
 main.querySelector('input').focus();
}
async function submitAccount(form,data){
 busy=true;
 const submit=form.querySelector('button[type="submit"],button:not([type])');
 submit.disabled=true;
 try{
  if(form.dataset.stage==='family'){
   await api('join',{code:data.code});
   incomingInvite='';
   await start();
  }else if(form.dataset.stage==='email'){
   signInEmail=data.email.trim();
   await api('auth',{action:'request',email:signInEmail});
   showSignIn('code');
  }else{
   await api('auth',{action:'verify',email:signInEmail,code:data.code});
   signInEmail='';
   await start();
  }
 }catch(error){form.querySelector('.error').textContent=error.message;}
 finally{busy=false;submit.disabled=false;}
}
document.addEventListener('submit',async e=>{
 const f=e.target;e.preventDefault();if(busy)return;
 const data=Object.fromEntries(new FormData(f));
 if(f.id==='account-form')return submitAccount(f,data);
 const required=[...f.querySelectorAll('[required]')].find(el=>!el.value.trim());
 if(required){const err=f.querySelector('.error');err.textContent='Enter '+({text:'the original wording',name:'a name',code:'an invitation code',question:'a question',title:f.id==='task'?'an action':'a plan title'}[required.name])+' to continue.';err.id=f.id+'-error';required.setAttribute('aria-invalid','true');required.setAttribute('aria-describedby',err.id);required.focus();return;}
 if(f.id==='member')return save('members',data,()=>{household();notify('Family member added.');});
 if(f.id==='invite')return save('access',{...data,action:'invite'},()=>{
  const code=state.inviteCode;
  delete state.inviteCode;
  accessPanel(code);
  content.querySelector('.invite-code input')?.focus();
 });
 if(f.id==='join')return save('join',data,()=>{
  conversation=[];weekOffset=0;selectedDay='';planFilter='';inboxFilter='pending';
  location.hash='briefing';render();main.focus();notify('You joined the household.');
 });
 if(f.id==='ask-form')return askQuestion(data.question);
 if(f.id==='intake'){
  await save('intake',data,()=>{inboxFilter='pending';location.hash='inbox';review(state.createdSourceId);notify('Suggestion ready to review.');});
 }
 if(f.id==='review'){
  if(pendingReconciliation){showError(new Error('Resolve the competing revision before approving.'));return;}
  const target=state.plans.find(p=>p.id===data.target);
  const draft={...data,id:f.dataset.id,decision:'approve',...(target?{expectedSourceId:target.sourceId}:{})};
  await save('review',draft,()=>{main.focus();notify('Approved and saved to the family plan.');},async err=>{
   if(err.code!=='plan_changed'&&err.code!=='suggestion_reviewed')return false;
   await showReconciliation(f,target,draft);
   return true;
  });
 }
 if(f.id==='task')await save('tasks',{action:'create',title:data.title,person:data.person,plan:f.dataset.plan},()=>{main.focus();notify('Follow-through action added.');});
});
document.addEventListener('click',async e=>{
 const el=e.target.closest('[data-action]');if(!el||busy)return;
 const id=el.dataset.id;
 switch(el.dataset.action){
 case 'retry':return start();
 case 'account-email':return showSignIn();
 case 'copy-invite':{
  const input=content.querySelector('#invite-link');
  if(!input)return;
  try{await navigator.clipboard.writeText(input.value);notify('Invitation link copied.');}
  catch{input.select();notify('Invitation link selected. Copy it to share.');}
  return;
 }
 case 'account-signout':
  if(familyMode&&state?.access?.viewer.role!=='owner'&&!confirm('Sign out on this device? You will need a new invitation to sign in again.'))return;
  try{await api('auth',{action:'signout'});showSignIn();}catch(error){notify(error.message);}
  return;
 case 'reconcile':return reconcileDraft();
 case 'intake':return intake();
 case 'household':return household();
 case 'access':return accessPanel();
 case 'join':return joinPanel();
 case 'access-remove':return removeAccess(id);
 case 'confirm-remove':return save('access',{id,action:'remove'},()=>{accessPanel();notify('Household access removed.');});
 case 'revoke-invite':return save('access',{id,action:'revoke'},()=>{accessPanel();notify('Invitation revoked.');});
 case 'access-role':{
  const person=state.access.people.find(item=>item.id===id);
  if(person)return save('access',{id,action:'role',role:person.role==='admin'?'member':'admin'},()=>{accessPanel();notify('Role updated.');});
  return;
 }
 case 'detail':return detail(id);
 case 'source':return review(id);
 case 'close':return closePanel();
 case 'discard':discard=true;return closePanel();
 case 'keep':content.querySelector('.discard')?.remove();content.querySelector('input,textarea,select')?.focus();return;
 case 'plan-filter':planFilter=id;render('filter');break;
 case 'person-plan':planFilter=id;location.hash='plan';return;
 case 'inbox-filter':inboxFilter=id;render('filter');break;
 case 'calendar-day':selectedDay=selectedDay===id?'':id;render('day');break;
 case 'next':weekOffset++;selectedDay='';render('next');break;
 case 'previous':weekOffset--;selectedDay='';render('previous');break;
 case 'prompt':return askQuestion(id);
 case 'toggle-task':return save('tasks',{action:'toggle',id},()=>{main.focus();notify('Follow-through updated.');});
 case 'reject':return save('review',{id,decision:'reject'},()=>{main.focus();notify('Suggestion rejected.');});
 case 'reset-confirm':return openPanel('Delete household data?','<p>This permanently removes your family names, plans, sources, actions, and history from Relay. Export a copy first if you need one.</p><p class="error" role="alert"></p><div class="actions"><button class="btn secondary" data-action="household" autofocus>Keep data</button>'+button('reset','Delete data','btn danger')+'</div>');
 case 'reset':return save('reset',{},()=>{conversation=[];weekOffset=0;selectedDay='';planFilter='';inboxFilter='pending';location.hash='briefing';render();main.focus();notify('Household data deleted.');});
 }
 if(!el.isConnected)Array.from(main.querySelectorAll('[data-action]')).find(x=>x.dataset.action===el.dataset.action&&x.dataset.id===el.dataset.id)?.focus({preventScroll:true});
});
window.addEventListener('hashchange',()=>{if(!state)return;render('route');if(!dialog.open){main.focus({preventScroll:true});window.scrollTo(0,0);}});
async function start(){
 try{state=await api('state');accountMode=Boolean(state.accountMode);familyMode=Boolean(state.familyMode);incomingInvite='';render();}
 catch(err){
  if(err.code==='sign_in_required'||err.code==='family_sign_in_required'){
   accountMode=true;
   familyMode=err.code==='family_sign_in_required';
   showSignIn();
  }else if(err.code==='access_removed'){
   if(familyMode)return showSignIn();
   state=undefined;
   main.innerHTML=empty('Household access removed','You can join again with a new invitation.')+button('join','Join a household','btn primary');
  }else main.innerHTML=empty('Briefing unavailable','Check the connection to the Relay server and try again.')+button('retry','Try again','btn primary');
 }
}
start();

