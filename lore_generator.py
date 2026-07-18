"""
Lore Generator – LangChain + Groq (llama3-70b-8192) with Gemini fallback

Accepts a list of 2–6 NodeRef objects and weaves them into a single lore narrative.

Orchestration order:
  1. cascade_config  → verify budget & latency constraints
  2. memory_manager  → recall any prior lore for this entity group
  3. Groq Llama 3 70B → generate new lore (ultra-fast via Groq API)
  4. memory_manager  → retain the generated lore
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI  # Kept for future fallback!
from langchain_core.prompts import PromptTemplate
from fastapi import HTTPException

from agents.cascade_config import check_constraints, record_call
from agents.memory_manager import recall, retain

if TYPE_CHECKING:
    # NodeRef is a Pydantic model defined in app.py; imported only for type hints
    # to avoid a circular import at runtime.
    from app import NodeRef


async def generate_lore(nodes: list) -> str:
    """Generate lore that weaves together all supplied nodes (2–6 entities).

    Args:
        nodes: list of NodeRef-like objects with `.name` and `.type` attributes.
    """
    # 1. Load keys (Keeping both in the codebase as requested)
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")  # Kept for fallback

    if not groq_key:
        raise HTTPException(status_code=500, detail="Groq API Key missing in .env file.")

    # 2. Governance check
    check_constraints()

    # 3. Build a stable memory key from all node names (sorted for consistency)
    sorted_names = sorted(n.name.lower() for n in nodes)
    memory_key = "::".join(sorted_names)
    prior = recall(memory_key)
    memory_context = prior if prior else "No prior history recorded."

    # 4. Dynamically format the entity list for the prompt
    entities_text = "\n".join(
        f"{i}. {node.name} (Type: {node.type})"
        for i, node in enumerate(nodes, 1)
    )

    try:
        print("\n--- GENERATING LORE WITH GROQ (Llama 3) ---")
        
        # 5. Connect to Groq instead of Gemini
        llm = ChatGroq(
            model="openai/gpt-oss-120b",  # Using the newer, more powerful 120B model
            api_key=groq_key,
            temperature=0.8
        )

        template = (
            "You are a master fantasy worldbuilder. The user has selected a web of "
            "interconnected entities from their world.\n\n"
            "Entities to connect:\n{entity_list}\n\n"
            "Prior context: {memory_context}\n\n"
            "Write a cohesive, engaging, 3-paragraph piece of lore that organically "
            "weaves all of these specific characters, locations, events, and organizations "
            "together into a single narrative or historical record. Make it mysterious and "
            "highly detailed. Ensure every entity listed above plays a meaningful role in "
            "the story. Do not use markdown formatting."
        )

        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm
        response = await chain.ainvoke({
            "entity_list": entities_text,
            "memory_context": memory_context,
        })

        lore = response.content

        # 6. Persist to memory
        retain(memory_key, lore)

        # 7. Record usage for cascadeflow budget tracking
        record_call()

        print("Success! Lore generated instantly.")
        print("-------------------------------------------\n")

        return lore

    except HTTPException:
        raise
    except Exception as e:
        print(f"Groq API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to Groq API.")
