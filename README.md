# ⚡ Dashboard Mix Électrique – La Réunion

Dashboard temps réel de la production électrique de La Réunion,  
alimenté par l'**Open Data EDF Réunion**.

---

## 📦 Installation

```bash
# 1. Cloner / déposer les fichiers dans un dossier
cd dashboard-reunion

# 2. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## 🚀 Lancement

```bash
streamlit run dashboard_reunion.py
```

Ouvre automatiquement **http://localhost:8501** dans votre navigateur.

---

## 🔄 Rafraîchissement automatique

Les données sont mises à jour **toutes les 5 minutes** (cache `@st.cache_data(ttl=300)`).  
Le dashboard se recharge automatiquement via `st.rerun()`.

---

## 📊 Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| **KPI instantanés** | Production totale, ENR, % renouvelable, thermique |
| **Mix empilé** | Aire empilée Photovoltaïque / Éolien / Hydraulique / Bioénergies / Charbon / Diesel / Turbines |
| **Production totale** | Courbe lissée avec remplissage |
| **% Renouvelables** | Évolution temporelle |
| **🔥 Centrales thermiques** | Courbes individuelles Charbon / Diesel / Turbines — observer les démarrages |

---

## 🌐 Source de données

- **API** : `https://opendata-reunion.edf.fr/api/explore/v2.1/catalog/datasets/prod-electricite-temps-reel/records`
- **Doc API** : https://opendata-reunion.edf.fr/datasets/prod-electricite-temps-reel-974/api-doc
- Pas de clé API requise (données publiques)
- Granularité : **15 minutes**, données estimées puis consolidées

---

## 🗂️ Structure des fichiers

```
dashboard-reunion/
├── dashboard_reunion.py   # Application Streamlit principale
├── requirements.txt       # Dépendances Python
└── README.md              # Ce fichier
```
