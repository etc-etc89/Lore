import urllib.parse
import requests
import base64
import asyncio
from fastapi import HTTPException

async def generate_avatar(character_name: str, entity_type: str, description: str) -> str:
    # 1. Build the prompt
    prompt = (
        f"A stunning fantasy digital art portrait of {character_name}. "
        f"They are a {entity_type}. "
        f"Distinctive features: {description}. "
        "Highly detailed, cinematic lighting, concept art style, centered, dark background, no text."
    )

    # 2. Safely encode the text so it can be sent inside a URL
    safe_prompt = urllib.parse.quote(prompt)
    
    # 3. Use Pollinations AI (Free, No Auth, FLUX model under the hood)
    # We add width, height, and nologo=true to keep the image clean
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=512&height=512&nologo=true"

    def _fetch_image():
        # Notice this is a simple GET request now, no headers or tokens needed!
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")
        return response.content

    try:
        print("\n--- FETCHING FROM POLLINATIONS AI ---")
        print(f"Bypassing Hugging Face...")
        
        image_bytes = await asyncio.to_thread(_fetch_image)
        
        # 4. Format for the React frontend
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        print("Success! Image generated.")
        print("-------------------------------------\n")
        
        return f"data:image/jpeg;base64,{b64}"
        
    except Exception as e:
        print(f"\n--- API ERROR ---")
        print(str(e))
        print(f"-----------------\n")
        raise HTTPException(status_code=500, detail=str(e))