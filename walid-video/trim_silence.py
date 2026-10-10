"""Usage: python3 trim_silence.py in.mp3 out.wav [--ratio 0.25] [--min 0.12] [--max 0.30] [--db -32] [--minsil 0.35]
Shortens every pause longer than --minsil: keeps `ratio` of it (clamped to min..max seconds), split half at each
side of the cut so the speech keeps a natural breath instead of running together. Writes out.wav and out.map.json
(list of [old_start, old_end, new_start] pieces) so scene timings can be remapped to the trimmed audio."""
import sys, re, subprocess, json, argparse
p=argparse.ArgumentParser(); p.add_argument('src'); p.add_argument('dst')
p.add_argument('--ratio',type=float,default=.25); p.add_argument('--min',type=float,default=.12); p.add_argument('--max',type=float,default=.30)
p.add_argument('--db',type=float,default=-32); p.add_argument('--minsil',type=float,default=.35); a=p.parse_args()
log=subprocess.run(['ffmpeg','-i',a.src,'-af',f'silencedetect=n={a.db}dB:d={a.minsil}','-f','null','-'],capture_output=True,text=True).stderr
m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',log); dur=int(m[1])*3600+int(m[2])*60+float(m[3])
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
if len(en)<len(st): en.append(dur)
keep=[]; cur=0.0
for s,e in zip(st,en):
    k=min(a.max,max(a.min,a.ratio*(e-s)))
    if e-s<=k+.02: continue
    keep.append((cur,s+k/2)); cur=e-k/2          # speech + half the kept pause, then jump
keep.append((cur,dur))
keep=[(x,y) for x,y in keep if y-x>0.02]
fc=''.join(f'[0:a]atrim={x:.3f}:{y:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0,y-x-.01):.3f}:d=0.01[a{i}];' for i,(x,y) in enumerate(keep))
fc+=''.join(f'[a{i}]' for i in range(len(keep)))+f'concat=n={len(keep)}:v=0:a=1[o]'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',a.src,'-filter_complex',fc,'-map','[o]',a.dst],check=True)
t=0; mp=[]
for x,y in keep: mp.append([round(x,3),round(y,3),round(t,3)]); t+=y-x
json.dump(mp,open(a.dst.rsplit('.',1)[0]+'.map.json','w'))
print(f'{dur:.2f}s -> {t:.2f}s  (removed {dur-t:.2f}s, {len(keep)-1} pauses shortened)')
