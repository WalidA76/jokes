// usage: node render.js <t0> <t1> <outfile> [fps]   -> renders frames [t0,t1) to an mp4 segment
const {chromium}=require('playwright');
const {spawn}=require('child_process');const fs=require('fs');const path=require('path');
(async()=>{
 const [a,b,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
 const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'config.json')));const fps=cfg.fps;
 const br=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--font-render-hinting=none']});
 const pg=await br.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 await pg.addInitScript(`window.CFG=${JSON.stringify(cfg)}`);
 await pg.goto('file://'+path.join(__dirname,'index.html'));await pg.evaluate(()=>window.READY);
 if(process.argv[5]==='still'){const t=+process.argv[3];await pg.evaluate(t=>window.render(t),t);await pg.screenshot({path:out});await br.close();return}
 const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p','-r',String(fps),out],{stdio:['pipe','inherit','inherit']});
 const n0=Math.round(a*fps),n1=Math.round(b*fps);
 for(let n=n0;n<n1;n++){await pg.evaluate(t=>window.render(t),n/fps);const buf=await pg.screenshot({type:'jpeg',quality:95});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r))}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await br.close();
})();
