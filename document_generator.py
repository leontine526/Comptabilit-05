import os
import json
import logging
from datetime import datetime
from decimal import Decimal

import xlsxwriter
from jinja2 import Environment, FileSystemLoader

from app import app, db
from models import Exercise, Account, Transaction, TransactionItem
from utils import format_currency, format_date, get_account_balance, get_exercise_totals

logger = logging.getLogger(__name__)

def generate_report(exercise_id, report_type, format='html', start_date=None, end_date=None, account_id=None):
    """Generate a report for the specified exercise and type"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(exercise.user_id), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{report_type}_{exercise.id}_{timestamp}.{format}"
    file_path = os.path.join(reports_dir, filename)
    
    # Generate report based on type
    if report_type == 'balance_sheet':
        data = generate_balance_sheet(exercise_id, end_date)
    elif report_type == 'income_statement':
        data = generate_income_statement(exercise_id, start_date, end_date)
    elif report_type == 'trial_balance':
        data = generate_trial_balance(exercise_id, end_date)
    elif report_type == 'general_ledger':
        data = generate_general_ledger(exercise_id, start_date, end_date)
    elif report_type == 'account_statement':
        if not account_id:
            raise ValueError("Account ID is required for account statement reports")
        data = generate_account_statement(exercise_id, account_id, start_date, end_date)
    else:
        raise ValueError(f"Unsupported report type: {report_type}")
    
    # Generate report file
    if format == 'html':
        generate_html_report(data, file_path, report_type)
    elif format == 'xlsx':
        generate_excel_report(data, file_path, report_type)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return file_path

def generate_balance_sheet(exercise_id, end_date=None):
    """Generate balance sheet data"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not end_date:
        end_date = exercise.end_date
    
    data = {
        'exercise': exercise,
        'end_date': end_date,
        'assets': [],
        'liabilities': [],
        'equity': [],
        'total_assets': Decimal('0'),
        'total_liabilities': Decimal('0'),
        'total_equity': Decimal('0')
    }
    
    # Get asset accounts
    asset_accounts = Account.query.filter_by(account_type='asset', is_active=True).order_by(Account.account_number).all()
    for account in asset_accounts:
        balance = get_account_balance(account.id, exercise_id, end_date)
        if balance != 0:
            data['assets'].append({
                'account': account,
                'balance': balance
            })
            data['total_assets'] += balance
    
    # Get liability accounts
    liability_accounts = Account.query.filter_by(account_type='liability', is_active=True).order_by(Account.account_number).all()
    for account in liability_accounts:
        balance = get_account_balance(account.id, exercise_id, end_date)
        if balance != 0:
            data['liabilities'].append({
                'account': account,
                'balance': balance
            })
            data['total_liabilities'] += balance
    
    # Get equity accounts
    equity_accounts = Account.query.filter_by(account_type='equity', is_active=True).order_by(Account.account_number).all()
    for account in equity_accounts:
        balance = get_account_balance(account.id, exercise_id, end_date)
        if balance != 0:
            data['equity'].append({
                'account': account,
                'balance': balance
            })
            data['total_equity'] += balance
    
    # Calculate retained earnings (net income/loss for the period)
    totals = get_exercise_totals(exercise_id)
    net_income = totals['net_income']
    
    data['net_income'] = net_income
    data['total_equity'] += net_income
    
    # Add net income to equity section if not zero
    if net_income != 0:
        data['equity'].append({
            'account': {'account_number': '', 'name': 'Résultat net de la période'},
            'balance': net_income
        })
    
    # Check if balance sheet balances
    data['is_balanced'] = (data['total_assets'] == (data['total_liabilities'] + data['total_equity']))
    
    return data

def generate_income_statement(exercise_id, start_date=None, end_date=None):
    """Generate income statement data"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not start_date:
        start_date = exercise.start_date
    
    if not end_date:
        end_date = exercise.end_date
    
    data = {
        'exercise': exercise,
        'start_date': start_date,
        'end_date': end_date,
        'revenues': [],
        'expenses': [],
        'total_revenues': Decimal('0'),
        'total_expenses': Decimal('0'),
        'net_income': Decimal('0')
    }
    
    # Get revenue accounts
    revenue_accounts = Account.query.filter_by(account_type='revenue', is_active=True).order_by(Account.account_number).all()
    
    # Get transaction items for revenues
    for account in revenue_accounts:
        balance = Decimal('0')
        
        # Get all transactions for this account in the date range
        query = db.session.query(
            TransactionItem.account_id,
            db.func.sum(TransactionItem.credit_amount - TransactionItem.debit_amount).label('balance')
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            TransactionItem.account_id == account.id,
            Transaction.exercise_id == exercise_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.is_posted == True
        ).group_by(
            TransactionItem.account_id
        )
        
        result = query.first()
        
        if result:
            balance = result.balance
        
        if balance != 0:
            data['revenues'].append({
                'account': account,
                'balance': balance
            })
            data['total_revenues'] += balance
    
    # Get expense accounts
    expense_accounts = Account.query.filter_by(account_type='expense', is_active=True).order_by(Account.account_number).all()
    
    # Get transaction items for expenses
    for account in expense_accounts:
        balance = Decimal('0')
        
        # Get all transactions for this account in the date range
        query = db.session.query(
            TransactionItem.account_id,
            db.func.sum(TransactionItem.debit_amount - TransactionItem.credit_amount).label('balance')
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            TransactionItem.account_id == account.id,
            Transaction.exercise_id == exercise_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.is_posted == True
        ).group_by(
            TransactionItem.account_id
        )
        
        result = query.first()
        
        if result:
            balance = result.balance
        
        if balance != 0:
            data['expenses'].append({
                'account': account,
                'balance': balance
            })
            data['total_expenses'] += balance
    
    # Calculate net income
    data['net_income'] = data['total_revenues'] - data['total_expenses']
    
    return data

def generate_trial_balance(exercise_id, end_date=None):
    """Generate trial balance data"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not end_date:
        end_date = exercise.end_date
    
    data = {
        'exercise': exercise,
        'end_date': end_date,
        'accounts': [],
        'total_debit': Decimal('0'),
        'total_credit': Decimal('0')
    }
    
    # Get all active accounts
    accounts = Account.query.filter_by(is_active=True).order_by(Account.account_number).all()
    
    for account in accounts:
        # Get debit and credit totals for this account
        query = db.session.query(
            db.func.sum(TransactionItem.debit_amount).label('total_debit'),
            db.func.sum(TransactionItem.credit_amount).label('total_credit')
        ).join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            TransactionItem.account_id == account.id,
            Transaction.exercise_id == exercise_id,
            Transaction.transaction_date <= end_date,
            Transaction.is_posted == True
        )
        
        result = query.first()
        
        total_debit = result.total_debit or Decimal('0')
        total_credit = result.total_credit or Decimal('0')
        
        # Determine final balance and debit/credit values for trial balance
        if total_debit > total_credit:
            debit_balance = total_debit - total_credit
            credit_balance = Decimal('0')
        else:
            debit_balance = Decimal('0')
            credit_balance = total_credit - total_debit
        
        if debit_balance != 0 or credit_balance != 0:
            data['accounts'].append({
                'account': account,
                'debit': debit_balance,
                'credit': credit_balance
            })
            
            data['total_debit'] += debit_balance
            data['total_credit'] += credit_balance
    
    # Check if trial balance balances
    data['is_balanced'] = (data['total_debit'] == data['total_credit'])
    
    return data

def generate_general_ledger(exercise_id, start_date=None, end_date=None):
    """Generate general ledger data"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    if not start_date:
        start_date = exercise.start_date
    
    if not end_date:
        end_date = exercise.end_date
    
    data = {
        'exercise': exercise,
        'start_date': start_date,
        'end_date': end_date,
        'accounts': []
    }
    
    # Get all active accounts
    accounts = Account.query.filter_by(is_active=True).order_by(Account.account_number).all()
    
    for account in accounts:
        account_data = {
            'account': account,
            'transactions': [],
            'opening_balance': Decimal('0'),
            'closing_balance': Decimal('0'),
            'total_debit': Decimal('0'),
            'total_credit': Decimal('0')
        }
        
        # Calculate opening balance (balance at start_date - 1 day)
        opening_balance = get_account_balance(account.id, exercise_id, start_date)
        account_data['opening_balance'] = opening_balance
        
        # Get all transactions for this account in the date range
        transaction_items = TransactionItem.query.join(
            Transaction, TransactionItem.transaction_id == Transaction.id
        ).filter(
            TransactionItem.account_id == account.id,
            Transaction.exercise_id == exercise_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date,
            Transaction.is_posted == True
        ).order_by(
            Transaction.transaction_date
        ).all()
        
        running_balance = opening_balance
        
        for item in transaction_items:
            transaction = Transaction.query.get(item.transaction_id)
            
            if account.account_type in ['asset', 'expense']:
                # For assets and expenses, debits increase, credits decrease
                running_balance += item.debit_amount - item.credit_amount
            else:
                # For liabilities, equity, and revenues, credits increase, debits decrease
                running_balance += item.credit_amount - item.debit_amount
            
            account_data['transactions'].append({
                'date': transaction.transaction_date,
                'reference': transaction.reference,
                'description': item.description or transaction.description,
                'debit': item.debit_amount,
                'credit': item.credit_amount,
                'balance': running_balance
            })
            
            account_data['total_debit'] += item.debit_amount
            account_data['total_credit'] += item.credit_amount
        
        account_data['closing_balance'] = running_balance
        
        # Only add accounts with transactions or non-zero balances
        if account_data['transactions'] or account_data['opening_balance'] != 0:
            data['accounts'].append(account_data)
    
    return data

def generate_account_statement(exercise_id, account_id, start_date=None, end_date=None):
    """Generate account statement data"""
    exercise = Exercise.query.get_or_404(exercise_id)
    account = Account.query.get_or_404(account_id)
    
    if not start_date:
        start_date = exercise.start_date
    
    if not end_date:
        end_date = exercise.end_date
    
    data = {
        'exercise': exercise,
        'account': account,
        'start_date': start_date,
        'end_date': end_date,
        'transactions': [],
        'opening_balance': Decimal('0'),
        'closing_balance': Decimal('0'),
        'total_debit': Decimal('0'),
        'total_credit': Decimal('0')
    }
    
    # Calculate opening balance (balance at start_date - 1 day)
    opening_balance = get_account_balance(account_id, exercise_id, start_date)
    data['opening_balance'] = opening_balance
    
    # Get all transactions for this account in the date range
    transaction_items = TransactionItem.query.join(
        Transaction, TransactionItem.transaction_id == Transaction.id
    ).filter(
        TransactionItem.account_id == account_id,
        Transaction.exercise_id == exercise_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
        Transaction.is_posted == True
    ).order_by(
        Transaction.transaction_date
    ).all()
    
    running_balance = opening_balance
    
    for item in transaction_items:
        transaction = Transaction.query.get(item.transaction_id)
        
        if account.account_type in ['asset', 'expense']:
            # For assets and expenses, debits increase, credits decrease
            running_balance += item.debit_amount - item.credit_amount
        else:
            # For liabilities, equity, and revenues, credits increase, debits decrease
            running_balance += item.credit_amount - item.debit_amount
        
        data['transactions'].append({
            'date': transaction.transaction_date,
            'reference': transaction.reference,
            'description': item.description or transaction.description,
            'debit': item.debit_amount,
            'credit': item.credit_amount,
            'balance': running_balance
        })
        
        data['total_debit'] += item.debit_amount
        data['total_credit'] += item.credit_amount
    
    data['closing_balance'] = running_balance
    
    return data

def generate_html_report(data, file_path, report_type):
    """Generate an HTML report from the data"""
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    
    # Define template name based on report type
    template_name = f"reports/{report_type}.html"
    
    # Get template
    try:
        template = env.get_template(template_name)
    except:
        # If template doesn't exist, use a generic one
        template = env.get_template("reports/generic.html")
    
    # Add helper functions to template context
    data['format_currency'] = format_currency
    data['format_date'] = format_date
    
    # Render template
    html = template.render(**data)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_excel_report(data, file_path, report_type):
    """Generate an Excel report from the data"""
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet(report_type.replace('_', ' ').title())
    
    # Define styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    subheader_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'num_format': '#,##0.00 "XOF"',
        'border': 1
    })
    
    total_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'num_format': '#,##0.00 "XOF"',
        'border': 1,
        'top': 2,
        'bottom': 2
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Generate report based on type
    if report_type == 'balance_sheet':
        generate_excel_balance_sheet(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format)
    elif report_type == 'income_statement':
        generate_excel_income_statement(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format)
    elif report_type == 'trial_balance':
        generate_excel_trial_balance(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format)
    elif report_type == 'general_ledger':
        generate_excel_general_ledger(worksheet, data, header_format, subheader_format, date_format, currency_format, total_format, cell_format)
    elif report_type == 'account_statement':
        generate_excel_account_statement(worksheet, data, header_format, subheader_format, date_format, currency_format, total_format, cell_format)
    
    workbook.close()

def generate_excel_balance_sheet(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format):
    """Generate balance sheet in Excel format"""
    # Set column widths
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:C', 20)
    
    # Write title
    worksheet.merge_range('A1:C1', f"BILAN AU {format_date(data['end_date'])}", header_format)
    worksheet.merge_range('A2:C2', f"Exercice: {data['exercise'].name}", subheader_format)
    
    # Write headers
    row = 4
    worksheet.write(row, 0, "N° Compte", header_format)
    worksheet.write(row, 1, "Compte", header_format)
    worksheet.write(row, 2, "Montant", header_format)
    row += 1
    
    # Write assets
    worksheet.merge_range(f'A{row+1}:C{row+1}', "ACTIF", subheader_format)
    row += 1
    
    for asset in data['assets']:
        worksheet.write(row, 0, asset['account'].account_number, cell_format)
        worksheet.write(row, 1, asset['account'].name, cell_format)
        worksheet.write(row, 2, float(asset['balance']), currency_format)
        row += 1
    
    # Write total assets
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL ACTIF", total_format)
    worksheet.write(row, 2, float(data['total_assets']), total_format)
    row += 2
    
    # Write liabilities
    worksheet.merge_range(f'A{row}:C{row}', "PASSIF", subheader_format)
    row += 1
    
    for liability in data['liabilities']:
        worksheet.write(row, 0, liability['account'].account_number, cell_format)
        worksheet.write(row, 1, liability['account'].name, cell_format)
        worksheet.write(row, 2, float(liability['balance']), currency_format)
        row += 1
    
    # Write total liabilities
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL PASSIF", total_format)
    worksheet.write(row, 2, float(data['total_liabilities']), total_format)
    row += 2
    
    # Write equity
    worksheet.merge_range(f'A{row}:C{row}', "CAPITAUX PROPRES", subheader_format)
    row += 1
    
    for equity in data['equity']:
        account_number = equity['account'].account_number if hasattr(equity['account'], 'account_number') else ""
        worksheet.write(row, 0, account_number, cell_format)
        worksheet.write(row, 1, equity['account'].name, cell_format)
        worksheet.write(row, 2, float(equity['balance']), currency_format)
        row += 1
    
    # Write total equity
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL CAPITAUX PROPRES", total_format)
    worksheet.write(row, 2, float(data['total_equity']), total_format)
    row += 2
    
    # Write total liabilities and equity
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL PASSIF ET CAPITAUX PROPRES", total_format)
    worksheet.write(row, 2, float(data['total_liabilities'] + data['total_equity']), total_format)

def generate_excel_income_statement(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format):
    """Generate income statement in Excel format"""
    # Set column widths
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:C', 20)
    
    # Write title
    worksheet.merge_range('A1:C1', f"COMPTE DE RÉSULTAT DU {format_date(data['start_date'])} AU {format_date(data['end_date'])}", header_format)
    worksheet.merge_range('A2:C2', f"Exercice: {data['exercise'].name}", subheader_format)
    
    # Write headers
    row = 4
    worksheet.write(row, 0, "N° Compte", header_format)
    worksheet.write(row, 1, "Compte", header_format)
    worksheet.write(row, 2, "Montant", header_format)
    row += 1
    
    # Write revenues
    worksheet.merge_range(f'A{row+1}:C{row+1}', "PRODUITS", subheader_format)
    row += 1
    
    for revenue in data['revenues']:
        worksheet.write(row, 0, revenue['account'].account_number, cell_format)
        worksheet.write(row, 1, revenue['account'].name, cell_format)
        worksheet.write(row, 2, float(revenue['balance']), currency_format)
        row += 1
    
    # Write total revenues
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL PRODUITS", total_format)
    worksheet.write(row, 2, float(data['total_revenues']), total_format)
    row += 2
    
    # Write expenses
    worksheet.merge_range(f'A{row}:C{row}', "CHARGES", subheader_format)
    row += 1
    
    for expense in data['expenses']:
        worksheet.write(row, 0, expense['account'].account_number, cell_format)
        worksheet.write(row, 1, expense['account'].name, cell_format)
        worksheet.write(row, 2, float(expense['balance']), currency_format)
        row += 1
    
    # Write total expenses
    worksheet.merge_range(f'A{row}:B{row}', "TOTAL CHARGES", total_format)
    worksheet.write(row, 2, float(data['total_expenses']), total_format)
    row += 2
    
    # Write net income
    worksheet.merge_range(f'A{row}:B{row}', "RÉSULTAT NET", total_format)
    worksheet.write(row, 2, float(data['net_income']), total_format)

def generate_excel_trial_balance(worksheet, data, header_format, subheader_format, currency_format, total_format, cell_format):
    """Generate trial balance in Excel format"""
    # Set column widths
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 40)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    
    # Write title
    worksheet.merge_range('A1:D1', f"BALANCE GÉNÉRALE AU {format_date(data['end_date'])}", header_format)
    worksheet.merge_range('A2:D2', f"Exercice: {data['exercise'].name}", subheader_format)
    
    # Write headers
    row = 4
    worksheet.write(row, 0, "N° Compte", header_format)
    worksheet.write(row, 1, "Compte", header_format)
    worksheet.write(row, 2, "Débit", header_format)
    worksheet.write(row, 3, "Crédit", header_format)
    row += 1
    
    # Write accounts
    for account_data in data['accounts']:
        worksheet.write(row, 0, account_data['account'].account_number, cell_format)
        worksheet.write(row, 1, account_data['account'].name, cell_format)
        worksheet.write(row, 2, float(account_data['debit']), currency_format)
        worksheet.write(row, 3, float(account_data['credit']), currency_format)
        row += 1
    
    # Write totals
    worksheet.merge_range(f'A{row}:B{row}', "TOTAUX", total_format)
    worksheet.write(row, 2, float(data['total_debit']), total_format)
    worksheet.write(row, 3, float(data['total_credit']), total_format)
    
    # Add note about balance
    row += 2
    if data['is_balanced']:
        worksheet.merge_range(f'A{row}:D{row}', "La balance est équilibrée.", cell_format)
    else:
        worksheet.merge_range(f'A{row}:D{row}', "ATTENTION: La balance n'est pas équilibrée!", cell_format)

def generate_excel_general_ledger(worksheet, data, header_format, subheader_format, date_format, currency_format, total_format, cell_format):
    """Generate general ledger in Excel format"""
    # Set column widths
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 15)
    
    # Write title
    worksheet.merge_range('A1:F1', f"GRAND LIVRE DU {format_date(data['start_date'])} AU {format_date(data['end_date'])}", header_format)
    worksheet.merge_range('A2:F2', f"Exercice: {data['exercise'].name}", subheader_format)
    
    row = 4
    
    # For each account
    for account_data in data['accounts']:
        # Write account header
        worksheet.merge_range(f'A{row}:F{row}', f"{account_data['account'].account_number} - {account_data['account'].name}", subheader_format)
        row += 1
        
        # Write column headers
        worksheet.write(row, 0, "Date", header_format)
        worksheet.write(row, 1, "Référence", header_format)
        worksheet.write(row, 2, "Description", header_format)
        worksheet.write(row, 3, "Débit", header_format)
        worksheet.write(row, 4, "Crédit", header_format)
        worksheet.write(row, 5, "Solde", header_format)
        row += 1
        
        # Write opening balance
        worksheet.merge_range(f'A{row}:C{row}', "Solde d'ouverture", cell_format)
        worksheet.write(row, 3, "", cell_format)
        worksheet.write(row, 4, "", cell_format)
        worksheet.write(row, 5, float(account_data['opening_balance']), currency_format)
        row += 1
        
        # Write transactions
        for transaction in account_data['transactions']:
            worksheet.write(row, 0, transaction['date'], date_format)
            worksheet.write(row, 1, transaction['reference'], cell_format)
            worksheet.write(row, 2, transaction['description'], cell_format)
            worksheet.write(row, 3, float(transaction['debit']), currency_format)
            worksheet.write(row, 4, float(transaction['credit']), currency_format)
            worksheet.write(row, 5, float(transaction['balance']), currency_format)
            row += 1
        
        # Write totals
        worksheet.merge_range(f'A{row}:B{row}', "Totaux", total_format)
        worksheet.write(row, 2, "", total_format)
        worksheet.write(row, 3, float(account_data['total_debit']), total_format)
        worksheet.write(row, 4, float(account_data['total_credit']), total_format)
        worksheet.write(row, 5, float(account_data['closing_balance']), total_format)
        
        row += 3  # Add space between accounts
        
def generate_excel_account_statement(worksheet, data, header_format, subheader_format, date_format, currency_format, total_format, cell_format):
    """Generate account statement in Excel format"""
    # Set column widths
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 15)
    
    # Write title
    worksheet.merge_range('A1:F1', f"RELEVÉ DE COMPTE DU {format_date(data['start_date'])} AU {format_date(data['end_date'])}", header_format)
    worksheet.merge_range('A2:F2', f"Compte: {data['account'].account_number} - {data['account'].name}", subheader_format)
    worksheet.merge_range('A3:F3', f"Exercice: {data['exercise'].name}", subheader_format)
    
    row = 5
    
    # Write column headers
    worksheet.write(row, 0, "Date", header_format)
    worksheet.write(row, 1, "Référence", header_format)
    worksheet.write(row, 2, "Description", header_format)
    worksheet.write(row, 3, "Débit", header_format)
    worksheet.write(row, 4, "Crédit", header_format)
    worksheet.write(row, 5, "Solde", header_format)
    row += 1
    
    # Write opening balance
    worksheet.merge_range(f'A{row}:C{row}', "Solde d'ouverture", cell_format)
    worksheet.write(row, 3, "", cell_format)
    worksheet.write(row, 4, "", cell_format)
    worksheet.write(row, 5, float(data['opening_balance']), currency_format)
    row += 1
    
    # Write transactions
    for transaction in data['transactions']:
        worksheet.write(row, 0, transaction['date'], date_format)
        worksheet.write(row, 1, transaction['reference'], cell_format)
        worksheet.write(row, 2, transaction['description'], cell_format)
        worksheet.write(row, 3, float(transaction['debit']), currency_format)
        worksheet.write(row, 4, float(transaction['credit']), currency_format)
        worksheet.write(row, 5, float(transaction['balance']), currency_format)
        row += 1
    
    # Write totals
    worksheet.merge_range(f'A{row}:C{row}', "Totaux", total_format)
    worksheet.write(row, 3, float(data['total_debit']), total_format)
    worksheet.write(row, 4, float(data['total_credit']), total_format)
    worksheet.write(row, 5, float(data['closing_balance']), total_format)
