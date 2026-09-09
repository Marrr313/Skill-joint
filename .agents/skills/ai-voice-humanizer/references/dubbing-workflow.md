# Dubbing Videos to Other Languages with ElevenLabs

## Why Dub

- 2.5 billion active YouTube users worldwide
- Less than 20% (~500M) speak English
- Adding the next 5 most-spoken languages reaches ~50% of YouTube
- Creators who dub (MrBeast, Mark Rober, Ruhi Cenet, Joe Hattab) see 2-3x growth in views and subscribers
- ElevenLabs dubbing consistently outperforms YouTube's built-in auto-dub (Google Translate voice)

## Step 1: Separate Audio Stems

Before touching any AI, separate your audio into two files:

1. **Voiceover only** -- Mute everything except the voiceover in your timeline. Export as MP3.
2. **Music + SFX only** -- Mute the voiceover, keep music and sound effects. Export as MP3.

## Step 2: Generate the Dub

1. Go to ElevenLabs > **Dubbing** tab
2. Create a new dub
3. Select original language (e.g., English)
4. Select target language (e.g., Portuguese, Spanish, Hindi)
5. Upload the voiceover-only MP3
6. Hit generate (takes a few minutes)
7. Download the dubbed file

## Step 3: Assemble in Your Editor

Set up 3 audio tracks in your timeline:

| Track | Content | Purpose |
|-------|---------|---------|
| Top | Original English voiceover | Timing guide (mute in final export) |
| Middle | New dubbed AI voice | The actual dubbed audio |
| Bottom | Music + SFX stem | Maintains all non-voice audio |

Line up the dubbed track so timing matches your visuals. Use the original English track as a reference for where each sentence should land.

## Step 4: Polish

1. Apply your EQ/voice preset to the dubbed track
2. Mute the original English track
3. Listen through once to verify timing and naturalness
4. Export audio only (not the full video -- just the audio track)

## Step 5: Upload to YouTube

1. YouTube Studio > select your video
2. Click **Languages**
3. Check if YouTube auto-dubbed to that language already -- if so, delete it (their Google Translate voice underperforms)
4. Click add language > select the dubbed language
5. Upload your audio file

## Step 6: Translate Metadata

Translate your video **title** and **description** to the target language. Use ChatGPT or similar. This helps the video surface in search results for that language.

## Priority Languages

Start with the highest-ROI languages based on YouTube user base:
- Spanish
- Hindi
- Portuguese
- Arabic
- French

Each language you add effectively "unlocks a new country" of potential viewers. Repeat the workflow for each language.
