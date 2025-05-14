# Comptabilité OHADA

Une solution de comptabilité basée sur le référentiel OHADA avec OCR, NLP et IA pour traiter automatiquement les documents comptables et analyser les exercices.

## 🚀 Fonctionnalités

- **Gestion comptable OHADA complète** : Suivez le référentiel OHADA et gérez facilement vos exercices comptables
- **Traitement automatisé des documents** : Extraction des données via OCR et analyse via NLP
- **Analyse intelligente** : Obtenez des insights sur vos exercices comptables grâce à l'IA
- **Interface utilisateur professionnelle** : Design soigné et ergonomique
- **Traitement de texte intégré** : Résumez et structurez vos textes facilement
- **Fonctionnalités sociales collaboratives** : Workgroups, chat en temps réel, système de posts et commentaires
- **Stories éphémères** : Partagez du contenu temporaire qui disparaît après 24h
- **Notifications temps réel** : Restez informé des activités importantes via Socket.IO

## 📋 Prérequis

- Python 3.11+
- PostgreSQL
- Bibliothèques Python listées dans `pyproject.toml`

## 🛠️ Installation

### Installation locale

1. Clonez ce dépôt
   ```bash
   git clone https://github.com/mushagakiriza/ohada-comptabilite.git
   cd ohada-comptabilite
   ```

2. Installez les dépendances
   ```bash
   pip install -e .
   # ou pour Replit
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost:5432/ohada_db
   export SESSION_SECRET=votre_secret_ici
   ```

4. Lancez l'application
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
   ```

### Déploiement sur Render

1. Connectez votre compte GitHub à Render
2. Créez un nouveau service Web, sélectionnez ce dépôt
3. Render détectera automatiquement le fichier `render.yaml` et configurera le déploiement
4. Cliquez sur "Deploy" pour déployer l'application

## 🔒 Variables d'environnement

- `DATABASE_URL` : URL de connexion à la base de données PostgreSQL
- `SESSION_SECRET` : Clé secrète pour la session Flask
- `SENDGRID_API_KEY` (optionnel) : Clé API SendGrid pour l'envoi d'emails
- `OPENAI_API_KEY` (optionnel) : Clé API OpenAI pour les fonctionnalités avancées d'IA
- `SLACK_BOT_TOKEN` (optionnel) : Jeton Slack pour les intégrations Slack
- `SLACK_CHANNEL_ID` (optionnel) : ID du canal Slack pour les notifications

## 🧪 Fonctionnalités avancées

### Traitement de texte

L'application intègre un outil de traitement de texte qui utilise NLTK et scikit-learn pour:

- Résumer automatiquement des textes en français
- Répartir les textes en paragraphes cohérents
- Analyser la complexité du vocabulaire et des phrases

### Fonctionnalités sociales

L'application offre un ensemble complet de fonctionnalités sociales et collaboratives:

- **Workgroups** : Créez des groupes de travail pour collaborer avec vos collègues
- **Chat en temps réel** : Communication instantanée via WebSockets/Socket.IO
- **Feed d'activités** : Fil d'actualités style Facebook pour partager des informations
- **Posts et commentaires** : Créez des publications et commentez celles des autres
- **Réactions personnalisées** : Like, love, et autres réactions aux publications
- **Stories éphémères** : Partagez du contenu qui disparaît après 24h
- **Notifications** : Recevez des alertes en temps réel pour les activités importantes
- **Indicateurs de présence** : Voyez qui est en ligne et disponible

## 📱 Contact et support

- **Email** : kirizamushaga@gmail.com
- **Téléphone** : +243 820 740 027
- **GitHub** : github.com/mushagakiriza

## 📜 Licence

© 2025 Comptabilité OHADA. Tous droits réservés.
Développé par Mushaga Kiriza