import json, wave, numpy as np
T=json.load(open('timing.json')); S=T['s']; K=T['K']; SR=44100; N=int(SR*48.0)
rng=np.random.default_rng(7)
sfx=np.zeros(N); 
def add(t,x,g=1.0):
    i=int(t*SR); x=x*g; e=min(N,i+len(x)); 
    if i<N: sfx[i:e]+=x[:e-i]
def tt(d): return np.arange(int(d*SR))/SR
def lp(x,a):  # one-pole lowpass
    y=np.zeros_like(x); s=0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def click(f=1800,d=.03):
    t=tt(d); return np.sin(2*np.pi*f*t)*np.exp(-t*160)+rng.normal(0,1,len(t))*np.exp(-t*220)*.5
def shutter():
    a=click(2600,.05)*1.0; b=np.zeros(int(.09*SR)); c=click(1500,.07)*.8
    return np.concatenate([a,b,c])
def whoosh(d=.7,up=True):
    t=tt(d); n=rng.normal(0,1,len(t)); env=np.sin(np.pi*np.clip(t/d,0,1))**2
    f=np.linspace(.03,.35,len(t)) if up else np.linspace(.35,.03,len(t))
    y=np.zeros(len(t)); s=0
    for i in range(len(t)): s+=f[i]*(n[i]-s); y[i]=s
    return y*env*2.2
def ping(f=1760,d=.5):
    t=tt(d); return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2*t))*np.exp(-t*7)*.5
def pop(f=520):
    t=tt(.12); return np.sin(2*np.pi*(f+f*t*4)*t)*np.exp(-t*30)
def blips(d=.8):
    out=np.zeros(int(d*SR)); notes=[880,1175,1568,1319,1760,1568,2093,1760]
    for k,f in enumerate(notes):
        t=tt(.07); b=np.sign(np.sin(2*np.pi*f*t))*.25*np.exp(-t*35); i=int(k*d/len(notes)*SR); out[i:i+len(b)]+=b
    return out
def chime():
    t=tt(1.0); return sum(np.sin(2*np.pi*f*t)*np.exp(-t*4) for f in (1046,1318,1568,2093))*.18
def hum(d=1.0):
    t=tt(d); f=200+500*t/d; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*t/d)*.25
a=lambda i,o:S[i]+o
# S1
add(a(0,K['s1_a']),shutter(),.8); add(a(0,K['s1_a'])-.2,whoosh(.5),.5); add(a(0,K['s1_b']),shutter(),.8); add(a(0,K['s1_b'])-.2,whoosh(.5),.5); add(a(0,K['s1_title']),pop(480),.4)
# transitions
for i in range(1,6): add(S[i]-.25,whoosh(.8),.55)
# S2
add(a(1,K['s2_bulb']),ping(),.7); add(a(1,K['s2_morph']),pop(),.5)
for j in range(6): add(a(1,K['s2_morph']+.4+j*.09),click(2200,.02),.25)
for o in K['s2_nodes']: add(a(1,o),pop(640),.45)
add(a(1,K['s2_head']),ping(1318,.5),.4)
# S3
add(a(2,K['s3_card']),pop(400),.5)
n=int((K['s3_type'][1]-K['s3_type'][0])*18)
for j in range(n): add(a(2,K['s3_type'][0])+j/18+rng.uniform(-.01,.01),click(rng.choice([1500,1900,2300]),.02),.28)
add(a(2,K['s3_proc'][0]),click(900,.05),.7); add(a(2,K['s3_proc'][0]),blips(.8),.5)
for o in K['s3_cards']: add(a(2,o),pop(560),.5)
add(a(2,K['s3_tag']),chime(),.6)
# S4
add(a(3,.25),shutter(),.7); add(a(3,1.8),shutter(),.6); add(a(3,K['s4_card']-.1),whoosh(.6,False),.4)
add(a(3,K['s4_bracket']),blips(.6),.35)
n=int((K['s4_type'][1]-K['s4_type'][0])*14)
for j in range(n): add(a(3,K['s4_type'][0])+j/14+rng.uniform(-.01,.01),click(rng.choice([1400,1800,2200]),.02),.28)
add(a(3,K['s4_send']),click(900,.05),.7); add(a(3,K['s4_shift'][0]),hum(1.2),.5); add(a(3,K['s4_text']),chime(),.5)
# S5
for o in K['s5_text']: add(a(4,o),pop(480),.35)
add(a(4,K['s5_morph']),whoosh(.7),.5)
for j in range(8): add(a(4,K['s5_morph']+.9+j*.14),click(2500,.015),.25)
add(a(4,K['s5_play']),pop(700),.7); add(a(4,K['s5_play']),chime(),.5)
# S6
for j in range(7): add(a(5,K['s6_words'][0]+j*(K['s6_words'][1]-K['s6_words'][0])/6),pop(420),.3)
add(a(5,K['s6_cta']),pop(600),.6); add(a(5,K['s6_cta']),ping(1568),.4)
sfx=np.tanh(sfx*1.3)
# ambient pad
t=np.arange(N)/SR; pad=np.zeros(N)
for f,g in [(110,1),(164.8,.7),(220,.6),(261.6,.5),(329.6,.4)]:
    for d in (-.6,.6): pad+=g*np.sin(2*np.pi*(f+d)*t+rng.uniform(0,6))
pad*=.5+.5*np.sin(2*np.pi*t/12-1.5)*.5+.25
pad*=np.clip(t/2,0,1)*np.clip((48-t)/2,0,1); pad/=np.abs(pad).max()
def w(name,x):
    x=np.clip(x,-1,1); st=np.stack([x,x],1); d=(st*32767).astype('<i2')
    f=wave.open(name,'wb'); f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes(d.tobytes()); f.close()
w('sfx.wav',sfx*.9); w('pad.wav',pad*.35)
