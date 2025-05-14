import os
import cv2
import logging
import pytesseract
from models import Document
from app import db

logger = logging.getLogger(__name__)

# Configure Tesseract path if needed
if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_CMD")

def process_document_ocr(document_id):
    """
    Process a document with OCR to extract text
    Returns the extracted text
    """
    document = Document.query.get(document_id)
    if not document:
        logger.error(f"Document not found: {document_id}")
        return None
    
    logger.info(f"Processing document: {document.original_filename}")
    
    try:
        # Load image
        image = cv2.imread(document.filename)
        if image is None:
            logger.error(f"Failed to load image: {document.filename}")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing to improve OCR
        # Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Perform OCR with Tesseract
        lang = os.environ.get("TESSERACT_LANG", "fra")  # Default to French
        config = r'--oem 3 --psm 6'  # Assume single uniform block of text
        text = pytesseract.image_to_string(denoised, lang=lang, config=config)
        
        # Update document with extracted text
        document.processing_result = text
        document.processed = True
        db.session.commit()
        
        logger.info(f"Document processed successfully: {len(text)} characters extracted")
        return text
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return None