from pathlib import Path
from .config import settings

def save_upload(upload, filename: str) -> str:
    """Demo-friendly local storage. For production, mount persistent storage or replace this service with S3/Supabase Storage."""
    root = Path(settings.upload_dir)
    root.mkdir(parents=True, exist_ok=True)
    safe = Path(filename).name.replace(" ", "_")
    path = root / safe
    with path.open("wb") as f:
        while chunk := upload.file.read(1024 * 1024):
            f.write(chunk)
    return f"/uploads/{safe}"

def generate_outreach(title: str, description: str, platform: str) -> str:
    if settings.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.openai_api_key)
            prompt = f"Create accurate outreach content for {platform}. Do not invent scientific facts. Clearly label it as a draft. Title: {title}\nDescription: {description}"
            r = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role":"system","content":"You are a careful science communication editor. Use only facts supplied in the source text and flag missing information."},
                    {"role":"user","content":prompt},
                ],
                temperature=0.2,
            )
            return r.choices[0].message.content or ""
        except Exception:
            pass
    if platform == "student":
        return f"{title}\n\nIn simple words: {description}\n\nWhy it matters: Polar research helps us understand Earth systems, climate and extreme environments.\n\n[DEMO DRAFT — review against the original source before publication.]"
    if platform in {"instagram", "linkedin", "x"}:
        return f"{title} ❄️\n\n{description[:500]}\n\n#PolarScience #Antarctica #Arctic #Science\n\n[DEMO DRAFT — review before publication.]"
    return f"# {title}\n\n{description}\n\nThis outreach draft is generated from repository metadata and must be reviewed against the source before publication."
