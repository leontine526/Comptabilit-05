"""
Routes pour les fonctionnalités sociales et de communication en temps réel
"""
import os
import uuid
import json
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app import app, db, socketio

# Import des routes sociales
from models import User, Workgroup, Message, Post, Comment, Like, Notification, Story, StoryView, ExerciseSolution

@app.route('/social/share-exercise-solution/<int:solution_id>', methods=['POST'])
@login_required
def share_exercise_solution(solution_id):
    """Partage une solution d'exercice sur le fil d'actualité"""
    solution = ExerciseSolution.query.get_or_404(solution_id)

    # Vérifie que l'utilisateur est le propriétaire de la solution
    if solution.user_id != current_user.id:
        abort(403)

    # Crée une publication à partir de la solution
    post = Post(
        content=f"J'ai résolu l'exercice : {solution.title}\n\nSolution :\n{solution.solution_text}",
        user_id=current_user.id,
        exercise_solution_id=solution.id
    )

    db.session.add(post)
    db.session.commit()

    flash('Solution partagée avec succès!', 'success')
    return redirect(url_for('feed'))
from utils import allowed_file, ensure_upload_dir

# Chat de groupe
@app.route('/workgroups/<int:workgroup_id>/chat')
@login_required
def workgroup_chat(workgroup_id):
    """Affiche le chat d'un groupe de travail"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)

    # Vérifie que l'utilisateur est membre du groupe
    if current_user not in workgroup.members and current_user != workgroup.owner:
        flash("Vous n'êtes pas membre de ce groupe de travail.", "warning")
        return redirect(url_for('workgroups'))

    # Récupère les messages du groupe
    messages = Message.query.filter_by(workgroup_id=workgroup_id) \
                    .order_by(Message.sent_at.asc()).all()

    return render_template('workgroups/chat.html', 
                          workgroup=workgroup, 
                          messages=messages)

# Publications de groupe
@app.route('/workgroups/<int:workgroup_id>/posts')
@login_required
def workgroup_posts(workgroup_id):
    """Affiche les publications d'un groupe de travail"""
    workgroup = Workgroup.query.get_or_404(workgroup_id)

    # Vérifie que l'utilisateur est membre du groupe
    if current_user not in workgroup.members and current_user != workgroup.owner:
        flash("Vous n'êtes pas membre de ce groupe de travail.", "warning")
        return redirect(url_for('workgroups'))

    # Récupère les publications du groupe
    posts = Post.query.filter_by(workgroup_id=workgroup_id) \
                .order_by(Post.created_at.desc()).all()

    # Récupère les likes de l'utilisateur actuel
    liked_posts = [like.post_id for like in Like.query.filter_by(
        user_id=current_user.id, post_id=Post.id).all()]

    liked_comments = [like.comment_id for like in Like.query.filter_by(
        user_id=current_user.id, comment_id=Comment.id).all()]

    return render_template('workgroups/posts.html', 
                          workgroup=workgroup, 
                          posts=posts,
                          liked_posts=liked_posts,
                          liked_comments=liked_comments)

# Fil d'actualité global
@app.route('/feed')
@login_required
def feed():
    """Affiche le fil d'actualité de l'utilisateur"""
    try:
        # Récupère les groupes de l'utilisateur
        user_workgroups = [wg.id for wg in current_user.workgroups]

        # Utiliser une requête SQL personnalisée pour éviter les problèmes de colonne
        from sqlalchemy.sql import text
        
        # Récupère les publications des groupes de l'utilisateur et les publications publiques
        posts = db.session.query(Post).filter(
            (Post.workgroup_id.in_(user_workgroups) if user_workgroups else False) | 
            (Post.workgroup_id == None)
        ).order_by(Post.created_at.desc()).limit(50).all()

        # Récupère les likes de l'utilisateur actuel
        liked_posts = [like.post_id for like in Like.query.filter_by(
            user_id=current_user.id).all() if like.post_id]

        liked_comments = [like.comment_id for like in Like.query.filter_by(
            user_id=current_user.id).all() if like.comment_id]

        return render_template('social/feed.html', 
                            posts=posts,
                            liked_posts=liked_posts,
                            liked_comments=liked_comments)
    except Exception as e:
        import logging
        logging.error(f"Erreur dans le fil d'actualité: {str(e)}")
        flash(f"Une erreur s'est produite lors du chargement du fil d'actualité: {str(e)}", "danger")
        return render_template('social/feed.html', 
                            posts=[],
                            liked_posts=[],
                            liked_comments=[])

# Page de notifications
@app.route('/notifications')
@login_required
def notifications():
    """Affiche les notifications de l'utilisateur"""
    notifications = Notification.query.filter_by(user_id=current_user.id) \
                        .order_by(Notification.created_at.desc()).all()

    # Marque toutes les notifications comme lues
    if notifications:
        current_user.mark_notifications_as_read()

    return render_template('social/notifications.html', notifications=notifications)

# API pour upload de fichier
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """API pour uploader un fichier (image ou document)"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Aucun fichier fourni'})

    file = request.files['file']
    file_type = request.form.get('type', 'file')  # 'image' ou 'file'
    workgroup_id = request.form.get('workgroup_id')

    if file.filename == '':
        return jsonify({'success': False, 'message': 'Aucun fichier sélectionné'})

    if file and allowed_file(file.filename):
        # Assure que le dossier d'upload existe
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'social')
        ensure_upload_dir(upload_folder)

        # Sécurise le nom de fichier et génère un nom unique
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Sauvegarde le fichier
        file.save(file_path)

        # Génère l'URL du fichier
        file_url = url_for('uploaded_file', filename=f"social/{unique_filename}")

        return jsonify({
            'success': True, 
            'url': file_url,
            'message': 'Fichier uploadé avec succès'
        })

    return jsonify({'success': False, 'message': 'Type de fichier non autorisé'})

# Route pour marquer les notifications comme lues
@app.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Marque toutes les notifications comme lues"""
    current_user.mark_notifications_as_read()
    return jsonify({'success': True})

# Route pour obtenir les utilisateurs en ligne
@app.route('/api/users/online')
@login_required
def get_online_users():
    """Récupère la liste des utilisateurs en ligne"""
    online_users = User.query.filter_by(is_online=True).all()

    user_data = [{
        'id': user.id,
        'username': user.username,
        'avatar': user.avatar,
        'last_seen': user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else None
    } for user in online_users]

    return jsonify({'users': user_data})

# Handler pour les connexions WebSocket
@socketio.on('connect')
def handle_connect(auth=None):
    """Gère la connexion WebSocket des clients"""
    if current_user.is_authenticated:
        # Met à jour le statut en ligne et l'heure de dernière connexion
        current_user.is_online = True
        current_user.last_seen = datetime.utcnow()
        current_user.socket_id = request.sid
        db.session.commit()

        # Rejoint les salles pour les groupes de l'utilisateur
        for workgroup in current_user.workgroups:
            socketio.join_room(f"workgroup_{workgroup.id}")

        # Rejoint sa propre salle pour les notifications personnelles
        socketio.join_room(f"user_{current_user.id}")

        # Notifie les autres utilisateurs
        socketio.emit('user_status_change', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_online': True
        }, broadcast=True)

# Handler pour les déconnexions WebSocket
@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion WebSocket des clients"""
    if current_user.is_authenticated:
        # Met à jour le statut hors ligne et l'heure de dernière connexion
        current_user.is_online = False
        current_user.last_seen = datetime.utcnow()
        current_user.socket_id = None
        db.session.commit()

        # Notifie les autres utilisateurs
        socketio.emit('user_status_change', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_online': False
        }, broadcast=True)

# Routes pour les stories

@app.route('/stories')
@login_required
def stories():
    """Affiche les stories des utilisateurs"""
    # Récupère les stories non expirées des utilisateurs que current_user suit
    now = datetime.utcnow()

    # Pour l'instant, affiche les stories de tous les utilisateurs (à remplacer par les contacts plus tard)
    # On filtre les stories qui ne sont pas expirées (moins de 24h)
    stories = Story.query.filter(
        Story.created_at > (now - timedelta(hours=24)),
        Story.is_expired == False
    ).order_by(Story.created_at.desc()).all()

    # Récupère les groupes de l'utilisateur pour le formulaire de création
    workgroups = current_user.workgroups.all()

    # Récupère les stories de l'utilisateur actuel
    user_stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.created_at.desc()).all()

    return render_template('social/stories.html',
                          stories=stories,
                          user_stories=user_stories,
                          workgroups=workgroups)

@app.route('/stories/create', methods=['POST'])
@login_required
def create_story():
    """Crée une nouvelle story"""
    if 'media' not in request.files:
        flash('Aucun fichier média fourni', 'danger')
        return redirect(url_for('stories'))

    media_file = request.files['media']
    content = request.form.get('content', '')
    workgroup_id = request.form.get('workgroup_id', '')

    if media_file.filename == '':
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(url_for('stories'))

    if media_file and allowed_file(media_file.filename):
        # Détermine le type de média
        if media_file.content_type.startswith('image/'):
            media_type = 'image'
        elif media_file.content_type.startswith('video/'):
            media_type = 'video'
        else:
            flash('Type de fichier non pris en charge', 'danger')
            return redirect(url_for('stories'))

        # Crée le dossier d'upload s'il n'existe pas
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'stories')
        ensure_upload_dir(upload_folder)

        # Sécurise le nom de fichier et génère un nom unique
        filename = secure_filename(media_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Sauvegarde le fichier
        media_file.save(file_path)

        # Génère l'URL du fichier
        media_url = url_for('uploaded_file', filename=f"stories/{unique_filename}")

        # Calcule la date d'expiration (24h après la création)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Crée la story
        story = Story(
            content=content if content else None,
            media_url=media_url,
            media_type=media_type,
            expires_at=expires_at,
            user_id=current_user.id,
            workgroup_id=int(workgroup_id) if workgroup_id else None
        )

        db.session.add(story)
        db.session.commit()

        # Notifie les utilisateurs concernés
        notify_story_creation(story)

        flash('Story publiée avec succès !', 'success')
    else:
        flash('Type de fichier non autorisé', 'danger')

    return redirect(url_for('stories'))

@app.route('/api/stories')
@login_required
def get_stories():
    """API pour récupérer les stories"""
    now = datetime.utcnow()

    # Récupère les stories non expirées
    stories = Story.query.filter(
        Story.created_at > (now - timedelta(hours=24)),
        Story.is_expired == False
    ).order_by(Story.created_at.desc()).all()

    # Formate les données
    story_data = []
    for story in stories:
        # Vérifie si l'utilisateur actuel a déjà vu cette story
        viewed = StoryView.query.filter_by(
            story_id=story.id,
            user_id=current_user.id
        ).first() is not None

        # Ajoute les données de la story
        story_data.append({
            'id': story.id,
            'content': story.content,
            'media_url': story.media_url,
            'media_type': story.media_type,
            'created_at': story.created_at.isoformat(),
            'created_at_formatted': story.created_at.strftime('%d/%m/%Y %H:%M'),
            'remaining_time': story.remaining_time,
            'view_count': story.view_count,
            'viewed': viewed,
            'user': {
                'id': story.user_id,
                'username': story.user.username
            },
            'workgroup_id': story.workgroup_id
        })

    return jsonify({'stories': story_data})

@app.route('/api/stories/<int:story_id>')
@login_required
def get_story(story_id):
    """API pour récupérer une story spécifique"""
    story = Story.query.get_or_404(story_id)

    # Vérifie si l'utilisateur a accès à cette story
    if story.workgroup_id:
        workgroup = Workgroup.query.get(story.workgroup_id)
        if current_user not in workgroup.members and workgroup.owner_id != current_user.id:
            return jsonify({'error': 'Accès non autorisé'}), 403

    # Vérifie si l'utilisateur actuel a déjà vu cette story
    viewed = StoryView.query.filter_by(
        story_id=story.id,
        user_id=current_user.id
    ).first() is not None

    # Formate les données de la story
    story_data = {
        'id': story.id,
        'content': story.content,
        'media_url': story.media_url,
        'media_type': story.media_type,
        'created_at': story.created_at.isoformat(),
        'created_at_formatted': story.created_at.strftime('%d/%m/%Y %H:%M'),
        'remaining_time': story.remaining_time,
        'view_count': story.view_count,
        'viewed': viewed,
        'user': {
            'id': story.user_id,
            'username': story.user.username
        },
        'workgroup_id': story.workgroup_id
    }

    return jsonify(story_data)

@app.route('/api/stories/<int:story_id>/view', methods=['POST'])
@login_required
def view_story(story_id):
    """Marque une story comme vue par l'utilisateur actuel"""
    story = Story.query.get_or_404(story_id)

    # Vérifie si l'utilisateur a déjà vu cette story
    existing_view = StoryView.query.filter_by(
        story_id=story_id,
        user_id=current_user.id
    ).first()

    if not existing_view:
        # Crée un nouvel enregistrement de vue
        view = StoryView(
            story_id=story_id,
            user_id=current_user.id
        )
        db.session.add(view)
        db.session.commit()

    return jsonify({'success': True})

@app.route('/api/stories/<int:story_id>', methods=['DELETE'])
@login_required
def delete_story(story_id):
    """Supprime une story"""
    story = Story.query.get_or_404(story_id)

    # Vérifie que l'utilisateur est le propriétaire de la story
    if story.user_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403

    # Supprime la story
    db.session.delete(story)
    db.session.commit()

    return jsonify({'success': True})

# Routes API pour les posts et commentaires
@app.route('/api/posts/create', methods=['POST'])
@login_required
def api_create_post():
    """API pour créer une nouvelle publication"""
    data = request.json
    
    # Vérifier les données requises
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': 'Contenu requis'})
    
    # Créer la publication
    post = Post(
        content=data['content'],
        user_id=current_user.id,
        workgroup_id=data.get('workgroup_id'),
        image_url=data.get('image_url'),
        file_url=data.get('file_url'),
        background_color=data.get('background_color')
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'post_id': post.id,
        'message': 'Publication créée avec succès'
    })

@app.route('/api/comments/create', methods=['POST'])
@login_required
def api_create_comment():
    """API pour créer un nouveau commentaire"""
    data = request.json
    
    # Vérifier les données requises
    if not data or 'content' not in data or 'post_id' not in data:
        return jsonify({'success': False, 'message': 'Contenu et ID de publication requis'})
    
    # Vérifier que la publication existe
    post = Post.query.get(data['post_id'])
    if not post:
        return jsonify({'success': False, 'message': 'Publication non trouvée'})
    
    # Créer le commentaire
    comment = Comment(
        content=data['content'],
        user_id=current_user.id,
        post_id=data['post_id'],
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # Notifier l'auteur de la publication si ce n'est pas le même utilisateur
    if post.user_id != current_user.id:
        notification = Notification(
            user_id=post.user_id,
            title="Nouveau commentaire",
            content=f"{current_user.username} a commenté votre publication.",
            notification_type="comment",
            source_id=post.id,
            source_type="post"
        )
        db.session.add(notification)
        db.session.commit()
    
    # Notifier aussi l'auteur du commentaire parent si c'est une réponse
    if comment.parent_id and comment.parent.user_id != current_user.id:
        notification = Notification(
            user_id=comment.parent.user_id,
            title="Réponse à votre commentaire",
            content=f"{current_user.username} a répondu à votre commentaire.",
            notification_type="reply",
            source_id=comment.id,
            source_type="comment"
        )
        db.session.add(notification)
        db.session.commit()
    
    return jsonify({
        'success': True, 
        'comment_id': comment.id,
        'message': 'Commentaire ajouté avec succès'
    })

# Routes pour les réactions personnalisées

@app.route('/api/reactions', methods=['POST'])

# Routes pour la messagerie privée
@app.route('/messages')
@login_required
def messages_list():
    """Affiche la liste des conversations de l'utilisateur"""
    # Récupère les utilisateurs avec qui l'utilisateur actuel a échangé des messages
    sent_to = db.session.query(User).join(
        PrivateMessage, User.id == PrivateMessage.recipient_id
    ).filter(PrivateMessage.sender_id == current_user.id).distinct().all()
    
    received_from = db.session.query(User).join(
        PrivateMessage, User.id == PrivateMessage.sender_id
    ).filter(PrivateMessage.recipient_id == current_user.id).distinct().all()
    
    # Combine les deux listes sans doublons
    conversation_users = list(set(sent_to + received_from))
    
    # Pour chaque utilisateur, récupère le dernier message
    conversations = []
    for user in conversation_users:
        last_message = PrivateMessage.query.filter(
            ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.recipient_id == user.id)) |
            ((PrivateMessage.sender_id == user.id) & (PrivateMessage.recipient_id == current_user.id))
        ).order_by(PrivateMessage.sent_at.desc()).first()
        
        unread_count = PrivateMessage.query.filter_by(
            sender_id=user.id,
            recipient_id=current_user.id,
            is_read=False
        ).count()
        
        conversations.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Trie les conversations par date du dernier message (plus récent en premier)
    conversations.sort(key=lambda x: x['last_message'].sent_at if x['last_message'] else datetime.min, reverse=True)
    
    return render_template('social/messages_list.html', conversations=conversations)

@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def messages_conversation(user_id):
    """Affiche et permet d'envoyer des messages dans une conversation"""
    other_user = User.query.get_or_404(user_id)
    
    # Si c'est une requête POST, c'est un nouveau message
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if content:
            message = PrivateMessage(
                content=content,
                sender_id=current_user.id,
                recipient_id=user_id
            )
            db.session.add(message)
            db.session.commit()
            
            # Émission d'un événement Socket.IO pour informer le destinataire
            socketio.emit('private_message', {
                'sender_id': current_user.id,
                'sender_username': current_user.username,
                'message': content,
                'timestamp': message.sent_at.strftime('%H:%M')
            }, room=f'user_{user_id}')
            
            # Notification pour le destinataire
            recipient = User.query.get(user_id)
            if recipient:
                notification = Notification(
                    user_id=user_id,
                    title="Nouveau message privé",
                    content=f"{current_user.username} vous a envoyé un message.",
                    notification_type="private_message",
                    source_id=message.id,
                    source_type="private_message"
                )
                db.session.add(notification)
                db.session.commit()
    
    # Récupérer tous les messages entre les deux utilisateurs
    messages = PrivateMessage.query.filter(
        ((PrivateMessage.sender_id == current_user.id) & (PrivateMessage.recipient_id == user_id)) |
        ((PrivateMessage.sender_id == user_id) & (PrivateMessage.recipient_id == current_user.id))
    ).order_by(PrivateMessage.sent_at).all()
    
    # Marquer les messages non lus comme lus
    unread_messages = PrivateMessage.query.filter_by(
        sender_id=user_id,
        recipient_id=current_user.id,
        is_read=False
    ).all()
    
    for msg in unread_messages:
        msg.is_read = True
    
    db.session.commit()
    
    return render_template(
        'social/messages_conversation.html',
        other_user=other_user,
        messages=messages
    )

@app.route('/api/messages/unread-count')
@login_required
def unread_messages_count():
    """Retourne le nombre de messages non lus"""
    count = PrivateMessage.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()
    
    return jsonify({'count': count})

@login_required
def toggle_reaction():
    """Bascule une réaction sur un post ou un commentaire"""
    data = request.json

    post_id = data.get('post_id')
    comment_id = data.get('comment_id')
    reaction_type = data.get('reaction_type', 'like')

    if not post_id and not comment_id:
        return jsonify({'error': 'Post ID ou Comment ID requis'}), 400

    # Vérifie si l'utilisateur a déjà réagi à cet élément
    existing_reaction = None
    if post_id:
        existing_reaction = Like.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).first()
    else:
        existing_reaction = Like.query.filter_by(
            user_id=current_user.id,
            comment_id=comment_id
        ).first()

    if existing_reaction:
        # Si le même type de réaction, on la supprime
        if existing_reaction.reaction_type == reaction_type:
            db.session.delete(existing_reaction)
            db.session.commit()
            action = 'removed'
        else:
            # Sinon, on met à jour le type de réaction
            existing_reaction.reaction_type = reaction_type
            db.session.commit()
            action = 'updated'
    else:
        # Crée une nouvelle réaction
        new_reaction = Like(
            user_id=current_user.id,
            post_id=post_id,
            comment_id=comment_id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        db.session.commit()
        action = 'added'

    # Récupère les détails des réactions
    reactions = get_reaction_details(post_id, comment_id)

    return jsonify({
        'success': True,
        'action': action,
        'reactions': reactions
    })

# Handlers Socket.IO pour les réactions

@socketio.on('toggle_like')
def handle_toggle_like(data):
    """Gère les réactions en temps réel"""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentification requise'}

    post_id = data.get('post_id')
    comment_id = data.get('comment_id')
    reaction_type = data.get('reaction_type', 'like')

    if not post_id and not comment_id:
        return {'status': 'error', 'message': 'ID de post ou de commentaire requis'}

    # Vérifie si l'utilisateur a déjà réagi
    existing_reaction = None
    if post_id:
        existing_reaction = Like.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).first()
    else:
        existing_reaction = Like.query.filter_by(
            user_id=current_user.id,
            comment_id=comment_id
        ).first()

    # Détermine l'action à effectuer
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Supprime la réaction si c'est la même
            db.session.delete(existing_reaction)
            action = 'remove'
        else:
            # Met à jour le type de réaction
            existing_reaction.reaction_type = reaction_type
            action = 'update'
    else:
        # Ajoute une nouvelle réaction
        new_reaction = Like(
            user_id=current_user.id,
            post_id=post_id,
            comment_id=comment_id,
            reaction_type=reaction_type
        )
        db.session.add(new_reaction)
        action = 'add'

    db.session.commit()

    # Récupère les détails des réactions
    count = 0
    if post_id:
        count = Like.query.filter_by(post_id=post_id).count()
    else:
        count = Like.query.filter_by(comment_id=comment_id).count()

    # Émet un événement pour notifier les autres utilisateurs
    socketio.emit('reaction_update', {
        'user_id': current_user.id,
        'username': current_user.username,
        'post_id': post_id,
        'comment_id': comment_id,
        'reaction_type': reaction_type,
        'action': action,
        'count': count
    }, broadcast=True)

    return {
        'status': 'success',
        'action': action,
        'count': count
    }

# Fonctions utilitaires

def notify_story_creation(story):
    """Notifie les utilisateurs appropriés de la création d'une story"""
    # Si la story est dans un groupe, notifie les membres du groupe
    if story.workgroup_id:
        workgroup = Workgroup.query.get(story.workgroup_id)
        if workgroup:
            for member in workgroup.members:
                if member.id != current_user.id:
                    notification = Notification(
                        user_id=member.id,
                        title="Nouvelle story",
                        content=f"{current_user.username} a publié une nouvelle story dans le groupe {workgroup.name}",
                        notification_type="story",
                        source_id=story.id,
                        source_type="story"
                    )
                    db.session.add(notification)

    db.session.commit()

def get_reaction_details(post_id=None, comment_id=None):
    """Récupère les détails des réactions pour un post ou un commentaire"""
    reactions = {'count': 0, 'details': {}}

    # Récupère toutes les réactions
    if post_id:
        likes = Like.query.filter_by(post_id=post_id).all()
    elif comment_id:
        likes = Like.query.filter_by(comment_id=comment_id).all()
    else:
        return reactions

    # Compte le nombre total de réactions
    reactions['count'] = len(likes)

    # Compte par type de réaction
    reaction_counts = {}
    for like in likes:
        reaction_type = like.reaction_type
        if reaction_type in reaction_counts:
            reaction_counts[reaction_type] += 1
        else:
            reaction_counts[reaction_type] = 1

    reactions['details'] = reaction_counts

    return reactions

@app.route('/api/posts/schedule', methods=['POST'])
@login_required
def schedule_post():
    """Planifie une publication pour une date ultérieure"""
    data = request.json
    
    if not data or 'content' not in data or 'scheduled_for' not in data:
        return jsonify({'success': False, 'message': 'Contenu et date de publication requis'})
    
    try:
        # Convertir la date de publication
        scheduled_for = datetime.fromisoformat(data['scheduled_for'])
        
        # Vérifier que la date est dans le futur
        if scheduled_for <= datetime.utcnow():
            return jsonify({'success': False, 'message': 'La date de publication doit être dans le futur'})
        
        # Créer la publication
        post = Post(
            content=data['content'],
            user_id=current_user.id,
            workgroup_id=data.get('workgroup_id'),
            image_url=data.get('image_url'),
            file_url=data.get('file_url'),
            background_color=data.get('background_color'),
            privacy_level=data.get('privacy_level', 'public'),
            is_published=False,  # Non publié car c'est programmé
            scheduled_for=scheduled_for
        )
        
        db.session.add(post)
        db.session.commit()
        
        # Ajouter une tâche planifiée pour publier le post
        # Note: Ceci nécessiterait une implémentation de tâches planifiées comme APScheduler
        # scheduler.add_job(publish_scheduled_post, 'date', run_date=scheduled_for, args=[post.id])
        
        return jsonify({
            'success': True, 
            'post_id': post.id,
            'message': f'Publication programmée pour le {scheduled_for.strftime("%d/%m/%Y à %H:%M")}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
