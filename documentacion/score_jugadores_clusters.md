# Comprehensive Documentation – World Cup Player Recommender & Clustering

## 1. Overview
The **worldcup‑app** repository implements a pipeline that:
1. **Ingests** raw player data from a CSV (FC26_20250921.csv). 
2. **Filters** the data against the *convocados* SQLite database (players that were officially called up). 
3. **Normalises** names (Unicode NFD → ASCII, lower‑casing) so that accented characters are compared correctly.
4. **Generates** macro‑group JSON files (`player_clustering_{position}.json`) that contain only the players kept after filtering.
5. **Runs two clustering algorithms** per position:
   - **Hierarchical Agglomerative Clustering (HAC)** with cosine distance (average linkage).
   - **KMeans** with cosine distance emulated via L2‑normalisation.
6. **Selects a representative** for each cluster – the player with the **maximum `overall` rating**. The representative’s name and overall are printed in the log.

All steps are fully automated and re‑runnable from the command line.

---

## 2. Data Ingestion & Normalisation (`scrapping_clustering.py`)
```python
# Load CSV
df = pd.read_csv("data/player_similarity/FC26_20250921.csv", low_memory=False)

# Keep only the columns needed for clustering
columns_to_keep = [
    "long_name", "player_positions", "nationality_name", "overall",
    "age", "height_cm", "weight_kg", "pace", "passing", "shooting",
    "dribbling", "defending", "physic", "attacking_crossing",
    "attacking_finishing", "attacking_heading_accuracy",
    "attacking_short_passing", "attacking_volleys", "skill_dribbling",
    "skill_curve", "skill_fk_accuracy", "skill_long_passing",
    "skill_ball_control", "movement_acceleration", "movement_sprint_speed",
    "movement_agility", "movement_reactions", "movement_balance",
    "power_shot_power", "power_jumping", "power_stamina",
    "power_strength", "power_long_shots", "mentality_aggression",
    "mentality_interceptions", "mentality_positioning", "mentality_vision",
    "mentality_penalties", "mentality_composure",
    "defending_marking_awareness", "defending_standing_tackle",
    "defending_sliding_tackle"
]

df_filtered = df[columns_to_keep].copy()
```

### 2.1. Database Filtering
```python
conn = sqlite3.connect("data/recommender_data/convocados.db")
query = "SELECT id, pais, jugador, equipo FROM convocados"
df_convocados = pd.read_sql_query(query, conn)
conn.close()
```

### 2.2. Normalisation of Strings
```python
import unicodedata

def normalize_string(s):
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').strip().lower()

# Apply normalisation to the columns used for matching
df_filtered['long_name_lower'] = df_filtered['long_name'].apply(normalize_string)
df_filtered['nationality_lower'] = df_filtered['nationality_name'].apply(normalize_string)
```

### 2.3. Matching Logic
For every row in `convocados` we build a regex pattern with word boundaries (`\b`) so that "pedri" does **not** match "Zampedri".
```python
for _, row in df_convocados.iterrows():
    name_db = normalize_string(row['jugador'])
    pais_db = normalize_string(row['pais'])
    pattern = r'\b' + re.escape(name_db) + r'\b'
    matches = df_filtered[df_filtered['long_name_lower'].str.contains(pattern, regex=True)]
    # Country check – keep only if the DB country matches the CSV nationality
    matches = matches[matches['nationality_lower'] == pais_db]
    # Keep the first match (unique) …
```

### 2.4. Output JSON
The macro‑group (`goalkeeper`, `defender`, `midfielder`, `striker`, `winger`) files are written with **UTF‑8** and **`force_ascii=False`** to preserve accents:
```python
macro_df.to_json(file_path, orient="records", indent=4, force_ascii=False)
```

---

## 3. Clustering Engine (`scripts/recommender/HAC_clustering.py`)
### 3.1. Imports & Utilities
```python
import json, os, sys
import numpy as np, pandas as pd
from sklearn.preprocessing import MaxAbsScaler, normalize
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import pairwise_distances
```
- `normalize` and `MaxAbsScaler` are used to scale and project features to a unit hypersphere to isolate playstyles.

### 3.2. Data Pre‑processor
```python
class DataPreprocessor:
    @staticmethod
    def preprocess(df):
        # Seleccionar todas las columnas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Eliminar 'overall' de las características numéricas si está presente
        if 'overall' in numeric_cols:
            numeric_cols.remove('overall')
            
        # Fase 1: Imputación informada con la mediana de cada columna
        df_numeric = df[numeric_cols].apply(lambda col: col.fillna(col.median()))
        df_numeric = df_numeric.fillna(0)
        
        # Fase 2: Homogeneización del Espacio (MaxAbsScaler por columna)
        scaler = MaxAbsScaler()
        scaled_features = scaler.fit_transform(df_numeric)
        
        # Fase 3: Extracción de Magnitud (Normalización L2 por fila)
        normalized_features = normalize(scaled_features, norm='l2')
        
        # Guardamos 'overall' (imputado con la mediana o 50 si falta)
        overall_median = df['overall'].median() if 'overall' in df.columns else 50
        if pd.isna(overall_median):
            overall_median = 50
        overalls = df['overall'].fillna(overall_median).values
        
        return normalized_features, df['long_name'].values, overalls
```
- `overall` is extracted **only** for representative selection and filled with the median.
- Missing feature values are imputed using column medians instead of 0 to protect the vector topology.
- Column scaling is done via `MaxAbsScaler` to bound columns to `[0, 1]` without translation.
- L2 row normalization is applied to project the players onto a unit hypersphere, stripping out magnitude/quality and leaving only style direction.

### 3.3. HAC Engine
```python
class ClusteringEngine:
    def __init__(self, n_clusters=5, metric='cosine', linkage='average'):
        self.model = AgglomerativeClustering(n_clusters=n_clusters,
                                            metric=metric, linkage=linkage)
    def fit_predict(self, features):
        return self.model.fit_predict(features)

    @staticmethod
    def find_representatives(labels, player_names, overalls):
        """Select the player with the highest overall inside each cluster."""
        n_clusters = len(np.unique(labels))
        reps = {}
        for cid in range(n_clusters):
            idx = np.where(labels == cid)[0]
            best = np.argmax(overalls[idx])
            reps[cid + 1] = {
                'name': player_names[idx[best]],
                'overall': int(overalls[idx[best]])
            }
        return reps
```

### 3.4. KMeans Engine (Cosine on unit hypersphere)
```python
class KMeansEngine:
    """KMeans with cosine similarity – achieved by operating directly on the L2-normalised features.
    Operating Euclidean distance KMeans on a unit hypersphere is mathematically equivalent
    to maximizing cosine similarity.
    """
    def __init__(self, n_clusters=5, random_state=42):
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init='auto')
    def fit_predict(self, features):
        self.labels_ = self.model.fit_predict(features)
        self.features_normalized_ = features
        return self.labels_
    def find_representatives(self, player_names, overalls):
        n_clusters = len(np.unique(self.labels_))
        reps = {}
        for cid in range(n_clusters):
            idx = np.where(self.labels_ == cid)[0]
            best = np.argmax(overalls[idx])
            reps[cid + 1] = {
                'name': player_names[idx[best]],
                'overall': int(overalls[idx[best]])
            }
        return reps
```

### 3.5. Position Factory & Dynamic Cluster Counts
```python
class PositionFactory:
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'clustering_players'))
    positions = {
        'Goalkeepers': 'player_clustering_goalkeeper.json',
        'Defenders':   'player_clustering_defender.json',
        'Midfielders':'player_clustering_midfielder.json',
        'Strikers':   'player_clustering_striker.json',
        'Wingers':    'player_clustering_wingers.json'
    }
    @classmethod
    def get_filepath(cls, name):
        return os.path.join(cls.base_path, cls.positions[name])
```
- The `main()` function uses a dictionary `positions_clusters` to configure **different numbers of clusters per position** (Goalkeepers 3, Defenders 5, Midfielders 7, Strikers 3, Wingers 5).

### 3.6. Main Workflow (HAC vs KMeans)
```python
positions_clusters = {
    'Goalkeepers': 3,
    'Defenders': 5,
    'Midfielders': 7,
    'Strikers': 3,
    'Wingers': 5
}
for position, n_clusters in positions_clusters.items():
    filepath = PositionFactory.get_filepath(position)
    df = DataLoader.load_data(filepath)
    features, names, overalls = DataPreprocessor.preprocess(df)

    # HAC
    hac = ClusteringEngine(n_clusters=n_clusters, metric='cosine', linkage='average')
    hac_labels = hac.fit_predict(features)
    hac_reps = hac.find_representatives(hac_labels, names, overalls)
    print(f"HAC {position}:")
    for cid, rep in sorted(hac_reps.items()):
        print(f"  Cluster {cid} = {rep['name']} (overall: {rep['overall']})")

    # KMeans (cosine)
    km = KMeansEngine(n_clusters=n_clusters)
    km.fit_predict(features)
    km_reps = km.find_representatives(names, overalls)
    print(f"KMeans {position}:")
    for cid, rep in sorted(km_reps.items()):
        print(f"  Cluster {cid} = {rep['name']} (overall: {rep['overall']})")
    print()
```
- Both algorithms now **log the representative name *and* its overall**, making comparison straightforward.

---

## 4. Logging & Unicode Handling
- `sys.stdout.reconfigure(encoding='utf-8')` guarantees that Windows consoles display accented names correctly.
- All JSON dumps use `force_ascii=False` so that characters such as `á`, `ñ`, `中`, `ع` are preserved.

---

## 5. Tests & Validation
Running the scripts after each change produced output similar to:
```
HAC Goalkeepers:
  Cluster 1 = Alisson Ramsés Becker (overall: 89)
  Cluster 2 = Joan García Pons (overall: 83)
  Cluster 3 = Dominik Kotarski (overall: 77)
KMeans Goalkeepers:
  Cluster 1 = Yehvann Diouf (overall: 78)
  Cluster 2 = David Raya Martín (overall: 87)
  Cluster 3 = Alisson Ramsés Becker (overall: 89)
…
```
- The numbers of clusters respect the configuration per position.
- Representative players match the **maximum `overall`** in each cluster, as verified by manual inspection of the generated JSON files.

---

## 6. How to Run the Full Pipeline
```bash
# 1. Build the macro‑group JSON files (filter + normalise)
python data/clustering_players/scrapping_clustering.py

# 2. Run the clustering comparison (HAC + KMeans)
python scripts/recommender/HAC_clustering.py
```
The scripts are **self‑contained** – no external configuration files are required beyond the CSV and SQLite DB present in `data/`.

---

## 7. Future Enhancements (Ideas)
| Feature | Rationale |
|---|---|
| **Parameterise the exponent used in the original distance/overall scoring** | Allows experimentation with how strongly `overall` influences the representative selection.
| **Add silhouette / Davies‑Bouldin scores** | Gives quantitative evaluation of cluster quality for each algorithm.
| **Persist the cluster labels** back into the macro JSON files | Makes downstream services (e.g., a recommender UI) able to query “players in cluster 3 of midfielders”.
| **Expose a CLI wrapper** (`--engine hac|kmeans --position GK`) | Enables quick ad‑hoc runs without editing the source.
| **Unit tests for the matching logic** | Guarantees that accent normalisation and country checks stay robust.

---

## 8. References
- **scikit‑learn** documentation for AgglomerativeClustering, KMeans, and pairwise_distances.
- **Unicode Normalization** (NFD) – Python `unicodedata` module.
- **World Cup 2022 data** – source CSV generated from the FIFA database.

---

*Prepared by Antigravity (AI coding assistant) – June 2026*
