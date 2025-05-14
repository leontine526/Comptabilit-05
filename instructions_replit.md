# Instructions pour cloner dans Replit

## 1. Préparation du dépôt GitHub

1. Créez un compte GitHub si vous n'en avez pas déjà un
2. Créez un nouveau dépôt public sur GitHub (ex: ohada-comptabilite)
3. Dans Replit, ouvrez un terminal et exécutez les commandes suivantes :

```bash
# Initialiser git
git init

# Ajouter l'URL du dépôt distant (remplacez par votre URL)
git remote add origin https://github.com/votre-username/ohada-comptabilite.git

# Vérifier que le remote a été ajouté
git remote -v

# Ajouter tous les fichiers au suivi git
git add .

# Créer un commit initial
git commit -m "Version initiale de l'application Comptabilité OHADA"

# Pousser le code vers GitHub (branche principale)
git push -u origin main
```

Si la branche s'appelle "master" au lieu de "main", utilisez :
```bash
git push -u origin master
```

## 2. Cloner dans un nouveau Replit

1. Connectez-vous à Replit avec votre compte
2. Cliquez sur "Create Repl" (Créer un nouveau Repl)
3. Choisissez "Import from GitHub"
4. Collez l'URL de votre dépôt GitHub
5. Sélectionnez le template "Python"
6. Cliquez sur "Import from GitHub"

## 3. Configuration du nouveau Replit

1. Créez une base de données PostgreSQL depuis l'onglet "Database" dans Replit
2. Configurez les secrets/variables d'environnement dans l'onglet "Secrets" :
   - `DATABASE_URL` : Copiez l'URL de la BD PostgreSQL fournie par Replit
   - `SESSION_SECRET` : Créez une chaîne aléatoire sécurisée

3. Ajoutez les dépendances nécessaires en exécutant ces commandes dans le Shell :
```bash
pip install email-validator eventlet flask flask-login flask-socketio flask-sqlalchemy flask-wtf gunicorn nltk numpy openai opencv-python psycopg2-binary pymupdf pytesseract python-dotenv reportlab requests scikit-learn sendgrid slack-sdk spacy sqlalchemy xlsxwriter
```

4. Configurez le fichier `.replit` pour définir la commande d'exécution :
```
run = "gunicorn --bind 0.0.0.0:5000 --reuse-port main:app"
```

5. Lancez l'application en cliquant sur "Run"

## 4. Gestion des mises à jour

Pour synchroniser votre Replit avec les mises à jour GitHub :

1. Dans le terminal de Replit, exécutez :
```bash
git pull origin main
```

2. Pour envoyer des modifications de Replit vers GitHub :
```bash
git add .
git commit -m "Description des changements"
git push origin main
```

## Notes importantes

- Les fichiers de configuration spécifiques à Replit (`.replit`, etc.) ne doivent pas être modifiés manuellement
- Utilisez toujours l'interface Replit pour configurer les secrets et les variables d'environnement
- Pour les dépendances, utilisez l'outil "Packages" de Replit ou les commandes pip dans le Shell