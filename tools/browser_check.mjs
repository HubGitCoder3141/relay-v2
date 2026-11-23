import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { mkdir, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createInterface } from 'node:readline';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.RELAY_PLAYWRIGHT || 'playwright');
const folder = await mkdtemp(join(tmpdir(), 'relay-browser-'));
const output = 'output/playwright';
const server = spawn('python', ['server.py', '--port', '0', '--database', join(folder, 'test.sqlite3')], {
  stdio: ['ignore', 'pipe', 'inherit']
});
const exit = once(server, 'exit');
const lines = createInterface({input: server.stdout});
let browser;
try {
  const address = await Promise.race([
    once(lines, 'line').then(([line]) => line.match(/http:\/\/127\.0\.0\.1:\d+/)?.[0]),
    exit.then(() => { throw new Error('Relay exited before serving.'); })
  ]);
  assert.ok(address);
  await mkdir(output, {recursive:true});
  browser = await chromium.launch({channel:'msedge'});
  const page = await browser.newPage({viewport:{width:1440,height:1000}, acceptDownloads:true});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  const capture = async (name) => {
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, name);
    await page.screenshot({path:join(output, 'v3-'+name+'.png'), fullPage:true});
  };
  await page.goto(address);
  await page.getByRole('heading', {name:'Family briefing'}).waitFor();
  assert.equal(await page.getByText('No scheduled plans').count(), 1);
  await page.getByRole('button', {name:'Household and data settings'}).click();
  await page.getByLabel('Name', {exact:true}).fill('Morgan');
  await page.getByRole('button', {name:'Add family member'}).click();
  await page.getByRole('listitem').filter({hasText:'Morgan'}).waitFor();
  await capture('household');
  await page.keyboard.press('Escape');
  await page.getByRole('button', {name:'Add information'}).click();
  await page.getByRole('button', {name:'Create suggestion'}).click();
  assert.equal(await page.getByLabel('Original wording').getAttribute('aria-invalid'), 'true');
  await page.getByLabel('Short title (optional)').fill('Community garden');
  const today = await page.evaluate(() => {
    const day = new Date();
    return [day.getFullYear(), day.getMonth()+1, day.getDate()].map(value=>String(value).padStart(2,'0')).join('-');
  });
  await page.getByLabel('Original wording').fill(
    'Date: '+today+'\nDate: 2027-05-27\nFor: Morgan\nWhere: Community center\nResponsible: Morgan\nPlease bring gloves.\nInstructions: Meet at the east gate'
  );
  await capture('intake-desktop');
  await page.getByRole('button', {name:'Create suggestion'}).click();
  await page.getByText('Conflicting values').waitFor();
  assert.equal(await page.getByLabel('Date', {exact:true}).inputValue(), '');
  assert.equal(await page.getByLabel('Affected person').inputValue(), 'Morgan');
  assert.equal(await page.getByLabel('Location',{exact:true}).inputValue(), 'Community center');
  assert.equal(await page.getByLabel('Responsible person').inputValue(), 'Morgan');
  await page.getByLabel('Date', {exact:true}).fill(today);
  await page.getByLabel('What to bring').fill('Gloves and water');
  await capture('review-desktop');
  await page.setViewportSize({width:390,height:850});
  await page.locator('.evidence summary').click();
  await capture('review-mobile');
  await page.getByRole('button', {name:'Approve plan'}).click();
  await page.getByRole('status').filter({hasText:'Approved and saved'}).waitFor();
  const nav = page.getByRole('navigation');
  await nav.getByRole('link', {name:'Ask Relay'}).click();
  await page.getByRole('button', {name:'What should we prepare?'}).click();
  await page.getByText('Community garden · Gloves and water · Meet at the east gate').waitFor();
  const question=page.getByRole('textbox',{name:'Ask about your family plan'});
  await question.fill('Where is the community garden?');
  await question.press('Enter');
  await page.getByText(/Location · Community center/).waitFor();
  await question.fill('Who’s responsible for it?');
  await question.press('Enter');
  await page.getByText(/Responsible person · Morgan/).waitFor();
  await capture('ask-mobile');
  await nav.getByRole('link', {name:'Family plan'}).click();
  await page.getByRole('button', {name:/Community garden/}).click();
  await capture('plan-detail-mobile');
  await page.getByLabel('Action', {exact:true}).fill('Pack gloves');
  await page.getByRole('button', {name:'Add action'}).click();
  await page.getByRole('status').filter({hasText:'Action added'}).waitFor();
  await page.reload();
  await page.getByRole('button', {name:/Community garden/}).click();
  await page.getByRole('button', {name:'Mark Pack gloves as done'}).click();
  await page.getByRole('status').filter({hasText:'Action completed'}).waitFor();
  await page.keyboard.press('Escape');
  await page.getByRole('status').filter({hasText:'Action completed'}).waitFor({state:'hidden'});
  await page.setViewportSize({width:1440,height:1000});
  await page.getByRole('button', {name:'Household and data settings'}).click();
  await page.getByRole('button', {name:'Household access',exact:true}).click();
  await page.getByLabel('Name', {exact:true}).fill('Jordan');
  await page.getByRole('button', {name:'Create invitation'}).click();
  const codeInput=page.getByLabel('One-time invitation code');
  await codeInput.waitFor();
  const code=await codeInput.inputValue();
  await page.keyboard.press('Escape');
  const guestContext=await browser.newContext();
  const guest=await guestContext.newPage();
  guest.on('pageerror', error=>errors.push(error.message));
  await guest.goto(address);
  await guest.getByRole('heading',{name:'Family briefing'}).waitFor();
  await guest.getByRole('button',{name:'Household and data settings'}).click();
  await guest.getByRole('button',{name:'Household access',exact:true}).click();
  await guest.getByRole('button',{name:'Join another household'}).click();
  await guest.getByLabel('Invitation code').fill(code);
  await guest.getByRole('button',{name:'Join household',exact:true}).click();
  await guest.locator('.calendar-room').getByRole('button',{name:/Community garden/}).waitFor();
  const post=async (context,route,data)=>{
    const response=await context.request.post(address+'/api/'+route,{data});
    assert.equal(response.status(),200);
    return response.json();
  };
  const original=(await (await page.request.get(address+'/api/state')).json()).plans[0];
  const draft=(await post(page,'intake',{title:'Garden reminder',text:'Bring: Gloves'})).sources[0];
  const competing=(await post(guest,'intake',{title:original.title,text:'Date: '+today+'\nFor: Morgan\nWhere: Community center\nResponsible: Morgan\nBring: Boots\nInstructions: Meet at the east gate'})).sources[0];
  await page.reload();
  await nav.getByRole('link',{name:/Inbox/}).click();
  await page.getByRole('button',{name:/Garden reminder/}).click();
  await page.getByLabel('Apply this suggestion to').selectOption(original.id);
  await page.getByLabel('What to bring').fill('Gloves and a hat');
  await post(guest,'review',{id:competing.id,target:original.id,decision:'approve',expectedSourceId:original.sourceId});
  await page.getByRole('button',{name:'Approve plan'}).click();
  await page.getByRole('heading',{name:'The family plan changed'}).waitFor();
  assert.equal(await page.locator('#review textarea[name="preparation"]').inputValue(),'Gloves and a hat');
  await capture('competing-review-desktop');
  await page.setViewportSize({width:390,height:850});
  await page.getByRole('heading',{name:'The family plan changed'}).evaluate(element=>element.scrollIntoView({block:'center'}));
  await capture('competing-review-mobile');
  await page.setViewportSize({width:1440,height:1000});
  for(const choice of await page.locator('[data-reconcile]').all()) await choice.selectOption('current');
  await page.getByLabel('Choose what to bring').selectOption('draft');
  await page.getByRole('button',{name:'Apply choices to draft'}).click();
  await page.getByRole('button',{name:'Approve plan'}).click();
  await page.getByRole('status').filter({hasText:'Approved and saved'}).waitFor();
  const resolved=(await (await page.request.get(address+'/api/state')).json()).plans[0];
  assert.equal(resolved.preparation,'Gloves and a hat');
  assert.equal(resolved.date,today);
  assert.equal(resolved.person,'Morgan');
  assert.equal(resolved.location,'Community center');
  assert.equal(resolved.responsibility,'Morgan');
  assert.equal(resolved.instructions,'Meet at the east gate');
  assert.equal(resolved.history.at(-1).sourceId,competing.id);
  assert.equal(resolved.history.at(-1).preparation,'Boots');
  await page.getByRole('status').filter({hasText:'Approved and saved'}).waitFor({state:'hidden'});
  await page.getByRole('button',{name:'Household and data settings'}).click();
  await page.getByRole('button',{name:'Household access',exact:true}).click();
  await capture('access-desktop');
  await page.getByRole('button',{name:'Remove access',exact:true}).click();
  await page.getByRole('button',{name:'Remove access',exact:true}).click();
  await page.getByRole('status').filter({hasText:'Household access removed'}).waitFor();
  await page.keyboard.press('Escape');
  await guest.reload();
  await guest.getByRole('heading',{name:'Household access removed'}).waitFor();
  await guestContext.close();
  await page.getByRole('status').filter({hasText:'Household access removed'}).waitFor({state:'hidden'});
  await post(page,'members',{name:'Casey'});
  const tomorrow=await page.evaluate(()=>{
    const next=new Date();
    next.setDate(next.getDate()+1);
    return [next.getFullYear(),next.getMonth()+1,next.getDate()].map(value=>String(value).padStart(2,'0')).join('-');
  });
  const visit=(await post(page,'intake',{title:'Library visit',text:'Date: '+tomorrow+'\nTime: 10:30\nFor: Casey\nBring: Library books'})).sources[0];
  await post(page,'review',{id:visit.id,decision:'approve'});
  await post(page,'intake',{title:'Swim lesson update',text:'Please confirm the start time for next week.'});
  await post(page,'tasks',{action:'create',title:'Pack library tote',person:'Casey',due:tomorrow});
  await page.reload();
  await nav.getByRole('link',{name:'Actions',exact:true}).click();
  await page.getByRole('button',{name:'Add action',exact:true}).click();
  const taskEditor=page.getByRole('dialog');
  await taskEditor.getByRole('button',{name:'Add action',exact:true}).click();
  assert.equal(await taskEditor.getByLabel('Action',{exact:true}).getAttribute('aria-invalid'),'true');
  await taskEditor.getByLabel('Action',{exact:true}).fill('Return library books');
  await taskEditor.getByLabel('Due date').fill(today);
  await taskEditor.getByLabel('Who will handle it?').selectOption('Casey');
  await taskEditor.getByRole('button',{name:'Add action',exact:true}).click();
  await page.locator('[data-action-group="today"]').getByRole('button',{name:'Return library books',exact:true}).waitFor();
  await nav.getByRole('link',{name:'Ask Relay',exact:true}).click();
  await page.getByRole('button',{name:'What’s due today?',exact:true}).click();
  await page.getByRole('button',{name:'Action · Return library books',exact:true}).waitFor();
  await nav.getByRole('link',{name:'Actions',exact:true}).click();
  await page.locator('[data-action-group="today"]').getByRole('button',{name:'Return library books',exact:true}).click();
  await taskEditor.getByLabel('Due date').fill(tomorrow);
  await taskEditor.getByRole('button',{name:'Save changes',exact:true}).click();
  await page.reload();
  const upcomingAction=page.locator('[data-action-group="upcoming"]').getByRole('button',{name:'Mark Return library books as done',exact:true});
  await upcomingAction.focus();
  await page.keyboard.press('Space');
  const reopen=page.getByRole('button',{name:'Mark Return library books as open',exact:true});
  await reopen.waitFor();
  assert.equal(await reopen.evaluate(element=>element===document.activeElement),true);
  await page.getByRole('button',{name:'Return library books',exact:true}).click();
  await taskEditor.getByRole('button',{name:'Delete action',exact:true}).click();
  await taskEditor.getByRole('button',{name:'Delete action',exact:true}).click();
  await page.getByRole('button',{name:'Return library books',exact:true}).waitFor({state:'hidden'});
  await nav.getByRole('link',{name:'Briefing',exact:true}).click();
  await page.getByRole('button',{name:'Casey',exact:true}).click();
  await page.getByRole('heading',{name:'Family plan'}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Casey',exact:true}).getAttribute('aria-pressed'),'true');
  assert.equal(await page.getByRole('button',{name:/Library visit/}).count(),1);
  assert.equal(await page.getByRole('button',{name:/Garden reminder/}).count(),0);
  await page.getByRole('button',{name:'Everyone',exact:true}).click();
  for (const viewport of [{width:390,height:850},{width:820,height:1000},{width:1440,height:1000}]) {
    await page.setViewportSize(viewport);
    for (const name of ['Briefing','Family plan','Actions','Inbox','Ask Relay']) {
      await nav.getByRole('link', {name:name==='Inbox'?/^Inbox(?: \d+)?$/:name,exact:name!=='Inbox'}).click();
      if (name === 'Inbox') await page.getByRole('button', {name:/^Approved/}).click();
      if (name === 'Ask Relay' && viewport.width === 390) {
        await page.getByRole('button', {name:'What should we prepare?'}).click();
      }
      await capture(name.toLowerCase().replaceAll(' ','-')+'-'+viewport.width);
    }
  }
  await page.setViewportSize({width:320,height:720});
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  const accessibilityTree=await nav.ariaSnapshot();
  for(const label of ['Briefing','Family plan','Actions','Inbox','Ask Relay']) assert.ok(accessibilityTree.includes(label));
  await nav.getByRole('link',{name:'Briefing',exact:true}).focus();
  await page.keyboard.press('Enter');
  const day=page.locator('[data-action="calendar-day"]').first();
  await day.focus();
  await page.keyboard.press('Space');
  assert.equal(await day.getAttribute('aria-pressed'),'true');
  assert.equal(await day.evaluate(element=>element===document.activeElement),true);
  const activeMotion=()=>page.evaluate(()=>document.getAnimations().some(animation=>animation.id==='relay-settle'));
  assert.equal(await activeMotion(),true);
  await page.emulateMedia({reducedMotion:'reduce'});
  await day.press('Space');
  assert.equal(await day.getAttribute('aria-pressed'),'false');
  assert.equal(await activeMotion(),false);
  await page.getByRole('button',{name:'Add information',exact:true}).click();
  await page.getByLabel('Original wording').fill('Book club is on tomorrow at 4 pm at the library. Please bring a book.');
  await page.getByText('Does the message say “tomorrow” or give a date without a year?',{exact:true}).click();
  await page.getByLabel('Date the message was sent').fill(today);
  await page.getByRole('button',{name:'Create suggestion'}).click();
  const inferredDate=page.getByRole('dialog').getByLabel('Date',{exact:true});
  await inferredDate.waitFor();
  assert.equal(await inferredDate.inputValue(),tomorrow);
  assert.equal(await page.getByRole('dialog').getByLabel('Location',{exact:true}).inputValue(),'the library');
  await capture('plain-notice-review');
  await page.keyboard.press('Escape');
  await nav.getByRole('link',{name:'Briefing',exact:true}).click();
  await page.getByRole('button',{name:'Add information',exact:true}).click();
  await page.getByLabel('Original wording').fill('Hey, soccer practice is Tuesday at 5 PM. Bring cleats and water. Meet Coach Alex at the community field by 4:45.');
  await page.getByText('Does the message say “tomorrow” or give a date without a year?',{exact:true}).click();
  await page.getByLabel('Date the message was sent').fill('2026-11-23');
  await page.getByRole('button',{name:'Create suggestion'}).click();
  const learnedReview=page.getByRole('dialog');
  await learnedReview.getByText('Suggested plan type · Sports',{exact:true}).waitFor();
  assert.equal(await learnedReview.getByLabel('Date',{exact:true}).inputValue(),'2026-11-24');
  assert.equal(await learnedReview.getByLabel('Time',{exact:true}).inputValue(),'17:00');
  assert.equal(await learnedReview.getByLabel('Location',{exact:true}).inputValue(),'the community field');
  assert.equal(await learnedReview.locator('select[name="responsibility"]').inputValue(),'');
  await capture('learned-notice-review');
  await page.keyboard.press('Escape');
  for(let index=0;index<120;index++){
    await post(page,'intake',{title:'Synthetic notice '+index,text:'Date: '+today+'\nInstructions: '+('Bring equipment. '.repeat(36))});
  }
  const readings=[];
  let bytes=0;
  for(let trial=0;trial<25;trial++){
    const started=performance.now();
    const response=await page.request.get(address+'/api/state');
    assert.equal(response.status(),200);
    bytes=(await response.body()).length;
    readings.push(performance.now()-started);
  }
  readings.sort((a,b)=>a-b);
  console.log('Local snapshot with 125 sources:',bytes,'bytes, p50',readings[12].toFixed(1),'ms, p95',readings[23].toFixed(1),'ms.');
  assert.deepEqual(errors, []);
  console.log('Edge verified roster, validation, source evidence, approval, preparation lookup, restart of browser view, follow-through, navigation and layout.');
} finally {
  try {
    await browser?.close();
  } finally {
    server.kill();
    await exit;
    await rm(folder, {recursive:true,force:true});
  }
}
