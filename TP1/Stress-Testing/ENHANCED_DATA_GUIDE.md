# Guide des Données Enrichies (Enhanced)

## Qu'est-ce qu'un fichier "Enhanced"?

Les fichiers `reviews_enhanced_*.csv` contiennent **toutes les données originales PLUS une analyse automatique de sentiment**.

L'objectif: **Détecter les contradictions** où ce que dit l'utilisateur (texte) ne correspond pas à la note qu'il donne (rating).

---

## Colonnes Originales (dans tous les fichiers)

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `app_name` | Nom de l'application | "Otter AI" |
| `userName` | Nom de l'utilisateur | "Ahmed" |
| `score` | Note donnée (1-5 étoiles) | 1 |
| `content` | Texte de la review | "Stopped syncing...." |

---

## Colonnes NOUVELLES Ajoutées par l'Analyse

### 1. **`text_sentiment_score`** 
**Sentiment du TEXTE** (-1 à +1)

```
-1.0  = Très négatif (mots: terrible, hate, broken)
-0.5  = Négatif (mots: bad, slow, issue)
 0.0  = Neutre (pas d'émotions)
+0.5  = Positif (mots: good, great, nice)
+1.0  = Très positif (mots: excellent, amazing, love)
```

**Exemple:**
- Review: "Stopped syncing.... Broken for days."
- Score de sentiment: **-1.0** (deux mots négatifs)

---

### 2. **`positive_keywords_count`**
**Combien de mots positifs** détectés dans le texte

Mots positifs: great, excellent, amazing, love, perfect, wonderful, best...

**Exemple:**
- Text: "Good app, excellent performance"
- Count: **2** (good + excellent)

---

### 3. **`negative_keywords_count`**
**Combien de mots négatifs** détectés dans le texte

Mots négatifs: terrible, awful, horrible, hate, worst, bad, broken, slow, crash...

**Exemple:**
- Text: "Broke after update. Very slow and crashes."
- Count: **3** (broke + slow + crashes)

---

### 4. **`detected_keywords`**
**Liste des mots-clés trouvés**

Tous les mots positifs ou négatifs trouvés

**Exemple:**
- Text: "Great app but buggy"
- Keywords: `['great', 'buggy']`

---

### 5. **`is_contradiction`** 
**Y a-t-il une contradiction?** (true/false)

**TRUE** = Le sentiment du texte ≠ le rating donné

```
Cas TRUE (CONTRADICTION):
  Rating: 1/5 (très mauvais)
  Text sentiment: 0.0 (neutre)
  → Utilisateur a donné mauvaise note mais texte ne le montre pas

Cas FALSE (COHERENT):
  Rating: 5/5 (excellent)
  Text sentiment: +1.0 (très positif)
  → Cohérent! Excellente note ET texte positif
```

---

### 6. **`contradiction_type`**
**Quel TYPE de contradiction?**

Seulement si `is_contradiction = true`

```
- mixed_contradiction = Mélange incompatible
  Exemple: Note 1/5 + texte neutre
  
- high_rating_negative_text = Bonne note mais texte négatif
  Exemple: Note 5/5 + "buggy" dans le texte
  
- low_rating_positive_text = Mauvaise note mais texte positif
  Exemple: Note 1/5 + "excellent" dans le texte

- no_contradiction = Pas de contradiction
```

---

### 7. **`contradiction_severity`**
**Sévérité de la contradiction** (0 à 1)

```
0.0 = Pas de contradiction
0.1 = Très légère
0.5 = Modérée
1.0 = Extrêmement grave
```

**Exemple:**
- Rating: 1/5 + Text sentiment neutre = 0.10 (légère)
- Rating: 5/5 + Text très négatif = 0.95 (grave!)

---

## Exemple Concret

### Review Originale:
```
app_name: "Otter AI"
userName: "Nadia"
score: 1
content: "Stopped syncing...."
```

### Après Enrichissement:
```
app_name: "Otter AI"
userName: "Nadia"
score: 1
content: "Stopped syncing...."
text_sentiment_score: 0.00         ← Texte neutre
positive_keywords_count: 0          ← Pas de mots positifs
negative_keywords_count: 1          ← 1 mot négatif: "syncing"
detected_keywords: ['syncing']       ← Mots trouvés
is_contradiction: true              ← CONTRADICTION DÉTECTÉE!
contradiction_type: mixed_contradiction
contradiction_severity: 0.10        ← Légère contradiction
```

### Interprétation:
**Nadia a donné 1/5 (très mauvaise note) avec un texte neutre.**

Pourquoi c'est une contradiction?
- Note 1/5 = très mécontent
- Texte = "Stopped syncing..." (neutre, juste décriptif)
- La note ne reflète pas le texte

---

## Comment Utiliser Ces Données?

### For Analysts (Manual Review):
→ Regarder les fichiers **`serving_layer_details_*.csv`**
→ Contient UNIQUEMENT les contradictions
→ Pour investiguer les reviews suspectes

### For Dashboards:
→ Utiliser colonne `is_contradiction` pour filtrer
→ Utiliser `contradiction_severity` pour prioritiser

### For Quality Control:
→ Identifier les apps avec taux de contradiction élevé
→ Investiguer les faux avis (sentiment ≠ rating)

---

## Résumé

| Colonne | Pourquoi? | Utilisation |
|---------|-----------|-------------|
| `text_sentiment_score` | Mesurer sentiment du texte | Comparaison avec rating |
| `positive_keywords_count` | Compter mots positifs | Debug sentiment |
| `negative_keywords_count` | Compter mots négatifs | Debug sentiment |
| `detected_keywords` | Voir exactement quels mots | Validation manuelle |
| `is_contradiction` | DÉTECTER contradiction | Filtrer/alerter |
| `contradiction_type` | CLASSIFIER contradiction | Analyser patterns |
| `contradiction_severity` | PRIORISER | Urgence d'investigation |

