"""
Embed text → optionally compress with autoencoder → upsert to Pinecone.

Usage from orchestrator background tasks:
    from app.vector_db.embed_and_upsert import embed_and_upsert
    await embed_and_upsert(task_id, text, is_answer=True, app=request.app)
"""
import torch
from typing import Dict
from app.vector_db.embedder import embed_text
from app.vector_db.vector_db import get_index, INDEX_NAME

COMPRESSED_INDEX = f"{INDEX_NAME}-256"


async def embed_and_upsert(
    task_id: str,
    text: str,
    is_answer: bool,
    app,
) -> Dict:
    """Returns the vector dict that was upserted to the 256-index."""
    vec768 = await embed_text(text)

    encoder = getattr(app.state, "encoder", None)
    if encoder:
        with torch.no_grad():
            vec256 = encoder(torch.tensor(vec768)).tolist()
    else:
        vec256 = vec768[:256]

    meta = {
        "type": "answer" if is_answer else "question",
        "task_id": task_id,
        "text": text,
    }

    idx256 = get_index(COMPRESSED_INDEX)
    idx256.upsert(
        vectors=[{"id": f"{task_id}-{'a' if is_answer else 'q'}", "values": vec256, "metadata": meta}]
    )

    # ── Optional archival upsert to 768 index (for future retraining) ────
    # TODO: comment out the next four lines when we want to fully deprecate 768
    idx768 = get_index(INDEX_NAME)
    idx768.upsert(
        vectors=[{"id": f"{task_id}-{'a' if is_answer else 'q'}", "values": vec768, "metadata": meta}]
    )

    return {"id": f"{task_id}-{'a' if is_answer else 'q'}", "values": vec256, "metadata": meta}
