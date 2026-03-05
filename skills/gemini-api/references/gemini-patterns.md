# Gemini API Patterns Reference

> **Source**: googleapis/python-genai official codegen_instructions.md
> **Last verified**: March 2026
> **WARNING**: Always web search to confirm — APIs change between versions.

## Installation
```bash
pip install google-genai
```

## Client Setup
```python
from google import genai

# Preferred: uses GOOGLE_API_KEY env var
client = genai.Client()

# Or explicit:
client = genai.Client(api_key='YOUR_API_KEY')
```

## Current Models (March 2026)
- `gemini-3.1-pro-preview` — Most advanced, complex reasoning (latest)
- `gemini-3-flash-preview` — Fast general purpose
- `gemini-3-pro-preview` — DEPRECATED (migrating to 3.1), shuts down March 9 2026
- `gemini-2.5-flash` — Production tier, fast and efficient
- `gemini-2.5-flash-lite` — Low latency, high volume
- `gemini-2.5-flash-image` — Image generation
- `gemini-3-pro-image-preview` — High-quality image generation

**ALWAYS use the model name the user specifies. This list will be outdated.**

## Basic Text Generation
```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model='MODEL_NAME',  # User-specified
    contents='Your prompt here',
)
print(response.text)
```

## Streaming
```python
response = client.models.generate_content_stream(
    model='MODEL_NAME',
    contents='Your prompt here',
)
for chunk in response:
    print(chunk.text, end='')
```

## System Instructions
```python
from google.genai import types

response = client.models.generate_content(
    model='MODEL_NAME',
    contents='Your prompt',
    config=types.GenerateContentConfig(
        system_instruction='You are a helpful assistant.',
    )
)
```

## Chat (Multi-turn)
```python
chat = client.chats.create(model='MODEL_NAME')
response1 = chat.send_message('Hello')
response2 = chat.send_message('Follow up question')

# Access history
for msg in chat.get_history():
    print(f'{msg.role}: {msg.parts[0].text}')
```

## Thinking (Gemini 3 series)
```python
from google.genai import types

response = client.models.generate_content(
    model='gemini-3-pro-preview',
    contents='Complex question',
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level=types.ThinkingLevel.HIGH
        )
    )
)
for part in response.candidates[0].content.parts:
    if part.thought:
        print(f"Thought: {part.text}")
    else:
        print(f"Response: {part.text}")
```

## Thinking (Gemini 2.5 series — uses budget, not level)
```python
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0)
)
```

## Multimodal (Images)
```python
from PIL import Image

image = Image.open('image.jpg')
response = client.models.generate_content(
    model='MODEL_NAME',
    contents=[image, 'Describe this image.'],
)
```

## Multimodal (Audio/Video/PDF bytes)
```python
from google.genai import types

with open('audio.mp3', 'rb') as f:
    audio_bytes = f.read()

response = client.models.generate_content(
    model='MODEL_NAME',
    contents=[
        types.Part.from_bytes(data=audio_bytes, mime_type='audio/mp3'),
        'Transcribe this audio.'
    ]
)
```

## File Upload (large files)
```python
my_file = client.files.upload(file='video.mp4')
response = client.models.generate_content(
    model='MODEL_NAME',
    contents=[my_file, 'What happens in this video?']
)
client.files.delete(name=my_file.name)  # Cleanup
```

## Structured Output (Pydantic)
```python
from pydantic import BaseModel

class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    steps: list[str]

response = client.models.generate_content(
    model='MODEL_NAME',
    contents='Give me a cookie recipe.',
    config=types.GenerateContentConfig(
        response_mime_type='application/json',
        response_json_schema=Recipe,
    ),
)
recipe = Recipe.model_validate_json(response.text)
```

## Function Calling
```python
def get_weather(city: str) -> str:
    """Returns current weather for a city."""
    return f'Weather in {city}: 15C, sunny.'

response = client.models.generate_content(
    model='MODEL_NAME',
    contents='What is the weather in Boston?',
    config=types.GenerateContentConfig(
        tools=[get_weather]
    ),
)
if response.function_calls:
    for fc in response.function_calls:
        print(f'{fc.name}({dict(fc.args)})')
```

## Grounding with Google Search
```python
response = client.models.generate_content(
    model='MODEL_NAME',
    contents='Latest news about X?',
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    ),
)
```

## Image Generation
```python
response = client.models.generate_content(
    model='gemini-2.5-flash-image',  # or gemini-3-pro-image-preview
    contents='A cat wearing a top hat',
)
for part in response.parts:
    if part.inline_data is not None:
        part.as_image().save('output.png')
```

## Safety Settings
```python
config=types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
    ]
)
```

## Video Generation (Veo)
```python
import time

operation = client.models.generate_videos(
    model='veo-3.0-fast-generate-001',
    prompt='A kitten sleeping in sunshine',
    config=types.GenerateVideosConfig(
        aspect_ratio='16:9',
        number_of_videos=1,
        duration_seconds=8,
    ),
)
while not operation.done:
    time.sleep(20)
    operation = client.operations.get(operation)

for vid in operation.response.generated_videos:
    client.files.download(file=vid.video)
    vid.video.save('output.mp4')
```

## Key Imports Summary
```python
from google import genai
from google.genai import types
from PIL import Image          # For image I/O
from pydantic import BaseModel  # For structured output
```
