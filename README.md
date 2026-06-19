# MusCoRe Benchmark Suite

**Built in Cape Town, South Africa.**

## What MusCoRe is

A binary serialisation standard using bijective bit-packing to encode structured event data into fixed-width byte sequences. Each event (zone, direction, velocity, etc.) is packed into 3-4 bytes based on a fixed per-type schema, instead of a self-describing format like JSON.

## What the benchmark confirms

Measured by binary_benchmark.py, against a fair baseline (JSON includes only the fields each event type actually uses, no padding):

| Comparison               | Result                                  |
|---------------------------|------------------------------------------|
| vs raw JSON                | ~92% smaller                            |
| vs gzip-compressed JSON     | 45-61% smaller (gap narrows at scale)   |
| vs MessagePack              | ~88-89% smaller                         |
| vs CBOR                     | ~89% smaller                            |

The advantage over MessagePack/CBOR comes from MusCoRe using a fixed, known schema, so field names are never transmitted — the same category of advantage Protocol Buffers has over JSON, not raw byte-packing cleverness.

## How to run

    pip install msgpack cbor2
    python3 binary_benchmark.py

## Not yet benchmarked

- Encode/decode throughput (no speed claims until this is actually measured)
- Real-world, non-uniform telemetry data (current data is synthetic, weighted-random)
- Physical network transmission, VR hardware thermal effects
