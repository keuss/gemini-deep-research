from pathlib import Path

def concatener_csv_sans_entete(repertoire_source, fichier_sortie):
    chemin_sortie = Path(fichier_sortie)
    repertoire = Path(repertoire_source)
    
    with open(chemin_sortie, 'w', encoding='utf-8-sig') as outline:
        # Récupération de tous les fichiers .csv
        fichiers_csv = sorted(repertoire.glob('*.csv'))
        
        for fichier in fichiers_csv:
            # On évite de lire le fichier de sortie s'il est dans le même répertoire
            if fichier.resolve() == chemin_sortie.resolve():
                continue
                
            derniere_ligne_ecrite_a_un_saut = True
            
            with open(fichier, 'r', encoding='utf-8-sig') as inline:
                for ligne in inline:
                    # Si la ligne commence par l'en-tête spécifique, on la passe
                    if ligne.startswith("CAT;"):
                        continue
                    
                    # On écrit la ligne
                    outline.write(ligne)
                    # On stocke si la ligne courante se termine par un saut de ligne
                    derniere_ligne_ecrite_a_un_saut = ligne.endswith('\n')
            
            # Si le fichier s'est terminé sans saut de ligne, on l'ajoute 
            # pour le fichier suivant
            if not derniere_ligne_ecrite_a_un_saut:
                outline.write('\n')

if __name__ == "__main__":
    # Utilise le répertoire courant '.' et génère 'fusion.csv'
    concatener_csv_sans_entete('.', 'fusion.csv')
    print("Fusion et nettoyage des en-têtes terminés avec succès !")