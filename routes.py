import os
import uuid
import logging
import xlsxwriter
import traceback
from flask import render_template, request, redirect, url_for, flash, abort, send_file, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from ecriture_generator import ComptableIA

compta = ComptableIA()

from app import app, db, socketio
from db_helper import safe_db_operation, init_db_connection
from models import User, Exercise, Account, Transaction, TransactionItem, Document, ExerciseExample, ExerciseSolution, Workgroup, Message, Note, Notification, Post, Comment, Like

# Import des routes sociales
from flask import Blueprint
routes = Blueprint('routes', __name__)

from routes_social import *
from forms import (
    LoginForm, RegistrationForm, ProfileForm, ExerciseForm, AccountForm, 
    TransactionForm, DocumentUploadForm, ReportGenerationForm, ForgotPasswordForm, 
    ResetPasswordForm, TextProcessingForm, ExerciseExampleUploadForm, ExerciseSolverForm,
    WorkgroupForm, MessageForm, NoteForm, MemberInviteForm, WorkgroupExerciseForm, SearchForm,
    CompleteExerciseSolverForm
)
from text_processor import process_text
from exercise_solver import solver, save_example_pdf
from exercise_resolution import resolve_exercise_completely
from models import ExerciseExample, ExerciseSolution
import json
import os
from utils import allowed_file, ensure_upload_dir, format_amount, parse_amount
from accounting_processor import create_transaction_from_document, post_transaction, auto_categorize_transaction
from ocr_processor import process_document_ocr
from nlp_processor import extract_data_from_text

logger = logging.getLogger(__name__)

# Home route
@app.route('/')
@app.route('/index')
def index():
    """Route pour la page d'accueil"""
    return render_template('index.html', title="Accueil")

# About route
@app.route('/about')
def about():
    return render_template('about.html', title="À propos")

@app.route('/resoudre-exercice', methods=['GET', 'POST'])
@login_required
def resoudre_exercice():
    if request.method == 'POST':
        operations = []
        
        textes = request.form.getlist('texte')
        montants = request.form.getlist('montant_ht')
        dates = request.form.getlist('date_op')
        taux_tva = request.form.getlist('taux_tva')
        
        for i in range(len(textes)):
            operations.append({
                "texte": textes[i],
                "montant_ht": float(montants[i]),
                "taux_tva": float(taux_tva[i]) if taux_tva[i] else 0,
                "date_op": dates[i]
            })
            
        resultat = compta.generer_journal_complet(operations)
        
        return render_template(
            'resultats.html',
            journal=resultat['journal'],
            grand_livre=resultat['grand_livre'],
            bilan=resultat['bilan']
        )
        
    return render_template('formulaire.html')

# Text processing route
@app.route('/text-processing', methods=['GET', 'POST'])
@login_required
def text_processing():
    form = TextProcessingForm()
    result = None
    
    if form.validate_on_submit():
        # Process the text based on form options
        compression_rate = float(form.compression_rate.data)
        result = process_text(
            form.text.data,
            summarize=form.summarize.data,
            split_paragraphs=form.split_paragraphs.data,
            analyze=form.analyze.data,
            compression_rate=compression_rate
        )
        
        flash('Texte traité avec succès!', 'success')
    
    return render_template(
        'text_processing.html',
        title='Traitement de texte',
        form=form,
        result=result
    )

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Bienvenue, {user.full_name}!', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'danger')
    
    return render_template('auth/login.html', title='Connexion', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Votre compte a été créé avec succès! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            import logging
            logging.error(f"Erreur lors de l'inscription: {str(e)}")
            flash(f"Une erreur s'est produite lors de la création de votre compte. Veuillez réessayer.", 'danger')
    
    return render_template('auth/register.html', title='Inscription', form=form)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.email = form.email.data
        
        # Update password if provided
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Votre profil a été mis à jour avec succès!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('auth/profile.html', title='Profil', form=form)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate reset token
            token = user.get_reset_token()
            db.session.commit()
            
            # TODO: In production, send an email with the reset link
            reset_url = url_for('reset_password', token=token, _external=True)
            logger.info(f"Reset URL for {user.email}: {reset_url}")
            
            flash(
                'Si un compte existe avec cette adresse email, les instructions de réinitialisation '
                'de mot de passe ont été envoyées. Veuillez vérifier votre boîte de réception.', 
                'info'
            )
        else:
            # Don't reveal if email exists in database
            flash(
                'Si un compte existe avec cette adresse email, les instructions de réinitialisation '
                'de mot de passe ont été envoyées. Veuillez vérifier votre boîte de réception.', 
                'info'
            )
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html', title='Mot de passe oublié', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Find user by token
    user = User.find_by_reset_token(token)
    if not user or not user.verify_reset_token(token):
        flash('Le lien de réinitialisation est invalide ou a expiré.', 'danger')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Votre mot de passe a été mis à jour avec succès! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', title='Réinitialiser mot de passe', form=form, token=token)

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Get current date
    from datetime import datetime
    now = datetime.utcnow()
    
    # Get recent exercises
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.start_date.desc()).limit(5).all()
    
    # Get recent transactions
    recent_transactions = []
    if exercises:
        recent_transactions = Transaction.query.filter_by(
            user_id=current_user.id,
            exercise_id=exercises[0].id if exercises else None
        ).order_by(Transaction.transaction_date.desc()).limit(10).all()
    
    # Get recent documents
    recent_documents = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(Document.upload_date.desc()).limit(5).all()
    
    # Get user's workgroups
    workgroups = Workgroup.query.join(Workgroup.members).filter(User.id == current_user.id).limit(5).all()
    
    return render_template(
        'dashboard.html',
        title='Tableau de bord',
        exercises=exercises,
        recent_transactions=recent_transactions,
        recent_documents=recent_documents,
        now=now,
        workgroups=workgroups
    )

# Exercise routes
@app.route('/exercises')
@login_required
def exercises_list():
    exercises = Exercise.query.filter_by(user_id=current_user.id).order_by(Exercise.start_date.desc()).all()
    return render_template('exercises/list.html', title='Exercices', exercises=exercises)

@app.route('/exercises/new', methods=['GET', 'POST'])
@login_required
def exercise_new():
    form = ExerciseForm()
    
    if form.validate_on_submit():
        exercise = Exercise(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        db.session.add(exercise)
        db.session.commit()
        
        flash('Exercice créé avec succès!', 'success')
        return redirect(url_for('exercises_list'))
    
    return render_template('exercises/form.html', title='Nouvel exercice', form=form)

@app.route('/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
@login_required
def exercise_edit(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    form = ExerciseForm(obj=exercise)
    
    if form.validate_on_submit():
        exercise.name = form.name.data
        exercise.start_date = form.start_date.data
        exercise.end_date = form.end_date.data
        exercise.description = form.description.data
        
        db.session.commit()
        
        flash('Exercice mis à jour avec succès!', 'success')
        return redirect(url_for('exercises_list'))
    
    return render_template('exercises/form.html', title='Modifier exercice', form=form, exercise=exercise)

@app.route('/exercises/<int:exercise_id>/close', methods=['POST'])
@login_required
def exercise_close(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    exercise.is_closed = True
    db.session.commit()
    
    flash('Exercice clôturé avec succès!', 'success')
    return redirect(url_for('exercises_list'))

# Account routes
@app.route('/exercises/<int:exercise_id>/accounts')
@login_required
def accounts_list(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    accounts = Account.query.filter_by(exercise_id=exercise_id, parent_id=None).order_by(Account.account_number).all()
    
    return render_template('accounts/list.html', title='Plan comptable', exercise=exercise, accounts=accounts)

@app.route('/exercises/<int:exercise_id>/accounts/new', methods=['GET', 'POST'])
@login_required
def account_new(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de créer un compte sur un exercice clôturé.', 'danger')
        return redirect(url_for('accounts_list', exercise_id=exercise_id))
    
    form = AccountForm()
    
    # Load parent accounts for dropdown
    form.parent_id.choices = [(0, 'Aucun')] + [
        (a.id, a.full_name) for a in Account.query.filter_by(exercise_id=exercise_id).order_by(Account.account_number).all()
    ]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        
        account = Account(
            account_number=form.account_number.data,
            name=form.name.data,
            account_type=form.account_type.data,
            description=form.description.data,
            parent_id=parent_id,
            exercise_id=exercise_id
        )
        
        db.session.add(account)
        db.session.commit()
        
        flash('Compte créé avec succès!', 'success')
        return redirect(url_for('accounts_list', exercise_id=exercise_id))
    
    return render_template('accounts/form.html', title='Nouveau compte', form=form, exercise=exercise)

@app.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def account_edit(account_id):
    account = Account.query.get_or_404(account_id)
    exercise = account.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de modifier un compte sur un exercice clôturé.', 'danger')
        return redirect(url_for('accounts_list', exercise_id=exercise.id))
    
    form = AccountForm(obj=account)
    
    # Load parent accounts for dropdown, excluding the current account and its children
    def get_child_ids(account_id):
        ids = [account_id]
        children = Account.query.filter_by(parent_id=account_id).all()
        for child in children:
            ids.extend(get_child_ids(child.id))
        return ids
    
    excluded_ids = get_child_ids(account_id)
    
    form.parent_id.choices = [(0, 'Aucun')] + [
        (a.id, a.full_name) for a in Account.query.filter_by(exercise_id=exercise.id).filter(
            Account.id.notin_(excluded_ids)
        ).order_by(Account.account_number).all()
    ]
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        
        account.account_number = form.account_number.data
        account.name = form.name.data
        account.account_type = form.account_type.data
        account.description = form.description.data
        account.parent_id = parent_id
        
        db.session.commit()
        
        flash('Compte mis à jour avec succès!', 'success')
        return redirect(url_for('accounts_list', exercise_id=exercise.id))
    
    return render_template('accounts/form.html', title='Modifier compte', form=form, exercise=exercise, account=account)

@app.route('/accounts/<int:account_id>/toggle', methods=['POST'])
@login_required
def account_toggle(account_id):
    account = Account.query.get_or_404(account_id)
    exercise = account.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de modifier un compte sur un exercice clôturé.', 'danger')
        return redirect(url_for('accounts_list', exercise_id=exercise.id))
    
    account.is_active = not account.is_active
    db.session.commit()
    
    status = 'activé' if account.is_active else 'désactivé'
    flash(f'Compte {status} avec succès!', 'success')
    
    return redirect(url_for('accounts_list', exercise_id=exercise.id))

# Transaction routes
@app.route('/exercises/<int:exercise_id>/transactions')
@login_required
def transactions_list(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    transactions = Transaction.query.filter_by(exercise_id=exercise_id).order_by(Transaction.transaction_date.desc()).all()
    
    return render_template('transactions/list.html', title='Journal', exercise=exercise, transactions=transactions)

@app.route('/exercises/<int:exercise_id>/transactions/new', methods=['GET', 'POST'])
@login_required
def transaction_new(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de créer une transaction sur un exercice clôturé.', 'danger')
        return redirect(url_for('transactions_list', exercise_id=exercise_id))
    
    form = TransactionForm()
    
    # Load at least 2 items
    form.setup_transaction_items()
    
    if form.validate_on_submit():
        transaction = Transaction(
            reference=form.reference.data,
            transaction_date=form.transaction_date.data,
            description=form.description.data,
            is_posted=form.is_posted.data,
            user_id=current_user.id,
            exercise_id=exercise_id
        )
        
        db.session.add(transaction)
        db.session.flush()  # To get transaction ID
        
        # Process transaction items
        for item in form.items:
            if item.account_id.data and (item.debit_amount.data > 0 or item.credit_amount.data > 0):
                transaction_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=item.account_id.data,
                    description=item.description.data,
                    debit_amount=item.debit_amount.data or 0,
                    credit_amount=item.credit_amount.data or 0
                )
                db.session.add(transaction_item)
        
        db.session.commit()
        
        flash('Transaction créée avec succès!', 'success')
        return redirect(url_for('transactions_list', exercise_id=exercise_id))
    
    # Load accounts for dropdown
    accounts = Account.query.filter_by(exercise_id=exercise_id, is_active=True).order_by(Account.account_number).all()
    
    return render_template('transactions/form.html', title='Nouvelle transaction', form=form, exercise=exercise, accounts=accounts)

@app.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def transaction_edit(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    exercise = transaction.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de modifier une transaction sur un exercice clôturé.', 'danger')
        return redirect(url_for('transactions_list', exercise_id=exercise.id))
    
    # Check if transaction is posted
    if transaction.is_posted:
        flash('Impossible de modifier une transaction déjà comptabilisée.', 'danger')
        return redirect(url_for('transaction_view', transaction_id=transaction_id))
    
    form = TransactionForm(obj=transaction)
    
    # Setup transaction items
    form.setup_transaction_items(transaction)
    
    if form.validate_on_submit():
        transaction.reference = form.reference.data
        transaction.transaction_date = form.transaction_date.data
        transaction.description = form.description.data
        transaction.is_posted = form.is_posted.data
        
        # Remove all existing items
        for item in transaction.items.all():
            db.session.delete(item)
        
        # Add new items
        for item in form.items:
            if item.account_id.data and (item.debit_amount.data > 0 or item.credit_amount.data > 0):
                transaction_item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=item.account_id.data,
                    description=item.description.data,
                    debit_amount=item.debit_amount.data or 0,
                    credit_amount=item.credit_amount.data or 0
                )
                db.session.add(transaction_item)
        
        db.session.commit()
        
        flash('Transaction mise à jour avec succès!', 'success')
        return redirect(url_for('transactions_list', exercise_id=exercise.id))
    
    # Load accounts for dropdown
    accounts = Account.query.filter_by(exercise_id=exercise.id, is_active=True).order_by(Account.account_number).all()
    
    return render_template('transactions/form.html', title='Modifier transaction', form=form, exercise=exercise, transaction=transaction, accounts=accounts)

@app.route('/transactions/<int:transaction_id>')
@login_required
def transaction_view(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    exercise = transaction.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    return render_template('transactions/view.html', title='Détails de la transaction', transaction=transaction, exercise=exercise)

@app.route('/transactions/<int:transaction_id>/post', methods=['POST'])
@login_required
def transaction_post(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    exercise = transaction.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de comptabiliser une transaction sur un exercice clôturé.', 'danger')
        return redirect(url_for('transaction_view', transaction_id=transaction_id))
    
    # Try to post the transaction
    if post_transaction(transaction_id):
        flash('Transaction comptabilisée avec succès!', 'success')
    else:
        flash('Impossible de comptabiliser la transaction. Vérifiez que les débits et crédits sont équilibrés.', 'danger')
    
    return redirect(url_for('transaction_view', transaction_id=transaction_id))

@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
def transaction_delete(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    exercise = transaction.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de supprimer une transaction sur un exercice clôturé.', 'danger')
        return redirect(url_for('transactions_list', exercise_id=exercise.id))
    
    # Check if transaction is posted
    if transaction.is_posted:
        flash('Impossible de supprimer une transaction déjà comptabilisée.', 'danger')
        return redirect(url_for('transaction_view', transaction_id=transaction_id))
    
    # Delete transaction (cascade will delete items)
    db.session.delete(transaction)
    db.session.commit()
    
    flash('Transaction supprimée avec succès!', 'success')
    return redirect(url_for('transactions_list', exercise_id=exercise.id))

@app.route('/exercises/<int:exercise_id>/journal/export')
@login_required
def journal_export(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Get all transactions for the exercise
    transactions = Transaction.query.filter_by(exercise_id=exercise_id).order_by(Transaction.transaction_date).all()
    
    # Create Excel file
    filename = f"journal_{exercise.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Journal')
    
    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#333333',
        'font_color': 'white',
        'border': 1
    })
    
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    number_format = workbook.add_format({
        'num_format': '# ##0.00',
        'border': 1
    })
    
    # Set column widths
    worksheet.set_column('A:A', 12)  # Date
    worksheet.set_column('B:B', 12)  # Référence
    worksheet.set_column('C:C', 15)  # N° Compte
    worksheet.set_column('D:D', 40)  # Libellé
    worksheet.set_column('E:E', 15)  # Débit
    worksheet.set_column('F:F', 15)  # Crédit
    
    # Write headers
    headers = ['Date', 'Référence', 'N° Compte', 'Libellé', 'Débit', 'Crédit']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data
    row = 1
    for transaction in transactions:
        # Write transaction date and reference for first item only
        first_item = True
        
        for item in transaction.items:
            worksheet.write(row, 0, transaction.transaction_date, date_format if first_item else cell_format)
            worksheet.write(row, 1, transaction.reference, cell_format if first_item else cell_format)
            worksheet.write(row, 2, item.account.account_number, cell_format)
            worksheet.write(row, 3, item.description or transaction.description, cell_format)
            worksheet.write(row, 4, float(item.debit_amount), number_format)
            worksheet.write(row, 5, float(item.credit_amount), number_format)
            
            first_item = False
            row += 1
        
        # Add a blank row between transactions
        row += 1
    
    workbook.close()
    
    return send_file(filepath, as_attachment=True)

# Document routes
@app.route('/exercises/<int:exercise_id>/documents')
@login_required
def documents_list(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    documents = Document.query.filter_by(exercise_id=exercise_id).order_by(Document.upload_date.desc()).all()
    
    return render_template('documents/list.html', title='Documents', exercise=exercise, documents=documents)

@app.route('/exercises/<int:exercise_id>/documents/upload', methods=['GET', 'POST'])
@login_required
def document_upload(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible d\'ajouter un document sur un exercice clôturé.', 'danger')
        return redirect(url_for('documents_list', exercise_id=exercise_id))
    
    form = DocumentUploadForm()
    
    if form.validate_on_submit():
        file = form.document.data
        
        if file and allowed_file(file.filename):
            # Secure filename and make unique
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Ensure upload directory exists
            upload_folder = ensure_upload_dir()
            
            # Save file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Create document record
            document = Document(
                original_filename=original_filename,
                filename=file_path,
                document_type=form.document_type.data,
                description=form.description.data,
                user_id=current_user.id,
                exercise_id=exercise_id
            )
            
            db.session.add(document)
            db.session.commit()
            
            flash('Document téléchargé avec succès!', 'success')
            
            # Process document with OCR if auto-process is checked
            if form.auto_process.data:
                # Run OCR
                extracted_text = process_document_ocr(document.id)
                
                if extracted_text:
                    # Extract structured data using NLP
                    extracted_data = extract_data_from_text(extracted_text)
                    
                    if extracted_data:
                        # Create transaction from extracted data
                        transaction_id = create_transaction_from_document(document.id, extracted_data)
                        
                        if transaction_id:
                            flash('Une transaction a été automatiquement créée à partir du document.', 'success')
                            return redirect(url_for('transaction_view', transaction_id=transaction_id))
                        else:
                            flash('Impossible de créer une transaction automatiquement. Veuillez vérifier le document.', 'warning')
                    else:
                        flash('Extraction des données échouée. Veuillez créer une transaction manuellement.', 'warning')
                else:
                    flash('OCR échoué. Veuillez traiter le document manuellement.', 'warning')
            
            return redirect(url_for('documents_list', exercise_id=exercise_id))
        else:
            flash('Type de fichier non autorisé.', 'danger')
    
    return render_template('documents/upload.html', title='Télécharger un document', form=form, exercise=exercise)

@app.route('/documents/<int:document_id>')
@login_required
def document_view(document_id):
    document = Document.query.get_or_404(document_id)
    exercise = document.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    return render_template('documents/view.html', title='Détails du document', document=document, exercise=exercise)

@app.route('/documents/<int:document_id>/process', methods=['POST'])
@login_required
def document_process(document_id):
    document = Document.query.get_or_404(document_id)
    exercise = document.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de traiter un document sur un exercice clôturé.', 'danger')
        return redirect(url_for('document_view', document_id=document_id))
    
    # Process document with OCR
    extracted_text = process_document_ocr(document_id)
    
    if extracted_text:
        # Extract structured data using NLP
        extracted_data = extract_data_from_text(extracted_text)
        
        if extracted_data:
            # Create transaction from extracted data
            transaction_id = create_transaction_from_document(document_id, extracted_data)
            
            if transaction_id:
                flash('Une transaction a été automatiquement créée à partir du document.', 'success')
                return redirect(url_for('transaction_view', transaction_id=transaction_id))
            else:
                flash('Impossible de créer une transaction automatiquement. Veuillez vérifier le document.', 'warning')
        else:
            flash('Extraction des données échouée. Veuillez créer une transaction manuellement.', 'warning')
    else:
        flash('OCR échoué. Veuillez traiter le document manuellement.', 'warning')
    
    return redirect(url_for('document_view', document_id=document_id))

@app.route('/documents/<int:document_id>/download')
@login_required
def document_download(document_id):
    document = Document.query.get_or_404(document_id)
    exercise = document.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    return send_file(document.filename, as_attachment=True, download_name=document.original_filename)

@app.route('/documents/<int:document_id>/delete', methods=['POST'])
@login_required
def document_delete(document_id):
    document = Document.query.get_or_404(document_id)
    exercise = document.exercise
    
    # Check if user has permission
    if exercise.user_id != current_user.id:
        abort(403)
    
    # Check if exercise is closed
    if exercise.is_closed:
        flash('Impossible de supprimer un document sur un exercice clôturé.', 'danger')
        return redirect(url_for('documents_list', exercise_id=exercise.id))
    
    # Delete file
    try:
        if os.path.exists(document.filename):
            os.remove(document.filename)
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
    
    # Delete document record
    db.session.delete(document)
    db.session.commit()
    
    flash('Document supprimé avec succès!', 'success')
    return redirect(url_for('documents_list', exercise_id=exercise.id))

# Exercise examples and solver routes
@app.route('/exercise-examples')
@login_required
def exercise_examples_list():
    """Liste des exemples d'exercices pour l'apprentissage."""
    # Filtrer les exercices selon la catégorie si elle est fournie
    category = request.args.get('category')
    
    # Base query
    query = ExerciseExample.query
    
    # Filtrer par catégorie si spécifiée
    if category:
        query = query.filter_by(category=category)
    
    # Limiter l'accès aux exercices selon les droits de l'utilisateur
    if not current_user.is_admin:
        # Pour les utilisateurs normaux, afficher uniquement les exercices publics
        # Ou ceux qu'ils ont créés eux-mêmes
        query = query.filter((ExerciseExample.user_id == current_user.id) | 
                            (ExerciseExample.category == 'comptabilité ohada'))
    
    # Récupérer les exemples triés par date
    examples = query.order_by(ExerciseExample.upload_date.desc()).all()
    
    # Récupérer toutes les catégories distinctes pour le filtre
    categories = db.session.query(ExerciseExample.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template(
        'exercise_solver/examples_list.html',
        title='Exemples d\'exercices',
        examples=examples,
        categories=categories,
        current_category=category
    )

@app.route('/exercise-examples/upload', methods=['GET', 'POST'])
@login_required
def exercise_example_upload():
    """Téléchargement d'un exemple d'exercice résolu."""
    form = ExerciseExampleUploadForm()
    
    if form.validate_on_submit():
        example_file = form.example_file.data
        
        # Créer le répertoire des exemples s'il n'existe pas
        example_dir = os.path.join(os.getcwd(), 'examples')
        os.makedirs(example_dir, exist_ok=True)
        
        # Générer un nom de fichier sécurisé
        filename = secure_filename(example_file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        file_path = os.path.join(example_dir, unique_filename)
        
        # Sauvegarder le fichier
        example_file.save(file_path)
        
        # Extraire le texte et les données
        example_data = solver._extract_from_pdf(file_path)
        
        if example_data:
            # Créer l'entrée en base de données
            example = ExerciseExample(
                title=form.title.data,
                filename=unique_filename,
                problem_text=example_data.get('problem_text', ''),
                solution_text=example_data.get('solution_text', ''),
                category=form.category.data,
                difficulty=form.difficulty.data,
                user_id=current_user.id
            )
            
            db.session.add(example)
            db.session.commit()
            
            # Recharger les exemples dans le solveur
            solver.load_examples()
            
            flash('Exemple d\'exercice téléchargé avec succès!', 'success')
            return redirect(url_for('exercise_examples_list'))
        else:
            # Si l'extraction a échoué, supprimer le fichier
            os.remove(file_path)
            flash('Impossible d\'extraire les données de l\'exercice. Vérifiez que le PDF contient du texte et non des images.', 'danger')
    
    return render_template(
        'exercise_solver/example_upload.html',
        title='Télécharger un exemple d\'exercice',
        form=form
    )

@app.route('/exercise-examples/<int:example_id>')
@login_required
def exercise_example_view(example_id):
    """Visualiser un exemple d'exercice résolu."""
    example = ExerciseExample.query.get_or_404(example_id)
    
    return render_template(
        'exercise_solver/example_view.html',
        title=f'Exemple: {example.title}',
        example=example
    )

@app.route('/exercise-solver', methods=['GET', 'POST'])
@login_required
def exercise_solver_form():
    """Formulaire de résolution d'exercice."""
    form = ExerciseSolverForm()
    solution = None
    
    if form.validate_on_submit():
        # Résoudre l'exercice
        result = solver.solve_exercise(form.problem_text.data)
        
        if result['success']:
            # Créer l'entrée en base de données
            solution = ExerciseSolution(
                title=form.title.data,
                problem_text=form.problem_text.data,
                solution_text=result['solution'],
                confidence=result['confidence'],
                examples_used=json.dumps(result['similar_examples']),
                user_id=current_user.id
            )
            
            db.session.add(solution)
            db.session.commit()
            
            flash('Exercice résolu avec succès!', 'success')
        else:
            solution = {
                'title': form.title.data,
                'problem_text': form.problem_text.data,
                'solution_text': 'Aucune solution n\'a pu être générée. Veuillez vérifier votre énoncé ou ajouter plus d\'exemples similaires.',
                'confidence': 0.0,
                'examples_used': []
            }
            flash(result['message'], 'warning')
    
    return render_template(
        'exercise_solver/solver_form.html',
        title='Résoudre un exercice',
        form=form,
        solution=solution
    )

@app.route('/exercise-solutions')
@login_required
def exercise_solutions_list():
    """Liste des solutions générées."""
    solutions = ExerciseSolution.query.filter_by(user_id=current_user.id).order_by(ExerciseSolution.created_at.desc()).all()
    
    return render_template(
        'exercise_solver/solutions_list.html',
        title='Mes solutions d\'exercices',
        solutions=solutions
    )

@app.route('/exercise-solutions/<int:solution_id>')
@login_required
def exercise_solution_view(solution_id):
    """Visualiser une solution générée."""
    solution = ExerciseSolution.query.get_or_404(solution_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette solution
    if solution.user_id != current_user.id:
        abort(403)
    
    # Récupérer les exemples utilisés pour la solution
    examples_used = []
    if solution.examples_used:
        try:
            example_data = json.loads(solution.examples_used)
            for example in example_data:
                example_obj = ExerciseExample.query.filter_by(filename=example['filename']).first()
                if example_obj:
                    examples_used.append({
                        'example': example_obj,
                        'similarity': example['similarity']
                    })
        except:
            pass
    
    return render_template(
        'exercise_solver/solution_view.html',
        title=f'Solution: {solution.title}',
        solution=solution,
        examples_used=examples_used
    )

# Communication and Workgroup routes
@app.route('/workgroups')
@login_required
def workgroups_list():
    """List all workgroups the user is a member of"""
    try:
        # Get workgroups where user is owner
        owned_workgroups = Workgroup.query.filter_by(owner_id=current_user.id).all()
        
        # Get workgroups where user is a member
        member_workgroups = Workgroup.query.join(
            Workgroup.members
        ).filter(
            User.id == current_user.id
        ).all()
        
        # Get public workgroups that the user isn't a member of
        member_workgroup_ids = [wg.id for wg in owned_workgroups + member_workgroups]
        
        # Utilisation de safe_db_operation pour cette requête plus complexe
        # qui pourrait causer des problèmes
        def get_public_workgroups():
            try:
                return Workgroup.query.filter(
                    Workgroup.is_private == False,
                    ~Workgroup.id.in_(member_workgroup_ids) if member_workgroup_ids else True
                ).all()
            except Exception as e:
                logger.error(f"Erreur lors de la récupération des groupes publics: {str(e)}")
                return []
        
        public_workgroups = get_public_workgroups() or []
        
        return render_template(
            'workgroups/list.html',
            title='Groupes de travail',
            owned_workgroups=owned_workgroups,
            member_workgroups=member_workgroups,
            public_workgroups=public_workgroups
        )
    except SQLAlchemyError as e:
        # Gestion spécifique pour les erreurs de base de données
        logger.error(f"Erreur SQL lors de la récupération des groupes de travail: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Tentative de reconnexion à la base de données
        init_db_connection()
        
        flash("Une erreur de base de données s'est produite. Veuillez réessayer.", "danger")
        return render_template(
            'workgroups/list.html',
            title='Groupes de travail - Erreur DB',
            owned_workgroups=[],
            member_workgroups=[],
            public_workgroups=[]
        )
    except Exception as e:
        # Log détaillé pour faciliter le débogage
        logger.error(f"Erreur lors de la récupération des groupes de travail: {str(e)}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Message utilisateur plus informatif
        error_msg = "Une erreur s'est produite lors du chargement des groupes de travail."
        if app.config.get('DEBUG', False):
            error_msg += f" Détails: {str(e)}"
        
        flash(error_msg, "danger")
        
        return render_template(
            'workgroups/list.html',
            title='Groupes de travail - Erreur',
            owned_workgroups=[],
            member_workgroups=[],
            public_workgroups=[],
            error=True
        )

@app.route('/workgroups/new', methods=['GET', 'POST'])
@login_required
def workgroup_new():
    """Create a new workgroup"""
    form = WorkgroupForm()
    
    if form.validate_on_submit():
        workgroup = Workgroup(
            name=form.name.data,
            description=form.description.data,
            is_private=form.is_private.data,
            owner_id=current_user.id
        )
        
        # Add owner as a member with admin role
        db.session.add(workgroup)
        db.session.commit()
        
        # Now we can add the user to the workgroup since it has an ID
        workgroup.add_member(current_user, role='admin')
        
        flash('Groupe de travail créé avec succès!', 'success')
        return redirect(url_for('workgroups_list'))
    
    return render_template('workgroups/form.html', title='Nouveau groupe', form=form)

@app.route('/workgroups/<int:workgroup_id>')
@login_required
def workgroup_view(workgroup_id):
    """View a workgroup's details and messages"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is member or owner
    if workgroup.owner_id != current_user.id and current_user not in workgroup.members:
        if workgroup.is_private:
            abort(403)
    
    # Form for sending messages
    message_form = MessageForm()
    
    # Get messages for this workgroup
    messages = Message.query.filter_by(
        workgroup_id=workgroup_id, 
        parent_id=None
    ).order_by(Message.sent_at.desc()).all()
    
    # Get shared exercises
    shared_exercises = workgroup.exercises
    
    # Get workgroup members
    members = workgroup.members
    
    return render_template(
        'workgroups/view.html',
        title=workgroup.name,
        workgroup=workgroup,
        message_form=message_form,
        messages=messages,
        shared_exercises=shared_exercises,
        members=members,
        is_admin=(workgroup.owner_id == current_user.id or workgroup.get_member_role(current_user) == 'admin')
    )

@app.route('/workgroups/<int:workgroup_id>/edit', methods=['GET', 'POST'])
@login_required
def workgroup_edit(workgroup_id):
    """Edit a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is owner or admin
    if workgroup.owner_id != current_user.id and workgroup.get_member_role(current_user) != 'admin':
        abort(403)
    
    form = WorkgroupForm(obj=workgroup)
    
    if form.validate_on_submit():
        workgroup.name = form.name.data
        workgroup.description = form.description.data
        workgroup.is_private = form.is_private.data
        
        db.session.commit()
        
        flash('Groupe de travail mis à jour avec succès!', 'success')
        return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
    
    return render_template('workgroups/form.html', title='Modifier groupe', form=form, workgroup=workgroup)

@app.route('/workgroups/<int:workgroup_id>/delete', methods=['POST'])
@login_required
def workgroup_delete(workgroup_id):
    """Delete a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Only the owner can delete the workgroup
    if workgroup.owner_id != current_user.id:
        abort(403)
    
    db.session.delete(workgroup)
    db.session.commit()
    
    flash('Groupe de travail supprimé avec succès!', 'success')
    return redirect(url_for('workgroups_list'))

@app.route('/workgroups/<int:workgroup_id>/invite', methods=['GET', 'POST'])
@login_required
def workgroup_invite(workgroup_id):
    """Invite a user to a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is owner or admin
    if workgroup.owner_id != current_user.id and workgroup.get_member_role(current_user) != 'admin':
        abort(403)
    
    form = MemberInviteForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            # Check if user is already a member
            if user in workgroup.members:
                flash(f"{user.username} est déjà membre de ce groupe.", 'warning')
            else:
                # Add user to workgroup
                workgroup.add_member(user, role=form.role.data)
                
                # Create notification for invited user
                notification = Notification(
                    user_id=user.id,
                    title=f"Invitation à rejoindre {workgroup.name}",
                    content=f"{current_user.username} vous a invité(e) à rejoindre le groupe de travail '{workgroup.name}'.",
                    notification_type='invite',
                    source_id=workgroup.id,
                    source_type='workgroup'
                )
                
                db.session.add(notification)
                db.session.commit()
                
                flash(f"{user.username} a été ajouté au groupe avec succès!", 'success')
                return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
        else:
            flash("Utilisateur non trouvé.", 'danger')
    
    return render_template(
        'workgroups/invite.html',
        title='Inviter un membre',
        form=form,
        workgroup=workgroup
    )

@app.route('/workgroups/<int:workgroup_id>/leave', methods=['POST'])
@login_required
def workgroup_leave(workgroup_id):
    """Leave a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is a member
    if current_user not in workgroup.members:
        abort(403)
    
    # Can't leave if you're the owner
    if workgroup.owner_id == current_user.id:
        flash("Vous ne pouvez pas quitter un groupe dont vous êtes le propriétaire.", 'danger')
        return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
    
    # Remove user from workgroup
    workgroup.remove_member(current_user)
    
    flash('Vous avez quitté le groupe avec succès!', 'success')
    return redirect(url_for('workgroups_list'))

@app.route('/workgroups/<int:workgroup_id>/remove/<int:user_id>', methods=['POST'])
@login_required
def workgroup_remove_member(workgroup_id, user_id):
    """Remove a member from a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    user = User.query.get_or_404(user_id)
    
    # Check if current user is owner or admin
    if workgroup.owner_id != current_user.id and workgroup.get_member_role(current_user) != 'admin':
        abort(403)
    
    # Can't remove the owner
    if user.id == workgroup.owner_id:
        flash("Vous ne pouvez pas retirer le propriétaire du groupe.", 'danger')
        return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
    
    # Remove user from workgroup
    workgroup.remove_member(user)
    
    # Create notification for removed user
    notification = Notification(
        user_id=user.id,
        title=f"Retrait du groupe {workgroup.name}",
        content=f"Vous avez été retiré(e) du groupe de travail '{workgroup.name}'.",
        notification_type='system',
        source_id=workgroup.id,
        source_type='workgroup'
    )
    
    db.session.add(notification)
    db.session.commit()
    
    flash(f"{user.username} a été retiré du groupe avec succès!", 'success')
    return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))

@app.route('/workgroups/<int:workgroup_id>/share-exercise', methods=['GET', 'POST'])
@login_required
def workgroup_share_exercise(workgroup_id):
    """Share an exercise with a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is a member
    if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
        abort(403)
    
    form = WorkgroupExerciseForm()
    
    # Get user's exercises that aren't already shared with this workgroup
    shared_exercise_ids = [e.id for e in workgroup.exercises]
    user_exercises = Exercise.query.filter_by(user_id=current_user.id).filter(
        ~Exercise.id.in_(shared_exercise_ids) if shared_exercise_ids else True
    ).all()
    
    if not user_exercises:
        flash("Vous n'avez aucun exercice à partager avec ce groupe.", 'warning')
        return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
    
    # Setup exercise choices for form
    form.exercise_id.choices = [(e.id, e.name) for e in user_exercises]
    
    if form.validate_on_submit():
        exercise = Exercise.query.get_or_404(form.exercise_id.data)
        
        # Check if user owns the exercise
        if exercise.user_id != current_user.id:
            abort(403)
        
        # Share exercise with workgroup
        workgroup.share_exercise(exercise, current_user)
        
        # Create notifications for all workgroup members except current user
        for member in workgroup.members:
            if member.id != current_user.id:
                notification = Notification(
                    user_id=member.id,
                    title=f"Nouvel exercice partagé dans {workgroup.name}",
                    content=f"{current_user.username} a partagé l'exercice '{exercise.name}' dans le groupe '{workgroup.name}'.",
                    notification_type='share',
                    source_id=workgroup.id,
                    source_type='workgroup'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        flash(f"Exercice '{exercise.name}' partagé avec succès!", 'success')
        return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))
    
    return render_template(
        'workgroups/share_exercise.html',
        title='Partager un exercice',
        form=form,
        workgroup=workgroup
    )

@app.route('/workgroups/<int:workgroup_id>/unshare-exercise/<int:exercise_id>', methods=['POST'])
@login_required
def workgroup_unshare_exercise(workgroup_id, exercise_id):
    """Unshare an exercise from a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    exercise = Exercise.query.get_or_404(exercise_id)
    
    # Check if user is owner or admin or the one who shared the exercise
    is_admin = workgroup.owner_id == current_user.id or workgroup.get_member_role(current_user) == 'admin'
    shared_by_user = db.session.execute(
        db.select([workgroup_exercises.c.shared_by]).where(
            workgroup_exercises.c.exercise_id == exercise_id,
            workgroup_exercises.c.workgroup_id == workgroup_id
        )
    ).scalar() == current_user.id
    
    if not (is_admin or shared_by_user):
        abort(403)
    
    # Unshare exercise from workgroup
    workgroup.unshare_exercise(exercise)
    
    flash(f"L'exercice n'est plus partagé avec ce groupe.", 'success')
    return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))

@app.route('/workgroups/<int:workgroup_id>/post-message', methods=['POST'])
@login_required
def workgroup_post_message(workgroup_id):
    """Post a message in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is a member
    if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
        abort(403)
    
    form = MessageForm()
    
    if form.validate_on_submit():
        parent_id = None
        if form.parent_id.data and form.parent_id.data.isdigit():
            parent_message = Message.query.get(int(form.parent_id.data))
            if parent_message and parent_message.workgroup_id == workgroup.id:
                parent_id = parent_message.id
        
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            workgroup_id=workgroup.id,
            parent_id=parent_id
        )
        
        db.session.add(message)
        
        # Create notifications for all workgroup members except current user
        for member in workgroup.members:
            if member.id != current_user.id:
                notification = Notification(
                    user_id=member.id,
                    title=f"Nouveau message dans {workgroup.name}",
                    content=f"{current_user.username} a publié un message dans le groupe '{workgroup.name}'.",
                    notification_type='message',
                    source_id=message.id,
                    source_type='message'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        flash('Message publié avec succès!', 'success')
    else:
        for _, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')
    
    return redirect(url_for('workgroup_view', workgroup_id=workgroup.id))

@app.route('/workgroups/<int:workgroup_id>/notes')
@login_required
def workgroup_notes(workgroup_id):
    """View all notes in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is a member
    if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
        abort(403)
    
    notes = Note.query.filter_by(workgroup_id=workgroup.id).order_by(Note.updated_at.desc()).all()
    
    return render_template(
        'workgroups/notes.html',
        title=f'Notes - {workgroup.name}',
        workgroup=workgroup,
        notes=notes
    )

@app.route('/workgroups/<int:workgroup_id>/notes/new', methods=['GET', 'POST'])
@login_required
def workgroup_note_new(workgroup_id):
    """Create a new note in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    
    # Check if user is a member
    if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
        abort(403)
    
    form = NoteForm()
    
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            creator_id=current_user.id,
            workgroup_id=workgroup.id
        )
        
        db.session.add(note)
        
        # Create notifications for all workgroup members except current user
        for member in workgroup.members:
            if member.id != current_user.id:
                notification = Notification(
                    user_id=member.id,
                    title=f"Nouvelle note dans {workgroup.name}",
                    content=f"{current_user.username} a créé une nouvelle note '{note.title}' dans le groupe '{workgroup.name}'.",
                    notification_type='note',
                    source_id=workgroup.id,
                    source_type='workgroup'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        flash('Note créée avec succès!', 'success')
        return redirect(url_for('workgroup_notes', workgroup_id=workgroup.id))
    
    return render_template(
        'workgroups/note_form.html',
        title='Nouvelle note',
        form=form,
        workgroup=workgroup
    )

@app.route('/workgroups/<int:workgroup_id>/notes/<int:note_id>')
@login_required
def workgroup_note_view(workgroup_id, note_id):
    """View a note in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    note = Note.query.get_or_404(note_id)
    
    # Check if note belongs to the workgroup
    if note.workgroup_id != workgroup.id:
        abort(404)
    
    # Check if user is a member
    if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
        abort(403)
    
    return render_template(
        'workgroups/note_view.html',
        title=note.title,
        workgroup=workgroup,
        note=note
    )

@app.route('/workgroups/<int:workgroup_id>/notes/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def workgroup_note_edit(workgroup_id, note_id):
    """Edit a note in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    note = Note.query.get_or_404(note_id)
    
    # Check if note belongs to the workgroup
    if note.workgroup_id != workgroup.id:
        abort(404)
    
    # Check if user is a member and is the creator or admin
    is_admin = workgroup.owner_id == current_user.id or workgroup.get_member_role(current_user) == 'admin'
    if note.creator_id != current_user.id and not is_admin:
        abort(403)
    
    form = NoteForm(obj=note)
    
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Note mise à jour avec succès!', 'success')
        return redirect(url_for('workgroup_note_view', workgroup_id=workgroup.id, note_id=note.id))
    
    return render_template(
        'workgroups/note_form.html',
        title='Modifier note',
        form=form,
        workgroup=workgroup,
        note=note
    )

@app.route('/workgroups/<int:workgroup_id>/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def workgroup_note_delete(workgroup_id, note_id):
    """Delete a note in a workgroup"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)
    note = Note.query.get_or_404(note_id)
    
    # Check if note belongs to the workgroup
    if note.workgroup_id != workgroup.id:
        abort(404)
    
    # Check if user is a member and is the creator or admin
    is_admin = workgroup.owner_id == current_user.id or workgroup.get_member_role(current_user) == 'admin'
    if note.creator_id != current_user.id and not is_admin:
        abort(403)
    
    db.session.delete(note)
    db.session.commit()
    
    flash('Note supprimée avec succès!', 'success')
    return redirect(url_for('workgroup_notes', workgroup_id=workgroup.id))

@app.route('/notifications')
@login_required
def notifications_list():
    """View all user notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark all as read
    for notification in notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return render_template(
        'notifications/list.html',
        title='Notifications',
        notifications=notifications
    )

@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def notification_delete(notification_id):
    """Delete a notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Check if notification belongs to user
    if notification.user_id != current_user.id:
        abort(403)
    
    db.session.delete(notification)
    db.session.commit()
    
    flash('Notification supprimée avec succès!', 'success')
    return redirect(url_for('notifications_list'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for users, workgroups, and exercises"""
    form = SearchForm()
    results = None
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data if form.validate_on_submit() else request.args.get('query')
        search_type = form.search_type.data if form.validate_on_submit() else request.args.get('search_type', 'all')
        
        results = {
            'users': [],
            'workgroups': [],
            'exercises': []
        }
        
        # Search for users
        if search_type in ['all', 'users']:
            users = User.query.filter(
                (User.username.ilike(f'%{query}%')) | 
                (User.full_name.ilike(f'%{query}%'))
            ).all()
            results['users'] = users
        
        # Search for workgroups
        if search_type in ['all', 'workgroups']:
            # Get public workgroups
            public_workgroups = Workgroup.query.filter(
                (Workgroup.name.ilike(f'%{query}%')) & 
                (Workgroup.is_private == False)
            ).all()
            
            # Get private workgroups where user is a member
            private_workgroups = Workgroup.query.join(
                workgroup_members, 
                workgroup_members.c.workgroup_id == Workgroup.id
            ).filter(
                (Workgroup.name.ilike(f'%{query}%')) & 
                (workgroup_members.c.user_id == current_user.id)
            ).all()
            
            # Combine and remove duplicates
            results['workgroups'] = list(set(public_workgroups + private_workgroups))
        
        # Search for exercises
        if search_type in ['all', 'exercises']:
            # Get user's own exercises
            own_exercises = Exercise.query.filter(
                (Exercise.name.ilike(f'%{query}%')) & 
                (Exercise.user_id == current_user.id)
            ).all()
            
            # Get exercises shared with user in workgroups
            shared_exercises = Exercise.query.join(
                workgroup_exercises,
                workgroup_exercises.c.exercise_id == Exercise.id
            ).join(
                workgroup_members,
                workgroup_members.c.workgroup_id == workgroup_exercises.c.workgroup_id
            ).filter(
                (Exercise.name.ilike(f'%{query}%')) & 
                (workgroup_members.c.user_id == current_user.id)
            ).all()
            
            # Combine and remove duplicates
            results['exercises'] = list(set(own_exercises + shared_exercises))
    
    return render_template(
        'search.html',
        title='Recherche',
        form=form,
        results=results,
        query=request.args.get('query', ''),
        search_type=request.args.get('search_type', 'all')
    )

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.route('/exercise-solver/complete', methods=['GET', 'POST'])
@login_required
def exercise_solver_complete():
    """Formulaire de résolution complète d'exercice avec génération des documents comptables."""
    form = CompleteExerciseSolverForm()
    
    # Charge les exercices disponibles pour l'utilisateur
    form.exercise_id.choices = [(e.id, e.name) for e in Exercise.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        # Résoudre l'exercice et générer les documents
        result = resolve_exercise_completely(
            exercise_id=form.exercise_id.data,
            problem_text=form.problem_text.data
        )
        
        if result['success']:
            # Ajouter les liens vers les documents générés
            solution_id = result.get('solution')
            solution = ExerciseSolution.query.get(solution_id) if solution_id else None
            
            flash('Exercice résolu et documents générés avec succès!', 'success')
            return render_template(
                'exercise_solver/complete_solution.html',
                title='Solution complète',
                exercise=Exercise.query.get(form.exercise_id.data),
                solution=solution,
                documents={
                    'journal': result.get('journal'),
                    'grand_livre': result.get('grand_livre'),
                    'bilan': result.get('bilan')
                }
            )
        else:
            for error in result.get('errors', []):
                flash(error, 'danger')
    
    return render_template(
        'exercise_solver/complete_form.html',
        title='Résolution complète d\'exercice',
        form=form
    )

@app.route('/reports/<path:filename>')
@login_required
def download_report(filename):
    """Télécharger un rapport généré"""
    # Trouver le chemin du rapport dans le dossier uploads
    reports_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id), 'reports')
    return send_file(os.path.join(reports_dir, filename), as_attachment=True)


@app.route('/exercise-examples/import', methods=['GET', 'POST'])
@login_required
def exercise_import():
    """Importation d'exercices depuis un fichier JSON."""
    # Vérifier si l'utilisateur a les droits d'importation (admin ou enseignant)
    if not current_user.is_admin:
        flash('Vous n\'avez pas les droits pour importer des exercices.', 'danger')
        return redirect(url_for('exercise_examples_list'))
    
    form = ExerciseImportForm()
    
    if form.validate_on_submit():
        json_file = form.json_file.data
        
        # Enregistrer temporairement le fichier
        filename = secure_filename(json_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        json_file.save(temp_path)
        
        # Importer les exercices
        from import_exercises import import_exercises_from_json
        count, errors = import_exercises_from_json(temp_path)
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Afficher les résultats
        if count > 0:
            flash(f'{count} exercices importés avec succès!', 'success')
        
        if errors:
            for error in errors[:5]:  # Afficher jusqu'à 5 erreurs
                flash(error, 'warning')
            
            if len(errors) > 5:
                flash(f'...et {len(errors) - 5} autres erreurs. Vérifiez le format du fichier JSON.', 'warning')
        
        if count > 0:
            return redirect(url_for('exercise_examples_list'))
    
    return render_template(
        'exercise_solver/import_form.html',
        title='Importer des exercices',
        form=form
    )
