import json, numpy as np, wave, sys
cfg=json.load(open('config.json')); SR=44100; D=cfg['duration']; N=int(SR*D)
rs=np.random.RandomState(7); L=np.zeros(N); R=np.zeros(N)
def add(sig,t,g=1.0,pan=0.0):
    t=max(0,t); i=int(t*SR); 
    if i>=N: return
    s=sig[:N-i]; L[i:i+len(s)]+=s*g*(1-pan)/1; R[i:i+len(s)]+=s*g*(1+pan)/1
def tt(d): return np.arange(int(d*SR))/SR
def lp(x,a): 
    y=np.zeros_like(x); s=0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def noise(d): return rs.randn(int(d*SR))
def click(): t=tt(.06); return np.sin(2*np.pi*1800*t)*np.exp(-t*90)+np.sin(2*np.pi*900*t)*np.exp(-t*60)*.5
def key(): t=tt(.04); return noise(.04)*np.exp(-t*140)*.5+np.sin(2*np.pi*(1200+rs.rand()*500)*t)*np.exp(-t*120)*.3
def whoosh(d=.7):
    t=tt(d); n=noise(d); f=np.linspace(.01,.25,len(t)); env=np.sin(np.pi*t/d)**2
    y=np.zeros_like(n); s=0
    for i in range(len(n)): s+=f[i]*(n[i]-s); y[i]=s
    return y*env*2.2
def proc(d):
    t=tt(d); f=300+600*t/d; ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*.4+np.sin(ph*1.5)*.2)*(1+.5*np.sin(2*np.pi*14*t))*np.sin(np.pi*t/d)
def sweep(d):
    t=tt(d); f=200*(2**(t/d*3.2)); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*.25+np.sign(np.sin(ph))*.07)*np.minimum(1,t/.3)*np.minimum(1,(d-t)/.4)
for t in cfg['whoosh']: add(whoosh(),t-.3,.5)
for t in cfg['click']: add(click(),t,.55)
for a,b,*_ in [ (x['t0'],x['t1']) for x in cfg['typing']]: pass
for x in cfg['typing']:
    n=len(x['text'])
    for i in range(n): add(key(),x['t0']+(x['t1']-x['t0'])*i/n,.45,pan=(rs.rand()-.5)*.3)
for a,b in cfg['process']: add(proc(b-a+.2),a,.5)
for a,b in cfg['sweep']: add(sweep(b-a),a,.55)
for t in cfg['hit']:
    tt_=tt(1.6); add(np.sin(2*np.pi*55*tt_)*np.exp(-tt_*3)*.9+noise(1.6)*np.exp(-tt_*6)*.12,t,.8)
    for k,fq in enumerate([523.25,659.25,783.99,1046.5]): add(np.sin(2*np.pi*fq*tt_)*np.exp(-tt_*2.5)*.12,t+k*.07,.8)
# music: 120 bpm, A minor
bpm=120; beat=60/bpm
def kick(): t=tt(.35); f=130*np.exp(-t*18)+45; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat(): t=tt(.06); return noise(.06)*np.exp(-t*70)*.3
def bass(f,d): t=tt(d); w=2*(((t*f)%1))-1; return lp(w,.06)*np.exp(-t*4)*.9
def pluck(f,d=.3): t=tt(d); w=np.sign(np.sin(2*np.pi*f*t))*.5+np.sin(2*np.pi*f*2*t)*.3; return w*np.exp(-t*9)*.35
roots=[110,87.31,130.81,98]  # A F C G
arp=[[0,3,7,12],[0,4,7,12],[0,4,7,12],[0,4,7,12]]
nb=int(D/beat)
for b in range(nb):
    t=b*beat
    if t<1: g=0
    else: g=min(1,.55+t/38*.6)
    if t>=1:
        if b%1==0: add(kick(),t,.55*g)
        add(hat(),t+beat/2,.35*g)
        if 4<t: add(hat(),t+beat/4,.12*g)
    bar=(b//4)%4; rt=roots[bar]
    if t>=2:
        add(bass(rt,beat*.9),t,.5*g)
        for k in range(2):
            n=arp[bar][(b*2+k)%4]; add(pluck(rt*4*2**(n/12)),t+k*beat/2,.55*g,pan=.25 if k else -.25)
# pad
t=tt(D); pad=sum(np.sin(2*np.pi*f*t+rs.rand()*6) for f in [220,261.63,329.63,440])*.04*np.minimum(1,t/4)
pad*=np.where(t>33.3,1,.6); L+=pad; R+=pad
# fade out
fo=np.minimum(1,(D-np.arange(N)/SR)/1.2); L*=fo; R*=fo
m=max(abs(L).max(),abs(R).max()); L=L/m*.85; R=R/m*.85
out=(np.stack([L,R],1)*32767).astype('<i2')
w=wave.open('/tmp/claude-0/-home-user-jokes/832c973b-1afc-56c4-b239-3da2d5652a9f/scratchpad/audio.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
