from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FileField, FloatField, IntegerField, HiddenField, SubmitField, DateField, DecimalField, EmailField
from wtforms.fields import FormField, FieldList
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from datetime import date

from models import User
from app import db

class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Adresse email', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Nom complet', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    show_password = BooleanField('Afficher le mot de passe')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà utilisé. Veuillez en choisir un autre.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Cette adresse email est déjà utilisée. Veuillez en choisir une autre.')

class ProfileForm(FlaskForm):
    """Form for editing user profile"""
    full_name = StringField('Nom complet', validators=[DataRequired(), Length(max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    profile_picture = FileField('Photo de profil', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images uniquement!')
    ])
    current_password = PasswordField('Mot de passe actuel', validators=[Optional()])
    new_password = PasswordField('Nouveau mot de passe', validators=[Optional(), Length(min=8)])
    confirm_new_password = PasswordField('Confirmer le nouveau mot de passe', validators=[
        Optional(), EqualTo('new_password', message='Les mots de passe doivent correspondre')
    ])
    show_password = BooleanField('Afficher les mots de passe')

    def validate_current_password(self, field):
        from flask_login import current_user

        if field.data and not current_user.check_password(field.data):
            raise ValidationError('Mot de passe incorrect')

        if self.new_password.data and not field.data:
            raise ValidationError('Veuillez saisir votre mot de passe actuel pour le modifier')

class ExerciseForm(FlaskForm):
    """Form for creating/editing exercises"""
    name = StringField('Nom de l\'exercice', validators=[DataRequired(), Length(max=100)])
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])

    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('La date de fin doit être postérieure à la date de début')

class AccountForm(FlaskForm):
    """Form for creating/editing accounts"""
    account_number = StringField('Numéro de compte', validators=[DataRequired(), Length(max=10)])
    name = StringField('Nom du compte', validators=[DataRequired(), Length(max=200)])
    account_type = SelectField('Type de compte', choices=[
        ('asset', 'Actif'), 
        ('liability', 'Passif'), 
        ('equity', 'Capitaux propres'), 
        ('revenue', 'Produit'), 
        ('expense', 'Charge')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    parent_id = SelectField('Compte parent', coerce=int, validators=[Optional()])

class TransactionItemForm(FlaskForm):
    """Form for transaction items"""
    id = HiddenField('ID')
    account_id = SelectField('Compte', coerce=int, validators=[DataRequired()])
    description = StringField('Description', validators=[Optional(), Length(max=200)])
    debit_amount = DecimalField('Débit', validators=[Optional()], default=0)
    credit_amount = DecimalField('Crédit', validators=[Optional()], default=0)

class TransactionForm(FlaskForm):
    """Form for creating/editing transactions"""
    reference = StringField('Référence', validators=[DataRequired(), Length(max=50)])
    transaction_date = DateField('Date de transaction', validators=[DataRequired()], default=date.today)
    description = TextAreaField('Description', validators=[Optional()])
    is_posted = BooleanField('Comptabilisé', default=False)
    items = FieldList(FormField(TransactionItemForm), min_entries=2)

    def setup_transaction_items(self, transaction=None):
        """Add transaction items to the form"""
        if transaction:
            # Clear existing entries
            self.items.entries = []

            # Add existing items
            for item in transaction.items:
                self.items.append_entry({
                    'id': item.id,
                    'account_id': item.account_id,
                    'description': item.description,
                    'debit_amount': item.debit_amount,
                    'credit_amount': item.credit_amount
                })

            # Ensure we have at least 2 entries
            while len(self.items) < 2:
                self.items.append_entry()
        else:
            # For new transactions, add two empty entries
            while len(self.items) < 2:
                self.items.append_entry()

    def validate(self):
        """Custom validation for transaction form"""
        if not super().validate():
            return False

        # Check if at least two valid items are provided
        valid_items = 0
        total_debit = 0
        total_credit = 0

        for item in self.items:
            if item.account_id.data and (item.debit_amount.data > 0 or item.credit_amount.data > 0):
                valid_items += 1
                total_debit += float(item.debit_amount.data or 0)
                total_credit += float(item.credit_amount.data or 0)

        if valid_items < 2:
            self.items[0].account_id.errors = ["Au moins deux lignes d'écriture sont nécessaires"]
            return False

        # Check if transaction is balanced (if it's to be posted)
        if self.is_posted.data and abs(total_debit - total_credit) > 0.01:
            self.is_posted.errors = ["L'écriture doit être équilibrée pour être comptabilisée"]
            return False

        return True

class DocumentUploadForm(FlaskForm):
    """Form for uploading documents"""
    document = FileField('Document', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'tiff'], 'Seuls les fichiers PDF et image sont autorisés')
    ])
    document_type = SelectField('Type de document', choices=[
        ('invoice', 'Facture'),
        ('receipt', 'Reçu'),
        ('statement', 'Relevé bancaire'),
        ('contract', 'Contrat'),
        ('other', 'Autre')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    auto_process = BooleanField('Traiter automatiquement', default=True)

class ForgotPasswordForm(FlaskForm):
    """Form for requesting password reset"""
    email = StringField('Adresse email', validators=[DataRequired(), Email(), Length(max=120)])

class ResetPasswordForm(FlaskForm):
    """Form for resetting password"""
    password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    show_password = BooleanField('Afficher le mot de passe')

class TextProcessingForm(FlaskForm):
    """Form for text processing (summarization and paragraph structuring)"""
    text = TextAreaField('Texte à traiter', validators=[DataRequired(), Length(min=50, message="Le texte doit contenir au moins 50 caractères")])
    summarize = BooleanField('Résumer le texte', default=True)
    split_paragraphs = BooleanField('Répartir en paragraphes', default=True)
    analyze = BooleanField('Analyser la complexité du texte', default=True)
    compression_rate = SelectField('Taux de compression pour le résumé', choices=[
        ('0.2', '20% (résumé très court)'),
        ('0.3', '30% (résumé court)'),
        ('0.5', '50% (résumé moyen)'),
        ('0.7', '70% (résumé long)')
    ], default='0.3')

class ReportGenerationForm(FlaskForm):
    """Form for generating reports"""
    name = StringField('Nom du rapport', validators=[DataRequired(), Length(max=100)])
    report_type = SelectField('Type de rapport', choices=[
        ('balance_sheet', 'Bilan'),
        ('income_statement', 'Compte de résultat'),
        ('trial_balance', 'Balance générale'),
        ('general_ledger', 'Grand livre'),
        ('account_statement', 'Relevé de compte')
    ], validators=[DataRequired()])
    format = SelectField('Format', choices=[
        ('html', 'HTML'),
        ('xlsx', 'Excel')
    ], validators=[DataRequired()])
    start_date = DateField('Date de début', validators=[Optional()])
    end_date = DateField('Date de fin', validators=[Optional()])
    account_id = SelectField('Compte (pour relevé de compte)', coerce=int, validators=[Optional()])

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('La date de fin doit être postérieure à la date de début')

class ExerciseExampleUploadForm(FlaskForm):
    """Form for uploading example exercises"""
    title = StringField('Titre de l\'exemple', validators=[DataRequired(), Length(max=255)])
    example_file = FileField('Fichier PDF de l\'exemple', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Seuls les fichiers PDF sont autorisés')
    ])
    category = SelectField('Catégorie', choices=[
        ('journal', 'Écriture au journal'),
        ('bilan', 'Bilan'),
        ('resultat', 'Compte de résultat'),
        ('tva', 'TVA'),
        ('amortissement', 'Amortissement'),
        ('provision', 'Provision'),
        ('inventaire', 'Inventaire'),
        ('autre', 'Autre')
    ], validators=[DataRequired()])
    difficulty = SelectField('Niveau de difficulté', choices=[
        ('1', 'Très facile'),
        ('2', 'Facile'),
        ('3', 'Moyen'),
        ('4', 'Difficile'),
        ('5', 'Très difficile')
    ], coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])

class ExerciseSolverForm(FlaskForm):
    """Form for solving exercises using examples"""
    title = StringField('Titre de l\'exercice', validators=[DataRequired(), Length(max=255)])
    problem_text = TextAreaField('Texte de l\'exercice', validators=[
        DataRequired(), 
        Length(min=50, message="Le texte de l'exercice doit contenir au moins 50 caractères")
    ])
    category = SelectField('Catégorie', choices=[
        ('journal', 'Écriture au journal'),
        ('bilan', 'Bilan'),
        ('resultat', 'Compte de résultat'),
        ('tva', 'TVA'),
        ('amortissement', 'Amortissement'),
        ('provision', 'Provision'),
        ('inventaire', 'Inventaire'),
        ('autre', 'Autre')
    ], validators=[DataRequired()])


# Forms for communication and group collaboration
class WorkgroupForm(FlaskForm):
    """Form for creating and editing workgroups"""
    name = StringField('Nom du groupe', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    is_private = BooleanField('Groupe privé', default=False)

class MessageForm(FlaskForm):
    """Form for sending messages in workgroups"""
    content = TextAreaField('Message', validators=[DataRequired()])
    parent_id = HiddenField('Message parent')

class NoteForm(FlaskForm):
    """Form for creating and editing shared notes"""
    title = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Contenu', validators=[DataRequired()])

class MemberInviteForm(FlaskForm):
    """Form for inviting members to a workgroup"""
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    role = SelectField('Rôle', choices=[
        ('member', 'Membre'),
        ('admin', 'Administrateur')
    ], default='member', validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError('Cet utilisateur n\'existe pas.')

class WorkgroupExerciseForm(FlaskForm):
    """Form for sharing exercises with a workgroup"""
    exercise_id = SelectField('Exercice à partager', coerce=int, validators=[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Rechercher', validators=[DataRequired()])
    search_type = SelectField('Type', choices=[
        ('all', 'Tout'),
        ('users', 'Utilisateurs'),
        ('workgroups', 'Groupes de travail'),
        ('exercises', 'Exercices')
    ], default='all')
    submit = SubmitField('Rechercher')

class CompleteExerciseSolverForm(FlaskForm):
    """Formulaire pour la résolution complète d'un exercice avec génération des documents comptables"""
    title = StringField('Titre', validators=[DataRequired(), Length(min=3, max=255)])
    problem_text = TextAreaField('Énoncé de l\'exercice', validators=[DataRequired()])
    exercise_id = SelectField('Exercice', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Résoudre et générer les documents')

class ExerciseImportForm(FlaskForm):
    """Formulaire pour importer des exercices depuis un fichier JSON"""
    json_file = FileField(
        'Fichier JSON',
        validators=[
            DataRequired(),
            FileAllowed(['json'], 'Seuls les fichiers JSON sont acceptés')
        ]
    )
    submit = SubmitField('Importer')