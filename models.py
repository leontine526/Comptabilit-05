from datetime import datetime, timedelta
import secrets
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # Admin flag pour gérer les permissions
    
    # Profile fields
    avatar = db.Column(db.String(255))  # Lien vers l'avatar ou le chemin du fichier
    profile_picture = db.Column(db.String(255))  # Photo de profil de l'utilisateur
    bio = db.Column(db.Text)  # Courte biographie de l'utilisateur
    position = db.Column(db.String(100))  # Poste ou fonction
    company = db.Column(db.String(100))  # Entreprise
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # Dernière connexion
    is_online = db.Column(db.Boolean, default=False)  # Statut de connexion
    
    # Social fields
    socket_id = db.Column(db.String(100))  # ID de la connexion WebSocket
    
    # Dashboard personalization
    dashboard_layout = db.Column(db.Text, default='{}')  # JSON stockant la disposition des widgets
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    exercises = db.relationship('Exercise', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self):
        """Generate a secure password reset token that expires in 24 hours"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify the reset token is valid and not expired"""
        if self.reset_token != token:
            return False
        if not self.reset_token_expiry or datetime.utcnow() > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear the reset token after it has been used"""
        self.reset_token = None
        self.reset_token_expiry = None
    
    @staticmethod
    def find_by_reset_token(token):
        """Find a user by reset token"""
        return User.query.filter_by(reset_token=token).first()
    
    def __repr__(self):
        return f'<User {self.username}>'
        
    @property
    def unread_notifications_count(self):
        """Retourne le nombre de notifications non lues"""
        return self.notifications.filter_by(is_read=False).count()
        
    def mark_notifications_as_read(self):
        """Marque toutes les notifications de l'utilisateur comme lues"""
        self.notifications.filter_by(is_read=False).update({Notification.is_read: True})
        db.session.commit()
        
    def update_last_seen(self):
        """Met à jour la date de dernière connexion de l'utilisateur"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
        
    def set_online_status(self, is_online=True):
        """Met à jour le statut de connexion de l'utilisateur"""
        self.is_online = is_online
        db.session.commit()
        
    def add_notification(self, title, content, notification_type, source_id=None, source_type=None):
        """Ajoute une notification pour l'utilisateur"""
        notification = Notification(
            user_id=self.id,
            title=title,
            content=content,
            notification_type=notification_type,
            source_id=source_id,
            source_type=source_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
        
    def get_dashboard_layout(self):
        """Récupère la disposition des widgets du tableau de bord"""
        if not self.dashboard_layout or self.dashboard_layout == '{}':
            # Disposition par défaut si aucune n'est définie
            default_layout = {
                'widgets': [
                    {'id': 'exercises', 'title': 'Exercices récents', 'position': {'col': 1, 'row': 1, 'size': 'medium'}},
                    {'id': 'transactions', 'title': 'Transactions récentes', 'position': {'col': 2, 'row': 1, 'size': 'medium'}},
                    {'id': 'documents', 'title': 'Documents récents', 'position': {'col': 1, 'row': 2, 'size': 'medium'}},
                    {'id': 'workgroups', 'title': 'Groupes de travail', 'position': {'col': 2, 'row': 2, 'size': 'small'}},
                    {'id': 'notifications', 'title': 'Notifications', 'position': {'col': 2, 'row': 3, 'size': 'small'}},
                    {'id': 'tools', 'title': 'Outils et ressources', 'position': {'col': 1, 'row': 3, 'size': 'large'}}
                ],
                'layout': {
                    'columns': 2,
                    'rows': 3
                }
            }
            return default_layout
        try:
            return json.loads(self.dashboard_layout)
        except json.JSONDecodeError:
            return {'widgets': [], 'layout': {'columns': 2, 'rows': 2}}
    
    def save_dashboard_layout(self, layout):
        """Enregistre la disposition des widgets du tableau de bord"""
        self.dashboard_layout = json.dumps(layout)
        db.session.commit()
        return self.dashboard_layout

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    is_closed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    accounts = db.relationship('Account', backref='exercise', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='exercise', lazy='dynamic')
    documents = db.relationship('Document', backref='exercise', lazy='dynamic')
    
    def __repr__(self):
        return f'<Exercise {self.name}>'

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    account_type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, revenue, expense
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    is_system = db.Column(db.Boolean, default=False)  # Indicates if it's a system account (from OHADA)
    
    # Relationships
    children = db.relationship('Account', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    transaction_items = db.relationship('TransactionItem', backref='account', lazy='dynamic')
    
    def __repr__(self):
        return f'<Account {self.account_number} - {self.name}>'
    
    @property
    def full_name(self):
        return f"{self.account_number} - {self.name}"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    is_posted = db.Column(db.Boolean, default=False)  # Whether transaction is posted to the ledger
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    
    # Relationships
    items = db.relationship('TransactionItem', backref='transaction', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Transaction {self.reference}>'
    
    @property
    def total_debit(self):
        return sum(item.debit_amount for item in self.items)
    
    @property
    def total_credit(self):
        return sum(item.credit_amount for item in self.items)
    
    @property
    def is_balanced(self):
        return abs(self.total_debit - self.total_credit) < 0.01  # Allow rounding errors

class TransactionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    debit_amount = db.Column(db.Numeric(15, 2), default=0)
    credit_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    
    def __repr__(self):
        return f'<TransactionItem {self.id} - {self.description}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename
    document_type = db.Column(db.String(50), nullable=False)  # invoice, receipt, statement, etc.
    description = db.Column(db.Text)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)  # Whether OCR/NLP has been run
    processing_result = db.Column(db.Text)  # Raw OCR text or processing result
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='document', lazy='dynamic')
    
    def __repr__(self):
        return f'<Document {self.original_filename}>'

class ExerciseExample(db.Model):
    """Modèle pour les exemples d'exercices résolus."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Nom du fichier PDF stocké
    problem_text = db.Column(db.Text)  # Texte de l'énoncé extrait
    solution_text = db.Column(db.Text)  # Texte de la solution extrait
    category = db.Column(db.String(100))  # Catégorie de l'exercice (ex: journal, bilan, TVA)
    difficulty = db.Column(db.Integer)  # Niveau de difficulté (1-5)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Utilisateur qui a téléchargé l'exemple
    user = db.relationship('User', backref=db.backref('exercise_examples', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ExerciseExample {self.title}>'

class ExerciseSolution(db.Model):
    """Modèle pour les solutions générées par le système."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    problem_text = db.Column(db.Text, nullable=False)  # Texte de l'énoncé soumis
    solution_text = db.Column(db.Text, nullable=False)  # Solution générée
    confidence = db.Column(db.Float, nullable=False)  # Niveau de confiance dans la solution (0-1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Référence aux exemples utilisés pour générer la solution
    examples_used = db.Column(db.Text)  # Liste des IDs d'exemples au format JSON
    
    # Utilisateur propriétaire
    user = db.relationship('User', backref=db.backref('exercise_solutions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<ExerciseSolution {self.title}>'
        
        
# Association table for users in workgroups (many-to-many)
workgroup_members = db.Table('workgroup_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('workgroup_id', db.Integer, db.ForeignKey('workgroup.id'), primary_key=True),
    db.Column('role', db.String(20), default='member'),  # admin, member
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

# Association table for exercises shared in workgroups (many-to-many)
workgroup_exercises = db.Table('workgroup_exercises',
    db.Column('exercise_id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True),
    db.Column('workgroup_id', db.Integer, db.ForeignKey('workgroup.id'), primary_key=True),
    db.Column('shared_at', db.DateTime, default=datetime.utcnow),
    db.Column('shared_by', db.Integer, db.ForeignKey('user.id'))
)


class Workgroup(db.Model):
    """Modèle pour les groupes de travail collaboratifs."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    owner = db.relationship('User', backref='owned_workgroups')
    members = db.relationship('User', secondary=workgroup_members, 
                              backref=db.backref('workgroups', lazy='dynamic'))
    exercises = db.relationship('Exercise', secondary=workgroup_exercises,
                               backref=db.backref('shared_in_workgroups', lazy='dynamic'))
    messages = db.relationship('Message', backref='workgroup', lazy='dynamic',
                              cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='workgroup', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Workgroup {self.name}>'
    
    def add_member(self, user, role='member'):
        """Add a user to the workgroup with the specified role."""
        stmt = workgroup_members.insert().values(
            user_id=user.id, 
            workgroup_id=self.id,
            role=role
        )
        db.session.execute(stmt)
        db.session.commit()
    
    def remove_member(self, user):
        """Remove a user from the workgroup."""
        stmt = workgroup_members.delete().where(
            workgroup_members.c.user_id == user.id,
            workgroup_members.c.workgroup_id == self.id
        )
        db.session.execute(stmt)
        db.session.commit()
    
    def get_member_role(self, user):
        """Get the role of a user in the workgroup."""
        stmt = db.select([workgroup_members.c.role]).where(
            workgroup_members.c.user_id == user.id,
            workgroup_members.c.workgroup_id == self.id
        )
        result = db.session.execute(stmt).fetchone()
        return result[0] if result else None
    
    def share_exercise(self, exercise, shared_by):
        """Share an exercise with the workgroup."""
        stmt = workgroup_exercises.insert().values(
            exercise_id=exercise.id,
            workgroup_id=self.id,
            shared_by=shared_by.id
        )
        db.session.execute(stmt)
        db.session.commit()
    
    def unshare_exercise(self, exercise):
        """Remove an exercise from the workgroup."""
        stmt = workgroup_exercises.delete().where(
            workgroup_exercises.c.exercise_id == exercise.id,
            workgroup_exercises.c.workgroup_id == self.id
        )
        db.session.execute(stmt)
        db.session.commit()


class Message(db.Model):
    """Modèle pour les messages dans les groupes de travail."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')
    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    def __repr__(self):
        return f'<Message {self.id} by {self.sender.username}>'


class Note(db.Model):
    """Modèle pour les notes partagées dans les groupes de travail."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='created_notes')
    
    def __repr__(self):
        return f'<Note {self.title}>'


class Post(db.Model):
    """Modèle pour les publications de style Facebook."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'), nullable=True)  # Peut être null si publication générale
    image_url = db.Column(db.String(255))  # URL de l'image attachée (optionnel)
    file_url = db.Column(db.String(255))  # URL du fichier attaché (optionnel)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def comment_count(self):
        return self.comments.count()
    
    def __repr__(self):
        return f'<Post {self.id} by {self.author.username}>'


class Comment(db.Model):
    """Modèle pour les commentaires sur les publications."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # Pour les réponses aux commentaires
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    likes = db.relationship('Like', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def like_count(self):
        return self.likes.count()
    
    def __repr__(self):
        return f'<Comment {self.id} on Post {self.post_id}>'


class Like(db.Model):
    """Modèle pour les likes sur publications et commentaires."""
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    reaction_type = db.Column(db.String(20), default='like')  # like, love, haha, wow, sad, angry
    
    def __repr__(self):
        target = f"Post {self.post_id}" if self.post_id else f"Comment {self.comment_id}"
        return f'<Like {self.reaction_type} on {target}>'

class Story(db.Model):
    """Modèle pour les stories éphémères."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)  # Peut être null si image uniquement
    media_url = db.Column(db.String(255), nullable=False)  # URL de l'image ou vidéo
    media_type = db.Column(db.String(20), default='image')  # image, video
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Date d'expiration (24h après création)
    is_expired = db.Column(db.Boolean, default=False)  # Flag pour indiquer si expiré
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workgroup_id = db.Column(db.Integer, db.ForeignKey('workgroup.id'), nullable=True)  # Si partagé dans un groupe
    
    # Relations
    user = db.relationship('User', backref=db.backref('stories', lazy='dynamic'))
    views = db.relationship('StoryView', backref='story', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Story {self.id} by {self.user.username}>'
    
    @property
    def view_count(self):
        return self.views.count()
    
    @property
    def remaining_time(self):
        """Retourne le temps restant en minutes avant expiration"""
        if self.is_expired:
            return 0
        now = datetime.utcnow()
        if now > self.expires_at:
            return 0
        diff = self.expires_at - now
        return int(diff.total_seconds() / 60)

class StoryView(db.Model):
    """Modèle pour suivre qui a vu une story."""
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation unique: un utilisateur ne peut voir une story qu'une fois
    __table_args__ = (db.UniqueConstraint('story_id', 'user_id', name='story_user_uc'),)
    
    # Relations
    user = db.relationship('User', backref=db.backref('story_views', lazy='dynamic'))
    
    def __repr__(self):
        return f'<StoryView {self.story_id} by {self.user.username}>'


class Notification(db.Model):
    """Modèle pour les notifications utilisateur."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # message, invite, system, etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_id = db.Column(db.Integer)  # ID of the source object (workgroup, message, etc.)
    source_type = db.Column(db.String(20))  # Type of the source (workgroup, message, etc.)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Notification {self.id} for {self.user.username}>'
    
    @property
    def source_url(self):
        """Generate the URL to the source of the notification."""
        if self.source_type == 'workgroup':
            return f'/workgroups/{self.source_id}'
        elif self.source_type == 'message':
            # Get the workgroup ID for the message
            message = Message.query.get(self.source_id)
            if message:
                return f'/workgroups/{message.workgroup_id}#message-{self.source_id}'
        elif self.source_type == 'exercise':
            return f'/exercises/{self.source_id}'
        return '#'  # Default URL