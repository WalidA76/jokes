import json
# Scene boundaries snapped to the pauses detected in the voice track (47.6s).
OLD = [0.0, 4.2, 10.5, 22.3, 36.1, 41.8, 48.0]
# new boundaries on the silence-trimmed voice (42.0s), aligned to the transcript phrases
S = [0.0, 3.6, 8.4, 18.3, 27.0, 33.8, 42.0]
F = [1.0]+[(S[i+1]-S[i])/(OLD[i+1]-OLD[i]) for i in range(1,6)]  # per-scene time stretch
K = dict(
 s1_a=0.1, s1_b=1.4, s1_title=2.5,
 s2_bulb=0.2, s2_morph=1.1, s2_nodes=[1.8,2.7,3.6,4.5], s2_head=5.0,
 s3_card=0.2, s3_type=[0.8,5.2], s3_proc=[5.3,6.0], s3_cards=[6.0,6.55,7.1,7.65,8.2], s3_tag=9.2,
 s4_card=3.6, s4_bracket=4.6, s4_type=[6.4,8.6], s4_send=8.9, s4_shift=[9.1,10.3], s4_text=10.6,
 s5_text=[0.4,1.5,2.6], s5_morph=3.1, s5_swap=4.2, s5_play=4.9,
 s6_words=[0.3,1.8], s6_chips=[0.9,2.05,3.2], s6_cta=4.3, s6_sig=5.0,
)
PROMPT = "اكتب وصفًا احترافيًا لأنيميشن تعليمي، وحدد المشاهد والحركات والألوان والمؤثرات الصوتية."
CMD = "/changeyellowto teal"
T = dict(total=S[-1], F=F, s=S, K=K, prompt=PROMPT, cmd=CMD)
json.dump(T, open('timing.json','w'))
open('timing.js','w').write('window.TIMING='+json.dumps(T, ensure_ascii=False)+';')
