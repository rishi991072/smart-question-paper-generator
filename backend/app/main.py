import uuid
from pathlib import Path
from datetime import datetime, timezone
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .config import settings
from .database import init_db,save_document,get_document,save_paper,get_paper,list_papers,counts
from .schemas import GenerateRequest
from .services.pdf_extractor import extract_pages,make_chunks
from .services.ai_generator import generate_from_text
from .services.paper_builder import create_sets,validate
from .services.pdf_generator import render_pdf
from fastapi.responses import FileResponse
app=FastAPI(title='Offline Smart Question Paper Generator',version='1.1.0')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
UPLOADS=Path('uploads');UPLOADS.mkdir(exist_ok=True);init_db()
@app.get("/")
async def root():
    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {"message": "Offline Smart Question Paper Generator API is running"}
@app.post('/api/documents/upload')
async def upload(file:UploadFile=File(...)):
    if not file.filename.lower().endswith('.pdf'):raise HTTPException(400,'Only PDF files are accepted.')
    content=await file.read()
    if len(content)>settings.max_upload_mb*1024*1024:raise HTTPException(413,f'PDF exceeds {settings.max_upload_mb} MB.')
    doc_id=str(uuid.uuid4());path=UPLOADS/f'{doc_id}.pdf';path.write_bytes(content)
    try:pages=extract_pages(str(path))
    except Exception as exc:
        path.unlink(missing_ok=True);raise HTTPException(400,f'Unable to read PDF: {exc}')
    chars=sum(len(p['text']) for p in pages)
    save_document(doc_id,{'filename':file.filename,'path':str(path),'pages':pages,'page_count':len(pages),'chars':chars})
    return {'document_id':doc_id,'filename':file.filename,'page_count':len(pages),'extracted_chars':chars,'needs_ocr':chars<100}
@app.post('/api/questions/generate')
async def generate(data:GenerateRequest):
    doc=get_document(data.document_id)
    if not doc:raise HTTPException(404,'Uploaded PDF not found.')
    try:
        count=validate(data);chunks=make_chunks(doc['pages'])
        if not chunks:raise ValueError('No selectable text found. This may be a scanned PDF; use a text-based PDF for now.')
        pool=[]
        for chunk in chunks:pool.extend(generate_from_text(chunk,data.subject,max(20,count*3),data.difficulty,data.language))
        seen=set();clean=[]
        for q in pool:
            k=' '.join(str(q.get('question','')).lower().split())
            if k and k not in seen:seen.add(k);clean.append(q)
        sets=create_sets(clean,data);paper_id=str(uuid.uuid4());created=datetime.now(timezone.utc).isoformat()
        save_paper(paper_id,{'config':data.model_dump(),'sets':sets,'created_at':created})
        return {'paper_id':paper_id,'sets':sets,'question_pool_size':len(clean),'generation_mode':'offline-template-based'}
    except Exception as exc:raise HTTPException(400,str(exc))
@app.get('/api/papers')
async def papers():return list_papers()
@app.get('/api/papers/{paper_id}')
async def paper(paper_id:str):
    item=get_paper(paper_id)
    if not item:raise HTTPException(404,'Paper not found.')
    item['id']=paper_id;return item
@app.get('/api/papers/{paper_id}/download/{set_name}')
async def download(paper_id:str,set_name:str,answer_key:bool=False):
    item=get_paper(paper_id)
    if not item:raise HTTPException(404,'Paper not found.')
    selected=next((s for s in item['sets'] if s['set_name'].lower()==set_name.lower()),None)
    if not selected:raise HTTPException(404,'Set not found.')
    pdf=render_pdf(GenerateRequest(**item['config']),selected,answer_key);kind='answer-key' if answer_key else 'question-paper'
    return StreamingResponse(BytesIO(pdf),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename="{kind}-set-{set_name.upper()}.pdf"'})
@app.get('/api/dashboard/stats')
async def stats():return counts()


# Serve React frontend
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if not FRONTEND_DIST.exists():
        raise HTTPException(404, "Frontend build not found")

    requested_file = (FRONTEND_DIST / full_path).resolve()

    if requested_file.is_relative_to(FRONTEND_DIST.resolve()) and requested_file.is_file():
        return FileResponse(requested_file)

    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(404, "Page not found")