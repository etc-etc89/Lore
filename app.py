"""
Living Lore Board – FastAPI entry point.

Routes:
  POST /generate-lore    → LangChain + Gemini lore generation
  POST /generate-avatar  → FLUX.1 text-to-image avatar
  POST /extract-entities → BERT NER entity extraction
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from agents.lore_generator import generate_lore
from ml_pipeline.image_gen import generate_avatar
from ml_pipeline.nlp_extractor import extract_entities

app = FastAPI(title="Living Lore Board API", version="0.1.0")

# Allow the Vite dev server to call the API during development
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
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
