
#!/usr/bin/env python
"""
Script pour créer des données de test pour l'application SmartOHADA.
Ce script va créer des utilisateurs, des exercices, des transactions, et d'autres entités
pour permettre de tester toutes les fonctionnalités de l'application.
"""
import os
import sys
import random
import string
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Assurez-vous que l'environnement est correctement configuré
from dotenv import load_dotenv
load_dotenv()

# Importez l'application Flask et la base de données
try:
    from app import app, db
    from models import (User, Exercise, Account, Transaction, TransactionItem, 
                       Document, Workgroup, Message, Note, Post, Comment, Like,
                       Story, Notification, workgroup_members, workgroup_exercises)
except ImportError as e:
    logger.error(f"Erreur d'importation: {e}")
    sys.exit(1)

def random_string(length=10):
    """Génère une chaîne aléatoire de caractères."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_date(start_date, end_date):
    """Génère une date aléatoire entre start_date et end_date."""
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)

def create_test_users():
    """Crée des utilisateurs de test."""
    logger.info("Création des utilisateurs de test...")
    users = []
    
    # Récupérer ou créer l'administrateur
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@smartohada.com",
            full_name="Administrateur SmartOHADA",
            is_admin=True,
            bio="Administrateur du système SmartOHADA",
            position="Administrateur",
            company="SmartOHADA",
            is_online=True
        )
        admin.set_password("admin123")
        users.append(admin)
    
    # Créer quelques utilisateurs réguliers
    for i in range(1, 6):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            full_name=f"Utilisateur Test {i}",
            bio=f"Je suis l'utilisateur de test numéro {i}",
            position=f"Comptable {i}",
            company=f"Entreprise {i}",
            is_online=bool(random.getrandbits(1))
        )
        user.set_password(f"password{i}")
        users.append(user)
    
    # Ajouter les utilisateurs à la base de données
    for user in users:
        db.session.add(user)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(users)} utilisateurs réussie.")
        return users
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des utilisateurs: {e}")
        return []

def create_exercises(users):
    """Crée des exercices comptables pour les utilisateurs."""
    logger.info("Création des exercices comptables...")
    exercises = []
    
    for user in users:
        # Créer 1-3 exercices par utilisateur
        for i in range(random.randint(1, 3)):
            start_date = datetime.now().date() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=365)
            
            exercise = Exercise(
                name=f"Exercice {i+1} - {user.username}",
                start_date=start_date,
                end_date=end_date,
                description=f"Exercice comptable {i+1} pour l'utilisateur {user.username}",
                user_id=user.id,
                is_closed=random.random() < 0.3  # 30% de chance d'être clôturé
            )
            exercises.append(exercise)
    
    # Ajouter les exercices à la base de données
    for exercise in exercises:
        db.session.add(exercise)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(exercises)} exercices réussie.")
        return exercises
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des exercices: {e}")
        return []

def create_accounts(exercises):
    """Crée des comptes comptables pour les exercices."""
    logger.info("Création des comptes comptables...")
    accounts = []
    
    # Plan comptable de base OHADA
    base_accounts = [
        # Classe 1: Comptes de ressources durables
        {"number": "101", "name": "Capital", "type": "equity"},
        {"number": "106", "name": "Réserves", "type": "equity"},
        {"number": "120", "name": "Report à nouveau", "type": "equity"},
        {"number": "131", "name": "Résultat net de l'exercice", "type": "equity"},
        {"number": "165", "name": "Emprunts", "type": "liability"},
        
        # Classe 2: Comptes d'actifs immobilisés
        {"number": "211", "name": "Terrains", "type": "asset"},
        {"number": "213", "name": "Constructions", "type": "asset"},
        {"number": "244", "name": "Matériel", "type": "asset"},
        {"number": "245", "name": "Matériel de transport", "type": "asset"},
        {"number": "275", "name": "Dépôts et cautionnements", "type": "asset"},
        {"number": "281", "name": "Amortissements des immobilisations incorporelles", "type": "contra-asset"},
        {"number": "283", "name": "Amortissements des immobilisations corporelles", "type": "contra-asset"},
        
        # Classe 3: Comptes de stocks
        {"number": "311", "name": "Marchandises", "type": "asset"},
        {"number": "331", "name": "Matières premières", "type": "asset"},
        {"number": "351", "name": "Produits finis", "type": "asset"},
        {"number": "391", "name": "Dépréciations des stocks", "type": "contra-asset"},
        
        # Classe 4: Comptes de tiers
        {"number": "401", "name": "Fournisseurs", "type": "liability"},
        {"number": "411", "name": "Clients", "type": "asset"},
        {"number": "421", "name": "Personnel, avances et acomptes", "type": "asset"},
        {"number": "431", "name": "Sécurité sociale", "type": "liability"},
        {"number": "445", "name": "État, TVA récupérable", "type": "asset"},
        {"number": "447", "name": "État, TVA collectée", "type": "liability"},
        
        # Classe 5: Comptes de trésorerie
        {"number": "512", "name": "Banques", "type": "asset"},
        {"number": "521", "name": "Caisse", "type": "asset"},
        
        # Classe 6: Comptes de charges
        {"number": "601", "name": "Achats de marchandises", "type": "expense"},
        {"number": "607", "name": "Achats de matières premières", "type": "expense"},
        {"number": "612", "name": "Transports", "type": "expense"},
        {"number": "622", "name": "Locations et charges locatives", "type": "expense"},
        {"number": "624", "name": "Entretien, réparations et maintenance", "type": "expense"},
        {"number": "627", "name": "Publicité, publications, relations publiques", "type": "expense"},
        {"number": "631", "name": "Frais bancaires", "type": "expense"},
        {"number": "641", "name": "Impôts et taxes directs", "type": "expense"},
        {"number": "661", "name": "Charges de personnel", "type": "expense"},
        {"number": "681", "name": "Dotations aux amortissements", "type": "expense"},
        
        # Classe 7: Comptes de produits
        {"number": "701", "name": "Ventes de marchandises", "type": "revenue"},
        {"number": "706", "name": "Prestations de services", "type": "revenue"},
        {"number": "707", "name": "Ventes de produits finis", "type": "revenue"},
        {"number": "718", "name": "Autres produits d'exploitation", "type": "revenue"},
        {"number": "771", "name": "Intérêts et produits assimilés", "type": "revenue"},
        {"number": "791", "name": "Transferts de charges d'exploitation", "type": "revenue"},
    ]
    
    for exercise in exercises:
        # Ne pas créer de comptes pour les exercices clôturés
        if exercise.is_closed:
            continue
        
        for account_data in base_accounts:
            account = Account(
                account_number=account_data["number"],
                name=account_data["name"],
                account_type=account_data["type"],
                description=f"Compte {account_data['number']} - {account_data['name']}",
                exercise_id=exercise.id,
                is_system=True,
                is_active=True
            )
            accounts.append(account)
    
    # Ajouter les comptes à la base de données
    for account in accounts:
        db.session.add(account)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(accounts)} comptes comptables réussie.")
        return accounts
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des comptes: {e}")
        return []

def create_transactions(exercises, users):
    """Crée des transactions pour les exercices."""
    logger.info("Création des transactions...")
    transactions = []
    transaction_items = []
    
    for exercise in exercises:
        # Ne pas créer de transactions pour les exercices clôturés
        if exercise.is_closed:
            continue
            
        # Obtenir les comptes pour cet exercice
        accounts = Account.query.filter_by(exercise_id=exercise.id).all()
        if not accounts:
            continue
            
        # Créer 5-10 transactions par exercice
        for i in range(random.randint(5, 10)):
            transaction_date = random_date(exercise.start_date, min(exercise.end_date, datetime.now().date()))
            
            transaction = Transaction(
                reference=f"TR-{exercise.id}-{i+1}",
                transaction_date=transaction_date,
                description=f"Transaction {i+1} pour l'exercice {exercise.id}",
                is_posted=random.random() < 0.7,  # 70% de chance d'être comptabilisée
                user_id=exercise.user_id,
                exercise_id=exercise.id
            )
            db.session.add(transaction)
            # Flushons pour obtenir l'ID de la transaction
            db.session.flush()
            transactions.append(transaction)
            
            # Créer 2-5 lignes de transaction
            total_amount = random.randint(1000, 10000)
            debit_accounts = random.sample(accounts, min(random.randint(1, 3), len(accounts)))
            credit_accounts = random.sample([a for a in accounts if a not in debit_accounts], 
                                           min(random.randint(1, 3), len(accounts) - len(debit_accounts)))
            
            # Répartir le montant entre les comptes de débit
            debit_amounts = []
            remaining_amount = total_amount
            for _ in range(len(debit_accounts) - 1):
                amount = random.randint(1, remaining_amount // 2)
                debit_amounts.append(amount)
                remaining_amount -= amount
            debit_amounts.append(remaining_amount)
            
            # Créer les lignes de débit
            for debit_account, amount in zip(debit_accounts, debit_amounts):
                item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=debit_account.id,
                    description=f"Débit {debit_account.name}",
                    debit_amount=amount,
                    credit_amount=0
                )
                db.session.add(item)
                transaction_items.append(item)
            
            # Répartir le montant entre les comptes de crédit
            credit_amounts = []
            remaining_amount = total_amount
            for _ in range(len(credit_accounts) - 1):
                amount = random.randint(1, remaining_amount // 2)
                credit_amounts.append(amount)
                remaining_amount -= amount
            credit_amounts.append(remaining_amount)
            
            # Créer les lignes de crédit
            for credit_account, amount in zip(credit_accounts, credit_amounts):
                item = TransactionItem(
                    transaction_id=transaction.id,
                    account_id=credit_account.id,
                    description=f"Crédit {credit_account.name}",
                    debit_amount=0,
                    credit_amount=amount
                )
                db.session.add(item)
                transaction_items.append(item)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(transactions)} transactions et {len(transaction_items)} lignes réussie.")
        return transactions
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des transactions: {e}")
        return []

def create_documents(exercises, users):
    """Crée des documents fictifs pour les exercices."""
    logger.info("Création des documents fictifs...")
    documents = []
    
    document_types = ["invoice", "receipt", "statement", "contract", "report"]
    
    for exercise in exercises:
        # Ne pas créer de documents pour les exercices clôturés
        if exercise.is_closed:
            continue
            
        # Créer 3-7 documents par exercice
        for i in range(random.randint(3, 7)):
            doc_type = random.choice(document_types)
            original_filename = f"{doc_type}_{random_string()}.pdf"
            filename = f"uploads/{original_filename}"  # Chemin fictif
            
            document = Document(
                original_filename=original_filename,
                filename=filename,
                document_type=doc_type,
                description=f"Document {doc_type} pour l'exercice {exercise.id}",
                upload_date=random_date(exercise.start_date, datetime.now().date()),
                processed=random.random() < 0.5,  # 50% de chance d'être traité
                user_id=exercise.user_id,
                exercise_id=exercise.id
            )
            documents.append(document)
    
    # Ajouter les documents à la base de données
    for document in documents:
        db.session.add(document)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(documents)} documents réussie.")
        return documents
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des documents: {e}")
        return []

def create_workgroups(users):
    """Crée des groupes de travail."""
    logger.info("Création des groupes de travail...")
    workgroups = []
    
    # Créer 3 groupes de travail
    workgroup_data = [
        {"name": "Groupe de travail comptabilité générale", "is_private": False},
        {"name": "Experts OHADA", "is_private": True},
        {"name": "Projet comptable 2025", "is_private": False}
    ]
    
    for i, data in enumerate(workgroup_data):
        owner = users[i % len(users)]
        workgroup = Workgroup(
            name=data["name"],
            description=f"Description du groupe {data['name']}",
            is_private=data["is_private"],
            owner_id=owner.id
        )
        db.session.add(workgroup)
        db.session.flush()  # Pour obtenir l'ID du groupe
        
        # Ajouter le propriétaire comme membre admin
        db.session.execute(workgroup_members.insert().values(
            user_id=owner.id,
            workgroup_id=workgroup.id,
            role='admin'
        ))
        
        # Ajouter quelques membres
        members = random.sample([u for u in users if u.id != owner.id], 
                               min(random.randint(1, 3), len(users) - 1))
        for member in members:
            db.session.execute(workgroup_members.insert().values(
                user_id=member.id,
                workgroup_id=workgroup.id,
                role='member'
            ))
        
        workgroups.append(workgroup)
    
    try:
        db.session.commit()
        logger.info(f"Création de {len(workgroups)} groupes de travail réussie.")
        return workgroups
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des groupes de travail: {e}")
        return []

def create_workgroup_content(workgroups, users, exercises):
    """Crée du contenu pour les groupes de travail (messages, notes, etc.)."""
    logger.info("Création du contenu des groupes de travail...")
    
    for workgroup in workgroups:
        # Partager quelques exercices
        user_exercises = Exercise.query.filter(
            Exercise.user_id.in_([m.id for m in workgroup.members])
        ).limit(3).all()
        
        for exercise in user_exercises:
            db.session.execute(workgroup_exercises.insert().values(
                exercise_id=exercise.id,
                workgroup_id=workgroup.id,
                shared_by=exercise.user_id
            ))
        
        # Créer des messages
        for i in range(random.randint(5, 10)):
            sender = random.choice(workgroup.members)
            message = Message(
                content=f"Message {i+1} dans le groupe {workgroup.name}. Ceci est un exemple de message.",
                sender_id=sender.id,
                workgroup_id=workgroup.id,
                sent_at=datetime.now() - timedelta(days=random.randint(0, 30), 
                                                  hours=random.randint(0, 23))
            )
            db.session.add(message)
        
        # Créer des notes
        for i in range(random.randint(2, 5)):
            creator = random.choice(workgroup.members)
            note = Note(
                title=f"Note {i+1} - {workgroup.name}",
                content=f"Contenu de la note {i+1} pour le groupe {workgroup.name}. Ceci est un exemple de note partagée.",
                creator_id=creator.id,
                workgroup_id=workgroup.id
            )
            db.session.add(note)
    
    try:
        db.session.commit()
        logger.info("Création du contenu des groupes de travail réussie.")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création du contenu des groupes: {e}")
        return False

def create_social_content(users):
    """Crée du contenu social (posts, commentaires, likes, etc.)."""
    logger.info("Création du contenu social...")
    
    # Créer des posts
    posts = []
    for i in range(15):
        user = random.choice(users)
        post = Post(
            content=f"Publication {i+1} par {user.username}. Ceci est un exemple de publication.",
            user_id=user.id,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        db.session.add(post)
        db.session.flush()
        posts.append(post)
    
    # Créer des commentaires
    for post in posts:
        # 0-5 commentaires par post
        for i in range(random.randint(0, 5)):
            commenter = random.choice([u for u in users if u.id != post.user_id])
            comment = Comment(
                content=f"Commentaire {i+1} sur le post {post.id}. Ceci est un exemple de commentaire.",
                user_id=commenter.id,
                post_id=post.id,
                created_at=post.created_at + timedelta(hours=random.randint(1, 24))
            )
            db.session.add(comment)
    
    # Créer des likes
    for post in posts:
        # 0-8 likes par post
        likers = random.sample(users, min(random.randint(0, 8), len(users)))
        for liker in likers:
            like = Like(
                user_id=liker.id,
                post_id=post.id,
                reaction_type=random.choice(['like', 'love', 'haha', 'wow'])
            )
            db.session.add(like)
    
    # Créer des stories
    for i in range(min(5, len(users))):
        user = users[i]
        expires_at = datetime.now() + timedelta(hours=24)
        story = Story(
            content=f"Story {i+1} par {user.username}",
            media_url=f"/static/images/story_{i+1}.jpg",  # URL fictive
            media_type="image",
            created_at=datetime.now() - timedelta(hours=random.randint(1, 12)),
            expires_at=expires_at,
            is_expired=False,
            user_id=user.id
        )
        db.session.add(story)
    
    try:
        db.session.commit()
        logger.info("Création du contenu social réussie.")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création du contenu social: {e}")
        return False

def create_notifications(users):
    """Crée des notifications pour les utilisateurs."""
    logger.info("Création des notifications...")
    
    notification_types = ['message', 'invite', 'system', 'share']
    
    for user in users:
        # 3-8 notifications par utilisateur
        for i in range(random.randint(3, 8)):
            notification_type = random.choice(notification_types)
            is_read = random.random() < 0.5  # 50% de chance d'être lue
            
            notification = Notification(
                user_id=user.id,
                title=f"Notification {i+1} - {notification_type}",
                content=f"Contenu de la notification {i+1} pour {user.username}. Type: {notification_type}",
                notification_type=notification_type,
                is_read=is_read,
                created_at=datetime.now() - timedelta(days=random.randint(0, 14), 
                                                     hours=random.randint(0, 23))
            )
            db.session.add(notification)
    
    try:
        db.session.commit()
        logger.info("Création des notifications réussie.")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des notifications: {e}")
        return False

def main():
    """Fonction principale pour créer toutes les données de test."""
    with app.app_context():
        try:
            # Vérifier si des données existent déjà
            existing_users = User.query.count()
            if existing_users > 0:
                logger.warning(f"{existing_users} utilisateurs existent déjà dans la base de données.")
                choice = input("Des données existent déjà. Voulez-vous continuer et ajouter plus de données? (o/n): ")
                if choice.lower() != 'o':
                    logger.info("Opération annulée par l'utilisateur.")
                    return
            
            # Créer les données dans l'ordre de dépendance
            users = create_test_users()
            if not users:
                logger.error("Échec de la création des utilisateurs. Arrêt du script.")
                return
                
            exercises = create_exercises(users)
            if not exercises:
                logger.error("Échec de la création des exercices. Arrêt du script.")
                return
                
            accounts = create_accounts(exercises)
            
            transactions = create_transactions(exercises, users)
            
            documents = create_documents(exercises, users)
            
            workgroups = create_workgroups(users)
            if workgroups:
                create_workgroup_content(workgroups, users, exercises)
            
            create_social_content(users)
            
            create_notifications(users)
            
            logger.info("Création de toutes les données de test terminée avec succès!")
            logger.info(f"Utilisateurs créés: {len(users)} (admin/admin123, user1/password1, etc.)")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des données de test: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
