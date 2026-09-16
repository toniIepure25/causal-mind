import sys, time, os
sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
os.environ["HF_HOME"] = "/home/jovyan/work/.hf-home"
os.environ["TRANSFORMERS_CACHE"] = "/home/jovyan/work/.hf-home"
import numpy as np
from causal_mind.data.osf_a56rm import all_subjects, load_thought_events
from causal_mind.thought.encode import MiniLMEncoder, encode_subject_cached

t0 = time.time()
enc = MiniLMEncoder()
subs = all_subjects()
done = 0
for s in subs:
    evs = load_thought_events(s)
    texts = [e["transcript"] for e in evs]
    arr = encode_subject_cached(enc, s, texts)
    done += 1
    print(f"[{done}/{len(subs)}] {s}: {arr.shape} {time.time()-t0:.0f}s", flush=True)
print("ALL_DONE", done, f"{time.time()-t0:.0f}s", flush=True)
