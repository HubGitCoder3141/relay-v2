/** A small two-colour print of a neighbourhood at sunrise. */
export function drawNeighbourhood(canvas) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const w = 580, h = 304;
  canvas.width = w * 2;
  canvas.height = h * 2;
  ctx.scale(2, 2);
  let seed = 71;
  function random() {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  }
  function path(d, fill, stroke, width = 1) {
    const shape = new Path2D(d);
    if (fill) { ctx.fillStyle = fill; ctx.fill(shape); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke(shape); }
  }
  function circle(x, y, radius, fill) {
    ctx.fillStyle = fill; ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  }
  const dark = '#193f35', olive = '#9daa79', light = '#ebdba4', roof = '#d77952';
  circle(417, 79, 37, '#f3c075');
  for (let i = 0; i < 16; i++) {
    const a = i * Math.PI / 8;
    const x = Math.cos(a), y = Math.sin(a);
    path('M'+(417+x*44)+' '+(79+y*44)+'l'+(x*6)+' '+(y*6), null, '#dda05f', 1);
  }
  path('M-10 273Q70 253 141 208T267 154Q320 140 381 165Q417 175 474 139Q530 109 610 137V320H-10Z','#50735a');
  path('M-10 280Q90 272 179 236Q290 185 370 210Q451 227 590 151V320H-10Z','#89a17c');
  path('M35 304Q140 240 252 249T447 215Q532 174 610 203V320Z','#b3ba8d');
  function tree(x,y,size,color) {
    ctx.save();ctx.translate(x,y);ctx.scale(size,size);
    path('M-3 0L-2 -20L2 -20L3 0Z','#534d33');
    path('M0 -68L-12 -43L-7 -44L-19 -24L-11 -25L-23 -10Q0 0 22 -10L11 -26L17 -25L6 -44L12 -43Z',color);
    path('M0 -56L1 -10M0 -25L-8 -32M1 -18L11 -25',null,'#b6ba8c',.65);
    ctx.restore();
  }
  for (let i=0;i<28;i++) {
    const x=110+i*18;
    tree(x,202-29*Math.sin((x-155)/58),.24+random()*.26,'#375a48');
  }
  function house(x,y,s,body,tiles,side) {
    ctx.save();ctx.translate(x,y);ctx.scale(s,s);
    path('M0 0L0 -47L26 -72L52 -46V0Z',body);
    path('M52 -46L87 -53V-9L52 0Z',side);
    path('M-5 -45L25 -79L56 -48L51 -44L25 -70L2 -42Z',tiles);
    path('M25 -79L61 -84L93 -55L56 -48Z',tiles);
    path('M64 -78V-93L72 -94V-70Z',tiles);
    path('M17 0V-28L29 -28V0Z',dark);
    for(const wx of [5,35]) {
      path('M'+wx+' -36h10v12h-10Z',dark);
      path('M'+(wx+5)+' -36v12m-5 -6h10',null,light,1.4);
    }
    path('M62 -38l10 -2v12l-10 2Z',dark);
    path('M67 -39v12',null,light,1);
    for(let i=0;i<6;i++)path('M'+(34+i*4)+' '+(-76+i*4)+'l31 -5',null,'#a75f40',.7);
    ctx.restore();
  }
  house(158,231,.53,'#d9cba1','#b66d4f','#b8ab85');
  tree(205,242,.82,'#395e49');
  house(237,223,.96,'#f0deb5',roof,'#c5ae83');
  house(335,226,.68,'#e3d6ac','#6c7463','#bdac86');
  tree(410,222,1.13,'#314f3d');
  tree(437,222,.72,'#456546');
  path('M256 221C269 236 327 233 314 248S240 268 216 304H277C291 280 356 268 350 248S280 231 266 221Z','#e5cda0');
  path('M56 304Q105 266 176 262Q215 260 230 273Q172 287 151 305Z','#577a60');
  path('M335 304Q391 255 480 245T596 216V305Z','#638062');
  tree(478,263,1.72,'#244e3c');
  tree(514,267,1.13,'#365e44');
  tree(138,283,1.12,'#365942');
  for(let i=0;i<110;i++) {
    const x=80+random()*500,y=244+random()*62;
    if(x>212 && x<365)continue;
    path('M'+x+' '+y+'l-2 -4m2 4l2 -3',null,olive,.8);
  }
  for (let i = 0; i < 1200; i++) {
    const x = 130+random()*450, y = random()*304;
    ctx.fillStyle = random()>.5?'rgba(245,236,194,.12)':'rgba(20,44,28,.13)';
    ctx.fillRect(x,y,random()*1.8,.8);
  }
  for(const [x,y] of [[297,69],[312,58],[353,92]])path('M'+x+' '+y+'q4 0 6 3q2 -5 7 -6',null,'#acb995',1.4);
}
