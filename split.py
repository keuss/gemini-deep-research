import csv
import os

def decouper_csv(chemin_fichier_entree, lignes_par_fichier=10):
    """
    Découpe un fichier CSV en plusieurs petits fichiers.
    
    :param chemin_fichier_entree: Le chemin vers le fichier CSV source.
    :param lignes_par_fichier: Le nombre de lignes de données par fichier (hors en-tête).
    """
    # Vérifie si le fichier existe
    if not os.path.exists(chemin_fichier_entree):
        print(f"Erreur : Le fichier '{chemin_fichier_entree}' est introuvable.")
        return

    # Sépare le nom du fichier de son extension pour nommer les sorties
    nom_base, extension = os.path.splitext(chemin_fichier_entree)

    # Ouvre le fichier source en mode lecture
    with open(chemin_fichier_entree, mode='r', encoding='utf-8-sig') as fichier_in:
        lecteur = csv.reader(fichier_in)
        
        try:
            # Récupère la première ligne (l'en-tête)
            en_tete = next(lecteur)
        except StopIteration:
            print("Le fichier CSV est vide.")
            return

        compteur_fichier = 1
        lignes_courantes = []

        # Parcours des lignes restantes
        for ligne in lecteur:
            lignes_courantes.append(ligne)

            # Dès qu'on atteint la limite (ex: 10), on crée un nouveau fichier
            if len(lignes_courantes) == lignes_par_fichier:
                chemin_sortie = f"{nom_base}_partie_{compteur_fichier:03d}{extension}"
                
                with open(chemin_sortie, mode='w', encoding='utf-8-sig', newline='') as fichier_out:
                    ecrivain = csv.writer(fichier_out)
                    ecrivain.writerow(en_tete) # Écriture de l'en-tête
                    ecrivain.writerows(lignes_courantes) # Écriture des données
                
                print(f"Créé : {chemin_sortie}")
                compteur_fichier += 1
                lignes_courantes = [] # Réinitialise pour le prochain lot

        # Gestion des lignes restantes (s'il en reste moins de 10 à la fin)
        if lignes_courantes:
            chemin_sortie = f"{nom_base}_partie_{compteur_fichier:03d}{extension}"
            
            with open(chemin_sortie, mode='w', encoding='utf-8-sig', newline='') as fichier_out:
                ecrivain = csv.writer(fichier_out)
                ecrivain.writerow(en_tete)
                ecrivain.writerows(lignes_courantes)
            
            print(f"Créé : {chemin_sortie} (Fichier final)")

# --- Exécution ---
# Remplacez 'mon_gros_fichier.csv' par le nom exact de votre fichier
nom_de_votre_fichier = 'BaseSAE.csv' 
decouper_csv(nom_de_votre_fichier, lignes_par_fichier=10)
