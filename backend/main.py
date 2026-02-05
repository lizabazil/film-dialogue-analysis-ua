from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

app = FastAPI()

# Додаємо дозвіл для React
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


@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    Receives file from React, saves this file and runs analysis.
    """
    try:
        file_location = UPLOAD_DIR / file.filename

        # save file on the disk
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        print(f"File saved to {file_location}")

        # result = VideoPipeline.process(str(file_location))

        fake_result = {
            "filename": file.filename,
            "duration": "10:05",
            "speakers": 3,
            "scenes_detected": "54"
        }

        return fake_result

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# uvicorn main:app --reload --port 8000
