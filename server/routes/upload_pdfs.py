from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from modules.load_vectorstore import load_vectorstore
from fastapi.responses import JSONResponse
from logger import logger

router = APIRouter()

@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload PDF files and process them into vectorstore
    """
    try:
        # Validate input
        if not files:
            logger.warning("No files provided")
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Check if any files were actually selected
        if all(file.filename == "" or file.filename is None for file in files):
            logger.warning("No files selected (empty filenames)")
            raise HTTPException(status_code=400, detail="No files selected")
        
        # Validate file types and sizes
        valid_files = []
        max_file_size = 10 * 1024 * 1024  # 10MB limit
        
        for file in files:
            if not file.filename:
                continue
                
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue
            
            # Check file size (if available)
            if hasattr(file, 'size') and file.size and file.size > max_file_size:
                logger.warning(f"File {file.filename} too large: {file.size} bytes")
                continue
            
            valid_files.append(file)
        
        if not valid_files:
            logger.warning("No valid PDF files found")
            raise HTTPException(status_code=400, detail="No valid PDF files found")
        
        logger.info(f"Received {len(valid_files)} valid PDF files")
        for file in valid_files:
            logger.info(f"Processing file: {file.filename}")
        
        # Process files
        load_vectorstore(valid_files)
        
        logger.info("Documents successfully added to vectorstore")
        return {
            "message": "Files processed and vectorstore updated successfully",
            "processed_files": len(valid_files),
            "file_names": [file.filename for file in valid_files]
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.exception("Error during PDF upload")
        error_msg = f"Error processing files: {str(e)}"
        return JSONResponse(
            status_code=500, 
            content={"error": error_msg, "detail": "Please check your files and try again"}
        )