"""Usage: python3 transcribe.py voice.mp3 [language=ar] -> prints/saves phrase-level text with timestamps.
Phrases are split at silences (ffmpeg silencedetect), then each is decoded with Whisper small."""
import sys, os, re, subprocess, json, wave, glob, numpy as np, sherpa_onnx
src=sys.argv[1]; lang=sys.argv[2] if len(sys.argv)>2 else 'ar'
d=os.path.expanduser('~/asr/sherpa-onnx-whisper-small/')
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',src,'-ac','1','-ar','16000','/tmp/v16k.wav'],check=True)
log=subprocess.run(['ffmpeg','-i',src,'-af','silencedetect=n=-32dB:d=0.35','-f','null','-'],capture_output=True,text=True).stderr
dur=float(re.search(r'Duration: (\d+):(\d+):([\d.]+)',log).expand(r'\1')) *3600+0
m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',log); dur=int(m[1])*3600+int(m[2])*60+float(m[3])
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
segs=[]; cur=0.0
for s,e in zip(st,en):
    if s-cur>0.2: segs.append((cur,s))
    cur=e
if dur-cur>0.2: segs.append((cur,dur))
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+'small-encoder.int8.onnx',decoder=d+'small-decoder.int8.onnx',tokens=d+'small-tokens.txt',language=lang,task='transcribe',num_threads=4)
w=wave.open('/tmp/v16k.wav'); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
out=[]
for a,b in segs:
    s=r.create_stream(); s.accept_waveform(16000,x[int(max(0,a-.15)*16000):int((b+.15)*16000)]); r.decode_stream(s)
    out.append([round(a,2),round(b,2),s.result.text]); print(f'{a:6.2f}-{b:6.2f}  {s.result.text}')
json.dump(out,open(os.path.splitext(src)[0]+'.transcript.json','w'),ensure_ascii=False,indent=1)
