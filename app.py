"""
Living Lore Board – FastAPI entry point.

Routes:
  POST /generate-lore    → LangChain + Groq/Gemini lore generation
  POST /generate-avatar  → Pollinations AI text-to-image avatar
  POST /extract-entities → Groq/Llama 3 entity extraction
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

# FLATTENED IMPORTS: Importing directly from the root files instead of folders
from lore_generator import generate_lore
from image_gen import generate_avatar
from nlp_extractor import extract_entities

app = FastAPI(title="Living Lore Board API", version="0.1.0")

# Allowed origins updated to accept common local ports and placeholders for production
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://your-frontend-project.vercel.app" # <-- Replace with your real Vercel link later!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response Models ──────────────────────────────

class NodeRef(BaseModel):
    name: str
    type: str


class LoreRequest(BaseModel):
    nodes: list[NodeRef] = Field(..., description="List of 2 to 6 nodes to connect.")

    @field_validator("nodes")
    @classmethod
    def validate_node_count(cls, v: list[NodeRef]) -> list[NodeRef]:
        if len(v) < 2:
            raise ValueError("You must select at least 2 nodes to generate lore.")
        if len(v) > 6:
            raise ValueError("You cannot connect more than 6 nodes at once.")
        return v


class LoreResponse(BaseModel):
    lore: str


class AvatarRequest(BaseModel):
    name: str
    type: str
    description: str


class AvatarResponse(BaseModel):
    image_url: str


class ExtractRequest(BaseModel):
    text: str


class EntityItem(BaseModel):
    name: str
    type: str


class ExtractResponse(BaseModel):
    entities: list[EntityItem]


# ── Routes ─────────────────────────────────────────────────

@app.post("/generate-lore", response_model=LoreResponse)
async def lore_endpoint(req: LoreRequest):
    lore = await generate_lore(req.nodes)
    return LoreResponse(lore=lore)


@app.post("/generate-avatar", response_model=AvatarResponse)
async def avatar_endpoint(req: AvatarRequest):
    # Sends generation requirements off to the lightweight Pollinations handler
    url = await generate_avatar(req.name, req.type, req.description)
    return AvatarResponse(image_url=url)


@app.post("/extract-entities", response_model=ExtractResponse)
async def extract_endpoint(req: ExtractRequest):
    entities = await extract_entities(req.text)
    return ExtractResponse(entities=[EntityItem(**e) for e in entities])


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000)), reload=True)
