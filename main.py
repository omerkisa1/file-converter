import os
import uuid
import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from core import ConverterFactory, UnsupportedFormatError
from converters import ImageConverter, DocumentConverter, MediaConverter

app = FastAPI(title="Universal File Converter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ConverterFactory.register_converter(ImageConverter())
ConverterFactory.register_converter(DocumentConverter())
ConverterFactory.register_converter(MediaConverter())


def cleanup_files(*paths: str) -> None:
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/formats")
async def get_formats():
    return ConverterFactory.get_all_supported_formats()


@app.get("/api/formats/{input_format}")
async def get_available_formats(input_format: str):
    formats = ConverterFactory.get_available_formats(input_format)
    return {"input_format": input_format, "available_formats": formats}


@app.post("/convert")
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_format: str = Form(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    input_ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    target_format = target_format.lower().lstrip(".")
    
    if not input_ext:
        raise HTTPException(status_code=400, detail="Could not determine file type")
    
    try:
        converter = ConverterFactory.get_converter(input_ext, target_format)
    except UnsupportedFormatError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e.message)}
        )
    
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{unique_id}_{file.filename}"
    input_path = TEMP_DIR / safe_filename
    
    try:
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        output_path = converter.convert(str(input_path), target_format)
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Conversion failed - output file not created")
        
        output_filename = f"converted_{os.path.splitext(file.filename)[0]}.{target_format}"
        
        background_tasks.add_task(cleanup_files, str(input_path), output_path)
        
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/octet-stream",
            background=None
        )
        
    except UnsupportedFormatError as e:
        cleanup_files(str(input_path))
        return JSONResponse(
            status_code=400,
            content={"error": str(e.message)}
        )
    except Exception as e:
        cleanup_files(str(input_path))
        return JSONResponse(
            status_code=500,
            content={"error": f"Conversion failed: {str(e)}"}
        )


@app.on_event("startup")
async def startup_event():
    for file in TEMP_DIR.glob("*"):
        try:
            file.unlink()
        except Exception:
            pass


@app.on_event("shutdown")
async def shutdown_event():
    try:
        shutil.rmtree(TEMP_DIR)
    except Exception:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
