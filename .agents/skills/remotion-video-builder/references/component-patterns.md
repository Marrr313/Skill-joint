# Remotion Component Patterns

Reusable TypeScript component patterns for building video compositions from style guides. Each pattern is self-contained. Copy and adapt it to match the specific style guide values.

> **Important**: check <https://www.remotion.dev/docs> for the current Remotion API (animations, sequencing, fonts, audio). The patterns below show the architectural shape; the docs are the authoritative API reference.

---

## 1. FloatingCard

Renders an image centered on the canvas with configurable padding. Optional Ken Burns zoom effect (slow scale interpolation over the scene duration).

```typescript
import React from 'react';
import {
  useCurrentFrame,
  useVideoConfig,
  Img,
  interpolate,
  staticFile,
  Easing,
} from 'remotion';

type FloatingCardProps = {
  src: string;
  padding?: number;
  borderRadius?: number;
  shadow?: boolean;
  kenBurns?: {
    startScale: number;
    endScale: number;
  };
  objectPosition?: string;
  backgroundColor?: string;
};

export const FloatingCard: React.FC<FloatingCardProps> = ({
  src,
  padding = 60,
  borderRadius = 0,
  shadow = false,
  kenBurns,
  objectPosition = 'center',
  backgroundColor = '#FFFFFF',
}) => {
  const frame = useCurrentFrame();
  const { width, height, durationInFrames } = useVideoConfig();

  const scale = kenBurns
    ? interpolate(frame, [0, durationInFrames], [kenBurns.startScale, kenBurns.endScale], {
        easing: Easing.inOut(Easing.ease),
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 1;

  const imgWidth = width - padding * 2;
  const imgHeight = height - padding * 2;

  return (
    <div
      style={{
        width,
        height,
        backgroundColor,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          width: imgWidth,
          height: imgHeight,
          overflow: 'hidden',
          borderRadius,
          boxShadow: shadow ? '0 8px 32px rgba(0,0,0,0.15)' : 'none',
        }}
      >
        <Img
          src={staticFile(src)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition,
            transform: `scale(${scale})`,
          }}
        />
      </div>
    </div>
  );
};
```

### Variants

**Paper Presentation**: floating card on an animated paper background:
- Add a gentle vertical float: `translateY(Math.sin(frame / fps * Math.PI) * 12)`
- Add subtle rotation: `rotate(Math.sin(frame / fps * Math.PI * 0.67) * 1.2)deg`
- Scale-in entrance: interpolate scale from 0.9 to 1.0 over the first 12 frames

**Card Presentation**: static off-white background with a heavier shadow:
- Background: `#f0ede8`
- Shadow: `0 12px 48px rgba(0,0,0,0.2)`
- Gentler float, no rotation

---

## 2. KaraokeCaption

Word-by-word reveal synced to audio timestamps. Each word appears instantly at its timestamp. Words accumulate to form the current phrase, then hard-cut on sentence boundaries.

```typescript
import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

type WordTimestamp = {
  word: string;
  start: number; // seconds
};

type KaraokeCaptionProps = {
  words: WordTimestamp[];
  fontFamily?: string;
  fontSize?: number;
  fontWeight?: number | string;
  textTransform?: 'lowercase' | 'uppercase' | 'none';
  color?: string;
  textShadow?: string;
  maxWidth?: number;
  top?: number;
  sentenceBreakGapMs?: number;
};

export const KaraokeCaption: React.FC<KaraokeCaptionProps> = ({
  words,
  fontFamily = 'Inter',
  fontSize = 75,
  fontWeight = 900,
  textTransform = 'lowercase',
  color = '#000000',
  textShadow = 'none',
  maxWidth = 864,
  top = 1380,
  sentenceBreakGapMs = 500,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeSec = frame / fps;

  // Group words into phrases based on sentence boundaries
  const phrases = groupIntoPhrases(words, sentenceBreakGapMs);

  // Find the active phrase
  const activePhrase = phrases.find((phrase) => {
    const firstWordTime = phrase[0].start;
    const lastWordTime = phrase[phrase.length - 1].start;
    // Phrase is active from first word to next phrase start (or end)
    const phraseIndex = phrases.indexOf(phrase);
    const nextPhraseStart =
      phraseIndex < phrases.length - 1
        ? phrases[phraseIndex + 1][0].start
        : lastWordTime + 2; // buffer after last phrase
    return currentTimeSec >= firstWordTime && currentTimeSec < nextPhraseStart;
  });

  if (!activePhrase) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        transform: 'translateX(-50%)',
        maxWidth,
        textAlign: 'center',
      }}
    >
      {activePhrase.map((w, i) => {
        const visible = currentTimeSec >= w.start;
        return (
          <span
            key={`${w.word}-${i}`}
            style={{
              fontFamily,
              fontSize,
              fontWeight,
              textTransform,
              color,
              textShadow,
              letterSpacing: '-0.02em',
              lineHeight: 1.2,
              opacity: visible ? 1 : 0,
              display: 'inline',
            }}
          >
            {w.word}{' '}
          </span>
        );
      })}
    </div>
  );
};

function groupIntoPhrases(
  words: WordTimestamp[],
  gapMs: number
): WordTimestamp[][] {
  const phrases: WordTimestamp[][] = [];
  let current: WordTimestamp[] = [];

  for (let i = 0; i < words.length; i++) {
    current.push(words[i]);

    const isLast = i === words.length - 1;
    const nextGap = isLast ? Infinity : (words[i + 1].start - words[i].start) * 1000;
    const endsWithPunctuation = /[.!?]$/.test(words[i].word);

    if (endsWithPunctuation || nextGap > gapMs || isLast) {
      phrases.push(current);
      current = [];
    }
  }

  return phrases;
}
```

### Variant: Phrase-Based Dark Pill Captions

For styles that show full phrases in a dark pill (not word-by-word reveal):

```typescript
import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

type PhrasePillCaptionProps = {
  phrases: Array<{
    text: string;
    startTime: number; // seconds
    endTime: number;   // seconds
  }>;
  fontSize?: number;
  fontFamily?: string;
  pillColor?: string;
  textColor?: string;
  top?: number;
  maxWidth?: number;
};

export const PhrasePillCaption: React.FC<PhrasePillCaptionProps> = ({
  phrases,
  fontSize = 42,
  fontFamily = 'Sora',
  pillColor = 'rgba(25, 25, 25, 0.8)',
  textColor = '#FFFFFF',
  top = 1350,
  maxWidth = 900,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  const activePhrase = phrases.find(
    (p) => currentTime >= p.startTime && currentTime < p.endTime
  );

  if (!activePhrase) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '50%',
        transform: 'translateX(-50%)',
        maxWidth,
        display: 'flex',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          backgroundColor: pillColor,
          borderRadius: 10,
          padding: '8px 20px',
        }}
      >
        <span
          style={{
            fontFamily,
            fontSize,
            fontWeight: 700,
            color: textColor,
            textAlign: 'center',
            display: 'block',
          }}
        >
          {activePhrase.text}
        </span>
      </div>
    </div>
  );
};
```

---

## 3. HardCutSequencer

Scene manager that renders only the active scene at any given frame. Maps an array of scene configs to Remotion `<Sequence>` components.

```typescript
import React from 'react';
import { Sequence } from 'remotion';

type SceneConfig = {
  id: string;
  startFrame: number;
  durationInFrames: number;
  component: React.ReactNode;
};

type HardCutSequencerProps = {
  scenes: SceneConfig[];
};

export const HardCutSequencer: React.FC<HardCutSequencerProps> = ({ scenes }) => {
  return (
    <>
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationInFrames}
          layout="none"
        >
          {scene.component}
        </Sequence>
      ))}
    </>
  );
};
```

### Usage Pattern

Build the scenes array from clip config + word timestamps:

```typescript
const scenes: SceneConfig[] = clips.map((clip, index) => ({
  id: `scene-${index}`,
  startFrame: clip.startFrame,
  durationInFrames: clip.endFrame - clip.startFrame,
  component: (
    <FloatingCard
      src={clip.file}
      kenBurns={
        clip.kenBurns
          ? { startScale: 1.0, endScale: 1.12 }
          : undefined
      }
      backgroundColor={theme.colors.background}
      padding={theme.layout.padding}
    />
  ),
}));
```

### Scene Timing Helper

Convert word timestamps to frame-aligned scene boundaries:

```typescript
function buildSceneTimings(
  sentences: Array<{ words: WordTimestamp[] }>,
  fps: number,
  paddingFrames: number = 3
): Array<{ startFrame: number; endFrame: number }> {
  return sentences.map((sentence, i) => {
    const firstWord = sentence.words[0];
    const lastWord = sentence.words[sentence.words.length - 1];
    const startFrame = i === 0 ? 0 : Math.round(firstWord.start * fps);
    const endFrame =
      i === sentences.length - 1
        ? Math.round(lastWord.start * fps) + paddingFrames + Math.round(fps * 0.5) // buffer for last scene
        : Math.round(sentences[i + 1].words[0].start * fps);
    return { startFrame, endFrame };
  });
}
```

---

## 4. MusicBed

Looped background audio at a configurable volume. Typically runs for the full composition duration.

```typescript
import React from 'react';
import {
  Audio,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from 'remotion';

type MusicBedProps = {
  src: string;
  volume?: number;
  fadeInFrames?: number;
  fadeOutFrames?: number;
};

export const MusicBed: React.FC<MusicBedProps> = ({
  src,
  volume = 0.08,
  fadeInFrames = 15,
  fadeOutFrames = 30,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const computedVolume = interpolate(
    frame,
    [0, fadeInFrames, durationInFrames - fadeOutFrames, durationInFrames],
    [0, volume, volume, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  return (
    <Audio
      src={staticFile(src)}
      volume={computedVolume}
      loop
    />
  );
};
```

### Volume Reference

| Style | Typical Volume | Notes |
|-------|---------------|-------|
| Documentary / brand story | 0.05-0.08 | Music barely audible, voice dominant |
| Energetic / trend jack | 0.08-0.12 | Music provides energy, still under voice |
| Music-forward / montage | 0.15-0.25 | Music is a primary element |
| Voice only | 0.0 | No music bed |

---

## 5. HookScene

The opening 2-4 seconds. Colored or branded background with a hero asset and large text. Sets the visual tone.

```typescript
import React from 'react';
import {
  useCurrentFrame,
  useVideoConfig,
  Img,
  interpolate,
  staticFile,
  spring,
  Easing,
} from 'remotion';

type HookSceneProps = {
  backgroundSrc?: string;       // optional background image/video
  backgroundColor?: string;     // fallback solid color
  heroImageSrc?: string;        // main visual
  hookText?: string;            // large text overlay
  accentColor?: string;         // for text or accent elements
  textColor?: string;
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: number | string;
  textTransform?: 'lowercase' | 'uppercase' | 'none';
  entranceAnimation?: 'zoom-in' | 'scale-up' | 'none';
};

export const HookScene: React.FC<HookSceneProps> = ({
  backgroundColor = '#000000',
  heroImageSrc,
  hookText,
  accentColor,
  textColor = '#FFFFFF',
  fontSize = 110,
  fontFamily = 'Inter',
  fontWeight = 900,
  textTransform = 'lowercase',
  entranceAnimation = 'zoom-in',
}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();

  // Entrance animation
  let imageScale = 1;
  if (entranceAnimation === 'zoom-in') {
    imageScale = interpolate(frame, [0, 15], [1.4, 1.0], {
      easing: Easing.out(Easing.ease),
      extrapolateRight: 'clamp',
    });
  } else if (entranceAnimation === 'scale-up') {
    imageScale = interpolate(frame, [0, 20], [0.85, 1.0], {
      easing: Easing.out(Easing.ease),
      extrapolateRight: 'clamp',
    });
  }

  // Text fade-in
  const textOpacity = interpolate(frame, [5, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width,
        height,
        backgroundColor,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {heroImageSrc && (
        <Img
          src={staticFile(heroImageSrc)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: `scale(${imageScale})`,
          }}
        />
      )}
      {hookText && (
        <div
          style={{
            position: 'absolute',
            bottom: height * 0.2,
            left: '50%',
            transform: 'translateX(-50%)',
            maxWidth: width * 0.85,
            textAlign: 'center',
            opacity: textOpacity,
          }}
        >
          <span
            style={{
              fontFamily,
              fontSize,
              fontWeight,
              textTransform,
              color: textColor,
              letterSpacing: '-0.02em',
              lineHeight: 1.1,
              textShadow: '0 4px 16px rgba(0,0,0,0.4)',
            }}
          >
            {hookText}
          </span>
        </div>
      )}
    </div>
  );
};
```

---

## 6. SplitLayout

Canvas divided into two regions (typically top B-roll, bottom talking head).

```typescript
import React from 'react';
import { useVideoConfig } from 'remotion';

type SplitLayoutProps = {
  topContent: React.ReactNode;
  bottomContent: React.ReactNode;
  splitRatio?: number; // 0-1, fraction for top region (default 0.5)
};

export const SplitLayout: React.FC<SplitLayoutProps> = ({
  topContent,
  bottomContent,
  splitRatio = 0.5,
}) => {
  const { width, height } = useVideoConfig();
  const topHeight = height * splitRatio;
  const bottomHeight = height * (1 - splitRatio);

  return (
    <div style={{ width, height, position: 'relative' }}>
      <div
        style={{
          position: 'absolute',
          top: 0,
          width,
          height: topHeight,
          overflow: 'hidden',
        }}
      >
        {topContent}
      </div>
      <div
        style={{
          position: 'absolute',
          top: topHeight,
          width,
          height: bottomHeight,
          overflow: 'hidden',
        }}
      >
        {bottomContent}
      </div>
    </div>
  );
};
```

---

## 7. SlowZoom (Ken Burns Wrapper)

Wraps any content with a slow zoom-in or zoom-out effect. Useful for static images.

```typescript
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';

type SlowZoomProps = {
  children: React.ReactNode;
  startScale?: number;
  endScale?: number;
};

export const SlowZoom: React.FC<SlowZoomProps> = ({
  children,
  startScale = 1.0,
  endScale = 1.12,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const scale = interpolate(frame, [0, durationInFrames], [startScale, endScale], {
    easing: Easing.inOut(Easing.ease),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <div style={{ transform: `scale(${scale})`, width: '100%', height: '100%' }}>
        {children}
      </div>
    </div>
  );
};
```

**Alternating zoom direction**: For visual variety, alternate zoom-in and zoom-out per scene index:

```typescript
const isZoomIn = sceneIndex % 2 === 0;
const startScale = isZoomIn ? 1.0 : 1.12;
const endScale = isZoomIn ? 1.12 : 1.0;
```

---

## 8. Voiceover Audio

Simple voiceover audio component. Placed at the composition root level (outside sequences) so it plays continuously.

```typescript
import React from 'react';
import { Audio, staticFile } from 'remotion';

type VoiceoverProps = {
  src: string;
  volume?: number;
};

export const Voiceover: React.FC<VoiceoverProps> = ({ src, volume = 1.0 }) => {
  return <Audio src={staticFile(src)} volume={volume} />;
};
```

---

## Composition Assembly Pattern

Typical main composition that orchestrates all layers:

```typescript
import React from 'react';
import { AbsoluteFill, Audio, staticFile } from 'remotion';
import { HardCutSequencer } from './HardCutSequencer';
import { KaraokeCaption } from './KaraokeCaption';
import { MusicBed } from './MusicBed';

type MainCompositionProps = {
  audioSrc: string;
  captionsFile: string;
  clips: ClipConfig[];
  musicSrc?: string;
  musicVolume?: number;
};

export const MainComposition: React.FC<MainCompositionProps> = ({
  audioSrc,
  captionsFile,
  clips,
  musicSrc,
  musicVolume = 0.08,
}) => {
  // Load captions (use the project's pattern: delayRender/continueRender or static import)
  const words = useCaptions(captionsFile);

  // Build scenes from clips
  const scenes = clips.map((clip, i) => ({
    id: `scene-${i}`,
    startFrame: clip.startFrame,
    durationInFrames: clip.endFrame - clip.startFrame,
    component: renderClip(clip),
  }));

  return (
    <AbsoluteFill>
      {/* Layer 1: Visual scenes (B-roll / images) */}
      <HardCutSequencer scenes={scenes} />

      {/* Layer 2: Captions (on top of visuals) */}
      {words && <KaraokeCaption words={words} />}

      {/* Layer 3: Voiceover audio */}
      <Audio src={staticFile(audioSrc)} volume={1} />

      {/* Layer 4: Music bed audio */}
      {musicSrc && <MusicBed src={musicSrc} volume={musicVolume} />}
    </AbsoluteFill>
  );
};
```

**Layer order matters**: visuals at the bottom, captions on top, audio components anywhere (they have no visual output). Use `AbsoluteFill` for stacking.
