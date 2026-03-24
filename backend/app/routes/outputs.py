from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.config import settings

router = APIRouter(tags=["outputs"])


@router.get("/outputs")
async def list_outputs():
    output_dir = settings.OUTPUT_DIR
    if not output_dir.exists():
        return []

    results = []
    for f in sorted(output_dir.rglob("*.md")):
        rel = f.relative_to(output_dir)
        parts = rel.parts
        category = parts[0] if len(parts) > 1 else "uncategorized"
        results.append({
            "path": str(rel),
            "name": f.name,
            "category": category,
            "size": f.stat().st_size,
            "modified": f.stat().st_mtime,
        })

    return results


@router.get("/outputs/{file_path:path}")
async def get_output(file_path: str):
    full_path = (settings.OUTPUT_DIR / file_path).resolve()

    # Path traversal protection
    if not str(full_path).startswith(str(settings.OUTPUT_DIR.resolve())):
        raise HTTPException(403, "Access denied")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(404, "Output file not found")

    return PlainTextResponse(full_path.read_text(encoding="utf-8"))
