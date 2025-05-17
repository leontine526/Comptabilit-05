
#!/usr/bin/env python
"""
Script pour créer des publications dans le réseau social en utilisant les utilisateurs de test.
Ce script peut être exécuté indépendamment pour remplir le fil d'actualité avec du contenu de test.
"""
import os
import sys
import random
import logging
from datetime import datetime, timedelta
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
    from models import User, Post, Comment, Like, Workgroup
except ImportError as e:
    logger.error(f"Erreur d'importation: {e}")
    sys.exit(1)

# Contenu de test pour les publications
POST_CONTENTS = [
    "J'ai besoin d'aide sur l'application du système comptable OHADA pour une opération d'amortissement linéaire. Quelqu'un peut m'aider?",
    "Je viens de terminer la clôture de l'exercice comptable d'une PME. Quelle satisfaction de voir tous les comptes équilibrés!",
    "Bonjour à tous! Je suis nouveau dans ce réseau et je suis comptable depuis 5 ans dans une entreprise du secteur minier.",
    "Qui sera présent au séminaire sur la fiscalité des entreprises à Dakar le mois prochain?",
    "Voici un tableau de correspondance que j'ai créé entre le PCG français et le plan comptable OHADA. N'hésitez pas à le partager.",
    "Je recherche un logiciel de comptabilité compatible OHADA qui soit abordable pour une petite entreprise. Des suggestions?",
    "À tous les experts comptables: quelles sont les principales erreurs que vous avez rencontrées lors des audits cette année?",
    "J'organise une formation en ligne sur le traitement comptable des opérations de fusion-acquisition selon les normes OHADA. Contactez-moi si intéressé.",
    "La réforme fiscale qui entre en vigueur l'année prochaine va impacter considérablement nos méthodes de travail. Qu'en pensez-vous?",
    "Quelqu'un a-t-il déjà utilisé l'IA pour automatiser certaines tâches comptables? J'hésite à franchir le pas.",
    "Félicitations à tous les nouveaux diplômés en comptabilité! Bienvenue dans la profession.",
    "J'ai trouvé ce guide pratique sur l'application des IFRS dans le contexte OHADA. Très utile pour les opérations internationales.",
    "Comment gérez-vous les problèmes de trésorerie dans vos entreprises pendant la saison creuse?",
    "La numérisation des factures est devenue obligatoire pour les grandes entreprises. Quel système avez-vous adopté?",
    "Débat du jour: faut-il privilégier l'amortissement linéaire ou dégressif pour le matériel informatique?",
    "Je viens de lire un excellent article sur les enjeux de la comptabilité environnementale dans les pays africains. Je vous recommande cette lecture.",
    "Astuce du jour: pour optimiser votre TVA, n'oubliez pas de vérifier systématiquement les factures d'achat!",
    "Question technique: comment comptabilisez-vous les subventions d'investissement dans le système OHADA?",
    "Qui utilise SmartOHADA pour la gestion de sa comptabilité? J'aimerais avoir des retours d'expérience.",
    "Je viens de réussir mon examen d'expert-comptable! Tellement fier après toutes ces années d'effort."
]

# Contenu de test pour les commentaires
COMMENT_CONTENTS = [
    "Excellente publication, merci pour le partage!",
    "Je suis totalement d'accord avec ton point de vue.",
    "Je peux t'aider avec ça, envoie-moi un message.",
    "Intéressant! Je n'avais jamais vu les choses sous cet angle.",
    "Pourriez-vous préciser ce point particulier?",
    "J'ai eu la même expérience l'année dernière.",
    "Voici une ressource qui pourrait t'aider: [lien fictif]",
    "Je vais essayer cette approche dans mon travail.",
    "Félicitations pour cette réalisation!",
    "As-tu essayé la méthode alternative dont on parlait au séminaire?",
    "Cette information m'a beaucoup aidé, merci.",
    "J'aimerais en savoir plus sur ce sujet.",
    "Je partage ton opinion à 100%.",
    "Pourrions-nous en discuter plus en détail lors du prochain groupe de travail?",
    "C'est exactement le problème que nous avons rencontré le mois dernier."
]

def create_social_posts():
    """Crée des publications pour les utilisateurs de test."""
    logger.info("Création des publications sociales...")
    
    with app.app_context():
        # Récupérer tous les utilisateurs
        users = User.query.all()
        if not users:
            logger.error("Aucun utilisateur trouvé. Exécutez d'abord create_test_data.py.")
            return False
        
        # Récupérer tous les groupes
        workgroups = Workgroup.query.all()
        
        # Créer des publications
        posts_created = 0
        for _ in range(25):  # Créer 25 publications
            user = random.choice(users)
            content = random.choice(POST_CONTENTS)
            
            # Décider si la publication est dans un groupe ou publique
            workgroup_id = None
            if workgroups and random.random() < 0.3:  # 30% de chance d'être dans un groupe
                workgroup = random.choice(workgroups)
                # Vérifier si l'utilisateur est membre du groupe
                if user in workgroup.members or user.id == workgroup.owner_id:
                    workgroup_id = workgroup.id
            
            # Créer la publication
            post = Post(
                content=content,
                user_id=user.id,
                workgroup_id=workgroup_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 10), 
                                                       hours=random.randint(0, 23))
            )
            db.session.add(post)
            posts_created += 1
        
        try:
            db.session.commit()
            logger.info(f"{posts_created} publications créées.")
            
            # Créer des commentaires et likes pour les publications
            add_interactions()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Erreur lors de la création des publications: {e}")
            return False

def add_interactions():
    """Ajoute des commentaires et likes aux publications."""
    logger.info("Ajout de commentaires et likes aux publications...")
    
    # Récupérer tous les utilisateurs et publications
    users = User.query.all()
    posts = Post.query.all()
    
    if not posts:
        logger.error("Aucune publication trouvée.")
        return False
    
    comments_added = 0
    likes_added = 0
    
    # Pour chaque publication, ajouter des commentaires et likes
    for post in posts:
        # Ajouter des commentaires (0-5 par publication)
        for _ in range(random.randint(0, 5)):
            # Éviter que l'auteur commente sa propre publication
            potential_commenters = [u for u in users if u.id != post.user_id]
            if not potential_commenters:
                continue
                
            commenter = random.choice(potential_commenters)
            comment_content = random.choice(COMMENT_CONTENTS)
            
            comment = Comment(
                content=comment_content,
                user_id=commenter.id,
                post_id=post.id,
                created_at=post.created_at + timedelta(hours=random.randint(1, 24))
            )
            db.session.add(comment)
            comments_added += 1
        
        # Ajouter des likes (0-8 par publication)
        num_likes = random.randint(0, 8)
        potential_likers = random.sample(users, min(num_likes, len(users)))
        
        for liker in potential_likers:
            reaction_types = ['like', 'love', 'haha', 'wow', 'sad', 'angry']
            reaction = random.choice(reaction_types)
            
            like = Like(
                user_id=liker.id,
                post_id=post.id,
                reaction_type=reaction
            )
            db.session.add(like)
            likes_added += 1
    
    try:
        db.session.commit()
        logger.info(f"{comments_added} commentaires et {likes_added} likes ajoutés.")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erreur lors de l'ajout des interactions: {e}")
        return False

if __name__ == "__main__":
    logger.info("Début de la génération de contenu social...")
    success = create_social_posts()
    if success:
        logger.info("Génération de contenu social terminée avec succès!")
    else:
        logger.error("Échec de la génération de contenu social.")
