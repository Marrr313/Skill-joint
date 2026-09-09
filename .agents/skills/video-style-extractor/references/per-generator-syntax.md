# Per-Generator Prompt Syntax (2026)

## Static image generators

### Midjourney v7
- Positive: free-text, 60 words practical maximum
- Negative: `--no term1, term2, term3` at end
- Style: `--stylize 0-1000`, `--chaos 0-100`
- Reference image: `--cref <url> --cw 0-100`

### Ideogram 2.0
- Positive: free-text, 120 words max
- Negative: dedicated field (`negative_prompt` in API)
- Style: `style: Auto | General | Realistic | Design | 3D | Anime`

### FLUX.1 (dev / pro)
- Positive: free-text, 200 words max
- Negative: `negative_prompt` field
- Guidance: `guidance_scale` 1-10

### Nano Banana (Gemini image gen)
- Positive: free-text, 300 words max
- No negative field, so fold constraints into the prompt as "must not be ..." / "avoid ..."

## Image-to-video generators

### Runway Gen-4
- Positive: 500 chars max
- No native negative field, so fold taboos into the positive prompt as "avoid ..."
- Motion intensity: slider 1-10

### Kling 2.0
- Positive: 500 chars max
- Separate negative prompt field
- Camera control: pan, zoom, tilt

### Pika 2.2
- Positive: 400 chars max
- Negative via `-neg` flag inline (e.g., `-neg blurry, low quality`)
- Motion strength: `-motion 0-4`

### Veo 3
- Positive: 1000 chars max
- Negative via natural language in prompt
- Aspect: 16:9, 9:16, 1:1

### Sora 2
- Positive: 1000 chars max
- Negative via natural language in prompt
- Duration: 5 to 20s
