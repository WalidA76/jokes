
const TM=window.TIMING, S=TM.s, K=TM.K, $=id=>document.getElementById(id);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const pr=(t,a,b)=>clamp((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3), eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eb=x=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
const lerp=(a,b,p)=>a+(b-a)*p;
function tf(n,o){ // o: opacity, x, y, s, r, b(blur)
  n.style.opacity=o.o===undefined?1:o.o;
  n.style.transform=`translate(${o.x||0}px,${o.y||0}px) scale(${o.s===undefined?1:o.s}) rotate(${o.r||0}deg)`;
  n.style.filter=o.b?`blur(${o.b}px)`:'none';
}
function rev(n,lt,a,dur=.7,dy=40){const p=eo(pr(lt,a,a+dur)); tf(n,{o:p,y:(1-p)*dy,b:(1-p)*8});}
function typeText(str,lt,a,b){return str.slice(0,Math.floor(str.length*pr(lt,a,b)+1e-6));}

/* ---------- lens ---------- */
function makeLens(host,uid){
  const size=host.clientWidth||parseInt(host.style.width);
  let ticks='';
  for(let i=0;i<120;i++){const a=i*3*Math.PI/180,r1=i%10==0?246:254,r2=262;
    ticks+=`<line x1="${Math.sin(a)*r1}" y1="${-Math.cos(a)*r1}" x2="${Math.sin(a)*r2}" y2="${-Math.cos(a)*r2}" stroke="${i%10==0?'#f0bd4a':'rgba(160,168,185,.45)'}" stroke-width="${i%10==0?4:1.6}"/>`;}
  host.innerHTML=`<svg viewBox="-300 -300 600 600" width="100%" height="100%">
  <defs><radialGradient id="${uid}c" cx=".4" cy=".35" r=".85"><stop offset="0" stop-color="#3c66d0"/><stop offset="1" stop-color="#0f1b4c"/></radialGradient>
  <linearGradient id="${uid}r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#aab1c0"/><stop offset=".45" stop-color="#262b37"/><stop offset="1" stop-color="#9aa1b1"/></linearGradient>
  <radialGradient id="${uid}d"><stop offset="0" stop-color="#171b27"/><stop offset="1" stop-color="#0a0d14"/></radialGradient></defs>
  <circle r="292" fill="#05070b"/><circle r="283" fill="none" stroke="url(#${uid}r)" stroke-width="17"/>
  <circle r="269" fill="none" stroke="rgba(255,255,255,.22)" stroke-width="2"/>
  <g id="${uid}t">${ticks}</g><circle r="240" fill="url(#${uid}d)"/>
  <g id="${uid}b" stroke="rgba(190,196,212,.6)" stroke-width="2.4" fill="none"></g>
  <polygon id="${uid}p" fill="url(#${uid}c)" stroke="#f0bd4a" stroke-width="3.5"/></svg>`;
  const g=$(uid+'b'),poly=$(uid+'p'),tk=$(uid+'t'),N=9,R=238,lines=[];
  for(let i=0;i<N;i++){const l=document.createElementNS('http://www.w3.org/2000/svg','line');g.appendChild(l);lines.push(l);}
  return {set(r,rot,tr){
    const v=[];for(let i=0;i<N;i++){const a=(i*2*Math.PI/N)+rot*Math.PI/180;v.push([Math.sin(a)*r,-Math.cos(a)*r]);}
    poly.setAttribute('points',v.map(p=>p.join(',')).join(' '));
    for(let i=0;i<N;i++){const p=v[i],q=v[(i+1)%N];let dx=p[0]-q[0],dy=p[1]-q[1];const L=Math.hypot(dx,dy)||1;dx/=L;dy/=L;
      const b=p[0]*dx+p[1]*dy,c=p[0]*p[0]+p[1]*p[1]-R*R,s=-b+Math.sqrt(Math.max(0,b*b-c));
      const l=lines[i];l.setAttribute('x1',p[0]);l.setAttribute('y1',p[1]);l.setAttribute('x2',p[0]+dx*s);l.setAttribute('y2',p[1]+dy*s);}
    tk.setAttribute('transform',`rotate(${tr||0})`);}};
}
const L1=makeLens($('lens1'),'l1'),L4=makeLens($('lens4'),'l4'),L6=makeLens($('lens6'),'l6');
$('oai').setAttribute('d',"M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0804 4.7783-2.7582a.7948.7948 0 0 0 .3927-.6813v-6.7369l2.02 1.1686a.071.071 0 0 1 .038.052v5.5826a4.504 4.504 0 0 1-4.4945 4.4944zm-9.6607-4.1254a4.4708 4.4708 0 0 1-.5346-3.0137l.142.0852 4.783 2.7582a.7712.7712 0 0 0 .7806 0l5.8428-3.3685v2.3324a.0804.0804 0 0 1-.0332.0615L9.74 19.9502a4.4992 4.4992 0 0 1-6.1408-1.6464zM2.3408 7.8956a4.485 4.485 0 0 1 2.3655-1.9728V11.6a.7664.7664 0 0 0 .3879.6765l5.8144 3.3543-2.0201 1.1685a.0757.0757 0 0 1-.071 0l-4.8303-2.7865A4.504 4.504 0 0 1 2.3408 7.872zm16.5963 3.8558L13.1038 8.364 15.1192 7.2a.0757.0757 0 0 1 .071 0l4.8303 2.7913a4.4944 4.4944 0 0 1-.6765 8.1042v-5.6772a.79.79 0 0 0-.407-.667zm2.0107-3.0231l-.142-.0852-4.7735-2.7818a.7759.7759 0 0 0-.7854 0L9.409 9.2297V6.8974a.0662.0662 0 0 1 .0284-.0615l4.8303-2.7866a4.4992 4.4992 0 0 1 6.6802 4.66zM8.3065 12.863l-2.02-1.1638a.0804.0804 0 0 1-.038-.0567V6.0742a4.4992 4.4992 0 0 1 7.3757-3.4537l-.142.0805L8.704 5.459a.7948.7948 0 0 0-.3927.6813zm1.0976-2.3654l2.602-1.4998 2.6069 1.4998v2.9994l-2.5974 1.4997-2.6067-1.4997Z");

/* ---------- S2 build ---------- */
(function(){
  let r='';for(let i=0;i<10;i++){const a=(-90+i*36+18)*Math.PI/180;r+=`<line x1="${Math.cos(a)*92}" y1="${Math.sin(a)*92}" x2="${Math.cos(a)*118}" y2="${Math.sin(a)*118}"/>`;}
  $('rays').innerHTML=r;
  let f='';const pos=[];
  for(let i=0;i<6;i++){const c=i%3,rw=Math.floor(i/3);
    f+=`<div class="abs bf" style="left:${28+c*186}px;top:${34+rw*140}px;width:172px;height:118px;border-radius:12px;border:2px solid rgba(71,227,195,.55);background:rgba(71,227,195,.05)">
     <svg width="172" height="118" viewBox="0 0 172 118" fill="none" stroke="rgba(240,189,74,.85)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="position:absolute;left:0;top:0">
      ${[`<circle cx="120" cy="38" r="14"/><path d="M20 96L64 52L96 82L120 62L152 96Z"/>`,`<rect x="24" y="30" width="60" height="58" rx="8"/><path d="M104 44h46M104 62h46M104 80h30"/>`,`<circle cx="86" cy="60" r="30"/><circle cx="86" cy="60" r="10"/>`,`<path d="M22 86C50 20 90 100 150 34"/><circle cx="150" cy="34" r="7"/>`,`<rect x="22" y="34" width="52" height="52" rx="8"/><rect x="98" y="34" width="52" height="52" rx="8"/><path d="M76 60h20"/>`,`<path d="M30 90V40M62 90V24M94 90V56M126 90V30"/>`][i]}
     </svg><div class="abs mono" style="left:8px;top:6px;font-size:14px;color:#47e3c3;letter-spacing:.05em">0${i+1}</div></div>`;}
  $('bframes').innerHTML=f;
  const names=['الفكرة','السيناريو','حركة العناصر','المؤثرات الصوتية'];
  $('nodes').innerHTML=names.map((n,i)=>`<div class="abs nd" style="left:240px;width:600px;top:${790+i*124}px;height:84px;border-radius:44px;background:linear-gradient(90deg,rgba(240,189,74,.14),rgba(20,25,36,.95));border:2px solid rgba(240,189,74,.65);display:flex;align-items:center;justify-content:center;font-size:44px"><span class="abs mono gold" style="right:26px;top:0;line-height:84px;font-size:26px">0${i+1}</span>${n}</div>`).join('');
})();

/* ---------- S3 build ---------- */
const ICON={
 'Storyboard':'<rect x="6" y="8" width="16" height="12" rx="2"/><rect x="26" y="8" width="16" height="12" rx="2"/><rect x="6" y="26" width="16" height="12" rx="2"/><rect x="26" y="26" width="16" height="12" rx="2"/>',
 'Animation Timing':'<circle cx="24" cy="24" r="16"/><path d="M24 14v11l8 5"/>',
 'Visual Style':'<circle cx="24" cy="24" r="17"/><circle cx="17" cy="19" r="2.5"/><circle cx="26" cy="15" r="2.5"/><circle cx="32" cy="23" r="2.5"/><path d="M24 41c-6 0-3-8 2-8h6"/>',
 'Camera Movement':'<rect x="5" y="14" width="28" height="20" rx="4"/><path d="M33 22l10-6v16l-10-6"/>',
 'Sound Design':'<path d="M8 24v0M14 16v16M20 8v32M26 14v20M32 19v10M38 22v4"/>'};
const rowsData=[['Storyboard','تقسيم الفكرة إلى مشاهد'],['Animation Timing','توقيت دخول العناصر وخروجها'],['Visual Style','الألوان والخطوط والهوية'],['Camera Movement','حركة الكاميرا والتركيز'],['Sound Design','الغالق والنقرات والمؤثرات']];
$('rows').innerHTML=rowsData.map((r,i)=>`<div class="abs rw" style="left:70px;width:940px;top:${736+i*112}px;height:100px;border-radius:22px;background:linear-gradient(180deg,#181d2a,#11151e);border:2px solid rgba(240,189,74,.3);direction:ltr">
 <svg class="abs" style="left:24px;top:26px" width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="#f0bd4a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">${ICON[r[0]]}</svg>
 <div class="abs" style="left:100px;top:14px;font-family:'JB';font-weight:700;font-size:36px;letter-spacing:.01em">${r[0]}</div>
 <div class="abs" style="left:100px;top:58px;font-size:25px;font-weight:500;color:#8c97ab;direction:rtl;width:700px;text-align:left">${r[1]}</div>
 <div class="abs rk" style="right:26px;top:30px;width:40px;height:40px;border-radius:50%;background:var(--teal);display:flex;align-items:center;justify-content:center"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0a0d14" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l5 5L19 7"/></svg></div>
 </div>`).join('');

/* ---------- S4 art ---------- */
const BUSY=[243,194,31], BUSB=[34,196,176];
function mix(a,b,p){return `rgb(${a.map((v,i)=>Math.round(lerp(v,b[i],p))).join(',')})`;}
function rider(x,y,s,i){
  return `<g transform="translate(${x},${y}) scale(${s})">
  <rect x="-70" y="-20" width="140" height="120" rx="8" fill="#eef2f6"/><rect x="-58" y="-8" width="116" height="96" rx="4" fill="#3b8fe0"/>
  <circle cx="-30" cy="58" r="13" fill="#b84fd0"/><rect x="-10" y="44" width="26" height="36" rx="5" fill="#2bb5a6"/><circle cx="30" cy="62" r="12" fill="#f6c63d"/><circle cx="8" cy="30" r="9" fill="#e2493b"/>
  <ellipse cx="0" cy="-48" rx="38" ry="36" fill="${i==2?'#15181e':'#f1f3f6'}"/><rect x="-26" y="-70" width="52" height="8" rx="4" fill="rgba(255,255,255,.35)"/>
  <rect x="-60" y="100" width="120" height="40" rx="14" fill="#1f2937"/><rect x="-24" y="104" width="48" height="22" rx="8" fill="#e63a2e"/>
  <rect x="-30" y="148" width="60" height="26" rx="4" fill="#f3c21f"/><rect x="-14" y="176" width="28" height="60" rx="8" fill="#2a2f38"/></g>`;}
$('art').innerHTML=`<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c5f80"/><stop offset=".7" stop-color="#c8a07e"/><stop offset="1" stop-color="#e7b88a"/></linearGradient>
 <linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4f58"/><stop offset="1" stop-color="#23262d"/></linearGradient>
 <radialGradient id="rg"><stop offset="0" stop-color="#ff3b2e" stop-opacity=".9"/><stop offset="1" stop-color="#ff3b2e" stop-opacity="0"/></radialGradient></defs>
 <rect width="900" height="360" fill="url(#sky)"/>
 <g id="far"><rect x="640" y="236" width="90" height="120" fill="#a7a49e"/><rect x="740" y="270" width="80" height="90" fill="#8f8d89"/><rect x="40" y="260" width="60" height="100" fill="#9b6a63"/>
 <path d="M800 360V270M800 270q-30 -20 -50 -6M800 270q30 -24 56 -8M800 270q-6 -34 8 -50" stroke="#2f5a3c" stroke-width="7" fill="none"/></g>
 <g id="mid"><rect x="808" y="40" width="10" height="320" fill="#5d6068"/><rect x="560" y="60" width="256" height="10" fill="#5d6068"/>
 <rect x="530" y="58" width="42" height="84" rx="6" fill="#1c1e23"/><circle cx="551" cy="82" r="13" fill="#ff3b2e"/><circle id="rglow" cx="551" cy="82" r="38" fill="url(#rg)"/></g>
 <rect y="352" width="900" height="300" fill="url(#road)"/>
 <path d="M450 352L-120 650M450 352L1020 650" stroke="#e9e9e9" stroke-width="7" opacity=".7"/><path d="M450 352L860 650" stroke="#e8b52a" stroke-width="9" opacity=".85"/>
 <g id="bus"><rect x="238" y="120" width="424" height="262" rx="30" fill="${mix(BUSY,BUSY,0)}" id="busbody"/>
 <rect x="268" y="150" width="364" height="124" rx="16" fill="#1a222d"/><path d="M300 250q18 -50 44 -2M420 252q22 -56 52 0M560 252q14 -44 40 0" fill="#27303d"/>
 <rect x="408" y="288" width="84" height="12" rx="6" fill="#ff5a4d"/><circle cx="276" cy="318" r="18" fill="#d63a2c"/><circle cx="624" cy="318" r="18" fill="#d63a2c"/>
 <circle cx="262" cy="108" r="0" fill="none"/><rect x="238" y="372" width="424" height="22" rx="8" fill="#2b2e35"/></g>
 <g id="riders">${rider(300,330,.62,0)}${rider(430,350,.76,1)}${rider(620,378,1.02,2)}</g>
 <g id="bracket" fill="none" stroke="#47e3c3" stroke-width="5" stroke-linecap="round">
  <rect id="brect" pathLength="1" x="206" y="96" width="488" height="316" rx="6" stroke-dasharray="1" stroke-width="3" opacity=".9" style="stroke-dasharray:.02 .015"/>
  <path id="bcorn" pathLength="1" stroke-dasharray="1" d="M206 150V96H260M640 96H694V150M694 360V412H640M260 412H206V360"/></g>
 <g id="lbl"><rect x="222" y="62" width="346" height="50" rx="25" fill="rgba(8,12,14,.92)" stroke="#47e3c3" stroke-width="2"/>
 <text x="395" y="96" text-anchor="middle" font-family="JB,monospace" font-weight="700" font-size="22" letter-spacing="3" fill="#47e3c3">01 · COLOR · OBJECT</text></g>`;
['brect','bcorn'].forEach(id=>$(id));

/* ---------- S5 timeline ---------- */
(function(){
  let w='';for(let i=0;i<46;i++){const h=18+Math.abs(Math.sin(i*1.7)*Math.cos(i*.53))*52;w+=`<i class="wv" style="position:absolute;left:${130+i*17.4}px;top:${912-h/2}px;width:7px;height:${h}px;border-radius:4px;background:#47e3c3;display:block"></i>`;}
  let tk='';for(let i=0;i<=16;i++){tk+=`<i style="position:absolute;left:${130+i*50}px;top:${i%4==0?664:674}px;width:2px;height:${i%4==0?22:12}px;background:rgba(240,189,74,.7);display:block"></i>`;}
  let kf='';[170,300,470,640,790].forEach(x=>kf+=`<i style="position:absolute;left:${x}px;top:1040px;width:18px;height:18px;transform:rotate(45deg);background:#f0bd4a;display:block"></i>`);
  $('tl').innerHTML=`<div id="tlbg" class="abs" style="left:100px;top:630px;width:880px;height:470px;border-radius:24px;background:rgba(12,15,22,.85);border:2px solid rgba(240,189,74,.3)"></div>
  <div id="tlui"><div class="abs" style="left:130px;top:688px;width:800px;height:2px;background:rgba(240,189,74,.5)"></div>${tk}
  <div class="abs" style="left:130px;top:870px;width:800px;height:84px;border-radius:12px;background:rgba(71,227,195,.08);border:1px solid rgba(71,227,195,.4)"></div>${w}
  <div class="abs" style="left:130px;top:1020px;width:800px;height:58px;border-radius:12px;background:rgba(240,189,74,.07);border:1px solid rgba(240,189,74,.35)"></div>${kf}
  <div id="ph" class="abs" style="left:130px;top:650px;width:3px;height:450px;background:#f0bd4a;box-shadow:0 0 18px #f0bd4a"><div style="position:absolute;left:-10px;top:-6px;width:23px;height:23px;background:#f0bd4a;clip-path:polygon(0 0,100% 0,50% 100%)"></div></div></div>
  <div id="play" class="abs" style="left:440px;top:1170px;width:200px;height:200px">
   <div id="pring" class="abs" style="inset:0;border-radius:50%;border:4px solid var(--teal)"></div>
   <div class="abs" style="inset:14px;border-radius:50%;background:var(--teal);display:flex;align-items:center;justify-content:center"><svg width="80" height="80" viewBox="0 0 24 24" fill="#0a0d14"><path d="M8 5v14l11-7z"/></svg></div></div>`;
})();

/* ---------- S6 words ---------- */
const w6=['الوصف','الدقيق','يصنع','فرقًا','كبيرًا','في','النتيجة!'];
$('big6').innerHTML=w6.map((w,i)=>`<span class="w6" style="display:inline-block;margin:0 14px;${(i==3||i==4)?'color:#f0bd4a':''}">${w}</span>${i==1||i==4?'<br>':''}`).join('');
const w6n=[...document.querySelectorAll('.w6')];

/* ---------- scenes ---------- */
const scn=[1,2,3,4,5,6].map(i=>$('sc'+i));
function u1(lt){
  const open=eio(pr(lt,.15,1.5)), shut=pr(lt,.25,.4);
  L1.set(lerp(6,128,open)*(1-.55*Math.sin(Math.PI*pr(lt,.25,.45))),lt*14,lt*3);
  $('lens1').style.opacity=eo(pr(lt,0,.4)); $('lens1').style.transform=`scale(${lerp(.82,1,eo(pr(lt,0,1.2)))})`;
  [...$('guides1').querySelectorAll('path')].forEach((p,i)=>{if(p.parentNode.id==='xh1')return;p.style.strokeDasharray=1;p.style.strokeDashoffset=1-eio(pr(lt,.3+i*.12,1.5+i*.12));});
  $('xh1').style.opacity=pr(lt,1.3,1.8)*(.6+.4*Math.sin(lt*8));
  rev($('h1'),lt,.9,.7,50);
  const q=pr(lt,K.s1_q,K.s1_q+.6); tf($('q1'),{o:eo(q),y:(1-eo(q))*60,b:(1-eo(q))*10});
  const hy=-eio(pr(lt,K.s1_q,K.s1_q+.6))*70; $('h1').style.transform+=` translateY(${hy}px)`;
  $('t1').style.opacity=eo(pr(lt,.2,.9));
}
function u2(lt){
  const b=pr(lt,K.s2_bulb,K.s2_bulb+.5), m=eio(pr(lt,K.s2_morph,K.s2_morph+.6));
  const glow=.55+.45*Math.sin(lt*7)*(1-m);
  $('bulb').style.opacity=eo(b)*(1-m); $('bulb').style.transform=`scale(${lerp(.4,1,eb(b))*(1-.35*m)}) rotate(${m*-20}deg)`;
  $('bglow').style.opacity=glow; $('fil').style.strokeDasharray=1; $('fil').style.strokeDashoffset=1-eo(pr(lt,.3,.8));
  [...$('rays').children].forEach((l,i)=>{const p=eo(pr(lt,.35+i*.03,.75+i*.03));l.style.opacity=p;});
  const bd=$('board'); const bp=eo(pr(lt,K.s2_morph+.1,K.s2_morph+.8));
  tf(bd,{o:bp,s:lerp(.8,1,bp),y:(1-bp)*30});
  [...document.querySelectorAll('.bf')].forEach((f,i)=>{const p=eb(pr(lt,K.s2_morph+.4+i*.09,K.s2_morph+.8+i*.09));f.style.opacity=clamp(p*1.2);f.style.transform=`scale(${lerp(.6,1,p)})`;});
  const nd=[...document.querySelectorAll('.nd')];
  nd.forEach((n,i)=>{const p=eo(pr(lt,K.s2_nodes[i],K.s2_nodes[i]+.55));tf(n,{o:p,x:(1-p)*-90,s:lerp(.92,1,p)});});
  const cl=$('chainline');cl.style.strokeDashoffset=1-clamp((lt-K.s2_nodes[0])/(K.s2_nodes[3]-K.s2_nodes[0]+.4));
  const cp=clamp((lt-K.s2_nodes[0])/(K.s2_nodes[3]-K.s2_nodes[0]+.4)); const cd=$('chaindot');
  cd.setAttribute('cx',540);cd.setAttribute('cy',826+cp*374);cd.style.opacity=cp>0&&cp<1?1:0;
  rev($('h2'),lt,K.s2_head,.7,50);
}
function u3(lt){
  const c=eo(pr(lt,K.s3_card,K.s3_card+.6)); tf($('chat'),{o:c,y:(1-c)*70});
  const ty=typeText(TM.prompt,lt,K.s3_type[0],K.s3_type[1]);
  const typing=lt>=K.s3_type[0]&&lt<K.s3_type[1]+.6;
  $('typed').innerHTML=ty+(lt>=K.s3_type[0]-.2?`<span class="caret" style="opacity:${typing||Math.floor(lt*2)%2==0?1:0}"></span>`:'');
  const pp=pr(lt,K.s3_proc[0],K.s3_proc[1]+.6);
  const d=[...$('dots').children];
  $('dots').style.opacity=(lt>K.s3_proc[0]&&lt<K.s3_cards[0]+.8)?1:0;
  d.forEach((x,i)=>{x.style.transform=`translateY(${-Math.abs(Math.sin(lt*9-i*.7))*12}px)`;});
  $('scan').style.opacity=(lt>K.s3_proc[0]&&lt<K.s3_proc[1]+.5)?1:0;
  $('scan').style.left=`${lerp(-130,940,pr(lt,K.s3_proc[0],K.s3_proc[1]+.5))}px`;
  [...document.querySelectorAll('.rw')].forEach((r,i)=>{const a=K.s3_cards[i],p=eb(pr(lt,a,a+.5));
    r.style.opacity=clamp(p*1.4);r.style.transform=`translateY(${(1-p)*50}px) scale(${lerp(.94,1,p)})`;
    const k=r.querySelector('.rk');const kp=eb(pr(lt,a+.3,a+.7));k.style.transform=`scale(${kp})`;});
  rev($('tag3'),lt,K.s3_tag,.8,50);
}
function u4(lt){
  const A=pr(lt,0,.6), toSmall=eio(pr(lt,2.6,3.6));
  const r=lerp(150,22,eio(pr(lt,.2,1.6)))+ (lt>1.6? (60-20)*Math.sin(clamp((lt-1.6)/1.2)*Math.PI):0) ;
  L4.set(lerp(r,60,toSmall),lt*22,lt*4);
  const lh=$('lens4'); lh.style.opacity=eo(A)*(1-.0*toSmall);
  const sc=lerp(1,.14,toSmall), ty=lerp(0,-405,toSmall); // scale around center (540,760) -> (540,270)
  lh.style.transform=`translateY(${ty}px) scale(${sc})`;
  $('t4').style.opacity=1;
  const cp=eo(pr(lt,K.s4_card,K.s4_card+.8)); tf($('scard'),{o:cp,y:(1-cp)*80,s:lerp(.94,1,cp)});
  $('cap4').style.opacity=cp*(lt<K.s4_text-.5?1:Math.max(0,1-(lt-K.s4_text+.5)*2));
  // camera drift in art
  const dr=Math.sin(lt*.9);$('far').setAttribute('transform',`translate(${dr*6},0)`);$('mid').setAttribute('transform',`translate(${dr*12},0)`);
  $('bus').setAttribute('transform',`translate(${dr*20},0)`);$('riders').setAttribute('transform',`translate(${dr*34},${Math.abs(Math.sin(lt*1.4))*1.5})`);
  $('rglow').style.opacity=.6+.4*Math.sin(lt*3);
  // bracket
  const bp=eio(pr(lt,K.s4_bracket,K.s4_bracket+1.0));
  $('bcorn').style.strokeDashoffset=1-bp; $('brect').style.opacity=bp*.9;
  const lb=$('lbl');lb.style.opacity=eo(pr(lt,K.s4_bracket+.4,K.s4_bracket+.9));
  // command
  const ct=typeText(TM.cmd,lt,K.s4_type[0],K.s4_type[1]).slice(1);
  $('cmdtxt').textContent=ct; $('cmd').style.opacity=eo(pr(lt,K.s4_card+.5,K.s4_card+1.1));
  $('ccaret').style.opacity=(lt<K.s4_send+.3)?(Math.floor(lt*2.5)%2==0||lt<K.s4_type[1]+.2?1:0):0;
  const sp=pr(lt,K.s4_send,K.s4_send+.3); $('send').style.transform=`scale(${1-.22*Math.sin(sp*Math.PI)})`;
  const sh=eio(pr(lt,K.s4_shift[0],K.s4_shift[1]));
  $('busbody').setAttribute('fill',mix(BUSY,BUSB,sh));
  $('bracket').style.opacity=1;
  $('scard').style.boxShadow=`0 20px 60px rgba(0,0,0,.5), 0 0 ${Math.sin(sh*Math.PI)*70}px rgba(71,227,195,${Math.sin(sh*Math.PI)*.55})`;
  const h=pr(lt,K.s4_text,K.s4_text+.8); tf($('h4'),{o:eo(h),y:(1-eo(h))*50,b:(1-eo(h))*8});
}
function u5(lt){
  const cam=lt/5.7, ent=eo(pr(lt,0,.9));
  const base=[{x:70+120,w:380},{x:550+120-0,w:380}]; // left positions 140 / 560
  const A=[[140,590,380,670],[560,590,380,670]], B=[[130,700,430,140],[560,700,370,140]];
  const m=eio(pr(lt,K.s5_morph,K.s5_morph+.8));
  ['fr1','fr2'].forEach((id,i)=>{const n=$(id);
    const e=eo(pr(lt,i*.12,.9+i*.12));
    const x=lerp(A[i][0],B[i][0],m),y=lerp(A[i][1],B[i][1],m),w=lerp(A[i][2],B[i][2],m),h=lerp(A[i][3],B[i][3],m);
    n.style.left=x+'px';n.style.top=y+'px';n.style.width=w+'px';n.style.height=h+'px';n.style.borderRadius=lerp(26,10,m)+'px';
    const ry=(i==0?1:-1)*lerp(14,2,m)*(1-cam*.55)+Math.sin(lt*.8)*2*(1-m), sl=(1-e)*(i==0?-500:500);
    n.style.transform=`translateX(${sl}px) rotateY(${ry}deg) scale(${lerp(1,1.035,cam)})`;
    n.style.opacity=clamp(e*1.6);n.firstChild.style.objectPosition=`50% ${lerp(50,30,m)}%`;});
  [['l5a',0],['l5b',1],['l5c',2]].forEach(([id,i])=>rev($(id),lt,K.s5_text[i],.6,40));
  const tb=eo(pr(lt,K.s5_morph+.2,K.s5_morph+.9)); $('tl').style.opacity=tb; $('tlbg').style.opacity=tb;
  $('tlui').style.opacity=tb;
  const sweep=pr(lt,K.s5_morph+.9,K.s5_play+.2); $('ph').style.left=(130+eio(sweep)*800)+'px';
  [...document.querySelectorAll('.wv')].forEach((w,i)=>{const on=(130+i*17.4)<(130+eio(sweep)*800);w.style.opacity=on?1:.28;w.style.transform=`scaleY(${on?.85+.3*Math.abs(Math.sin(lt*9+i)):1})`;});
  const pl=eb(pr(lt,K.s5_play,K.s5_play+.5)); $('play').style.transform=`scale(${pl})`;$('play').style.opacity=clamp(pl*2);
  const rp=pr(lt,K.s5_play+.3,K.s5_play+1.2);$('pring').style.transform=`scale(${1+rp*.35})`;$('pring').style.opacity=lt>K.s5_play+.3?1-rp:0;
}
function u6(lt){
  L6.set(110,lt*6,lt*2);
  const t0=K.s6_words[0],t1=K.s6_words[1];
  w6n.forEach((w,i)=>{const a=lerp(t0,t1,i/(w6n.length-1));rev(w,lt,a,.5,40);});
  const c=eb(pr(lt,K.s6_cta,K.s6_cta+.6)); const cta=$('cta'); cta.style.opacity=clamp(c*1.5);cta.style.transform=`scale(${lerp(.85,1,c)})`;
  cta.style.boxShadow=`0 0 ${30+20*Math.sin(lt*4)}px rgba(71,227,195,${.25+.15*Math.sin(lt*4)})`;
  $('pt').style.transform=`translateY(${Math.abs(Math.sin(lt*5))*16}px)`;
  const s=pr(lt,K.s6_sig,K.s6_sig+.8); tf($('sig'),{o:eo(s),x:(1-eo(s))*-40});
}
const U=[u1,u2,u3,u4,u5,u6];

window.render=function(t){
  $('progf').style.width=(t/TM.total*100)+'%';
  let ring=null;
  scn.forEach((n,i)=>{
    const a=S[i],b=S[i+1];
    const show=t>=a-.2&&(i==5||t<b+.8);
    n.style.display=show?'block':'none'; if(!show)return;
    n.style.zIndex=i+1;
    if(i>0){const p=pr(t,a-.15,a+.65);const r=eio(p)*1800;
      n.style.clipPath=p>=1?'none':`circle(${r}px at 540px 780px)`; if(p>0&&p<1)ring={r,p};}
    else n.style.clipPath='none';
    const nxt=pr(t,b-.15,b+.65); n.style.filter=nxt>0&&nxt<1?`brightness(${1-.4*nxt})`:'none';
    U[i](t-a);
  });
  const w=$('wring');
  if(ring){w.style.opacity=1-ring.p*.9;w.style.width=w.style.height=(ring.r*2-12)+'px';w.style.left=(540-ring.r)+'px';w.style.top=(780-ring.r)+'px';}
  else w.style.opacity=0;
  $('flash').style.opacity=Math.max(0,.55*(1-Math.abs(t-.28)/.06))*(t<.5?1:0);
};
window.render(0);
