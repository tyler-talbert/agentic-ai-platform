"""
Embed → (optionally) compress → upsert to Pinecone (256-dim index).

Safe for any payload: text, dict, list…
"""
import json
from typing import Dict

import torch

from app.vector_db.embedder import embed_text
from app.vector_db.vector_db import get_index, INDEX_NAME

COMPRESSED_INDEX = f"{INDEX_NAME}-256"


def _to_str(val) -> str:
    """Ensure metadata value is a plain UTF-8 string."""
    if isinstance(val, str):
        return val
    try:
        # compact JSON for structured objects
        return json.dumps(val, ensure_ascii=False, separators=(",", ":"))
    except Exception:  # fallback – best-effort
        return str(val)


async def embed_and_upsert(
    task_id: str,
    text,
    is_answer: bool,
    app,
) -> Dict:
    """Upserts vector into 256-dim index. Returns the 256-vector record."""
    text_str: str = _to_str(text)

    vec768 = await embed_text(text_str)

    encoder = getattr(app.state, "encoder", None)
    if encoder:
        with torch.no_grad():
            vec256 = encoder(torch.tensor(vec768)).tolist()
    else:
        vec256 = vec768[:256]

    meta = {
        "type": "answer" if is_answer else "question",
        "task_id": task_id,
        "text": text_str,
    }

    # ── upsert to 256-dim index ───────────────────────────────────────────
    idx256 = get_index(COMPRESSED_INDEX)
    idx256.upsert(
        vectors=[
            {"id": f"{task_id}-{'a' if is_answer else 'q'}",
             "values": vec256,
             "metadata": meta}
        ]
    )

    # ── optional archival of full 768-vector (kept for retraining) ───────
    idx768 = get_index(INDEX_NAME)
    idx768.upsert(
        vectors=[
            {"id": f"{task_id}-{'a' if is_answer else 'q'}",
             "values": vec768,
             "metadata": meta}
        ]
    )

    return {
        "id": f"{task_id}-{'a' if is_answer else 'q'}",
        "values": vec256,
        "metadata": meta,
    }
