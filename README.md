# Examen BentoML - Service de Prédiction d'Admission Universitaire

Ce projet implémente un pipeline complet de modélisation, de packaging et de déploiement MLOps basé sur **BentoML 1.4+** et **Docker**, permettant de prédire la chance d'admission d'un étudiant à l'université (`Chance of Admit`).

L'accès à l'API est protégé par une authentification par jeton **JWT**.

---

## 🚀 Guide d'Exécution Rapide (Checklist Correcteur)

Pour évaluer le projet, exécutez les commandes suivantes dans l'ordre strict :

### 1. Charger l'image Docker
Chargez l'archive de l'image Docker exportée :
```bash
docker load -i admission_prediction_service.tar
```

### 2. Démarrer le service API
Lancez le conteneur Docker en exposant le port **3000** :
```bash
docker run -d --rm -p 3000:3000 --name admission_service admission_prediction_service:latest
```

Vérifiez que le conteneur est bien actif et prêt :
```bash
docker ps
curl http://localhost:3000/livez
```

### 3. Installer les dépendances des tests (si nécessaire)
Dans votre environnement de test :
```bash
pip install -r requirements.txt
```

### 4. Lancer la suite de tests unitaires
Exécutez la suite de tests `pytest` (qui valide l'authentification JWT, l'API `/login` et l'API `/predict`) :
```bash
pytest -v
```

### 5. Arrêter le conteneur
Une fois l'évaluation terminée, arrêtez le conteneur :
```bash
docker stop admission_service
```

---

## 📡 Documentation des Endpoints de l'API

L'API expose deux endpoints principaux sur le port `3000` :

### 1. Endpoint d'Authentification : `POST /login`
Permet d'obtenir un jeton d'accès JWT valide pour accéder aux prédictions.

**Exemple de requête :**
```bash
curl -X POST "http://localhost:3000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "password": "password123"
  }'
```

**Réponse attendue (HTTP 200) :**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. Endpoint de Prédiction : `POST /predict`
Prédit la chance d'admission de l'étudiant à partir de ses caractéristiques académiques.
Cet endpoint exige un en-tête `Authorization: Bearer <TOKEN>`.

**Exemple de requête :**
```bash
TOKEN="<VOTRE_TOKEN_JWT>"

curl -X POST "http://localhost:3000/predict" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "gre_score": 337,
    "toefl_score": 118,
    "university_rating": 4,
    "sop": 4.5,
    "lor": 4.5,
    "cgpa": 9.65,
    "research": 1
  }'
```

**Réponse attendue (HTTP 200) :**
```json
{
  "prediction": [0.93]
}
```

---

## 🧪 Détail de la Couverture des Tests Pytest (`tests/`)

- `tests/test_auth.py` :
  - Validation des signatures et décodage de jetons valides.
  - Rejet des jetons expirés (`jwt.ExpiredSignatureError`).
  - Rejet des jetons invalides ou corrompus (`jwt.InvalidTokenError`).
- `tests/test_login.py` :
  - Succès (HTTP 200) lors de la saisie d'identifiants corrects.
  - Rejet (HTTP 401) en cas de mot de passe erroné ou d'utilisateur inconnu.
- `tests/test_predict.py` :
  - Rejet (HTTP 401) si le token JWT est absent, invalide ou expiré.
  - Prédiction nominale (HTTP 200) renvoyant un score entre `0.0` et `1.0`.
  - Rejet (HTTP 400 / 422) en cas de données invalides (hors bornes ou incomplètes).

---

## 📦 Contenu de l'Archive de Rendu

Conformément à la politique stricte d'évaluation, l'archive contient uniquement :
1. `admission_prediction_service.tar` (Archive Docker de l'API)
2. `requirements.txt` (Dépendances d'exécution et de test)
3. `README.md` (Présent document d'instructions)
4. `tests/` (Dossier contenant l'intégralité des tests unitaires `pytest`)
