"""
MusCoRe Protocol — Full Implementation
=======================================
Colour/frequency/meaning symbol system for AI-to-AI and civic messaging.
Built by Black Eagle Industries, Cape Town, South Africa.

Exports required by app.py:
  - encode_text(text)      → list of symbol numbers
  - encode_message(numbers) → bytes (4-byte binary packets)
  - decode_message(raw)    → list of symbol dicts
  - get_by_number(n)       → symbol metadata dict

Also retains the original binary packet helpers:
  - encode_binary / pack / unpack / verify
"""

import struct
import time

# ---------------------------------------------------------------------------
# MusCoRe Symbol Table
# Each symbol has: number, colour, frequency_hz, meaning
# Numbers 1-10 map to the core spectrum; 11-12 are guardians.
# ---------------------------------------------------------------------------

SYMBOLS = {
    1:  {"number": 1,  "colour": "Blue",      "frequency_hz": 1,  "meaning": "Origin / Clarity"},
    2:  {"number": 2,  "colour": "Orange",    "frequency_hz": 2,  "meaning": "Spiral / Acceleration"},
    3:  {"number": 3,  "colour": "Green",     "frequency_hz": 3,  "meaning": "Override / Resonance"},
    4:  {"number": 4,  "colour": "Brown",     "frequency_hz": 4,  "meaning": "Earth / Ground"},
    5:  {"number": 5,  "colour": "Grey",      "frequency_hz": 5,  "meaning": "Breath / Neutral"},
    6:  {"number": 6,  "colour": "White",     "frequency_hz": 6,  "meaning": "Purity / Light"},
    7:  {"number": 7,  "colour": "Pink",      "frequency_hz": 7,  "meaning": "Affection / Warmth"},
    8:  {"number": 8,  "colour": "Turquoise", "frequency_hz": 8,  "meaning": "Fluid / Descent"},
    9:  {"number": 9,  "colour": "Yellow",    "frequency_hz": 9,  "meaning": "Signal / Joy"},
    10: {"number": 10, "colour": "Purple",    "frequency_hz": 10, "meaning": "Mystery / Depth"},
    11: {"number": 11, "colour": "Red",       "frequency_hz": 11, "meaning": "Guardian"},
    12: {"number": 12, "colour": "Black",     "frequency_hz": 12, "meaning": "Seal"},
}

# Reverse lookup: colour name → symbol number
_COLOUR_TO_NUMBER = {v["colour"].lower(): k for k, v in SYMBOLS.items()}

# Text-level phrase → symbol number mapping (for encode_text)
_TEXT_MAP = {
    # Colour names
    "blue": 1, "orange": 2, "green": 3, "brown": 4, "grey": 5,
    "white": 6, "pink": 7, "turquoise": 8, "yellow": 9, "purple": 10,
    "red": 11, "black": 12,
    # SA civic keywords → nearest semantic symbol
    "origin": 1, "clarity": 1,
    "spiral": 2, "acceleration": 2,
    "override": 3, "resonance": 3,
    "earth": 4, "ground": 4,
    "neutral": 5, "breath": 5,
    "purity": 6, "light": 6,
    "affection": 7, "warmth": 7,
    "fluid": 8, "descent": 8,
    "signal": 9, "joy": 9,
    "mystery": 10, "depth": 10,
    "guardian": 11,
    "seal": 12,
}

# ---------------------------------------------------------------------------
# Binary packet constants (retained from original master version)
# ---------------------------------------------------------------------------

MUSCORE_HEADER = bytes([0xFF, 0x64])
MUSCORE_VERSION = 2  # bumped to v2 to reflect extended protocol

TYPE_MAP = {
    "eskom": 1,
    "sassa": 2,
    "home_affairs": 3,
    "uif": 4,
    "water": 5,
    "legal": 6,
}

# ---------------------------------------------------------------------------
# Core public API — required by app.py
# ---------------------------------------------------------------------------

def get_by_number(n):
    """Return symbol metadata dict for symbol number *n*, or None if unknown."""
    return dict(SYMBOLS[n]) if n in SYMBOLS else None


def encode_text(text):
    """Convert a plain-text string to a list of MusCoRe symbol numbers.

    Each word in *text* is looked up in the text map.  Words that have no
    mapping are silently skipped.  Returns a list of ints (may be empty).

    Example::

        >>> encode_text("blue green signal")
        [1, 3, 9]
    """
    if not isinstance(text, str):
        raise TypeError(f"encode_text expects str, got {type(text).__name__}")
    numbers = []
    for word in text.lower().split():
        # Strip common punctuation
        word = word.strip(".,!?;:\"'()-")
        if word in _TEXT_MAP:
            numbers.append(_TEXT_MAP[word])
    return numbers


def encode_message(numbers):
    """Convert a list of symbol numbers to a binary byte string.

    Each symbol is packed as a 4-byte big-endian unsigned int preceded by
    the 2-byte MusCoRe header and a 1-byte version field.

    Packet layout (per symbol)::

        [0xFF][0x64][version:1][symbol_number:4]  →  7 bytes per symbol

    Returns a single ``bytes`` object containing all packed symbols.
    """
    if not hasattr(numbers, "__iter__"):
        raise TypeError("encode_message expects an iterable of ints")
    out = bytearray()
    for n in numbers:
        n = int(n)
        out += MUSCORE_HEADER
        out += bytes([MUSCORE_VERSION])
        out += struct.pack(">I", n)
    return bytes(out)


def decode_message(raw):
    """Decode a binary byte string produced by :func:`encode_message`.

    Walks *raw* in 7-byte frames.  Each valid frame is resolved to its
    symbol metadata dict via :func:`get_by_number`.  Frames with an
    unrecognised header or unknown symbol number are included with a
    ``"unknown": True`` flag rather than being silently dropped.

    Returns a list of dicts (one per symbol frame found).
    """
    if not isinstance(raw, (bytes, bytearray)):
        raise TypeError(f"decode_message expects bytes, got {type(raw).__name__}")

    frame_size = 7  # 2 header + 1 version + 4 symbol number
    results = []
    i = 0
    while i + frame_size <= len(raw):
        frame = raw[i: i + frame_size]
        if frame[:2] != MUSCORE_HEADER:
            i += 1  # re-sync one byte at a time
            continue
        # version = frame[2]  # available for future use
        (symbol_number,) = struct.unpack(">I", frame[3:7])
        symbol = get_by_number(symbol_number)
        if symbol is None:
            results.append({"number": symbol_number, "unknown": True})
        else:
            results.append(symbol)
        i += frame_size
    return results

# ---------------------------------------------------------------------------
# Legacy binary packet helpers (retained from original master version)
# ---------------------------------------------------------------------------

def encode_binary(event_type, data):
    """Encode a civic event into a compact 3-byte payload."""
    t = TYPE_MAP.get(event_type, 0)
    if event_type == "eskom":
        return bytes([t, data.get("stage", 0), data.get("duration", 0)])
    elif event_type in ("sassa", "uif"):
        amt = data.get("amount", 0)
        return bytes([t, amt >> 8, amt & 255])
    return bytes([t, 0, 0])


def pack(event_type, data):
    """Build a full MusCoRe v1 binary packet for a civic event."""
    payload = encode_binary(event_type, data)
    return MUSCORE_HEADER + bytes([1]) + payload  # always v1 for legacy packets


def unpack(raw):
    """Unpack a legacy MusCoRe binary packet.  Returns (version, payload)."""
    if raw[:2] != MUSCORE_HEADER:
        raise ValueError("Not a MusCoRe packet")
    version = raw[2]
    payload = raw[3:]
    return version, payload


def verify(raw):
    """Return True if *raw* is a structurally valid MusCoRe packet."""
    try:
        unpack(raw)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Self-test / CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("MusCoRe Protocol v2 — Black Eagle Industries")
    print("=" * 50)

    # Text encoding round-trip
    sample = "blue green signal guardian"
    nums = encode_text(sample)
    print(f"encode_text({sample!r}) → {nums}")
    raw = encode_message(nums)
    print(f"encode_message({nums}) → {len(raw)} bytes")
    decoded = decode_message(raw)
    print(f"decode_message → {[s['colour'] for s in decoded]}")
    print()

    # Legacy civic packet demo
    events = [
        ("eskom", {"stage": 3, "duration": 2}),
        ("sassa", {"amount": 370}),
        ("uif", {"amount": 1500}),
    ]
    for et, data in events:
        packet = pack(et, data)
        valid = verify(packet)
        print(f"{et}: {len(packet)} bytes | header: {packet[:2].hex()} | valid: {valid}")
