import json
import logging
import requests
from decimal import Decimal

from app import db
from models import Exercise, Transaction, TransactionItem, Account, ExerciseAnalysis
from utils import get_account_balance, get_exercise_totals, DecimalEncoder
from config import Config

logger = logging.getLogger(__name__)

def analyze_exercise(exercise_id):
    """Analyze an exercise using AI and financial calculations"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Get basic financial data
    financial_data = calculate_financial_indicators(exercise_id)
    
    # Perform AI analysis if enabled
    if Config.ENABLE_AI_ANALYSIS:
        ai_analysis = perform_ai_analysis(exercise_id, financial_data)
        
        # Combine financial data and AI analysis
        analysis_result = {**financial_data, **ai_analysis}
    else:
        # If AI analysis is disabled, just use financial data with placeholder recommendations
        analysis_result = {
            **financial_data,
            'recommendations': json.dumps([
                {'title': 'Analyse automatique désactivée', 'description': 'Veuillez activer l\'analyse par IA dans les paramètres.'}
            ]),
            'full_analysis': 'L\'analyse détaillée par IA est désactivée.'
        }
    
    return analysis_result

def calculate_financial_indicators(exercise_id):
    """Calculate key financial indicators for an exercise"""
    # Get exercise data
    totals = get_exercise_totals(exercise_id)
    
    # Get asset and liability balances
    current_assets = get_account_group_balance(exercise_id, ['10', '11', '12', '13', '14'])  # Adjust with actual OHADA current asset account numbers
    total_assets = totals['asset']
    
    current_liabilities = get_account_group_balance(exercise_id, ['40', '41', '42', '43'])  # Adjust with actual OHADA current liability account numbers
    total_liabilities = totals['liability']
    
    total_equity = totals['equity']
    net_income = totals['net_income']
    total_revenue = totals['revenue']
    total_expense = totals['expense']
    
    # Calculate key financial ratios
    try:
        # Liquidity ratio (current ratio)
        liquidity_ratio = float(current_assets / current_liabilities) if current_liabilities else 0
        
        # Solvency ratio (debt-to-equity)
        solvency_ratio = float(total_liabilities / total_equity) if total_equity else 0
        
        # Profitability ratio (return on equity)
        profitability_ratio = float(net_income / total_equity) if total_equity else 0
        
        # Overall financial health score (simple weighted average of normalized ratios)
        liquidity_score = min(1, liquidity_ratio / 2) if liquidity_ratio > 0 else 0  # Target: 2 or higher is good
        solvency_score = max(0, 1 - solvency_ratio / 3) if solvency_ratio > 0 else 1  # Target: lower is better, 0-3 range
        profitability_score = min(1, max(0, (profitability_ratio + 0.1) / 0.3)) if profitability_ratio > -0.1 else 0  # Target: higher is better
        
        # Overall score (0-100)
        financial_health_score = (liquidity_score * 0.3 + solvency_score * 0.3 + profitability_score * 0.4) * 100
    except (ZeroDivisionError, TypeError):
        liquidity_ratio = 0
        solvency_ratio = 0
        profitability_ratio = 0
        financial_health_score = 0
    
    return {
        'financial_health_score': financial_health_score,
        'liquidity_ratio': liquidity_ratio,
        'solvency_ratio': solvency_ratio,
        'profitability_ratio': profitability_ratio,
        'total_assets': float(total_assets),
        'total_liabilities': float(total_liabilities),
        'total_equity': float(total_equity),
        'net_income': float(net_income),
        'total_revenue': float(total_revenue),
        'total_expense': float(total_expense)
    }

def get_account_group_balance(exercise_id, account_prefixes):
    """Get the total balance for account numbers starting with specific prefixes"""
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

def perform_ai_analysis(exercise_id, financial_data):
    """Perform AI analysis using Ollama with Mistral 7B model"""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Prepare data for analysis
    financial_summary = json.dumps(financial_data, cls=DecimalEncoder)
    
    # Get transactions summary
    transactions = Transaction.query.filter_by(exercise_id=exercise_id).order_by(Transaction.transaction_date).all()
    transactions_summary = []
    
    for transaction in transactions:
        trans_data = {
            'reference': transaction.reference,
            'date': transaction.transaction_date.strftime('%Y-%m-%d'),
            'description': transaction.description,
            'items': []
        }
        
        for item in transaction.items:
            account = Account.query.get(item.account_id)
            trans_data['items'].append({
                'account': f"{account.account_number} - {account.name}",
                'debit': float(item.debit_amount),
                'credit': float(item.credit_amount)
            })
        
        transactions_summary.append(trans_data)
    
    # Convert data to simpler summary if there are too many transactions
    if len(transactions) > 20:
        # Group by account type
        account_type_summary = {
            'asset': 0,
            'liability': 0,
            'equity': 0,
            'revenue': 0,
            'expense': 0
        }
        
        for transaction in transactions:
            for item in transaction.items:
                account = Account.query.get(item.account_id)
                account_type_summary[account.account_type] += float(item.debit_amount) - float(item.credit_amount) if account.account_type in ['asset', 'expense'] else float(item.credit_amount) - float(item.debit_amount)
        
        transactions_data = json.dumps({
            'transaction_count': len(transactions),
            'by_account_type': account_type_summary
        })
    else:
        transactions_data = json.dumps(transactions_summary, cls=DecimalEncoder)
    
    # Prepare prompt for AI model
    prompt = f"""
Analyse de l'exercice comptable : {exercise.name}
Période : {exercise.start_date.strftime('%d/%m/%Y')} - {exercise.end_date.strftime('%d/%m/%Y')}

Voici les indicateurs financiers clés :
{financial_summary}

Voici un résumé des transactions :
{transactions_data}

En tant qu'expert-comptable spécialisé dans le système comptable OHADA, veuillez fournir une analyse détaillée de cet exercice comptable. Structurez votre analyse comme suit :

1. Résumé de la situation financière
2. Analyse de la liquidité, solvabilité et rentabilité
3. Points forts et points d'amélioration
4. Recommandations concrètes (maximum 5)
5. Conformité avec les normes OHADA
6. Suggestions d'optimisation fiscale

Veuillez fournir également une note explicative pour chaque ratio financier et sa signification dans le contexte de cette entreprise.
"""

    try:
        # Call Ollama API
        response = requests.post(
            f"{Config.OLLAMA_API_URL}/generate",
            json={
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        
        response.raise_for_status()
        result = response.json()
        
        analysis_text = result.get('response', '')
        
        # Extract recommendations from analysis
        recommendations = extract_recommendations(analysis_text)
        
        return {
            'recommendations': json.dumps(recommendations),
            'full_analysis': analysis_text
        }
    
    except Exception as e:
        logger.error(f"Error calling Ollama API: {str(e)}")
        
        # Return fallback analysis
        return {
            'recommendations': json.dumps([
                {'title': 'Erreur de l\'analyse IA', 'description': f'Une erreur est survenue lors de l\'analyse: {str(e)}'}
            ]),
            'full_analysis': f"Impossible de générer l'analyse complète. Erreur: {str(e)}"
        }

def extract_recommendations(analysis_text):
    """Extract recommendations from the AI analysis"""
    recommendations = []
    
    # Look for recommendations section
    try:
        if "Recommandations" in analysis_text:
            # Get recommendations section
            sections = analysis_text.split("Recommandations")
            if len(sections) >= 2:
                rec_section = sections[1].split("\n\n")[0]
                
                # Extract individual recommendations
                rec_lines = rec_section.strip().split("\n")
                
                # Skip the header line
                rec_lines = [line for line in rec_lines if line and not line.startswith("Recommandations")]
                
                for line in rec_lines:
                    # Clean up the line
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Remove bullet points or numbers
                    line = line.lstrip("0123456789.-* ")
                    
                    # Split title and description if possible
                    if ":" in line:
                        title, description = line.split(":", 1)
                        recommendations.append({
                            'title': title.strip(),
                            'description': description.strip()
                        })
                    else:
                        recommendations.append({
                            'title': line[:50] + "..." if len(line) > 50 else line,
                            'description': line
                        })
        
        # If no recommendations found or parsing failed, create a generic one
        if not recommendations:
            # Try to find any useful advice in the text
            useful_phrases = [
                "il est recommandé", 
                "vous devriez", 
                "il serait préférable", 
                "nous suggérons", 
                "vous pourriez"
            ]
            
            for phrase in useful_phrases:
                if phrase in analysis_text.lower():
                    start_index = analysis_text.lower().find(phrase)
                    sentence_end = analysis_text.find(".", start_index)
                    
                    if sentence_end != -1:
                        advice = analysis_text[start_index:sentence_end + 1].strip()
                        recommendations.append({
                            'title': "Suggestion",
                            'description': advice
                        })
                        break
    
    except Exception as e:
        logger.error(f"Error extracting recommendations: {str(e)}")
    
    # If still no recommendations, add a default one
    if not recommendations:
        recommendations.append({
            'title': 'Analyse complète',
            'description': 'Veuillez consulter l\'analyse complète pour plus de détails et recommandations.'
        })
    
    return recommendations[:5]  # Limit to 5 recommendations
