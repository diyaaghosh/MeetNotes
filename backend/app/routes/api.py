from fastapi import APIRouter, UploadFile, File
import shutil
import os
from ..services.hybrid_summarizer import summarize, extract_key_points
from fastapi.responses import FileResponse
from ..services.pdf_service import generate_pdf

router = APIRouter()


@router.post("/process_text")
async def process_text(data: dict):
    try:
        text = data["text"]

        summary = summarize(text)
        bullets = extract_key_points(summary)

        return {
            "summary": summary,
            "bullets": bullets
        }

    except Exception as e:
        import traceback

        error = traceback.format_exc()
        print(error)

        return {
            "error": str(e),
            "traceback": error
        }


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
