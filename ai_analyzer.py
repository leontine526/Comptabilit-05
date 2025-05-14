import logging
import json
import requests
import re
from datetime import datetime
from decimal import Decimal

from app import db
from models import Exercise, Transaction, TransactionItem, Account
from utils import DecimalEncoder, get_account_balance, get_exercise_totals
from config import Config

logger = logging.getLogger(__name__)

def get_exercise_analysis(exercise_id):
    """
    Get a comprehensive analysis of an accounting exercise using AI
    Returns analysis text and key financial indicators
    """
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Calculate key financial indicators
    indicators = calculate_financial_indicators(exercise_id)
    
    # If AI analysis is disabled, return just the indicators
    if not Config.ENABLE_AI_ANALYSIS:
        return {
            'financial_indicators': indicators,
            'analysis_text': "L'analyse par IA est désactivée. Veuillez activer cette fonctionnalité dans les paramètres.",
            'recommendations': ["L'analyse par IA est désactivée."]
        }
    
    # Get exercise data for AI analysis
    exercise_data = prepare_exercise_data(exercise_id)
    
    # Perform AI analysis
    analysis = perform_ai_analysis(exercise_data, indicators)
    
    # Extract recommendations from analysis
    recommendations = extract_recommendations(analysis)
    
    return {
        'financial_indicators': indicators,
        'analysis_text': analysis,
        'recommendations': recommendations
    }

def calculate_financial_indicators(exercise_id):
    """
    Calculate key financial indicators for the exercise
    Returns a dictionary of indicators
    """
    # Get exercise totals
    totals = get_exercise_totals(exercise_id)
    
    # Extract individual values
    total_assets = totals.get('asset', Decimal('0'))
    total_liabilities = totals.get('liability', Decimal('0'))
    total_equity = totals.get('equity', Decimal('0'))
    total_revenue = totals.get('revenue', Decimal('0'))
    total_expenses = totals.get('expense', Decimal('0'))
    net_income = totals.get('net_income', Decimal('0'))
    
    # Calculate liquidity ratio (current assets / current liabilities)
    current_assets = get_account_type_balance(exercise_id, ['10', '11', '12', '13', '14'])
    current_liabilities = get_account_type_balance(exercise_id, ['40', '41', '42', '43'])
    
    try:
        liquidity_ratio = float(current_assets / current_liabilities) if current_liabilities else 0
    except (ZeroDivisionError, TypeError):
        liquidity_ratio = 0
    
    # Calculate debt ratio (total liabilities / total assets)
    try:
        debt_ratio = float(total_liabilities / total_assets) if total_assets else 0
    except (ZeroDivisionError, TypeError):
        debt_ratio = 0
    
    # Calculate profit margin (net income / total revenue)
    try:
        profit_margin = float(net_income / total_revenue) if total_revenue else 0
    except (ZeroDivisionError, TypeError):
        profit_margin = 0
    
    # Calculate ROE (Return on Equity)
    try:
        roe = float(net_income / total_equity) if total_equity else 0
    except (ZeroDivisionError, TypeError):
        roe = 0
    
    # Calculate asset turnover (total revenue / total assets)
    try:
        asset_turnover = float(total_revenue / total_assets) if total_assets else 0
    except (ZeroDivisionError, TypeError):
        asset_turnover = 0
    
    # Return all indicators
    return {
        'total_assets': float(total_assets),
        'total_liabilities': float(total_liabilities),
        'total_equity': float(total_equity),
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'net_income': float(net_income),
        'liquidity_ratio': liquidity_ratio,
        'debt_ratio': debt_ratio,
        'profit_margin': profit_margin,
        'roe': roe,
        'asset_turnover': asset_turnover
    }

def get_account_type_balance(exercise_id, account_prefixes):
    """Get the balance for accounts starting with specific prefixes"""
    total_balance = Decimal('0')
    
    for prefix in account_prefixes:
        accounts = Account.query.filter(
            Account.account_number.like(f"{prefix}%"),
            Account.is_active == True
        ).all()
        
        for account in accounts:
            balance = get_account_balance(account.id, exercise_id)
            total_balance += balance
    
    return total_balance

def prepare_exercise_data(exercise_id):
    """
    Prepare exercise data for AI analysis
    Returns a dictionary with exercise information
    """
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Basic exercise information
    data = {
        'exercise_name': exercise.name,
        'start_date': exercise.start_date.strftime('%Y-%m-%d'),
        'end_date': exercise.end_date.strftime('%Y-%m-%d'),
        'description': exercise.description,
        'is_closed': exercise.is_closed
    }
    
    # Get account data
    accounts_data = []
    accounts = Account.query.filter_by(is_active=True).all()
    
    for account in accounts:
        balance = get_account_balance(account.id, exercise_id)
        
        if balance != 0:
            accounts_data.append({
                'account_number': account.account_number,
                'name': account.name,
                'type': account.account_type,
                'balance': float(balance)
            })
    
    data['accounts'] = accounts_data
    
    # Get transaction data
    transactions_data = []
    transactions = Transaction.query.filter_by(exercise_id=exercise_id).order_by(Transaction.transaction_date).all()
    
    for transaction in transactions:
        transaction_data = {
            'reference': transaction.reference,
            'date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'description': transaction.description,
            'is_posted': transaction.is_posted,
            'items': []
        }
        
        items = TransactionItem.query.filter_by(transaction_id=transaction.id).all()
        
        for item in items:
            account = Account.query.get(item.account_id)
            
            transaction_data['items'].append({
                'account_number': account.account_number,
                'account_name': account.name,
                'debit': float(item.debit_amount),
                'credit': float(item.credit_amount)
            })
        
        transactions_data.append(transaction_data)
    
    # Limit the number of transactions if there are too many
    if len(transactions_data) > 50:
        transactions_data = transactions_data[:50]
        data['transaction_count'] = len(transactions)
        data['transactions_limited'] = True
    
    data['transactions'] = transactions_data
    
    return data

def perform_ai_analysis(exercise_data, indicators):
    """
    Perform AI analysis on the exercise data using Ollama API
    Returns analysis text
    """
    try:
        # Prepare prompt for AI
        prompt = f"""
En tant qu'expert-comptable spécialisé dans le référentiel OHADA, analysez cet exercice comptable et fournissez des conseils détaillés.

INFORMATIONS SUR L'EXERCICE:
Nom: {exercise_data['exercise_name']}
Période: du {exercise_data['start_date']} au {exercise_data['end_date']}
{exercise_data.get('description', '')}

INDICATEURS FINANCIERS:
- Total Actif: {indicators['total_assets']} XOF
- Total Passif: {indicators['total_liabilities']} XOF
- Total Capitaux Propres: {indicators['total_equity']} XOF
- Chiffre d'Affaires: {indicators['total_revenue']} XOF
- Total Charges: {indicators['total_expenses']} XOF
- Résultat Net: {indicators['net_income']} XOF
- Ratio de Liquidité: {indicators['liquidity_ratio']:.2f}
- Ratio d'Endettement: {indicators['debt_ratio']:.2f}
- Marge Bénéficiaire: {indicators['profit_margin']:.2f}
- Rendement des Capitaux Propres: {indicators['roe']:.2f}
- Rotation des Actifs: {indicators['asset_turnover']:.2f}

COMPTES SIGNIFICATIFS:
"""
        # Add significant accounts
        accounts = sorted(
            exercise_data['accounts'], 
            key=lambda x: abs(x['balance']), 
            reverse=True
        )[:10]  # Top 10 by absolute balance
        
        for account in accounts:
            prompt += f"- {account['account_number']} {account['name']}: {account['balance']} XOF\n"
        
        prompt += """
Veuillez fournir une analyse détaillée de cet exercice comptable selon les normes OHADA:
1. Analyse de la situation financière générale
2. Analyse des ratios financiers et de leur signification
3. Identification des forces et faiblesses
4. Recommandations spécifiques pour améliorer la situation financière
5. Conseils pour la conformité avec le référentiel OHADA
6. Suggestions pour optimiser la fiscalité

Soyez précis et donnez des conseils pratiques adaptés à ces données financières spécifiques.
"""

        # Call Ollama API
        response = requests.post(
            f"{Config.OLLAMA_API_URL}/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result.get('response', '')
            return analysis_text
        else:
            logger.error(f"Error from Ollama API: {response.status_code} - {response.text}")
            return f"Erreur lors de l'analyse IA: {response.status_code}"
    
    except Exception as e:
        logger.error(f"Error performing AI analysis: {str(e)}")
        return f"Erreur lors de l'analyse IA: {str(e)}"

def extract_recommendations(analysis_text):
    """
    Extract recommendations from the analysis text
    Returns a list of recommendation strings
    """
    recommendations = []
    
    # Look for a recommendations section
    recommendation_section = re.search(r'(?:Recommandations|Conseils).*?\n(.*?)(?:\n\n|\n\d\.|\Z)', 
                                      analysis_text, re.DOTALL | re.IGNORECASE)
    
    if recommendation_section:
        rec_text = recommendation_section.group(1)
        
        # Extract individual points (bullets or numbered)
        points = re.findall(r'(?:^|\n)[•\-\*\d\.]+\s*(.*?)(?:\n|$)', rec_text)
        
        if points:
            recommendations = [p.strip() for p in points if p.strip()]
    
    # If no recommendations found with the section approach, try to find sentences
    # with recommendation language
    if not recommendations:
        recommendation_phrases = [
            r'(?:il est|nous|je) recommand[eé] de (.*?[\.!])',
            r'(?:vous|il faudrait) devriez (.*?[\.!])',
            r'il serait préférable de (.*?[\.!])',
            r'nous suggérons de (.*?[\.!])',
        ]
        
        for phrase in recommendation_phrases:
            matches = re.findall(phrase, analysis_text, re.IGNORECASE)
            if matches:
                recommendations.extend([m.strip() for m in matches if m.strip()])
    
    # If still no recommendations, look for any strong statements
    if not recommendations:
        statements = re.findall(r'(?:il est|il faut|vous devez|il convient de) (.*?[\.!])', 
                               analysis_text, re.IGNORECASE)
        if statements:
            recommendations = [s.strip() for s in statements if s.strip()][:5]  # Limit to 5
    
    # If still empty, add a default recommendation
    if not recommendations:
        recommendations = ["Consultez l'analyse complète pour des recommandations détaillées."]
    
    # Limit to 5 recommendations
    return recommendations[:5]

def analyze_transactions(exercise_id):
    """
    Analyze transactions for anomalies and patterns
    Returns a list of findings and insights
    """
    exercise = Exercise.query.get_or_404(exercise_id)
    findings = []
    
    # Get all transactions for this exercise
    transactions = Transaction.query.filter_by(exercise_id=exercise_id).all()
    
    # Check for unbalanced transactions
    unbalanced = []
    for transaction in transactions:
        items = TransactionItem.query.filter_by(transaction_id=transaction.id).all()
        total_debit = sum(item.debit_amount for item in items)
        total_credit = sum(item.credit_amount for item in items)
        
        if total_debit != total_credit:
            unbalanced.append({
                'id': transaction.id,
                'reference': transaction.reference,
                'date': transaction.transaction_date.strftime('%Y-%m-%d'),
                'difference': float(total_debit - total_credit)
            })
    
    if unbalanced:
        findings.append({
            'type': 'warning',
            'title': 'Transactions non équilibrées',
            'description': f"{len(unbalanced)} transaction(s) présentent des débits et crédits non équilibrés.",
            'details': unbalanced
        })
    
    # Check for duplicate transactions
    references = {}
    for transaction in transactions:
        ref = transaction.reference
        if ref in references:
            references[ref].append(transaction.id)
        else:
            references[ref] = [transaction.id]
    
    duplicates = {ref: ids for ref, ids in references.items() if len(ids) > 1}
    
    if duplicates:
        findings.append({
            'type': 'warning',
            'title': 'Références en double',
            'description': f"{len(duplicates)} référence(s) de transaction sont utilisées plus d'une fois.",
            'details': duplicates
        })
    
    # Look for unusual activity
    # (This is simplified; a real implementation would use statistical methods)
    account_activity = {}
    for transaction in transactions:
        for item in transaction.items:
            if item.account_id not in account_activity:
                account_activity[item.account_id] = []
            
            amount = max(item.debit_amount, item.credit_amount)
            account_activity[item.account_id].append(float(amount))
    
    unusual = []
    for account_id, amounts in account_activity.items():
        if len(amounts) < 2:
            continue
            
        avg = sum(amounts) / len(amounts)
        for amount in amounts:
            # Flag if amount is more than 3x the average
            if amount > avg * 3:
                account = Account.query.get(account_id)
                unusual.append({
                    'account': f"{account.account_number} - {account.name}",
                    'amount': amount,
                    'average': avg
                })
                break
    
    if unusual:
        findings.append({
            'type': 'info',
            'title': 'Montants inhabituels',
            'description': f"{len(unusual)} compte(s) présentent des montants inhabituellement élevés.",
            'details': unusual
        })
    
    return findings
