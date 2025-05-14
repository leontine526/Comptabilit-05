import logging
from datetime import datetime
import json
from app import db
from models import Document, Transaction, TransactionItem, Account, Exercise

logger = logging.getLogger(__name__)

def create_transaction_from_document(document_id, extracted_data):
    """
    Create a transaction based on the extracted data from a document
    Returns the transaction ID if successful, None otherwise
    """
    if not extracted_data:
        logger.warning("No extracted data provided")
        return None
    
    document = Document.query.get(document_id)
    if not document:
        logger.error(f"Document not found: {document_id}")
        return None
    
    logger.info(f"Creating transaction from document: {document.original_filename}")
    
    try:
        # Generate reference based on document type and number
        ref_prefix = 'FACT' if extracted_data.get('probable_type') == 'invoice' else 'DOC'
        reference = f"{ref_prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Use invoice number as reference if available
        if extracted_data.get('invoice_number'):
            reference = f"{ref_prefix}-{extracted_data.get('invoice_number')}"
        
        # Get transaction date from extracted data or use today
        transaction_date = None
        if extracted_data.get('date'):
            transaction_date = datetime.strptime(extracted_data.get('date'), '%Y-%m-%d').date()
        else:
            transaction_date = datetime.now().date()
        
        # Create transaction
        transaction = Transaction(
            reference=reference,
            transaction_date=transaction_date,
            description=f"Transaction générée automatiquement depuis {document.original_filename}",
            document_id=document_id,
            is_posted=False,  # Set as draft for review
            user_id=document.user_id,
            exercise_id=document.exercise_id
        )
        
        db.session.add(transaction)
        db.session.flush()  # To get transaction ID
        
        # Add transaction items based on document type and data
        success = add_transaction_items(transaction, extracted_data)
        if not success:
            db.session.rollback()
            logger.error("Failed to add transaction items")
            return None
        
        # Commit transaction
        db.session.commit()
        logger.info(f"Transaction created: {transaction.id}")
        return transaction.id
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating transaction: {str(e)}")
        return None

def add_transaction_items(transaction, extracted_data):
    """
    Add appropriate transaction items based on the document type and extracted data
    Returns True if successful, False otherwise
    """
    try:
        exercise = Exercise.query.get(transaction.exercise_id)
        if not exercise:
            return False
            
        # Extract total amount
        total_amount = extracted_data.get('total_amount')
        if not total_amount:
            logger.warning("No total amount extracted, using biggest amount available")
            amounts = extracted_data.get('amounts', [])
            if amounts:
                total_amount = max(amounts)
            else:
                logger.error("No amounts available")
                return False
        
        # Extract TVA amount
        tva_amount = extracted_data.get('tva_amount')
        
        # For invoices (create typical entries)
        if extracted_data.get('probable_type') == 'invoice':
            # Find appropriate accounts
            debit_account = find_suitable_account('6', exercise.id)  # Class 6: Expense
            credit_account_supplier = find_suitable_account('401', exercise.id)  # Supplier
            
            if tva_amount and tva_amount > 0:
                # With TVA
                net_amount = total_amount - tva_amount
                
                # Find TVA account
                tva_account = find_suitable_account('445', exercise.id)  # TVA account
                
                # Add expense item
                expense_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=debit_account.id,
                    description="Achat des marchandises",
                    debit_amount=net_amount,
                    credit_amount=0
                )
                db.session.add(expense_item)
                
                # Add TVA item
                tva_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=tva_account.id,
                    description="TVA récupérable",
                    debit_amount=tva_amount,
                    credit_amount=0
                )
                db.session.add(tva_item)
                
                # Add supplier credit
                supplier_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=credit_account_supplier.id,
                    description="à Fournisseur d'investissement corporelle",
                    debit_amount=0,
                    credit_amount=total_amount
                )
                db.session.add(supplier_item)
            else:
                # Without TVA
                # Add expense item
                expense_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=debit_account.id,
                    description="Achat des marchandises",
                    debit_amount=total_amount,
                    credit_amount=0
                )
                db.session.add(expense_item)
                
                # Add supplier credit
                supplier_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=credit_account_supplier.id,
                    description="à Fournisseur",
                    debit_amount=0,
                    credit_amount=total_amount
                )
                db.session.add(supplier_item)
        else:
            # For other document types, create a simple debit/credit entry
            debit_account = find_suitable_account('6', exercise.id)  # Class 6: Expense
            credit_account = find_suitable_account('5', exercise.id)  # Class 5: Cash/bank
            
            # Add expense item
            expense_item = TransactionItem(
                transaction_id=transaction.id,
                account_id=debit_account.id,
                description="Dépense diverse",
                debit_amount=total_amount,
                credit_amount=0
            )
            db.session.add(expense_item)
            
            # Add credit item
            credit_item = TransactionItem(
                transaction_id=transaction.id,
                account_id=credit_account.id,
                description="à Banque/Caisse",
                debit_amount=0,
                credit_amount=total_amount
            )
            db.session.add(credit_item)
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding transaction items: {str(e)}")
        return False

def find_suitable_account(account_prefix, exercise_id):
    """
    Find a suitable account that starts with the given prefix
    Returns the first active account found, or a default one if none found
    """
    # Try to find an account with the exact prefix
    account = Account.query.filter(
        Account.account_number.startswith(account_prefix),
        Account.is_active == True
    ).first()
    
    if account:
        return account
    
    # If no account found, try more generic prefix
    if len(account_prefix) > 1:
        return find_suitable_account(account_prefix[0], exercise_id)
    
    # If still no account found, return a default one
    return Account.query.filter(Account.is_active == True).first()

def get_transaction_balance(transaction_id):
    """
    Calculate the balance of a transaction (should be zero for balanced transactions)
    """
    items = TransactionItem.query.filter_by(transaction_id=transaction_id).all()
    
    total_debit = sum(item.debit_amount for item in items)
    total_credit = sum(item.credit_amount for item in items)
    
    return abs(total_debit - total_credit)

def post_transaction(transaction_id):
    """
    Post a transaction, making it part of the official accounting records
    Returns True if successful, False otherwise
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        logger.error(f"Transaction not found: {transaction_id}")
        return False
    
    # Check if the transaction is balanced
    balance = get_transaction_balance(transaction_id)
    if balance > 0.01:  # Allow small rounding differences
        logger.error(f"Transaction {transaction_id} is not balanced: {balance}")
        return False
    
    # Mark as posted
    transaction.is_posted = True
    db.session.commit()
    logger.info(f"Transaction {transaction_id} posted successfully")
    
    return True

def auto_categorize_transaction(transaction_id):
    """
    Attempt to automatically categorize a transaction based on its description
    Updates transaction items with suggested accounts
    Returns True if changes were made, False otherwise
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return False
    
    # Get all active accounts
    accounts = Account.query.filter_by(is_active=True).all()
    
    # Create a simple mapping of keywords to account numbers
    keyword_mapping = {
        'loyer': '613',        # Rent
        'électricité': '6051',  # Electricity
        'eau': '6052',         # Water
        'téléphone': '626',    # Phone
        'internet': '626',     # Internet
        'salaire': '661',      # Salary
        'fourniture': '604',   # Supplies
        'assurance': '616',    # Insurance
        'banque': '627',       # Bank fees
        'publicité': '623',    # Advertising
        'carburant': '6114',   # Fuel
        'voyage': '6251',      # Travel expenses
        'repas': '6252',       # Meals
        'client': '411',       # Clients
        'fournisseur': '401',  # Suppliers
        'tva': '445',          # VAT
        'impôt': '444',        # Taxes
        'vente': '707',        # Sales
        'achat': '601'         # Purchases
    }
    
    # Check transaction description for keywords
    description = transaction.description.lower()
    matched_accounts = {}
    
    for keyword, account_number in keyword_mapping.items():
        if keyword in description:
            # Find the account with this number
            account = next((a for a in accounts if a.account_number.startswith(account_number)), None)
            if account:
                matched_accounts[keyword] = account
    
    # If we found matches, update the transaction items
    if matched_accounts:
        # For now, just log the matches
        logger.info(f"Auto-categorization found matches for transaction {transaction_id}: {matched_accounts}")
        return True
    
    return False