import fitz

def extract_pages(path: str):
    doc = fitz.open(path)
    return [{"page": i + 1, "text": page.get_text("text").strip()} for i, page in enumerate(doc)]

def make_chunks(pages, limit=12000):
    chunks, current, length = [], [], 0
    for page in pages:
        if not page["text"]:
            continue
        part = f"\n[PAGE {page['page']}]\n{page['text']}"
        if current and length + len(part) > limit:
            chunks.append("\n".join(current))
            current, length = [], 0
        current.append(part)
        length += len(part)
    if current:
        chunks.append("\n".join(current))
    return chunks
