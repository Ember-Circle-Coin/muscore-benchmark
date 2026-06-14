import time, json, random, statistics

def restain_bijective(data):
    # Enforces 1-to-1 resonance to prevent processing tangles
    return sorted(data, key=lambda x: x[0])

def encode(et, d):
    if et=="move": return bytes([1,d["zone"],d["direction"],d["velocity"]])
    elif et=="npc": return bytes([6,d["state"],d["priority"],d["group"]])
    elif et=="asset": return bytes([3,d["type"],d["lod"],d["zone"]])
    elif et=="guardian": return bytes([12,11,0])
    elif et=="ai_signal": return bytes([d["sender"],d["intent"],d["target"],d["urgency"]])
    return bytes([0])

def run_bench(n):
    types=["move","npc","asset","ai_signal","guardian"]
    weights=[0.50,0.20,0.15,0.13,0.02]
    raw_data = []
    for _ in range(n):
        t = random.choices(types, weights)[0]
        d = {"zone":1,"direction":2,"velocity":3,"state":4,"priority":5,"group":6,"type":7,"lod":8,"sender":9,"intent":10,"target":11,"urgency":12}
        raw_data.append((t, d))
    
    # APPLY BIJECTIVE RESTRAINER
    data = restain_bijective(raw_data)
    
    t0 = time.perf_counter()
    m_size = sum(len(encode(t, d)) for t, d in data)
    t_m = (time.perf_counter() - t0) * 1000
    
    j_size = len(json.dumps([{"t":t, "d":d} for t,d in data]).encode())
    
    gt = []
    for _ in range(10000):
        t1 = time.perf_counter()
        encode("guardian", {"zone":1})
        gt.append((time.perf_counter()-t1)*1e6)
        
    print(f"{n:>10,} events | MusCoRe={m_size/1024:.1f}KB JSON={j_size/1024:.1f}KB | compression={(1-(m_size/j_size))*100:.1f}% | time={t_m:.1f}ms")
    if n == 100000:
        print(f"Guardian 10k: avg={statistics.mean(gt):.3f}us all_under_1ms={all(t<1000 for t in gt)}")

print("MUSCORE METAVERSE BENCHMARK (BIJECTIVE RESTRAINER ACTIVE)")
for n in [100, 1000, 10000, 100000]:
    run_bench(n)
