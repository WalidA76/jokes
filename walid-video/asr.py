import sherpa_onnx, wave, numpy as np, json, sys
d='/tmp/sh/sherpa-onnx-whisper-small/'
import glob
enc=glob.glob(d+'*encoder*.onnx'); dec=glob.glob(d+'*decoder*.onnx'); enc=[e for e in enc if 'int8' in e] or enc; dec=[e for e in dec if 'int8' in e] or dec
r=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=enc[0],decoder=dec[0],tokens=glob.glob(d+'*tokens.txt')[0],language='ar',task='transcribe',num_threads=4)
w=wave.open('voice16k.wav'); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs=[(0.74,1.88),(2.34,3.29),(4.21,7.13),(7.74,9.54),(10.48,13.62),(14.08,18.68),(19.32,20.56),(21.21,22.27),(22.76,25.92),(26.49,36.10),(36.71,39.08),(39.51,47.6)]
out=[]
for a,b in segs:
    s=r.create_stream(); s.accept_waveform(16000,x[int(max(0,a-.15)*16000):int((b+.15)*16000)]); r.decode_stream(s)
    out.append((a,b,s.result.text)); print(f'{a:6.2f}-{b:6.2f}  {s.result.text}')
json.dump(out,open('/home/user/jokes/walid-video/transcript_small.json','w'),ensure_ascii=False,indent=1)
