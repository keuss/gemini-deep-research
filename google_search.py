import os
import pandas as pd
import csv
from google import genai
from google.genai import types

# Configuration des répertoires et fichiers
DOSSIER_DONNEES = "./mon_repertoire_csv"  # Dossier contenant vos fichiers CSV à traiter
FICHIER_SORTIE = "resultats_deep_research.csv" # Le fichier CSV unique contenant les résultats

# Initialisation du client Gemini
client = genai.Client()

#for model in client.models.list():
#    print(model.name)

# Contenu fixe de votre plan d'action (Ex: extrait de votre document Word)
PLAN_DACTION_CONTENT = """
Cahier des charges - Inventaire national des SAE (FFME)
Objectif
Vérifier, enrichir et corriger une base de données de Structures Artificielles d'Escalade (SAE) à partir d'un fichier initial issu de la FFME.
L'objectif est de produire un inventaire :
- fiable
- traçable
- homogène
- vérifié par sources
________________________________________
Règle fondamentale
Ne jamais inventer une information.
Toute donnée doit être :
- confirmée par une source
- ou explicitement estimée
- ou laissée vide / "Non trouvé"
________________________________________
1. Existence de la structure
Déterminer si la SAE existe encore.
Valeurs :
- Oui
- Non
- Incertain
________________________________________
2. Niveau de fiabilité
Confirmé
Source officielle :
- club
- mairie / collectivité
- gestionnaire
- fabricant
- architecte
- Google Maps fiable
- autre source officielle
Probable
Plusieurs indices concordants sans source officielle claire.
Incertain
Mention ancienne ou non vérifiable.
Non trouvé
Aucune information exploitable.
________________________________________
3. Dimensions (colonnes existantes "HAUTEUR" et "LINEAIRE SOL")
Colonnes déjà présentes dans le fichier :
- Hauteur (HAUTEUR)
- Linéaire (LINEAIRE SOL)
Elles doivent être :
- complétées si possible
- corrigées si des sources fiables existent
Ne pas rechercher
- nombre de voies
Estimation des dimensions
Si aucune donnée fiable :
Utiliser photos + référentiels visuels :
- but de handball (2 m)
- panier de basket (3,05 m)
- portes standard
- gradins
- hauteur sous plafond
- dimensions des terrains de sport (hand, basket, volley, badminton)
Permet aussi d'estimer le linéaire sur terrain complet
Toute estimation doit être clairement indiquée comme telle
________________________________________
4. Clubs utilisateurs
Identifier :
- club(s) utilisateur(s)
- nom exact du club
________________________________________
5. Fabricant (information secondaire)
À identifier uniquement si facilement trouvable.
Fabricants principaux :
- Pyramide
- EP Climbing
- Escatech
- Grimpomania
Ne pas faire de recherche longue uniquement pour cela
Les sites fabricants restent une source valable.
________________________________________
6. Vérification CAT et Qualité
Discipline difficulté (colonne "PA")
CAT
- Mur :
 - hauteur ≤ 7 m ET
 - linéaire < 21 m
- SAE :
 - hauteur ≥ 8 m ET
 - linéaire ≥ 21 m
Cas particuliers
- 9 m x 18 m -> SAE Initiation
- 6 m x 30 m -> Mur
La hauteur est le critère principal
________________________________________
Qualité
Mur
- Non classé
SAE
- appliquer référentiel FFME :
- Départemental : ≥ 9 m et ≥ 24 m
- Régional : ≥ 11 m et ≥ 36 m
- National : ≥ 13 m et ≥ 42 m
- International : ≥ 16 m et ≥ 51 m
Règle intermédiaire
SAE ne remplissant pas les seuils Départemental :
- Initiation
________________________________________
Discipline bloc (colonne "BLOC")
- hauteur fixe : 4,50 m
CAT
- Mur : linéaire < 21 m
- SAE : linéaire ≥ 21 m
Qualité
- Non classé
- Initiation (21-23,99 m)
- puis référentiel FFME
________________________________________
7. Cas atypiques (obligatoire)
Toujours signaler :
- commune fusionnée
- gymnase reconstruit
- SAE déplacée
- rénovation / extension
- changement de club
- contradictions de sources
- remplacement de mur
________________________________________
8. Sources (ordre de priorité)
	1.	Club
	2.	Mairie / collectivité
	3.	Gestionnaire
	4.	Fabricant
	5.	Architecte
	6.	Presse locale
	7.	RES (complément uniquement)
Le RES n'est pas une preuve suffisante.
________________________________________
9. Règle de résolution des conflits
Si contradiction :
	1.	source la plus récente officielle prioritaire
	2.	club / mairie > fabricant > presse > RES
	3.	expliquer dans commentaires
________________________________________
10. Colonnes à ajouter
Conserver colonnes existantes.
Ajouter :
- Existence actuelle
- Fiabilité
- Nature des dimensions (Publiées / Estimées)
- Club utilisateur
- Nom du club
- Fabricant
- Source principale
- URL source
- Date de vérification
- Commentaires
- Décision (optionnel mais recommandé)
________________________________________
11. Commentaires (standardisation)
Exemples :
- Existence confirmée par le club
- Dimensions publiées par fabricant
- Dimensions estimées via photos
- CAT corrigée : Mur -> SAE
- Qualité corrigée : Non classé -> Initiation
- Gymnase reconstruit en 2022
- Données contradictoires
________________________________________
12. Règle de cohérence
- privilégier source la plus récente
- corriger les données obsolètes
- documenter toute correction
________________________________________
Philosophie du projet
Ce travail est un inventaire technique, pas un simple enrichissement de données.
Chaque ligne doit être :
- vérifiable
- justifiable
- traçable
"""

# Liste pour stocker temporairement les lignes du rapport final
tous_les_resultats = []

# Boucle sur l'ensemble des fichiers du répertoire
print(f"Début de l'analyse des fichiers dans : {DOSSIER_DONNEES}")

# On vérifie si le dossier existe
if not os.path.exists(DOSSIER_DONNEES):
    print(f"Erreur : Le dossier {DOSSIER_DONNEES} n'existe pas.")
    exit()

# Liste tous les fichiers du répertoire
fichiers = os.listdir(DOSSIER_DONNEES)

for nom_fichier in fichiers:
    # On ne traite que les fichiers de données (ex: se terminant par .csv)
    if nom_fichier.endswith('.csv') and nom_fichier != FICHIER_SORTIE:
        chemin_complet = os.path.join(DOSSIER_DONNEES, nom_fichier)
        print(f"\nTraitement du fichier : {nom_fichier}...")
        
        # Lecture du CSV cible
        try:
            df_source = pd.read_csv(chemin_complet, sep=';', encoding='utf-8')
            csv_content = df_source.to_markdown(index=False)
        except Exception as e:
            print(f"❌ Impossible de lire le fichier {nom_fichier}: {e}")
            continue # Passe au fichier suivant en cas d'erreur
            
        # --- BLOC DE TEST TEMPORAIRE ---
        #print("\n=== CONTENU DU CSV EXTRAIT ===")
        #print(csv_content)
        #exit()
        # -------------------------------

        # Construction du prompt dédié à ce fichier
        prompt_complet = f"""
        Tu es un expert en recherche et analyse de données.

        Voici le plan d'action à suivre :
        {PLAN_DACTION_CONTENT}

        Voici les données cibles, pour le fichier ({nom_fichier}), pour lesquelles tu dois effectuer des recherches sur le Web :
        {csv_content}

        Consigne : En te basant sur le plan d'action et les données fournies, utilise l'outil de recherche Google Search pour trouver les informations les plus récentes et pertinentes sur le Web.
        Génère ta réponse directement sous forme de lignes CSV valides (avec point-virgule comme séparateur).
        Pour le réponse, je ne veux pas de texte (tu ne dois rien inventer).
        Ne mets pas de texte d'explication avant ou après, fournis uniquement le contenu CSV brut.
        Déterminer si la SAE existe encore en ajoutant les colonnes: (conserver colonnes existantes) :
        - Existence actuelle (Oui / Non / Incertain (exemple si sources insuffisantes, ou si tu ne sais pas)). La colonne la plus importante.
        Et si possible :
        - Fiabilité
        - Nature des dimensions (Publiées / Estimées)
        - Club utilisateur
        - Nom du club
        - Fabricant
        - Source principale
        - URL source
        - Date de vérification
        - Commentaires
        - Décision (optionnel mais recommandé)
        """
        
        # Appel de l'API Gemini (avec Deep Research / Google Search)
        try:
            response = client.models.generate_content(
                model='gemini-2.5-pro', # Utilisation de la version Pro stable et performante
                contents=prompt_complet,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.2,
                ),
            )
            
            # Extraction du texte de la réponse
            analyse_gemini = response.text
            
            # NETTOYAGE DES BALISES CODE (Nouveau)
            # On supprime les balises de bloc si Gemini en a ajouté au début ou à la fin
            analyse_gemini = analyse_gemini.replace("```csv", "")
            analyse_gemini = analyse_gemini.replace("```", "")
            # Optionnel : supprime les espaces ou lignes vides inutiles au début/fin du texte
            analyse_gemini = analyse_gemini.strip()
            
            print(f"✅ Analyse réussie et nettoyée pour {nom_fichier}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'appel API pour {nom_fichier}: {e}")
            analyse_gemini = f"Erreur API : {e}"


        #print(analyse_gemini)
        # Ajout direct de la chaîne brute de texte (déjà au format CSV)
        tous_les_resultats.append(analyse_gemini)

# ÉCRITURE BRUTE ET DIRECTE EN FIN DE SCRIPT
print(f"\nEnregistrement des résultats bruts dans '{FICHIER_SORTIE}'...")
try:
    with open(FICHIER_SORTIE, mode='w', encoding='utf-8') as f:
        for resultat in tous_les_resultats:
            f.write(resultat)
            f.write("\n")  # Un simple saut de ligne entre chaque bloc CSV retourné
            
    print(f"💾 Sauvegarde brute réussie !")
    
except Exception as e:
    print(f"❌ Erreur lors de l'écriture finale du fichier : {e}")

print(f"\n🎉 Traitement terminé ! Les résultats ont été enregistrés dans '{FICHIER_SORTIE}'.")