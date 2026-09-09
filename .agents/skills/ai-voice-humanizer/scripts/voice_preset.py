#!/usr/bin/env python3
"""
Voice Preset Processor - apply voice processing chains using FFmpeg.

Processing chain adapted from Isaac's (ISAACVERSE) Premiere presets.

Rebuilds 14 presets as FFmpeg filter chains, so no DAW or NLE is required.
Works on any platform with FFmpeg installed.

Usage:
    python3 voice_preset.py input.wav voice-enhancer
    python3 voice_preset.py input.wav movie-trailer -o output.wav
    python3 voice_preset.py --list
    python3 voice_preset.py input.wav voice-enhancer --dry-run
"""

import argparse
import subprocess
import sys
import shutil
from pathlib import Path


def _pitch_shift(semitones):
    """Build FFmpeg filter chain for pitch shifting without librubberband.

    Uses asetrate to change pitch (which also changes speed),
    then aresample to restore original speed/sample rate.
    """
    factor = 2 ** (semitones / 12)
    return f"asetrate=44100*{factor:.6f},aresample=44100"


PRESETS = {
    # === USEFUL PRESETS ===
    "voice-enhancer": {
        "description": "Radio-quality AI voiceover processing (compression + dynamics + EQ)",
        "category": "useful",
        "filters": [
            # Stage 1: Heavy compression (-10dB threshold, 12:1 ratio, near-instant attack)
            "acompressor=threshold=0.316:ratio=12:attack=0.01:release=20:makeup=1",
            # Stage 2: Noise gate (attenuate signals below -38dB)
            "agate=threshold=0.013:ratio=4:attack=2:release=50",
            # Stage 3: EQ chain
            "highpass=f=34:poles=2",                                # HP at 34 Hz, 12dB/oct
            "equalizer=f=75:width_type=h:width=110:g=1.1",         # +1.1dB warmth at 75Hz
            "equalizer=f=246:width_type=h:width=315:g=-0.9",       # -0.9dB mud cut at 246Hz
            "treble=g=4:f=15000",                                  # +4dB high shelf at 15kHz (air)
        ],
    },
    "movie-trailer": {
        "description": "Deep, full, broadcast voice (limiter + amp + comp + denoise + deesser + EQ)",
        "category": "useful",
        "filters": [
            # Stage 1: Hard limiter at -0.3dB
            "alimiter=limit=0.97:attack=5:release=50",
            # Stage 2: +6dB amplify
            "volume=6dB",
            # Stage 3: Heavy compression
            "acompressor=threshold=0.316:ratio=12:attack=0.01:release=20:makeup=1",
            # Stage 4: De-noise (high-pass removes hum, gate removes low noise)
            "agate=threshold=0.02:ratio=3:attack=1:release=50",
            # Stage 5: De-esser (cut sibilance around 7.8kHz)
            "equalizer=f=7826:width_type=h:width=2000:g=-3",
            # Stage 6: EQ #1 - main voice shaping
            "highpass=f=43:poles=2",                                # HP at 43 Hz
            "bass=g=2.6:f=68",                                     # +2.6dB low shelf at 68Hz
            "equalizer=f=240:width_type=h:width=410:g=-1.3",       # -1.3dB at 240Hz
            "treble=g=5.3:f=10178",                                # +5.3dB high shelf at 10kHz
            # Stage 7: EQ #2 - tone refinement
            "equalizer=f=646:width_type=h:width=400:g=-3.8",       # -3.8dB boxiness cut
            "treble=g=-1.4:f=8571",                                # -1.4dB tame harshness
        ],
    },
    "deeper-voice": {
        "description": "Pitch shift down ~5 semitones",
        "category": "useful",
        "filters": [
            _pitch_shift(-5),
        ],
    },
    "echo": {
        "description": "Spacious echoey room (studio reverb, 60/40 dry/wet)",
        "category": "useful",
        "filters": [
            "aecho=0.8:0.6:60|120|180:0.4|0.3|0.2",
        ],
    },
    "muffled": {
        "description": "Through-the-wall effect (-17.5dB high shelf at 7kHz)",
        "category": "useful",
        "filters": [
            "treble=g=-17.5:f=7054",
        ],
    },
    "noise-remover": {
        "description": "Conservative noise reduction via gating",
        "category": "useful",
        "filters": [
            "agate=threshold=0.01:ratio=3:attack=5:release=100",
            "highpass=f=80:poles=1",
        ],
    },
    "phone-call": {
        "description": "Classic telephone bandpass filter",
        "category": "useful",
        "filters": [
            "bass=g=-18.3:f=119",                                  # -18.3dB low shelf at 119Hz
            "equalizer=f=1638:width_type=h:width=3968:g=4.6",      # +4.6dB at 1638Hz
            "highpass=f=300:poles=2",                               # Extra HP to really kill bass
            "lowpass=f=3400:poles=2",                               # LP to kill highs (telephone BW)
        ],
    },

    # === FUN PRESETS ===
    "90s": {
        "description": "Lo-fi vintage radio/cassette (distortion + bandpass)",
        "category": "fun",
        "filters": [
            "volume=-6dB",                                         # -6dB reduction
            "highpass=f=110:poles=2",                               # Bandpass lower edge
            "lowpass=f=2500:poles=2",                               # Bandpass upper edge
            "acrusher=bits=8:mix=0.3:samples=1:mode=log:dc=1",     # Warm lo-fi distortion
        ],
    },
    "alien-voice": {
        "description": "Metallic otherworldly (100% wet flanger, 68% feedback)",
        "category": "fun",
        "filters": [
            "flanger=delay=3.7:depth=2.9:regen=68:width=50:speed=0.5:shape=sinusoidal:interp=quadratic",
        ],
    },
    "chipmunk": {
        "description": "Pitch shift up ~5 semitones",
        "category": "fun",
        "filters": [
            _pitch_shift(5),
        ],
    },
    "inner-monologue": {
        "description": "Inside-your-head reverb (50/50 dry/wet, strong reflections)",
        "category": "fun",
        "filters": [
            "aecho=0.8:0.5:40|80|120|160:0.5|0.4|0.3|0.2",
        ],
    },
    "pilot-voice": {
        "description": "Radio intercom (isolate 972-2552Hz, compress hard)",
        "category": "fun",
        "filters": [
            "highpass=f=972:poles=2",
            "lowpass=f=2552:poles=2",
            "acompressor=threshold=0.032:ratio=4:attack=5:release=50:makeup=6",
            "volume=6dB",
        ],
    },
    "robot-voice": {
        "description": "Metallic + deep (flanger + pitch down 6 semitones)",
        "category": "fun",
        "filters": [
            "flanger=delay=3.6:depth=3.6:regen=57:width=50:speed=0.1:shape=sinusoidal:interp=quadratic",
            _pitch_shift(-6),
        ],
    },
    "villain-voice": {
        "description": "Deep menacing (subtle flanger + pitch down 9 semitones)",
        "category": "fun",
        "filters": [
            "flanger=delay=0.5:depth=1.1:regen=0:width=50:speed=0.1:shape=sinusoidal",
            _pitch_shift(-9),
        ],
    },
}


def list_presets():
    print("\n  USEFUL PRESETS (for production):\n")
    for name, info in PRESETS.items():
        if info["category"] == "useful":
            print(f"    {name:<20} {info['description']}")
    print("\n  FUN PRESETS (for creative effects):\n")
    for name, info in PRESETS.items():
        if info["category"] == "fun":
            print(f"    {name:<20} {info['description']}")
    print()


def build_ffmpeg_command(input_path, output_path, preset_name, dry_run=False):
    if preset_name not in PRESETS:
        print(f"Error: Unknown preset '{preset_name}'")
        print(f"Available presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    preset = PRESETS[preset_name]
    filter_chain = ",".join(preset["filters"])

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", filter_chain,
        "-ar", "44100",
        str(output_path),
    ]

    if dry_run:
        print(f"\nPreset: {preset_name}")
        print(f"Description: {preset['description']}")
        print(f"\nFFmpeg command:\n")
        print("  " + " \\\n    ".join(cmd))
        print(f"\nFilter chain breakdown:")
        for i, f in enumerate(preset["filters"], 1):
            print(f"  {i}. {f}")
        return

    print(f"Applying '{preset_name}': {preset['description']}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: FFmpeg failed\n{result.stderr}")
        sys.exit(1)

    print(f"Done: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Apply voice processing presets to audio files using FFmpeg. "
                    "Processing chain adapted from Isaac's (ISAACVERSE) Premiere presets."
    )
    parser.add_argument("input", nargs="?", help="Input audio file")
    parser.add_argument("preset", nargs="?", help="Preset name")
    parser.add_argument("-o", "--output", help="Output file (default: input_preset.wav)")
    parser.add_argument("--list", action="store_true", help="List available presets")
    parser.add_argument("--dry-run", action="store_true", help="Show FFmpeg command without running")

    args = parser.parse_args()

    if args.list:
        list_presets()
        return

    if not args.input or not args.preset:
        parser.print_help()
        sys.exit(1)

    if not shutil.which("ffmpeg"):
        print("Error: FFmpeg not found. Install it from https://ffmpeg.org/download.html "
              "(macOS: brew install ffmpeg)")
        sys.exit(1)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_stem(f"{input_path.stem}_{args.preset}")

    build_ffmpeg_command(input_path, output_path, args.preset, args.dry_run)


if __name__ == "__main__":
    main()
