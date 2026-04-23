import os
import shutil
import json
import asyncio
import logging
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import existing logic from main.py
# We will use the functions directly to ensure "not a single word" of logic changes
from main import init_ocr, process_document_image, ScholarshipDecisionEngine, WatermarkDetector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScholarshipAPI")

app = FastAPI(title="Scholarship OCR API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
TEST_IMAGES_DIR = "test_images"
OUTPUT_DIR = "output"
ANNOTATED_DIR = os.path.join(OUTPUT_DIR, "annotated")

# Ensure directories exist
os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ANNOTATED_DIR, exist_ok=True)

# Mount static files for serving annotated images
app.mount("/api/images", StaticFiles(directory=ANNOTATED_DIR), name="images")

# Global state for progress tracking
class ProcessStatus(BaseModel):
    is_processing: bool = False
    progress: int = 0
    message: str = "Idle"
    error: Optional[str] = None

current_status = ProcessStatus()

# Helper to clear a directory
def clear_directory(directory: str):
    if not os.path.exists(directory):
        return
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}")

async def run_processing_task():
    global current_status
    try:
        current_status.is_processing = True
        current_status.progress = 5
        current_status.message = "Initializing AI verification engines..."
        
        # Clear annotated dir for a fresh run
        clear_directory(ANNOTATED_DIR)
        
        # 1. Initialize Engines
        ocr_engine = init_ocr()
        watermark_detector = WatermarkDetector()
        decision_engine = ScholarshipDecisionEngine()
        
        current_status.progress = 15
        current_status.message = "Analysis environment prepared. Executing logic..."
        
        # 2. Get images to process
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        image_paths = [
            os.path.join(TEST_IMAGES_DIR, f)
            for f in sorted(os.listdir(TEST_IMAGES_DIR))
            if os.path.splitext(f)[1].lower() in image_extensions
        ]
        
        if not image_paths:
            current_status.error = "No images found to process."
            current_status.is_processing = False
            return

        all_results = {}
        total_images = len(image_paths)
        
        # 3. Process each image
        for i, img_path in enumerate(image_paths):
            name = os.path.basename(img_path)
            current_status.message = "Analyzing document structural integrity..."
            if i == 1: current_status.message = "Performing biometric field extraction..."
            if i == 2: current_status.message = "Scanning for government authenticity seals..."
            # Increment progress proportionally (from 15 to 85)
            current_status.progress = 15 + int((i / total_images) * 70)
            
            # Using loop.run_in_executor to not block the event loop for heavy OCR
            loop = asyncio.get_event_loop()
            fields = await loop.run_in_executor(
                None, process_document_image, ocr_engine, watermark_detector, img_path, False
            )
            all_results[name] = fields
            
        current_status.progress = 85
        current_status.message = "Executing final eligibility consistency check..."
        
        # 4. Run Decision Engine
        decision = decision_engine.analyze(all_results)
        
        # 5. Save Results (Overwrite existing)
        results_json = os.path.join(OUTPUT_DIR, "results.json")
        decision_json = os.path.join(OUTPUT_DIR, "decision.json")
        
        with open(results_json, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        with open(decision_json, "w", encoding="utf-8") as f:
            json.dump(decision, f, indent=2, ensure_ascii=False)
            
        current_status.progress = 100
        current_status.message = "Analysis complete."
        current_status.is_processing = False
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        current_status.error = str(e)
        current_status.is_processing = False

@app.post("/api/upload")
async def upload_documents(
    id_card: UploadFile = File(...),
    marksheet: UploadFile = File(...),
    income: UploadFile = File(...)
):
    """Upload and overwrite existing test images."""
    if current_status.is_processing:
        raise HTTPException(status_code=400, detail="A process is already running.")
        
    # Clear existing images as requested
    clear_directory(TEST_IMAGES_DIR)
    clear_directory(ANNOTATED_DIR)
    
    # Save new files with descriptive names for internal tracking
    # We use .png to ensure compatibility with OpenCV logic in main.py
    files = [
        (id_card, "uploaded_id.png"),
        (marksheet, "uploaded_marksheet.png"),
        (income, "uploaded_income.png")
    ]
    
    for upload_file, target_name in files:
        file_path = os.path.join(TEST_IMAGES_DIR, target_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
    return {"message": "Files uploaded successfully."}

@app.post("/api/process")
async def start_processing(background_tasks: BackgroundTasks):
    """Start the OCR and Decision pipeline."""
    if current_status.is_processing:
        return {"message": "Processing already in progress."}
    
    # Reset status
    current_status.progress = 0
    current_status.message = "Starting..."
    current_status.error = None
    
    background_tasks.add_task(run_processing_task)
    return {"message": "Processing started."}

@app.get("/api/status", response_model=ProcessStatus)
async def get_status():
    """Poll current processing status."""
    return current_status

@app.get("/api/results")
async def get_results():
    """Fetch the final processing results."""
    decision_json = os.path.join(OUTPUT_DIR, "decision.json")
    results_json = os.path.join(OUTPUT_DIR, "results.json")
    
    if not os.path.exists(decision_json):
        raise HTTPException(status_code=404, detail="Results not found. Run processing first.")
        
    with open(decision_json, "r", encoding="utf-8") as f:
        decision = json.load(f)
    with open(results_json, "r", encoding="utf-8") as f:
        raw_results = json.load(f)
        
    # Get list of annotated images
    annotated_images = []
    if os.path.exists(ANNOTATED_DIR):
        annotated_images = [f for f in os.listdir(ANNOTATED_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
    return {
        "decision": decision,
        "details": raw_results,
        "annotated_images": annotated_images
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
