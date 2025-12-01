# app/main.py

from typing import Annotated
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import os

from .config import settings
from .database import init_db, get_db_session
from .models import Image
from .schemas import UploadResponse
from .compliance import validate_content
# Import the custom type hint for the Uploader dependency
from .storage import Uploader, StorageUploader

# Initialize the database and create tables if they don't exist
init_db()

# Alias for DB Session dependency injection, relying on the generator function
DB_Session = Annotated[Session, Depends(get_db_session)]

# --- FastAPI Application Initialization ---
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-ready Image Ingestion Microservice with decoupled architecture."
)


# --- Routes/Endpoints Definition ---
@app.post(
    "/upload",
    response_model=UploadResponse,
    summary="Uploads an image file and records metadata"
)
async def upload_image(
        file: UploadFile = File(..., description=f"Image file to upload (Max {settings.MAX_FILE_SIZE_MB}MB)."),
        uploader: Uploader = None,
        db: DB_Session = None
):
    """
    Handles the image ingestion pipeline: Compliance Check -> File Storage -> Metadata Record.
    """

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing or invalid.")

    # 1. Compliance Check (Fail Fast)
    if not validate_content(file):
        raise HTTPException(status_code=400, detail="Compliance check failed (File too large or content violation).")

    # 2. File Storage (Decoupled via Dependency Injection)
    try:
        # Destination path/prefix (e.g., local folder or OSS folder prefix)
        upload_destination = "ai_platform_images"
        storage_path = uploader.save(file, upload_destination)
    except Exception as e:
        print(f"Storage Error: {e}")
        # Log error details in production
        raise HTTPException(status_code=500, detail=f"Internal server error during file storage: {str(e)}")

    # 3. Database Metadata Record
    try:
        record = Image(
            original_filename=file.filename,
            storage_path=storage_path,
            validation_status="Validated"
        )
        db.add(record)
        db.commit()
        db.refresh(record)  # Refresh to get the auto-generated 'id' and 'upload_timestamp'
    except Exception as e:
        print(f"Database Error: {e}")
        db.rollback()
        # In a real system, asynchronous cleanup of the stored file would be triggered here.
        raise HTTPException(status_code=500, detail="Internal server error while recording metadata.")

    # 4. Response Generation (Final Fix: Clean Data & Explicit Mapping)

    # 1. Copy the record's dictionary
    response_data = record.__dict__.copy()

    # 2. CRITICAL FIX: Remove SQLAlchemy's internal state to prevent ResponseValidationError
    if '_sa_instance_state' in response_data:
        response_data.pop('_sa_instance_state')

        # 3. Explicitly construct the final data dictionary with correct Pydantic field names
    final_response = {
        # Custom message field
        "message": "Upload successful and metadata recorded",
        # Mapping ORM attributes to Pydantic Schema attributes
        "id": response_data.get("id"),
        "filename": response_data.get("original_filename"),  # Maps from original_filename
        "path": response_data.get("storage_path"),  # Maps from storage_path
        "status": response_data.get("validation_status"),  # Maps from validation_status
        "upload_timestamp": response_data.get("upload_timestamp"),
    }

    # 4. Use model_validate with the clean, mapped dictionary
    return UploadResponse.model_validate(final_response)