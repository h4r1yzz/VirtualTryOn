"""
FastAPI backend server for FashionNanoBanana project.
Provides REST API endpoints for clothing analysis and product image generation.
"""

import os
import uuid
import shutil
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import functions from existing banana.py
from banana import analyze_clothing_item, generate_fashion_product_images, ClothingAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create directories for static files
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(script_dir, "static")
os.makedirs(static_dir, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="FashionNanoBanana API",
    description="AI-powered fashion analysis and product image generation",
    version="1.0.0"
)

# Mount static files for serving generated images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Define response models
class AnalyzeResponse(BaseModel):
    """Response model for clothing analysis endpoint."""
    success: bool
    analysis: ClothingAnalysis
    message: str

class GenerateResponse(BaseModel):
    """Response model for product generation endpoint."""
    success: bool
    analysis: ClothingAnalysis
    generated_images: List[str]
    message: str

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool
    error: str
    details: Optional[str] = None

# Utility functions
def get_unique_filename(original_filename: str) -> str:
    """Generate a unique filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{file_extension}"

def validate_image_file(file: UploadFile) -> bool:
    """Validate if uploaded file is a valid image."""
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    # Check MIME type
    if file.content_type not in allowed_types:
        return False
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        return False
    
    return True

async def save_upload_file(upload_file: UploadFile, destination_folder: str) -> str:
    """Save uploaded file to destination folder and return the file path."""
    if not validate_image_file(upload_file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: JPEG, PNG, WebP"
        )

    # Get absolute path to the destination folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_destination = os.path.join(script_dir, destination_folder)

    # Create destination folder if it doesn't exist
    os.makedirs(absolute_destination, exist_ok=True)

    # Generate unique filename
    unique_filename = get_unique_filename(upload_file.filename)
    file_path = os.path.join(absolute_destination, unique_filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"File saved: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

def cleanup_file(file_path: str) -> None:
    """Clean up temporary file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "FashionNanoBanana API"}

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_clothing(
    clothing_image: UploadFile = File(..., description="Clothing item image to analyze")
):
    """
    Analyze a clothing item image and return structured information.
    
    Args:
        clothing_image: Image file of the clothing item
        
    Returns:
        ClothingAnalysis with detailed information about the clothing item
    """
    clothing_path = None
    
    try:
        logger.info(f"Starting clothing analysis for: {clothing_image.filename}")
        
        # Save uploaded clothing image
        clothing_path = await save_upload_file(clothing_image, "apparels")
        
        # Analyze the clothing item
        analysis = analyze_clothing_item(clothing_path)
        
        logger.info("Clothing analysis completed successfully")
        
        return AnalyzeResponse(
            success=True,
            analysis=analysis,
            message="Clothing analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during clothing analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )
    finally:
        # Cleanup temporary file
        if clothing_path:
            cleanup_file(clothing_path)

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_product_images(
    clothing_image: UploadFile = File(..., description="Clothing item image"),
    model_image: UploadFile = File(..., description="Model image"),
    output_prefix: str = "product"
):
    """
    Generate fashion product listing images showing model wearing clothing from multiple angles.
    
    Args:
        clothing_image: Image file of the clothing item
        model_image: Image file of the model
        output_prefix: Prefix for generated image files
        
    Returns:
        ClothingAnalysis and information about generated product images
    """
    clothing_path = None
    model_path = None
    
    try:
        logger.info(f"Starting product generation for: {clothing_image.filename} + {model_image.filename}")
        
        # Save uploaded images
        clothing_path = await save_upload_file(clothing_image, "apparels")
        model_path = await save_upload_file(model_image, "model")
        
        # Step 1: Analyze the clothing item
        logger.info("Step 1: Analyzing clothing item")
        analysis = analyze_clothing_item(clothing_path)
        
        # Step 2: Generate product images
        logger.info("Step 2: Generating product images")
        generate_fashion_product_images(clothing_path, model_path, output_prefix)

        # Find generated images and move them to static directory
        generated_files = []
        generated_urls = []
        for i in range(10):  # Check for up to 10 generated images
            image_file = f"{output_prefix}_{i}.png"
            if os.path.exists(image_file):
                # Move to static directory
                static_filename = f"generated_{uuid.uuid4().hex}_{i}.png"
                static_path = os.path.join(static_dir, static_filename)
                shutil.move(image_file, static_path)

                # Create accessible URL
                image_url = f"/static/{static_filename}"
                generated_files.append(static_filename)
                generated_urls.append(image_url)

        logger.info(f"Product generation completed. Generated {len(generated_files)} images")
        
        return GenerateResponse(
            success=True,
            analysis=analysis,
            generated_images=generated_urls,  # Return URLs instead of file paths
            message=f"Product generation completed successfully. Generated {len(generated_files)} images."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during product generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Product generation failed: {str(e)}"
        )
    finally:
        # Cleanup temporary files
        if clothing_path:
            cleanup_file(clothing_path)
        if model_path:
            cleanup_file(model_path)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            details=None
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            details=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
