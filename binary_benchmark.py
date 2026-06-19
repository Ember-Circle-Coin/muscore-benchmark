import time, json, gzip, random
import msgpack
import cbor2

FIELD_SETS = {
    "move":      lambda: {"zone": random.randint(0,255), "direction": random.randint(0,255), "velocity": random.randint(0,255)},
    "npc":       lambda: {"state": random.randint(0,255), "priority": random.randint(0,255), "group": random.randint(0,255)},
    "asset":     lambda: {"type": random.randint(0,255), "lod": random.randint(0,255), "zone": random.randint(0,255)},
    "ai_signal": lambda: {"sender": random.randint(0,255), "intent": random.randint(0,255), "target": random.randint(0,255), "urgency": random.randint(0,255)},
    "guardian":  lambda: {},
}

def encode(et, d):
    if et == "move":       return bytes([1, d["zone"], d["direction"], d["velocity"]])
    elif et == "npc":       return bytes([6, d["state"], d["priority"], d["group"]])
    elif et == "asset":     return bytes([3, d["type"], d["lod"], d["zone"]])
    elif et == "guardian":  return bytes([12, 11, 0])
    elif et == "ai_signal": return bytes([d["sender"], d["intent"], d["target"], d["urgency"]])
    return bytes([0])

def run_bench(n):
    types = ["move","npc","asset","ai_signal","guardian"]
    weights = [0.50,0.20,0.15,0.13,0.02]
    events = []
    for _ in range(n):
        t = random.choices(types, weights)[0]
        events.append((t, FIELD_SETS[t]()))

    payload = [{"t": t, **d} for t, d in events]

    m_bytes  = b"".join(encode(t, d) for t, d in events)
    j_bytes  = json.dumps(payload, separators=(",",":")).encode()
    gz_bytes = gzip.compress(j_bytes, compresslevel=9)
    mp_bytes = msgpack.packb(payload, use_bin_type=True)
    cb_bytes = cbor2.dumps(payload)

    sizes = {
        "MusCoRe":      len(m_bytes),
        "JSON":         len(j_bytes),
        "gzip(JSON)":   len(gz_bytes),
        "MessagePack":  len(mp_bytes),
        "CBOR":         len(cb_bytes),
    }

    print(f"--- {n:,} events ---")
    for name, size in sizes.items():
        print(f"  {name:<14} {size/1024:8.1f} KB")
    print(f"  MusCoRe vs MessagePack: {(1 - sizes['MusCoRe']/sizes['MessagePack'])*100:5.1f}% smaller")
    print(f"  MusCoRe vs CBOR:        {(1 - sizes['MusCoRe']/sizes['CBOR'])*100:5.1f}% smaller")
    print(f"  MusCoRe vs gzip(JSON):  {(1 - sizes['MusCoRe']/sizes['gzip(JSON)'])*100:5.1f}% smaller")
    print()

print("MUSCORE vs REAL BINARY SERIALIZATION FORMATS")
for n in [100, 1000, 10000, 100000]:
    run_bench(n)
