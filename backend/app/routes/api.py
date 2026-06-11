from fastapi import APIRouter, UploadFile, File
import shutil
import os
from ..services.hybrid_summarizer import summarize
from ..services.extractor import convert_to_bullets
from fastapi.responses import FileResponse
from ..services.pdf_service import generate_pdf
router = APIRouter()
# @router.post("/process-text")
# async def process_text(data: dict):
#     text = data["text"]

#     summary = summarize(text)
#     bullets = convert_to_bullets(summary)

#     return {
#         "summary": summary,  
#         "bullets": bullets
#     }
@app.post("/process_text")
async def process_text(data: dict):
    try:
        text = data["text"]

        print("Received text:", text[:100])

        summary = summarize(text)
        print("Summary generated")

        bullets = convert_to_bullets(summary)
        print("Bullets generated")

        return {
            "summary": summary,
            "bullets": bullets
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}
@router.post("/generate-pdf")
def create_pdf(data: dict):
    summary = data.get("summary", [])
    bullets = data.get("bullets", [])

    output_file = "output.pdf"
    generate_pdf(summary, bullets, output_file)

    return FileResponse(
        path=output_file,
        media_type="application/pdf",
        filename="notes.pdf"
    )
