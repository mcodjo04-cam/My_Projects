# **Analyse et prédiction de la maladie rénale chronique (CKD)**
![](https://sf.topsante.com/wp-content/uploads/topsante/2023/09/reins-quels-sont-leurs-principaux-ennemis-qui-peuvent-mener-insuffisance-renale-750x410.jpg)


                              CODJO Merveille  

---

## Données : Base Kidney Disease  
La base de données porte sur les caractéristiques biologiques et cliniques de patients pour lesquels des examens de maladie rénale chronique ont été effectués. Les données de cette base ont été recueillies via le dossier des patients d’une clinique X. La base est constituée de 400 observations décrites par 26 variables.  

**Source des données :** [UCI Machine Learning Repository – Kidney Disease Dataset](https://archive.ics.uci.edu/ml/datasets/kidney+disease)

---

## I - Introduction

La **maladie rénale chronique (CKD)** constitue un problème de santé majeur dans le monde, affectant des millions de personnes. Cette maladie silencieuse se caractérise par une perte progressive de la fonction rénale, pouvant aboutir à une insuffisance rénale terminale si elle n’est pas détectée et traitée à temps. Les causes principales incluent l’hypertension, le diabète, les maladies cardiovasculaires et certains facteurs génétiques.  

L’objectif de ce projet est de **prévoir la présence de la CKD** en fonction des **caractéristiques biologiques et cliniques** des patients, et d’identifier les variables les plus influentes pour le diagnostic.

---

## II - Analyse Exploratoire

Pour cette analyse, nous avons utilisé la base de données **"Kidney Disease"**.  
Cette base contient **400 observations** avec **26 variables**, représentant les mesures biologiques et cliniques des patients pour lesquels des examens de CKD ont été réalisés.

Les variables présentes dans le jeu de données sont décrites dans le tableau ci-dessous :

### Tableau : Description des variable

| Variable | Description | Interprétation / rôle dans le diagnostic |
|----------|------------|----------------------------------------|
| **Classe (classification)** | Indicateur de présence de CKD | 1 = CKD présente, 0 = CKD absente |
| **Âge (age)** | Âge du patient en années | Le risque de CKD augmente avec l’âge |
| **Pression Artérielle (bp)** | Pression artérielle en mm/Hg | L’hypertension est un facteur majeur de CKD |
| **Gravité Spécifique (sg)** | Concentration des urines | Indique la fonction rénale et l’hydratation |
| **Albumine (al)** | Taux d'albumine dans les urines | Une albuminurie élevée reflète des lésions rénales |
| **Sucre (su)** | Taux de sucre dans les urines | Peut indiquer un diabète non contrôlé |
| **Globules Rouges (rbc)** | Présence de globules rouges dans les urines | Signale une hématurie liée à une atteinte rénale |
| **Cellules Pus (pc)** | Présence de cellules de pus dans les urines | Suggère infection ou inflammation urinaire |
| **Aggrégation des Cellules Pus (pcc)** | Grumeaux de cellules de pus | Infection urinaire plus sévère |
| **Bactéries (ba)** | Présence de bactéries dans les urines | Infection urinaire pouvant affecter la fonction rénale |
| **Glucose Sanguin Aléatoire (bgr)** | Glucose sanguin aléatoire (mg/dL) | Glycémie élevée, facteur de risque CKD |
| **Urée Sanguine (bu)** | Taux d'urée sanguine (mg/dL) | Marqueur de fonction rénale diminuée |
| **Créatinine Sérique (sc)** | Taux de créatinine sérique (mg/dL) | Indicateur clé de la fonction rénale |
| **Sodium (sod)** | Taux de sodium (mEq/L) | Déséquilibre électrolytique possible avec CKD |
| **Potassium (pot)** | Taux de potassium (mEq/L) | Hyperkaliémie liée à l’insuffisance rénale |
| **Hémoglobine (hemo)** | Taux d'hémoglobine (g) | Une baisse reflète souvent l’anémie de CKD |
| **Volume des Cellules Packées (pcv)** | Hématocrite | Réduit en cas d’anémie associée à CKD |
| **Nombre de Globules Blancs (wc)** | Nombre de globules blancs | Indique infection ou inflammation |
| **Nombre de Globules Rouges (rc)** | Nombre de globules rouges | Réduction liée à l’anémie CKD |
| **Hypertension (htn)** | Présence d’hypertension | Facteur de risque majeur |
| **Diabète Mellitus (dm)** | Présence de diabète | Cause fréquente de CKD |
| **Maladie Coronarienne (cad)** | Maladie coronarienne | Risque cardiovasculaire élevé associé à CKD |
| **Appétit (appet)** | Bon ou mauvais | Perte d’appétit fréquente chez les patients CKD |
| **Œdème de Pieds (pe)** | Présence d’œdème | Signe d’insuffisance rénale ou rétention d’eau |
| **Anémie (ane)** | Présence d’anémie | Fréquente en CKD à cause de faible production d’érythropoïétine |

---

## III - Objectifs de l’analyse

1. Étudier les différences entre les profils biologiques et cliniques des patients **CKD vs non-CKD**.  
2. Identifier les **facteurs déterminants** pour le diagnostic et les stades de CKD. 
3. Visualiser les relations entre variables et construire éventuellement un **modèle prédictif** pour la détection de la CKD.

---
## Revue de littérature

**Hospital Clínic de Barcelona** – “Causes and risk factors associated with Chronic Kidney Failure” 
**Lien** : https://www.clinicbarcelona.org/en/assistance/diseases/chronic-kidney-disease/causes-and-risk-factors 
**Utilité pour mon projet**  : Justifie l’inclusion dans les variables de risque de l’hypertension, du diabète et des antécédents rénaux. Permet d’étayer l’explication sur pourquoi certaines variables sont pertinentes pour le diagnostic de CKD.

Comprendre la maladie rénale chronique(CHU Lille)
**Lien** : https://youtu.be/nZ-JJ5ImdsQ?si=3xfsYKjPt0omcSbe
**Utilité pour mon projet** : Aide dans la comprehension de la maladie et le choix des variables importantes dans cette analyse.

---
## Informations tirees des revues

**Variables** importantes : creatinine ,albumine,diabete , hypertension 
Au fur et à mesure que le CKD s'aggrave, le risque de complications augmente:
    -Pression artérielle élevée
    -Anémie (faible taux de globules rouges)
    -Hyperkalémie (taux élevés de potassium dans le sang)
Ces variables peuvent aidez pour detecter les stades de la maladie.   
    
---
