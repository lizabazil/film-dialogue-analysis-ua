import traceback

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from src.pipeline.video_pipeline import VideoPipeline
import subprocess
import yaml


app = FastAPI()

# allow interaction with React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def read_root():
    return {"status": "Backend is running!"}


@app.post("/upload-chunk")
async def upload_chunk(
        chunk: UploadFile = File(...),
        chunkIndex: int = Form(...),
        filename: str = Form(...)
):
    file_path = UPLOAD_DIR / filename

    # ab = append binary
    mode = "wb" if chunkIndex == 0 else "ab"

    with open(file_path, mode) as f:
        content = await chunk.read()
        f.write(content)

    return {"status": "chunk accepted", "index": chunkIndex}


@app.post("/analyze")
async def analyze_video(data: dict):
    """
    Receives file from React, saves the file and runs analysis.
    """
    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/backend/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    filename = data.get("filename")
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        return {"error": "File has not loaded..."}

    print("Starting downloading file...")
    try:
        first_minutes_ds = f"{UPLOAD_DIR}/trimmed_{filename}"
        trim_video(file_path, first_minutes_ds)

        print(f"First 14 minutes saved to {file_path}")

        #report = VideoPipeline({}).run(video_path=first_minutes_ds)
        #report = VideoPipeline(config).run_with_llm_integration(video_path=first_minutes_ds)
        report = VideoPipeline(config).run_with_existing_transcript(
            transcript_path="/home/liza/PycharmProjects/film-dialogue-analysis-ua/backend/data/working_files/trimmed_Povodir_final.jsonl",
            video_path="/home/liza/PycharmProjects/film-dialogue-analysis-ua/backend/data/uploads/trimmed_Povodir.mkv",
            udpipe_cache_file_path="/home/liza/PycharmProjects/film-dialogue-analysis-ua/backend/data/working_files/trimmed_Povodir_udpipe_cache.json"
        )

        return report

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def trim_video(input_path, output_path, duration="00:14:00"):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-t', duration,
        '-c', 'copy',
        output_path,
        '-y'
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")

# uvicorn main:app --reload --port 8000
