# Premiere Pro Voice Presets - Complete Parameter Extraction

**Processing chain adapted from Isaac's (ISAACVERSE) Premiere presets.**

Source file: `isaac+voice+presets.prfpset` (2.1MB XML, Premiere Pro v3 preset format).
Creator: Isaac (ISAACVERSE). This document records the measured parameter values so the
same processing can be rebuilt in FFmpeg, SoX, or any other DAW.

## File Structure

```
Root > Presets > ISAACVERSE > Isaac voice presets
  ├── fun/ (8 presets)
  │   ├── 90s
  │   ├── alien voice
  │   ├── chipmunk
  │   ├── inner monologue
  │   ├── pilot voice
  │   ├── robot voice
  │   ├── torture viewers
  │   └── villain voice
  └── useful/ (7 presets)
      ├── deeper voice
      ├── echo (echoey room)
      ├── movie trailer voice
      ├── muffled voice
      ├── noise remover
      ├── phone call
      └── voice enhancer
```

## Parameter Normalization Notes

Premiere Pro stores all audio effect parameters as normalized 0-1 floating point values. Key conversions:

| Parameter Type | Normalized Value | Real-World Value |
|---|---|---|
| EQ Frequency | `val * 20000` | Hz (linear mapping, 0-20kHz range) |
| EQ Gain | `(val - 0.5) * 40` | dB (0.5 = 0 dB, range approx -20 to +20 dB) |
| Compressor Threshold | `(val - 1.0) * 60` | dB (1.0 = 0 dB, 0.0 = -60 dB) |
| Compressor Ratio | `1 + val * 29` | ratio:1 (0 = 1:1, 1 = 30:1) |
| Pitch Shift | `(val * 24) - 12` | semitones (-12 to +12) |
| Amplify Gain | `(val - 0.6667) * 288` | dB (0.6667 = 0 dB) |
| DeNoise Amount | `val * 100` | percent |
| HP/LP Slope 0.4 | - | ~12 dB/oct (2nd order) |
| Shelf Filter Order 0 | - | 1st order (6 dB/oct) |
| Shelf Filter Order 1 | - | 2nd order (12 dB/oct) |

**Important**: Each preset has 3 effect "slots" per effect type (mono, stereo, 5.1 surround). Only slot 1 contains the actual custom settings. Slots 2 and 3 are typically factory defaults. In this document, only slot 1 (the active/customized slot) is detailed for each effect.

---

# USEFUL PRESETS

---

## 1. Voice Enhancer (MOST IMPORTANT FOR AI VOICEOVER)

**Effect Chain**: Single-band Compressor -> Dynamics Processing -> Parametric Equalizer

### Effect 1: Single-band Compressor

| Parameter | Normalized | Real-World (approx) |
|---|---|---|
| Gain | 0.500 | 0 dB (output gain) |
| Threshold | 0.833 | **-10 dB** |
| Ratio | 0.379 | **~12:1** |
| Attack | 0.000 | Fastest (0 ms) |
| Release | 0.020 | Fast (~20 ms) |
| Auto Makeup Gain | 0 (off) | - |

**Interpretation**: Aggressive compression (-10 dB threshold, 12:1 ratio) with instant attack. This catches all peaks and evens out dynamics significantly. The fast attack with a quick release keeps the voice tight and present.

### Effect 2: Dynamics Processing

| Parameter | Normalized | Real-World (approx) |
|---|---|---|
| Level Detector - Attack Time | 0.002 | ~2 ms |
| Level Detector - Release Time | 0.050 | ~50 ms |
| Gain Processor - Attack Time | 0.048 | ~48 ms |
| Gain Processor - Release Time | 0.050 | ~50 ms |
| Lookahead Time | 0.006 | ~6 ms |
| Input Gain | 0.500 | 0 dB |
| Output Gain | 0.500 | 0 dB |
| Low Cutoff | 0.000 | 0 Hz (full range) |
| High Cutoff | 1.000 | 20 kHz (full range) |
| Link Channels | 0 (off) | Independent channels |
| Peak/RMS | 1.0 | RMS detection |
| Spline Curves | 1.0 | Smooth curves (on) |
| Make-Up Gain | 0 (off) | - |

**Transfer Curve (5 points)**:

| Point | Location (Input dB norm) | Value (Output dB norm) |
|---|---|---|
| 1 | 0.000 (silence) | 0.000 (silence) |
| 2 | 0.370 (~-37.8 dB) | 0.131 (~-52.1 dB) |
| 3 | 0.516 (~-29.0 dB) | 0.503 (~-29.8 dB) |
| 4 | 0.716 (~-17.0 dB) | 0.775 (~-13.5 dB) |
| 5 | 1.000 (0 dB) | 1.000 (0 dB) |

**Interpretation**: Custom dynamics curve that acts as an expander for very quiet signals (reducing noise floor) while being nearly unity through the mid-range and adding slight expansion at louder levels. The curve:
- **Below -38 dB**: Quiet signals get pushed down further (noise gating / expansion)
- **-38 dB to -17 dB**: Near-unity, natural dynamics preserved
- **-17 dB to 0 dB**: Slight upward expansion (louder parts get boosted slightly)

This creates a subtle "noise gate + presence boost" combined effect.

### Effect 3: Parametric Equalizer

| Parameter | Normalized | Approx Hz/dB |
|---|---|---|
| **High-Pass Filter** | | |
| Enabled | 1 (on) | |
| Cutoff Frequency | 0.001695 | **~34 Hz** |
| Slope | 0.400 | ~12 dB/oct |
| **Low Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.000834 | ~17 Hz |
| Gain | 0.500 | 0 dB (flat) |
| Order | 0 | 1st order (6 dB/oct) |
| **Band 1** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.001251 | **~25 Hz** |
| Gain | 0.500 | 0 dB (flat/inactive) |
| Q / Width | 0.000200 | Narrow |
| Bandwidth | 0.002500 | |
| **Band 2** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.003749 | **~75 Hz** |
| Gain | 0.526316 | **+1.1 dB** |
| Q / Width | 0.000200 | |
| Bandwidth | 0.005495 | ~110 Hz wide |
| **Band 3** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.012291 | **~246 Hz** |
| Gain | 0.476974 | **-0.9 dB** |
| Q / Width | 0.000200 | |
| Bandwidth | 0.015736 | ~315 Hz wide |
| **Band 4** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.132611 | **~2,652 Hz** |
| Gain | 0.500 | 0 dB (flat) |
| Q / Width | 0.000200 | |
| Bandwidth | 0.160001 | |
| **Band 5** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.532944 | **~10,659 Hz** |
| Gain | 0.500 | 0 dB (flat) |
| Q / Width | 0.000200 | |
| Bandwidth | 0.640000 | |
| **High Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.749792 | **~14,996 Hz** |
| Gain | 0.600000 | **+4.0 dB** |
| Order | 0 | 1st order (6 dB/oct) |
| **Low-Pass Filter** | | |
| Enabled | 0 (off) | |
| **Other** | | |
| Master Gain | 0.666667 | 0 dB |
| Constant Q | 1 (on) | |
| Ultra-Quiet Mode | 0 (off) | |

**EQ Summary for Voice Enhancer**:
- **High-Pass at ~34 Hz** (12 dB/oct) - removes sub-bass rumble
- **+1.1 dB at ~75 Hz** - subtle low-end warmth boost
- **-0.9 dB at ~246 Hz** - subtle cut in the "mud" frequency range
- **+4.0 dB high shelf starting at ~15 kHz** - air/presence boost in the top end

**Overall Voice Enhancer Philosophy**: Compress hard to even out dynamics -> Custom dynamics curve to gate noise and add presence -> EQ to clean up low end, add warmth, cut mud, and boost air.

---

## 2. Movie Trailer Voice

**Effect Chain**: Hard Limiter -> Amplify -> Single-band Compressor -> DeNoise -> DeEsser -> Parametric Equalizer (x6)

### Effect 1: Hard Limiter

| Parameter | Normalized | Approx Real Value |
|---|---|---|
| Maximum Amplitude | 0.970 | **-0.3 dB** ceiling |
| Input Boost | 0.660 | ~0 dB (near default) |
| Look-Ahead Time | 0.133 | ~133 ms |
| Release Time | 0.375 | |
| Link Channels | 1 (on) | |
| Decay to Ceiling | 1 (on) | |
| Limit True Peak | 0 (off) | |

### Effect 2: Amplify

| Parameter | Normalized | Approx dB |
|---|---|---|
| Left | 0.6875 | **+6 dB** |
| Right | 0.6875 | **+6 dB** |
| Link Sliders | 1 (on) | |
| Factory Preset | "+3dB Boost" | (label says +3dB but actual value is +6dB) |

### Effect 3: Single-band Compressor

| Parameter | Normalized | Approx Real Value |
|---|---|---|
| Gain | 0.500 | 0 dB |
| Threshold | 0.833 | **-10 dB** |
| Ratio | 0.379 | **~12:1** |
| Attack | 0.000 | 0 ms (instant) |
| Release | 0.020 | ~20 ms |
| Auto Makeup Gain | 0 (off) | |

### Effect 4: DeNoise

| Parameter | Normalized | Approx Value |
|---|---|---|
| Amount | 0.144 | **~14.4%** |
| Make-Up Gain | 0 (off) | |
| Auto Gain | 0 (off) | |
| Shelve Type | 0 | |
| Output Difference Signal | 0 (off) | |

### Effect 5: DeEsser

| Parameter | Normalized | Approx Value |
|---|---|---|
| Threshold | 0.558 | |
| Attack | 0.200 | |
| Release | 0.184 | |
| Center Frequency | 0.391 | **~7,826 Hz** |
| Bandwidth | 0.392 | |
| Output Sibilance Only | 0 (off) | |
| Mode | 1 | Broadband |

### Effect 6: Parametric Equalizer (EQ #1 - Active)

| Parameter | Normalized | Approx Hz/dB |
|---|---|---|
| **High-Pass Filter** | | |
| Enabled | 1 (on) | |
| Cutoff Frequency | 0.002134 | **~43 Hz** |
| Slope | 0.400 | ~12 dB/oct |
| **Low Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.003397 | **~68 Hz** |
| Gain | 0.565789 | **+2.6 dB** |
| **Band 1** | Disabled | |
| **Band 2** | Disabled | |
| **Band 3** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.011994 | **~240 Hz** |
| Gain | 0.468750 | **-1.3 dB** |
| Bandwidth | 0.020508 | ~410 Hz |
| **Band 4** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.177171 | **~3,543 Hz** |
| Gain | 0.495066 | **-0.2 dB** (nearly flat) |
| Bandwidth | 0.213428 | ~4,269 Hz |
| **Band 5** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.532944 | **~10,659 Hz** |
| Gain | 0.500 | 0 dB (flat) |
| **High Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.508900 | **~10,178 Hz** |
| Gain | 0.631579 | **+5.3 dB** |
| **Low-Pass Filter** | Disabled | |
| Master Gain | 0.667 | 0 dB |
| Ultra-Quiet Mode | 1 (on) | |

### Effect 7: Parametric Equalizer (EQ #2 - Tone Shaping)

High shelf and band 3 are the active adjustments:

| Parameter | Normalized | Approx Hz/dB |
|---|---|---|
| **High Shelf** | | |
| Frequency | 0.428551 | **~8,571 Hz** |
| Gain | 0.463816 | **-1.4 dB** |
| **Band 3** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.032307 | **~646 Hz** |
| Gain | 0.406250 | **-3.8 dB** |
| All other bands | Flat / default | |

**Movie Trailer Voice Summary**:
1. **Hard Limiter** at -0.3 dB ceiling
2. **+6 dB Amplify** boost
3. **Heavy compression** (-10 dB threshold, 12:1 ratio, instant attack)
4. **DeNoise** at ~14% to clean up
5. **DeEsser** targeting ~7.8 kHz (sibilance control)
6. **EQ #1**: HP at 43 Hz, +2.6 dB low shelf at 68 Hz, -1.3 dB at 240 Hz, +5.3 dB high shelf at 10 kHz
7. **EQ #2**: -3.8 dB cut at 646 Hz (remove boxiness), -1.4 dB at 8.5 kHz (tame harshness)

The result is a deep, full, radio-quality voice with boosted lows, scooped mids, and bright presence.

---

## 3. Deeper Voice

**Effect Chain**: Pitch Shifter (x1 active)

### Effect 1: Pitch Shifter

| Parameter | Normalized | Approx Value |
|---|---|---|
| Transpose Ratio | 0.296 | **~-4.9 semitones** |
| Precision | 1.0 | High |
| Frequency | 0.089 | |
| Overlapping | 0.584 | |
| Use Default Setting | 0.75 | |
| Use Positive Cents | 0.75 | |

**Summary**: Simple pitch shift downward by approximately 5 semitones. Makes the voice noticeably deeper without being extreme.

---

## 4. Echo (Echoey Room)

**Effect Chain**: Studio Reverb (x1 active)

### Effect 1: Studio Reverb

| Parameter | Normalized | Description |
|---|---|---|
| Low Frequency Cut | 0.083 | ~1,660 Hz (cuts low reverb) |
| High Frequency Cut | 0.289 | ~5,786 Hz |
| Room Size | 0.622 | Medium-large room (~62%) |
| Width | 0.900 | Very wide stereo |
| Diffusion | 0.700 | High diffusion (smooth) |
| Damping | 0.350 | Low damping (bright reverb) |
| Decay | 0.337 | Medium decay (~3.4 sec range) |
| Early Reflections | 0.400 | Moderate |
| Early Reflections Delay | 0.500 | Medium |
| Dry Output Level | 0.600 | 60% dry |
| Wet Output Level | 0.400 | 40% wet |

**Summary**: Spacious room reverb with 60/40 dry/wet blend. Bright character with wide stereo. Creates a natural "echoey room" sound without being washy.

---

## 5. Muffled Voice

**Effect Chain**: Parametric Equalizer (x1 active)

### Effect 1: Parametric Equalizer

| Parameter | Normalized | Approx Hz/dB |
|---|---|---|
| **High Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.352689 | **~7,054 Hz** |
| Gain | 0.063158 | **-17.5 dB** |
| Order | 1 | 2nd order (12 dB/oct) |
| **Low Shelf** | Disabled | |
| **All 5 Bands** | Disabled | |
| **High-Pass Filter** | Disabled | |
| **Low-Pass Filter** | Disabled | |

**Summary**: Extremely simple -- just one steep high shelf cutting 17.5 dB starting at 7 kHz. This removes all the brightness and "air" from the voice, creating a muffled, through-the-wall or behind-a-door effect. The 2nd-order slope makes the cut sharper.

---

## 6. Noise Remover

**Effect Chain**: DeNoise (x1 active)

### Effect 1: DeNoise

| Parameter | Normalized | Approx Value |
|---|---|---|
| Amount | 0.199 | **~19.9%** |
| Make-Up Gain | 0 (off) | |
| Auto Gain | 0 (off) | |
| Shelve Type | 0 | |
| Output Difference Signal | 0 (off) | |

**Summary**: Moderate noise reduction at ~20%. Conservative enough to avoid artifacts while still removing background hiss/hum.

---

## 7. Phone Call

**Effect Chain**: Parametric Equalizer (x1 active)

### Effect 1: Parametric Equalizer

| Parameter | Normalized | Approx Hz/dB |
|---|---|---|
| **Low Shelf** | | |
| Enabled | 1 (on) | |
| Frequency | 0.005927 | **~119 Hz** |
| Gain | 0.042105 | **-18.3 dB** |
| Order | 1 | 2nd order (12 dB/oct) |
| **Band 1** | | |
| Enabled | 1 (on) | |
| Center Frequency | 0.081900 | **~1,638 Hz** |
| Gain | 0.615789 | **+4.6 dB** |
| Q / Width | 0.000100 | Very narrow |
| Bandwidth | 0.198395 | ~3,968 Hz |
| **Bands 2-5** | Disabled | |
| **High Shelf** | Disabled | |
| **High-Pass Filter** | Disabled | |
| **Low-Pass Filter** | Disabled | |

**Summary**: Classic telephone filter effect:
- **-18.3 dB low shelf at 119 Hz** (steep, 2nd-order) -- removes all bass
- **+4.6 dB boost at 1,638 Hz** -- emphasizes the midrange "telephone" frequency

This mimics the 300 Hz - 3.4 kHz bandwidth of a telephone by drastically cutting lows and boosting the upper-mid presence band.

---

# FUN PRESETS

---

## 8. 90s

**Effect Chain**: Amplify -> Distortion -> FFT Filter

### Effect 1: Amplify

| Parameter | Normalized | Approx dB |
|---|---|---|
| Left | 0.645833 | **-6 dB** |
| Right | 0.645833 | **-6 dB** |

### Effect 2: Distortion

| Parameter | Value |
|---|---|
| Positive Smoothing | 0.524 |
| Negative Smoothing | 0.417 |
| Time Smoothing | 0.555 |
| dB Range | 0.667 (default) |
| Symmetric | off |
| Linear Scale | off |
| Post-Filter DC Offset | on |

### Effect 3: FFT Filter

| Parameter | Value |
|---|---|
| FFT Size | 0.062 |
| Window Type | 0.375 (Hanning) |
| **Active Curve Points** | |
| Point 1: ~20 Hz | Muted |
| Point 2: ~65 Hz | Muted |
| Point 3: ~110 Hz | **Pass (0.751)** |
| Point 4: ~2,496 Hz | **Pass (0.747)** |
| Point 5: ~7,894 Hz | Muted |
| Point 6: 20,000 Hz | Muted |

**Summary**: Reduces gain by 6 dB, applies distortion (warm, asymmetric), then uses an FFT bandpass filter that only passes ~110 Hz to ~2,500 Hz range. This creates a lo-fi, vintage radio/cassette effect typical of 90s production.

---

## 9. Alien Voice

**Effect Chain**: Flanger (x1 active)

### Effect 1: Flanger

| Parameter | Value |
|---|---|
| Initial Delay Time | 0.185 |
| Final Delay Time | 0.147 |
| Stereo Phasing | 0.233 |
| Modulation Rate (Frequency) | 0.497 |
| Mix | **1.0 (100% wet)** |
| Feedback | **0.680 (68%)** |
| Inverted Mode | off |
| Special Effects Mode | **on** |
| Sinusoidal Mode | **on** |

**Summary**: Full-wet flanger with high feedback in Special Effects mode. The 100% wet mix and sinusoidal modulation creates a metallic, otherworldly vocal effect. The high feedback (68%) creates resonant sweeping.

---

## 10. Chipmunk

**Effect Chain**: Pitch Shifter (x1 active)

### Effect 1: Pitch Shifter

| Parameter | Normalized | Approx Value |
|---|---|---|
| Transpose Ratio | 0.700 | **~+4.8 semitones** |
| Precision | 1.0 | High |
| Frequency | 0.087 | |
| Overlapping | 0.545 | |
| Use Default Setting | 0.75 | |
| Use Positive Cents | 0.25 | Positive direction |

**Summary**: Pitch shift upward by approximately 5 semitones. Creates the classic chipmunk/helium effect. Moderate enough to still be intelligible.

---

## 11. Inner Monologue

**Effect Chain**: Studio Reverb (x1 active)

### Effect 1: Studio Reverb

| Parameter | Normalized | Description |
|---|---|---|
| Low Frequency Cut | 0.047 | ~940 Hz |
| High Frequency Cut | 0.299 | ~5,986 Hz |
| Room Size | 0.597 | Medium room (~60%) |
| Width | 0.578 | Moderate stereo width |
| Diffusion | 0.505 | Medium diffusion |
| Damping | 0.500 | Medium damping |
| Decay | 0.515 | Longer decay (~5.2 sec range) |
| Early Reflections | 0.621 | Strong early reflections |
| Early Reflections Delay | 0.500 | Medium |
| Dry Output Level | 0.500 | **50% dry** |
| Wet Output Level | 0.500 | **50% wet** |

**Summary**: 50/50 dry/wet reverb with strong early reflections and longer decay. Creates an intimate, "inside your head" sound. The moderate stereo width and balanced reflections give it a dreamy, introspective quality. Compared to the Echo preset, this has more early reflections and a closer dry/wet balance, making the voice feel more enclosed and contemplative.

---

## 12. Pilot Voice

**Effect Chain**: Multiband Compressor (x1 active)

### Effect 1: Multiband Compressor

| Parameter | Value | Notes |
|---|---|---|
| **Band Crossover Frequencies** | | |
| Cutoff 1 | 0.049 (~972 Hz) | |
| Cutoff 2 | 0.128 (~2,552 Hz) | |
| Cutoff 3 | 0.499 (~9,990 Hz) | |
| **Band 1** (sub-972 Hz) | | |
| Threshold | 1.0 (0 dB) | No compression |
| Ratio | 0 (1:1) | |
| Gain | 0.5 (0 dB) | |
| **Band 2** (972-2,552 Hz) | | |
| Threshold | 0.5 (-30 dB) | **Heavy compression** |
| Ratio | 0.103 (~4:1) | |
| Gain | **1.0 (max boost)** | |
| Solo | **1 (on)** | **Only this band plays!** |
| **Band 3** (2,552-9,990 Hz) | | |
| Threshold | 1.0 (0 dB) | No compression |
| Ratio | 0 (1:1) | |
| Gain | 0.5 (0 dB) | |
| **Band 4** (above 9,990 Hz) | | |
| Threshold | 1.0 (0 dB) | No compression |
| Ratio | 0 (1:1) | |
| Gain | 0.5 (0 dB) | |
| CrossOver Q | -0.026 | |
| Number of Bands | -0.333 (likely 3 bands) | |

**Summary**: The key insight is **Solo on Band 2**. This isolates only the 972-2,552 Hz range and compresses it (-30 dB threshold, 4:1 ratio) with maximum gain boost. This creates the classic "pilot/intercom" voice by:
1. Completely removing all bass (below 972 Hz)
2. Completely removing all treble (above 2,552 Hz)
3. Heavily compressing and boosting the remaining narrow midrange
The result sounds like audio transmitted over a radio intercom system.

---

## 13. Robot Voice

**Effect Chain**: Flanger -> Pitch Shifter

### Effect 1: Flanger

| Parameter | Value |
|---|---|
| Initial Delay Time | 0.180 |
| Final Delay Time | 0.180 |
| Stereo Phasing | 0.454 |
| Modulation Rate (Frequency) | 0.033 |
| Mix | 0.650 (65%) |
| Feedback | 0.568 (57%) |
| Inverted Mode | off |
| Special Effects Mode | **on** |
| Sinusoidal Mode | **on** |

### Effect 2: Pitch Shifter

| Parameter | Normalized | Approx Value |
|---|---|---|
| Transpose Ratio | 0.235 | **~-6.4 semitones** |
| Precision | 1.0 | High |
| Frequency | 0.092 | |
| Overlapping | 0.602 | |
| Use Positive Cents | 0.25 | |

**Summary**: Combines a metallic flanger (65% mix, 57% feedback, special effects mode) with a pitch shift down ~6 semitones. The flanger creates the metallic resonance while the pitch shift adds depth. The nearly identical initial and final delay times (0.180/0.180) on the flanger create a static metallic tone rather than a sweeping effect.

---

## 14. Villain Voice

**Effect Chain**: Flanger -> Pitch Shifter

### Effect 1: Flanger

| Parameter | Value |
|---|---|
| Initial Delay Time | 0.025 |
| Final Delay Time | 0.053 |
| Stereo Phasing | 0.500 |
| Modulation Rate (Frequency) | 0.117 |
| Mix | 0.450 (45%) |
| Feedback | 0.000 (0%) |
| Inverted Mode | off |
| Special Effects Mode | **on** |
| Sinusoidal Mode | **on** |

### Effect 2: Pitch Shifter

| Parameter | Normalized | Approx Value |
|---|---|---|
| Transpose Ratio | 0.117 | **~-9.2 semitones** |
| Precision | 1.0 | High |
| Frequency | 0.099 | |
| Overlapping | 0.639 | |
| Use Positive Cents | 0.25 | |

**Summary**: Much deeper pitch shift (-9 semitones) than the robot voice. The flanger is subtle (45% mix, 0% feedback) with very short delay times, adding just a slight metallic texture. The extreme downward pitch shift creates a deep, menacing voice.

---

## 15. Torture Viewers

**Effect Chain**: Distortion -> FFT Filter

### Effect 1: Distortion

| Parameter | Value |
|---|---|
| Positive Smoothing | 0.233 |
| Negative Smoothing | 0.369 |
| Time Smoothing | 0.034 |
| dB Range | 0.416 |
| Symmetric | off |
| Linear Scale | off |
| Post-Filter DC Offset | on |

### Effect 2: FFT Filter

Same curve as the 90s preset - bandpass allowing only ~110 Hz to ~2,500 Hz.

**Summary**: More extreme distortion than the 90s preset (lower smoothing values = harsher clipping, lower dB range = more aggressive) with the same lo-fi bandpass filter. Designed to be deliberately unpleasant.

---

# Quick Reference: Effects Used Per Preset

| Preset | Compressor | EQ | Pitch | Reverb | Flanger | Distortion | FFT | DeNoise | DeEsser | Limiter | Amplify |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voice Enhancer** | Single-band | Parametric | - | - | - | - | - | - | - | - | - |
| | + Dynamics | | | | | | | | | | |
| **Movie Trailer** | Single-band | Parametric x2 | - | - | - | - | - | Yes | Yes | Hard | +6dB |
| **Deeper Voice** | - | - | -5 semi | - | - | - | - | - | - | - | - |
| **Echo** | - | - | - | Studio | - | - | - | - | - | - | - |
| **Muffled** | - | Parametric | - | - | - | - | - | - | - | - | - |
| **Noise Remover** | - | - | - | - | - | - | - | Yes | - | - | - |
| **Phone Call** | - | Parametric | - | - | - | - | - | - | - | - | - |
| **90s** | - | - | - | - | - | Yes | Bandpass | - | - | - | -6dB |
| **Alien Voice** | - | - | - | - | Full-wet | - | - | - | - | - | - |
| **Chipmunk** | - | - | +5 semi | - | - | - | - | - | - | - | - |
| **Inner Monologue** | - | - | - | Studio | - | - | - | - | - | - | - |
| **Pilot Voice** | Multiband | - | - | - | - | - | - | - | - | - | - |
| **Robot Voice** | - | - | -6 semi | - | 65% mix | - | - | - | - | - | - |
| **Villain Voice** | - | - | -9 semi | - | 45% mix | - | - | - | - | - | - |
| **Torture Viewers** | - | - | - | - | - | Extreme | Bandpass | - | - | - | - |

---

# Replication Guide: Voice Enhancer for FFmpeg/SoX

The Voice Enhancer preset (the most relevant for AI voiceover production) can be approximated with standard audio tools:

```bash
# Step 1: Compression (approximate the -10dB threshold, 12:1 ratio)
ffmpeg -i input.wav -af "acompressor=threshold=-10dB:ratio=12:attack=0:release=20:makeup=0" step1.wav

# Step 2: EQ (HP at 34Hz, +1dB at 75Hz, -1dB at 246Hz, +4dB shelf at 15kHz)
ffmpeg -i step1.wav -af "highpass=f=34:poles=2,equalizer=f=75:width_type=h:width=110:g=1.1,equalizer=f=246:width_type=h:width=315:g=-0.9,treble=g=4:f=15000" output.wav
```

Or using SoX:
```bash
sox input.wav output.wav \
  compand 0,0.02 6:-10,-10,-1,-1,0,0 0 -90 0 \
  highpass 34 \
  equalizer 75 110h 1.1 \
  equalizer 246 315h -0.9 \
  treble 4 15000
```

Note: The Dynamics Processing effect with its custom transfer curve is harder to replicate exactly. It acts as a subtle noise gate (attenuating signals below -38 dB) with slight upward expansion above -17 dB.

---

# Raw Normalized Values (for programmatic use)

## Voice Enhancer - Complete Parameter Dump

```json
{
  "compressor": {
    "gain": 0.5,
    "threshold": 0.833333,
    "ratio": 0.379310,
    "attack": 0.0,
    "release": 0.02,
    "auto_makeup_gain": 0
  },
  "dynamics_processing": {
    "level_detector_attack": 0.002,
    "level_detector_release": 0.05,
    "gain_processor_attack": 0.048,
    "gain_processor_release": 0.05,
    "lookahead": 0.006,
    "input_gain": 0.5,
    "output_gain": 0.5,
    "low_cutoff": 0.0,
    "high_cutoff": 1.0,
    "link_channels": 0,
    "peak_rms": 1.0,
    "spline_curves": 1.0,
    "makeup_gain": 0,
    "transfer_curve": [
      [0.000, 0.000],
      [0.370, 0.131],
      [0.516, 0.503],
      [0.716, 0.775],
      [1.000, 1.000]
    ]
  },
  "parametric_eq": {
    "high_pass_enabled": 1,
    "high_pass_cutoff": 0.001695,
    "high_pass_slope": 0.4,
    "low_shelf_enabled": 1,
    "low_shelf_freq": 0.000834,
    "low_shelf_gain": 0.5,
    "low_shelf_order": 0,
    "band1_enabled": 1,
    "band1_freq": 0.001251,
    "band1_gain": 0.5,
    "band1_q": 0.0002,
    "band1_bandwidth": 0.0025,
    "band2_enabled": 1,
    "band2_freq": 0.003749,
    "band2_gain": 0.526316,
    "band2_q": 0.0002,
    "band2_bandwidth": 0.005495,
    "band3_enabled": 1,
    "band3_freq": 0.012291,
    "band3_gain": 0.476974,
    "band3_q": 0.0002,
    "band3_bandwidth": 0.015736,
    "band4_enabled": 1,
    "band4_freq": 0.132611,
    "band4_gain": 0.5,
    "band4_q": 0.0002,
    "band4_bandwidth": 0.160001,
    "band5_enabled": 1,
    "band5_freq": 0.532944,
    "band5_gain": 0.5,
    "band5_q": 0.0002,
    "band5_bandwidth": 0.64,
    "high_shelf_enabled": 1,
    "high_shelf_freq": 0.749792,
    "high_shelf_gain": 0.6,
    "high_shelf_order": 0,
    "low_pass_enabled": 0,
    "master_gain": 0.666667,
    "constant_q": 1,
    "ultra_quiet": 0
  }
}
```

## Movie Trailer Voice - Complete Parameter Dump

```json
{
  "hard_limiter": {
    "max_amplitude": 0.97,
    "input_boost": 0.66,
    "look_ahead": 0.133333,
    "release": 0.375,
    "link_channels": 1,
    "decay_to_ceiling": 1,
    "limit_true_peak": 0
  },
  "amplify": {
    "left": 0.6875,
    "right": 0.6875,
    "link_sliders": 1
  },
  "compressor": {
    "gain": 0.5,
    "threshold": 0.833333,
    "ratio": 0.379310,
    "attack": 0.0,
    "release": 0.02,
    "auto_makeup_gain": 0
  },
  "denoise": {
    "amount": 0.143743,
    "makeup_gain": 0,
    "auto_gain": 0
  },
  "deesser": {
    "threshold": 0.558302,
    "attack": 0.19984,
    "release": 0.183673,
    "center_frequency": 0.391304,
    "bandwidth": 0.391892,
    "mode": 1
  },
  "eq1": {
    "high_pass_enabled": 1,
    "high_pass_cutoff": 0.002134,
    "high_pass_slope": 0.4,
    "low_shelf_freq": 0.003397,
    "low_shelf_gain": 0.565789,
    "band3_enabled": 1,
    "band3_freq": 0.011994,
    "band3_gain": 0.46875,
    "band3_bandwidth": 0.020508,
    "band4_enabled": 1,
    "band4_freq": 0.177171,
    "band4_gain": 0.495066,
    "band4_bandwidth": 0.213428,
    "band5_enabled": 1,
    "band5_freq": 0.532944,
    "band5_gain": 0.5,
    "high_shelf_freq": 0.5089,
    "high_shelf_gain": 0.631579,
    "ultra_quiet": 1
  },
  "eq2": {
    "high_shelf_freq": 0.428551,
    "high_shelf_gain": 0.463816,
    "band3_enabled": 1,
    "band3_freq": 0.032307,
    "band3_gain": 0.40625
  }
}
```
