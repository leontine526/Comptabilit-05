"""
Socket.IO event handlers for real-time communication.
"""
import json
from flask import request
from flask_login import current_user
from datetime import datetime, timedelta

from app import socketio, db, logger, join_room, leave_room
from models import User, Message, Notification, Post, Comment, Like, Workgroup, Story, StoryView
from functools import wraps
import traceback
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask import _request_ctx_stack, current_app
from flask_socketio import emit

# Dictionary to store active user sessions
active_sessions = {}

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    if not current_user.is_authenticated:
        logger.warning("Unauthenticated connection attempt")
        return False

    logger.info(f"Client connected: {current_user.username}")

    # Store socket ID for the user
    current_user.socket_id = request.sid
    current_user.set_online_status(True)
    current_user.update_last_seen()
    db.session.commit()

    # Add user to active sessions
    active_sessions[request.sid] = {
        'user_id': current_user.id,
        'username': current_user.username,
        'connected_at': datetime.utcnow()
    }

    # Join user's personal room for private messages
    join_room(f'user_{current_user.id}')

    # Join rooms for all workgroups the user is in
    for workgroup in current_user.workgroups:
        join_room(f'workgroup_{workgroup.id}')

    # Broadcast user online status to other users
    socketio.emit('user_status_change', {
        'user_id': current_user.id,
        'username': current_user.username,
        'is_online': True
    }, broadcast=True)

    # Get lists of online users for the client
    online_user_ids = [user_id for user_id, user_data in active_sessions.items() 
                      if 'user_id' in user_data]

    return {'status': 'connected', 'online_users': online_user_ids}

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    if current_user.is_authenticated:
        logger.info(f"Client disconnected: {current_user.username}")

        # Update user status
        current_user.set_online_status(False)
        current_user.update_last_seen()
        current_user.socket_id = None
        db.session.commit()

        # Remove from active sessions
        if request.sid in active_sessions:
            del active_sessions[request.sid]

        # Broadcast user offline status to other users
        socketio.emit('user_status_change', {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_online': False
        }, broadcast=True)

@socketio.on('join_room')
def handle_join_room(data):
    """Join a specific room."""
    room = data.get('room')
    if room:
        join_room(room)
        logger.info(f"User {current_user.username} joined room: {room}")
        return {'status': 'success', 'message': f'Joined room: {room}'}
    return {'status': 'error', 'message': 'Room not specified'}

@socketio.on('leave_room')
def handle_leave_room(data):
    """Leave a specific room."""
    room = data.get('room')
    if room:
        leave_room(room)
        logger.info(f"User {current_user.username} left room: {room}")
        return {'status': 'success', 'message': f'Left room: {room}'}
    return {'status': 'error', 'message': 'Room not specified'}

@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a message to a workgroup."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    workgroup_id = data.get('workgroup_id')
    content = data.get('content')
    parent_id = data.get('parent_id')

    if not workgroup_id or not content:
        return {'status': 'error', 'message': 'Missing required fields'}

    # Verify workgroup exists and user is a member
    workgroup = Workgroup.query.get(workgroup_id)
    if not workgroup or current_user not in workgroup.members:
        return {'status': 'error', 'message': 'Access denied to this workgroup'}

    # Create and save the message
    message = Message(
        content=content,
        sender_id=current_user.id,
        workgroup_id=workgroup_id,
        parent_id=parent_id
    )
    db.session.add(message)
    db.session.commit()

    # Prepare message data for broadcast
    message_data = {
        'id': message.id,
        'content': message.content,
        'sent_at': message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
        'sender': {
            'id': current_user.id,
            'username': current_user.username
        },
        'workgroup_id': workgroup_id,
        'parent_id': parent_id
    }

    # Emit message to the workgroup room
    socketio.emit('new_message', message_data, to=f'workgroup_{workgroup_id}')

    # Create notifications for other members of the workgroup
    for member in workgroup.members:
        if member.id != current_user.id:
            notification = Notification(
                user_id=member.id,
                title=f"Nouveau message de {current_user.username}",
                content=f"{current_user.username} a envoyé un message dans le groupe '{workgroup.name}'",
                notification_type="message",
                source_id=message.id,
                source_type="message"
            )
            db.session.add(notification)

            # If the user is online, send the notification in real-time
            if member.is_online and member.socket_id:
                notification_data = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_read': notification.is_read,
                    'source_url': notification.source_url
                }
                socketio.emit('new_notification', notification_data, to=f'user_{member.id}')

    db.session.commit()

    return {'status': 'success', 'message_id': message.id}

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator."""
    if not current_user.is_authenticated:
        return

    workgroup_id = data.get('workgroup_id')
    is_typing = data.get('is_typing', False)

    if workgroup_id:
        typing_data = {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_typing': is_typing
        }
        socketio.emit('user_typing', typing_data, to=f'workgroup_{workgroup_id}')

@socketio.on('create_post')
def handle_create_post(data):
    """Handle creating a new post."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    content = data.get('content')
    workgroup_id = data.get('workgroup_id')
    image_url = data.get('image_url')
    file_url = data.get('file_url')

    if not content:
        return {'status': 'error', 'message': 'Content is required'}

    # Verify workgroup if specified
    if workgroup_id:
        workgroup = Workgroup.query.get(workgroup_id)
        if not workgroup or current_user not in workgroup.members:
            return {'status': 'error', 'message': 'Access denied to this workgroup'}

    # Create the post
    post = Post(
        content=content,
        user_id=current_user.id,
        workgroup_id=workgroup_id,
        image_url=image_url,
        file_url=file_url
    )
    db.session.add(post)
    db.session.commit()

    # Prepare post data for broadcast
    post_data = {
        'id': post.id,
        'content': post.content,
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'author': {
            'id': current_user.id,
            'username': current_user.username
        },
        'workgroup_id': workgroup_id,
        'image_url': post.image_url,
        'file_url': post.file_url,
        'like_count': 0,
        'comment_count': 0
    }

    # Emit to appropriate room (workgroup or global)
    if workgroup_id:
        socketio.emit('new_post', post_data, to=f'workgroup_{workgroup_id}')

        # Create notifications for workgroup members
        for member in workgroup.members:
            if member.id != current_user.id:
                notification = Notification(
                    user_id=member.id,
                    title=f"Nouvelle publication de {current_user.username}",
                    content=f"{current_user.username} a publié dans le groupe '{workgroup.name}'",
                    notification_type="post",
                    source_id=post.id,
                    source_type="post"
                )
                db.session.add(notification)

                # If the user is online, send notification in real-time
                if member.is_online and member.socket_id:
                    notification_data = {
                        'id': notification.id,
                        'title': notification.title,
                        'content': notification.content,
                        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'is_read': notification.is_read,
                        'source_url': f'/workgroups/{workgroup_id}#post-{post.id}'
                    }
                    socketio.emit('new_notification', notification_data, to=f'user_{member.id}')
    else:
        socketio.emit('new_post', post_data, broadcast=True)

    db.session.commit()

    return {'status': 'success', 'post_id': post.id}

@socketio.on('add_comment')
def handle_add_comment(data):
    """Handle adding a comment to a post."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    post_id = data.get('post_id')
    content = data.get('content')
    parent_id = data.get('parent_id')  # For replies to other comments

    if not post_id or not content:
        return {'status': 'error', 'message': 'Missing required fields'}

    # Verify post exists
    post = Post.query.get(post_id)
    if not post:
        return {'status': 'error', 'message': 'Post not found'}

    # If post is in a workgroup, check access
    if post.workgroup_id:
        workgroup = Workgroup.query.get(post.workgroup_id)
        if not workgroup or current_user not in workgroup.members:
            return {'status': 'error', 'message': 'Access denied to this post'}

    # Create the comment
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id
    )
    db.session.add(comment)
    db.session.commit()

    # Prepare comment data for broadcast
    comment_data = {
        'id': comment.id,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'author': {
            'id': current_user.id,
            'username': current_user.username
        },
        'post_id': post_id,
        'parent_id': parent_id,
        'like_count': 0
    }

    # Determine where to emit the comment
    room = f'workgroup_{post.workgroup_id}' if post.workgroup_id else None

    # Emit to appropriate room or broadcast
    if room:
        socketio.emit('new_comment', comment_data, to=room)
    else:
        socketio.emit('new_comment', comment_data, broadcast=True)

    # Create notification for post author (if not the same as commenter)
    if post.user_id != current_user.id:
        notification = Notification(
            user_id=post.user_id,
            title=f"Nouveau commentaire de {current_user.username}",
            content=f"{current_user.username} a commenté votre publication",
            notification_type="comment",
            source_id=comment.id,
            source_type="comment"
        )
        db.session.add(notification)

        # If the post author is online, send notification in real-time
        post_author = User.query.get(post.user_id)
        if post_author and post_author.is_online and post_author.socket_id:
            notification_data = {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read,
                'source_url': f'/posts/{post_id}#comment-{comment.id}'
            }
            socketio.emit('new_notification', notification_data, to=f'user_{post_author.user_id}')

    # If it's a reply, notify the parent comment author
    if parent_id and parent_id != current_user.id:
        parent_comment = Comment.query.get(parent_id)
        if parent_comment and parent_comment.user_id != current_user.id:
            notification = Notification(
                user_id=parent_comment.user_id,
                title=f"Réponse de {current_user.username}",
                content=f"{current_user.username} a répondu à votre commentaire",
                notification_type="reply",
                source_id=comment.id,
                source_type="comment"
            )
            db.session.add(notification)

            # If the parent comment author is online, send notification
            parent_author = User.query.get(parent_comment.user_id)
            if parent_author and parent_author.is_online and parent_author.socket_id:
                notification_data = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_read': notification.is_read,
                    'source_url': f'/posts/{post_id}#comment-{comment.id}'
                }
                socketio.emit('new_notification', notification_data, to=f'user_{parent_comment.user_id}')

    db.session.commit()

    return {'status': 'success', 'comment_id': comment.id}

from functools import wraps
import traceback
from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask import _request_ctx_stack, current_app
from flask_socketio import emit

# Gestionnaires Socket.IO améliorés pour une meilleure réactivité

# Classe pour les erreurs WebSocket
class WebSocketError(Exception):
    def __init__(self, message, code=400, data=None):
        self.message = message
        self.code = code
        self.data = data or {}
        super().__init__(self.message)

# Décorateur pour gérer les erreurs Socket.IO
def handle_socketio_errors(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Vérifier si l'utilisateur est authentifié
            if not current_user.is_authenticated:
                raise WebSocketError('Authentification requise', 401)

            # Vérifier si la connexion WebSocket est active
            if not hasattr(request, 'sid'):
                raise WebSocketError('Connexion WebSocket inactive', 400)

            # Exécuter la fonction
            return f(*args, **kwargs)
        except WebSocketError as e:
            # Erreur personnalisée
            emit('error', {
                'code': e.code,
                'message': e.message,
                'data': e.data
            })
            return {'status': 'error', 'code': e.code, 'message': e.message}
        except Exception as e:
            # Erreur inattendue
            logger.error(f"Erreur WebSocket non gérée: {str(e)}")
            logger.error(traceback.format_exc())
            emit('error', {
                'code': 500,
                'message': 'Une erreur inattendue s\'est produite'
            })
            return {'status': 'error', 'code': 500, 'message': 'Erreur interne'}
    return decorated

@socketio.on('toggle_like')
@handle_socketio_errors
def handle_toggle_like(data):
    """Gestion optimisée des réactions en temps réel"""
    post_id = data.get('post_id')
    comment_id = data.get('comment_id')
    reaction_type = data.get('reaction_type', 'like')

    if not post_id and not comment_id:
        raise WebSocketError('ID de post ou de commentaire requis', 400)

    # Valider que la cible existe
    if post_id:
        post = Post.query.get(post_id)
        if not post:
            raise WebSocketError('Publication non trouvée', 404, {'post_id': post_id})

        # Vérifier les permissions (si publication privée ou dans un groupe)
        if post.workgroup_id:
            workgroup = Workgroup.query.get(post.workgroup_id)
            if workgroup and workgroup.is_private and current_user not in workgroup.members and workgroup.owner_id != current_user.id:
                raise WebSocketError('Vous n\'avez pas accès à cette publication', 403)

    if comment_id:
        comment = Comment.query.get(comment_id)
        if not comment:
            raise WebSocketError('Commentaire non trouvé', 404, {'comment_id': comment_id})

    # Check if user already liked this item
    existing_like = None
    if post_id:
        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
        #target = Post.query.get(post_id)
        target = post # Use already fetched post object
        if not target:
            raise WebSocketError('Post not found', 404, {'post_id': post_id})

        # If post is in a workgroup, check access
        if target.workgroup_id:
            workgroup = Workgroup.query.get(target.workgroup_id)
            if not workgroup or current_user not in workgroup.members:
                raise WebSocketError('Access denied to this post', 403)
    else:
        existing_like = Like.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()
        #target_comment = Comment.query.get(comment_id)
        target_comment = comment # Use already fetched comment object
        if not target_comment:
            raise WebSocketError('Comment not found', 404, {'comment_id': comment_id})

        # Check if the comment's post is in a workgroup
        target = target_comment.post
        if target.workgroup_id:
            workgroup = Workgroup.query.get(target.workgroup_id)
            if not workgroup or current_user not in workgroup.members:
                raise WebSocketError('Access denied to this comment', 403)

    # If like exists, remove it; otherwise create it
    is_new_like = False
    if existing_like:
        db.session.delete(existing_like)
        action = 'unlike'
    else:
        new_like = Like(
            user_id=current_user.id,
            post_id=post_id,
            comment_id=comment_id,
            reaction_type=reaction_type
        )
        db.session.add(new_like)
        action = 'like'
        is_new_like = True

    db.session.commit()

    # Get updated counts
    like_count = 0
    if post_id:
        like_count = Like.query.filter_by(post_id=post_id).count()
    else:
        like_count = Like.query.filter_by(comment_id=comment_id).count()

    # Prepare like data for broadcast
    like_data = {
        'user_id': current_user.id,
        'username': current_user.username,
        'post_id': post_id,
        'comment_id': comment_id,
        'action': action,
        'reaction_type': reaction_type,
        'like_count': like_count
    }

    # Determine the room to emit to
    room = None
    if post_id and target.workgroup_id:
        room = f'workgroup_{target.workgroup_id}'

    # Emit to appropriate room or broadcast
    if room:
        socketio.emit('like_update', like_data, to=room)
    else:
        socketio.emit('like_update', like_data, broadcast=True)

    # Send notification for new likes (not for unlikes)
    if is_new_like:
        # Define the target user ID and content based on whether it's a post or comment
        if post_id:
            target_user_id = target.user_id
            notification_content = f"{current_user.username} a aimé votre publication"
            source_url = f'/posts/{post_id}'
        else:
            target_user_id = target_comment.user_id
            notification_content = f"{current_user.username} a aimé votre commentaire"
            source_url = f'/posts/{target_comment.post_id}#comment-{comment_id}'

        # Only notify if it's not the user liking their own content
        if target_user_id != current_user.id:
            notification = Notification(
                user_id=target_user_id,
                title=f"J'aime de {current_user.username}",
                content=notification_content,
                notification_type="like",
                source_id=post_id or comment_id,
                source_type="post" if post_id else "comment"
            )
            db.session.add(notification)

            # If target user is online, send real-time notification
            target_user = User.query.get(target_user_id)
            if target_user and target_user.is_online and target_user.socket_id:
                notification_data = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_read': notification.is_read,
                    'source_url': source_url
                }
                socketio.emit('new_notification', notification_data, to=f'user_{target_user_id}')

            db.session.commit()

    return {
        'status': 'success',
        'action': action,
        'like_count': like_count
    }

@socketio.on('mark_notifications_read')
def handle_mark_notifications_read():
    """Mark all notifications as read for the current user."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    current_user.mark_notifications_as_read()

    return {'status': 'success', 'message': 'All notifications marked as read'}

@socketio.on('create_story')
def handle_create_story(data):
    """Handle creating a new story."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    media_url = data.get('media_url')
    content = data.get('content')
    media_type = data.get('media_type', 'image')
    workgroup_id = data.get('workgroup_id')

    if not media_url:
        return {'status': 'error', 'message': 'Media URL is required'}

    # Create the story
    # Set expiration date to 24 hours from now
    expires_at = datetime.utcnow() + timedelta(hours=24)

    story = Story(
        user_id=current_user.id,
        media_url=media_url,
        content=content,
        media_type=media_type,
        workgroup_id=workgroup_id,
        expires_at=expires_at
    )
    db.session.add(story)
    db.session.commit()

    # Prepare story data for broadcast
    story_data = {
        'id': story.id,
        'media_url': story.media_url,
        'content': story.content,
        'media_type': story.media_type,
        'created_at': story.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'expires_at': story.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
        'author': {
            'id': current_user.id,
            'username': current_user.username
        }
    }

    # Broadcast to all users
    socketio.emit('new_story', story_data, broadcast=True)

    # Create notifications for friends or workgroup members
    # For simplicity, we'll notify all users who are in at least one workgroup with the author
    user_workgroups = set(wg.id for wg in current_user.workgroups)

    for user in User.query.filter(User.id != current_user.id).all():
        user_in_same_workgroup = False

        # Check if user shares a workgroup with story author
        for wg in user.workgroups:
            if wg.id in user_workgroups:
                user_in_same_workgroup = True
                break

        if user_in_same_workgroup:
            notification = Notification(
                user_id=user.id,
                title=f"Nouvelle story de {current_user.username}",
                content=f"{current_user.username} a ajouté une nouvelle story",
                notification_type="story",
                source_id=story.id,
                source_type="story"
            )
            db.session.add(notification)

            # If user is online, send notification in real-time
            if user.is_online and user.socket_id:
                notification_data = {
                    'id': notification.id,
                    'title': notification.title,
                    'content': notification.content,
                    'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_read': notification.is_read,
                    'source_url': '/stories'
                }
                socketio.emit('new_notification', notification_data, to=f'user_{user.id}')

    db.session.commit()

    return {'status': 'success', 'story_id': story.id}

@socketio.on('view_story')
def handle_view_story(data):
    """Handle marking a story as viewed."""
    if not current_user.is_authenticated:
        return {'status': 'error', 'message': 'Authentication required'}

    story_id = data.get('story_id')
    if not story_id:
        return {'status': 'error', 'message': 'Story ID is required'}

    # Get the story
    story = Story.query.get(story_id)
    if not story:
        return {'status': 'error', 'message': 'Story not found'}

    # Check if story is already viewed by the user
    existing_view = StoryView.query.filter_by(
        user_id=current_user.id, 
        story_id=story_id
    ).first()

    if not existing_view:
        # Create a new view record
        story_view = StoryView(
            user_id=current_user.id,
            story_id=story_id
        )
        db.session.add(story_view)
        db.session.commit()

        # If the story author is online, notify them about the view
        if story.user_id != current_user.id and story.user.is_online and story.user.socket_id:
            view_data = {
                'story_id': story_id,
                'viewer': {
                    'id': current_user.id,
                    'username': current_user.username
                },
                'viewed_at': story_view.viewed_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            socketio.emit('story_view', view_data, to=f'user_{story.user_id}')

    return {'status': 'success', 'message': 'Story marked as viewed'}