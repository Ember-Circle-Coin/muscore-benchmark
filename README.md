# MusCoRe Benchmark Suite
**Built in Cape Town, South Africa.**

## What MusCoRe is
A binary serialisation standard using bijective bit-packing to encode structured event data into 16-bit integers. Each event (zone, direction, velocity) is packed into 2 bytes instead of verbose JSON.

## What the benchmarks confirm
- **97.8%** compression on standard event data
- Up to **1,294× faster** than equivalent JSON (1.5 ms for 1M events in throttle test)
- Significant theoretical GPU/thermal savings in simulation models

## What the thermal / dual-particle scripts model
Simulation only — not measured on physical VR hardware.

## What needs independent lab testing
- Real VR headset thermal measurements
- Integration with actual rendering pipelines
- Physical network transmission benchmarks

## How to run
```bash
pip install numpy
python benchmark_muscore.py
python muscore_throttle_test.py
python muscore_phase_cooling.py
python muscore_dual_particle.py
