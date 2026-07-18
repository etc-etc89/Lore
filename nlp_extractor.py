import os
import json
import asyncio
from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI  # Kept for future fallback!
from langchain_core.prompts import PromptTemplate

async def extract_entities(text: str) -> list[dict]:
    # 1. Load keys (Keeping both in the codebase as requested)
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")  # Kept for fallback
    
    if not groq_key:
        raise HTTPException(status_code=500, detail="Groq API Key missing in .env file.")

    try:
        print("\n--- EXTRACTING ENTITIES WITH GROQ ---")
        
        # 2. Connect to Groq
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=groq_key,
            temperature=0.0  # Strict zero temperature for formatting consistency
        )

        # 3. Prompt tweaked to ensure strict JSON output for Llama 3
        template = """
        Analyze the following text and extract the key fantasy entities (characters, locations, events, or organizations).
        
        CRITICAL INSTRUCTIONS:
        1. Return the result ONLY as a valid JSON array of objects. 
        2. Absolutely NO conversational text, NO markdown formatting, and NO ```json blocks. 
        3. Each object must have exactly two keys: "name" (the entity name) and "type" (must be "character", "location", "event", or "organization").

        Text: {text}
        """
        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        
        # 4. Get the response
        response = await chain.ainvoke({"text": text})
        
        # 5. Clean up in case Llama 3 disobeys the "no markdown" rule
        raw_text = response.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3].strip()
            
        entities = json.loads(raw_text)
        print(f"Success! Found {len(entities)} entities.")
        print("-------------------------------------\n")
        
        return entities

    except Exception as e:
        print(f"\n--- EXTRACTION ERROR ---")
        print(str(e))
        print("------------------------\n")
        # Return an empty list if it fails so the frontend doesn't crash
        return []