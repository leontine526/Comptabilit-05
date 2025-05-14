import re
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Patterns réguliers pour l'extraction d'informations
AMOUNT_PATTERN = r'(\d{1,3}(?:\s?\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)'
DATE_PATTERN = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
INVOICE_PATTERN = r'(?:facture|invoice|fact)[^\d]*(\d+[-/]?\d*)'
TVA_PATTERN = r'(?:tva|t\.v\.a\.|taxe).*?(\d{1,2}(?:,\d{1,2})?)\s*%'
ACCOUNT_PATTERN = r'(?:compte|account)\s*(?:n[o°]?)?\s*[:.]?\s*(\d{1,6})'

def extract_data_from_text(text):
    """
    Extract structured data from OCR text using regular expressions
    Returns a dictionary with extracted information
    """
    if not text:
        logger.warning("No text provided for extraction")
        return None
    
    logger.info(f"Extracting data from text ({len(text)} characters)")
    
    # Initialize result dictionary
    result = {
        'date': None,
        'total_amount': None,
        'tva_amount': None,
        'invoice_number': None,
        'amounts': [],
        'accounts': [],
        'probable_type': 'unknown'
    }
    
    # Extract date (prioritize DD/MM/YYYY format)
    date_matches = re.findall(DATE_PATTERN, text)
    if date_matches:
        # Try to parse date
        for date_str in date_matches:
            try:
                # Replace possible separators with /
                date_str = re.sub(r'[-.]', '/', date_str)
                
                # Try different date formats
                for fmt in ['%d/%m/%Y', '%d/%m/%y']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        result['date'] = date_obj.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue
                        
                if result['date']:
                    break
            except Exception as e:
                logger.warning(f"Failed to parse date {date_str}: {str(e)}")
    
    # Extract all monetary amounts
    amount_matches = re.findall(AMOUNT_PATTERN, text)
    if amount_matches:
        # Clean and convert to float
        amounts = []
        for amount_str in amount_matches:
            try:
                # Remove spaces and replace comma with dot
                clean_amount = amount_str.replace(' ', '').replace(',', '.')
                amount = float(clean_amount)
                if amount > 0:
                    amounts.append(amount)
            except ValueError:
                continue
        
        # Sort amounts in descending order
        amounts.sort(reverse=True)
        result['amounts'] = amounts
        
        # The largest amount is likely the total
        if amounts:
            result['total_amount'] = amounts[0]
    
    # Extract invoice number
    invoice_matches = re.findall(INVOICE_PATTERN, text, re.IGNORECASE)
    if invoice_matches:
        result['invoice_number'] = invoice_matches[0]
    
    # Extract TVA information
    tva_matches = re.findall(TVA_PATTERN, text, re.IGNORECASE)
    if tva_matches:
        try:
            tva_rate = float(tva_matches[0].replace(',', '.'))
            
            # If we have a total amount, calculate TVA amount
            if result['total_amount']:
                # Assuming the total is tax inclusive
                result['tva_amount'] = round(result['total_amount'] * tva_rate / (100 + tva_rate), 2)
        except (ValueError, IndexError):
            pass
    
    # Extract account numbers
    account_matches = re.findall(ACCOUNT_PATTERN, text, re.IGNORECASE)
    if account_matches:
        result['accounts'] = account_matches
    
    # Determine document type based on keywords
    if re.search(r'\b(?:facture|invoice|fact)\b', text, re.IGNORECASE):
        result['probable_type'] = 'invoice'
    elif re.search(r'\b(?:reçu|receipt|ticket)\b', text, re.IGNORECASE):
        result['probable_type'] = 'receipt'
    elif re.search(r'\b(?:relevé|statement|bancaire)\b', text, re.IGNORECASE):
        result['probable_type'] = 'bank_statement'
    
    # Log extracted data for debugging
    logger.debug(f"Extracted data: {json.dumps(result, default=str)}")
    
    return result