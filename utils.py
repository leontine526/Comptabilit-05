import os
import logging
from decimal import Decimal
from datetime import datetime
from app import app, db

logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS', 
                               {'pdf', 'png', 'jpg', 'jpeg', 'tiff'})

def ensure_upload_dir():
    """Ensure the upload directory exists"""
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

def format_amount(amount):
    """Format amount with thousands separator and 2 decimal places"""
    if amount is None:
        return "0,00"
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")

def parse_amount(amount_str):
    """Parse amount string into float"""
    if not amount_str:
        return 0.0
    
    # Remove spaces and replace comma with dot
    clean_amount = amount_str.replace(' ', '').replace(',', '.')
    try:
        return float(clean_amount)
    except ValueError:
        logger.warning(f"Failed to parse amount: {amount_str}")
        return 0.0

def get_date_range_for_exercise(exercise):
    """Get date range for an exercise as string"""
    if not exercise:
        return ""
    
    start_date = exercise.start_date.strftime('%d/%m/%Y')
    end_date = exercise.end_date.strftime('%d/%m/%Y')
    
    return f"{start_date} - {end_date}"

def format_currency(amount):
    """Format a decimal amount as currency with XOF"""
    if amount is None:
        return "0 XOF"
    return f"{amount:,.2f} XOF".replace(",", " ")

def format_date(date_obj):
    """Format a date object as dd/mm/yyyy"""
    if date_obj is None:
        return ""
    return date_obj.strftime('%d/%m/%Y')

def get_account_balance(account_id, exercise_id, end_date=None):
    """Calculate account balance until the specified date"""
    from models import Account, Transaction, TransactionItem
    
    account = Account.query.get(account_id)
    if not account:
        return Decimal('0')
    
    # Default end_date to current date if not provided
    if end_date is None:
        end_date = datetime.now().date()
    
    # Get all transactions for this account until the end_date
    query = db.session.query(
        db.func.sum(TransactionItem.debit_amount).label('total_debit'),
        db.func.sum(TransactionItem.credit_amount).label('total_credit')
    ).join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).filter(
        TransactionItem.account_id == account_id,
        Transaction.exercise_id == exercise_id,
        Transaction.transaction_date <= end_date,
        Transaction.is_posted == True
    )
    
    result = query.first()
    
    total_debit = result.total_debit or Decimal('0')
    total_credit = result.total_credit or Decimal('0')
    
    # Calculate balance based on account type
    if account.account_type in ['asset', 'expense']:
        # For assets and expenses, debit increases, credit decreases
        balance = total_debit - total_credit
    else:
        # For liabilities, equity, and revenues, credit increases, debit decreases
        balance = total_credit - total_debit
    
    return balance

def get_exercise_totals(exercise_id):
    """Calculate exercise financial totals"""
    from models import Account
    
    # Get all asset accounts
    assets = Account.query.filter_by(account_type='asset', is_active=True).all()
    total_assets = sum(get_account_balance(a.id, exercise_id) for a in assets)
    
    # Get all liability accounts
    liabilities = Account.query.filter_by(account_type='liability', is_active=True).all()
    total_liabilities = sum(get_account_balance(a.id, exercise_id) for a in liabilities)
    
    # Get all equity accounts
    equity = Account.query.filter_by(account_type='equity', is_active=True).all()
    total_equity = sum(get_account_balance(a.id, exercise_id) for a in equity)
    
    # Get all revenue accounts
    revenues = Account.query.filter_by(account_type='revenue', is_active=True).all()
    total_revenues = sum(get_account_balance(a.id, exercise_id) for a in revenues)
    
    # Get all expense accounts
    expenses = Account.query.filter_by(account_type='expense', is_active=True).all()
    total_expenses = sum(get_account_balance(a.id, exercise_id) for a in expenses)
    
    # Calculate net income
    net_income = total_revenues - total_expenses
    
    return {
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'total_equity': total_equity,
        'total_revenues': total_revenues,
        'total_expenses': total_expenses,
        'net_income': net_income
    }