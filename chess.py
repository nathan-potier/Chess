from copy import deepcopy
import pygame 
import sys


"""
class :
    Joueur 
    Plateau
    Piece
        Roi
        Fou
        Reine
        Cavalier
        Tour
        Pion
    Game
    victoire/defaite/egalite
    
    
    
    
    faire affichage graphique et rendre le jeux plus jouable 
    
    
    
    
    améliorer la complexité pour le mat ( avec un tableau de pièces)
    
"""

TAILLE_CASE = 80
TAILLE_PLATEAU = TAILLE_CASE * 8
FPS = 10



class Plateau :

    def __init__(self) :

        self.plateau = [[None for i in range(8)] for y in range(8)]
        #self.initialiseur_plateau()
        self.init_plateau_test_unit()
    
    """TEST UNITAIRE UNIQUEMENT POUR LA PRODUCTION"""
    
    def init_plateau_test_unit(self):
        self.plateau[0][0] = Roi("noir", (0, 0))
        self.plateau[3][1] = Dame("blanc", (1, 3))
        self.plateau[2][1] = Roi("blanc", (1,2))
        self.plateau[1][5] = Pion("blanc", (5,1))
        self.plateau[7][1] = Tour("noir", (1,7))
        
    """TEST UNITAIRE UNIQUEMENT POUR LA PRODUCTION"""    
        
    def initialiseur_plateau(self):

        ordre_piece = [Tour,Cavalier,Fou,Dame,Roi,Fou,Cavalier,Tour]

        for i in range(8) :
            self.plateau[1][i] = Pion("noir", (i,1))
            self.plateau[-2][i] = Pion("blanc",(i,6))
            self.plateau[0][i] = ordre_piece[i]("noir",(i,0))
            self.plateau[-1][i] = ordre_piece[i]("blanc",(i,7))

    def afficher_plateau(self):
        for ligne in self.plateau :
            print ( " | ".join(str(piece) if piece else "." for piece in ligne) )
                     
            print("-"*30)

    def __repr__(self):  
        res = "     " + "    ".join("ABCDEFGH") + "\n"  
        res += "  " + "-" * 41 + "\n"

        for i, ligne in enumerate(self.plateau, start=1):  
            res += str(i) + " "  # Numérotation des lignes
            for piece in ligne:  
                res += " | "
                res += str(piece) if piece else ". "
            res += " |\n"
            res += "  " + "-" * 41 + "\n"
        
        return res

    def case_est_vide(self,position:tuple):
        x,y = position
        if self.plateau[y][x] == None :
            return True
        
        return False

    def case_occupe_par_adversaire(self,position:tuple,couleur:str):
        x,y = position
        if not self.case_est_vide(position)  and self.plateau[y][x].couleur != couleur : 
            return True
        
        return False
    

        
class Joueur :
    def __init__(self,nom,couleur) :
        self.nom = nom
        self.couleur = couleur

    def __str__(self):
        return f"{self.nom} ({self.couleur})"
    
    def est_en_echec(self, plateau):
        #Trouver le roi 
        for ligne in plateau.plateau:
            for piece in ligne:
                if isinstance(piece, Roi) and piece.couleur == self.couleur:
                    roi_pos = piece.position
                    break
        #vérifier si une pièce adverse peut l'atteindre (améliorable en regardant que les case qui on potentiellement accès au roi) 
        for ligne in plateau.plateau:
            for piece in ligne:
                if piece and piece.couleur != self.couleur:
                    if roi_pos in piece.deplacement_possible(plateau):
                        return True
        return False
    
    def a_au_moins_un_coup_legal(self, plateau):
        for y in range(8):
            for x in range(8):
                piece = plateau.plateau[y][x]
                if piece and piece.couleur == self.couleur:
                    for move in piece.deplacement_possible(plateau):
                        copie = deepcopy(plateau)
                        copie.plateau[y][x] = None
                        piece_copie = deepcopy(piece)
                        piece_copie.position = move
                        copie.plateau[move[1]][move[0]] = piece_copie
                        if not self.est_en_echec(copie):
                            return True
                        
        return False

class Piece:
    
    def __init__(self, couleur, position):
        self.couleur = couleur
        self.position = position
        
    def __str__(self):
        return self.__class__.__name__[0] + ("B" if self.couleur == "blanc" else "N")

class Pion(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        x,y = self.position
        direction = -1 if self.couleur == "blanc" else 1
        
        deplacements = []
        nouvelle_position = (x,y + direction)

        if 0 <= nouvelle_position[1] < 8 and plateau.case_est_vide(nouvelle_position):

            deplacements.append(nouvelle_position)

        nouvelle_position = (x,y + direction*2)
        if 0 <= nouvelle_position[1] < 8 and plateau.case_est_vide(nouvelle_position) and ( (self.couleur == "blanc" and y == 6 )or (self.couleur == "noir" and y == 1)):

            deplacements.append(nouvelle_position)

        for dx in [-1,1] :
            nouvelle_position = (x + dx , y + direction)

            if 0 <= nouvelle_position[1] < 8 and plateau.case_occupe_par_adversaire(nouvelle_position,self.couleur) and 0 <= nouvelle_position[0] < 8:

                deplacements.append(nouvelle_position)

        return deplacements

class Tour(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        x,y = self.position
        deplacements = []

        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] :
            nx,ny = dx + x , dy + y
            
            while 0 <= nx < 8 and 0 <= ny < 8 :

                if plateau.case_est_vide((nx,ny))  :
                    
                    deplacements.append((nx,ny))
                    
                elif plateau.case_occupe_par_adversaire((nx,ny),self.couleur) :

                    deplacements.append((nx,ny))
                    break


                else : 
                    break

                nx,ny = nx + dx , ny + dy

        return deplacements

class Cavalier(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        x,y = self.position
        deplacements = []
        mouvement = [(1,-2),(-1,2),(2,-1),(-2,1),(2,1),(1,2),(-2,-1),(-1,-2)]

        for dx,dy in mouvement :
            nx,ny = dx + x , dy + y

            if 0 <= nx < 8 and  0 <= ny < 8 and ( plateau.case_est_vide((nx,ny)) or plateau.case_occupe_par_adversaire((nx,ny),self.couleur) ):

                deplacements.append((nx,ny))

        return deplacements    

class Roi(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        x,y = self.position
        deplacements = []

        mouvement = [(1,0),(1,1),(0,1),(0,-1),(1,-1),(-1,-1),(-1,0),(-1,1)]

        for dx,dy in mouvement :
            nx,ny = dx + x , dy + y

            if 0 <= nx < 8 and  0 <= ny < 8 and ( plateau.case_est_vide((nx,ny)) or plateau.case_occupe_par_adversaire((nx,ny),self.couleur) ):

                deplacements.append((nx,ny))

        return deplacements 

class Fou(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        x,y = self.position
        deplacements = []

        mouvements = [(1,1),(-1,-1),(-1,1),(1,-1)]

        for dx , dy in mouvements :
            nx,ny = dx + x , dy + y

            while 0 <= nx < 8 and  0 <= ny < 8 :

                if plateau.case_est_vide((nx,ny)) :
                    deplacements.append((nx,ny))

                elif plateau.case_occupe_par_adversaire((nx,ny),self.couleur) :
                    deplacements.append((nx,ny))
                    break

                else :
                    break

                nx,ny = nx + dx , ny + dy    

        return deplacements

class Dame(Piece):
    def deplacement_possible(self, plateau:Plateau) -> list:
        
        deplacements = Tour(self.couleur,self.position).deplacement_possible(plateau) + Fou(self.couleur,self.position).deplacement_possible(plateau)
        
        return deplacements

def demander_deplacement():

    try : 

        piece_select = input("choisisser une piece ")
        x = convert_str_to_int(piece_select[0])
        y = int(piece_select[1]) - 1
        piece_select = (x,y)

        mouvement = input("choisisser une destination pour la piece ")
        x = convert_str_to_int(mouvement[0])
        y = int(mouvement[1]) - 1
        mouvement = (x,y)

    except Exception as e :
        print("vous avez choisis une valeur incorecte, réessayer")
        return demander_deplacement()
    
    return (piece_select , mouvement)


def convert_str_to_int (l):

    res = ord(l.upper()) - ord("A")

    if 0 <= res <= 7 :
        return res
    
    raise ValueError (" la lettre doit être entre A et H")

def charger_images():
    types = ['p', 'k', 'n', 'b', 'q', 'r']
    couleurs = ['w', 'b']
    images = {}
    
    for t in types :
        for c in couleurs :
            chemin = f"assets/{c}{t}.png"
            image = pygame.image.load(chemin)
            image = pygame.transform.scale(image, (TAILLE_CASE, TAILLE_CASE))
            images[f"{c}{t}"] = image
    return images

def get_image_for_piece(piece, images):
    if not piece:
        return None
    
    type_map = {
        "Pion"      : 'p',
        "Roi"       : 'k',
        "Dame"      : 'q',
        "Tour"      : 'r',
        "Fou"       : 'b',
        "Cavalier"  : 'n'
    }
        
    couleur = 'w' if piece.couleur == "blanc" else 'b'
    
    nom_type = type_map[piece.__class__.__name__]
    
    return images.get(f"{couleur}{nom_type}")


def afficher_plateau(screen, plateau, images, case_selectionne=None):
    couleurs = [(240,217,180), (180, 130, 99)]
    
    for y in range(8):
        for x in range(8):
            rect = pygame.Rect(x*TAILLE_CASE, y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            couleurs_case = couleurs[(x + y) % 2]
            pygame.draw.rect(screen, couleurs_case, rect)
            
            if case_selectionne == (x, y) :
                pygame.draw.rect(screen, (255, 255, 0), rect, 5)
            
            piece = plateau.plateau[y][x]
            image = get_image_for_piece(piece, images)
            if image :
                screen.blit(image, rect)
                
            

def game():
    
    pygame.init()
    screen = pygame.display.set_mode((TAILLE_PLATEAU, TAILLE_PLATEAU))
    pygame.display.set_caption("Echecs avec Pygame")
    clock = pygame.time.Clock()
    
    
    images = charger_images()
    case_selectionne = None
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    """Fonction principale gérant le cycle de la partie d'échecs."""
    plateau = Plateau()
    joueur_blanc = Joueur("Joueur Blanc", "blanc")
    joueur_noir = Joueur("Joueur Noir", "noir")
    joueur_actuel = joueur_blanc
    tour = 1
    
    
    
    afficher_plateau(screen, plateau, images, case_selectionne)
   

    print("Bienvenue dans le jeu d'échecs !")
    print(plateau)

    while True:
        print(f"\nTour {tour} - Au tour de {joueur_actuel}")


  
        selection, destination = demander_deplacement()
        x_depart, y_depart = selection
        x_arrivee, y_arrivee = destination

        piece_a_bouger = plateau.plateau[y_depart][x_depart]

        # Vérifier si une pièce a été sélectionnée et si elle appartient au joueur actuel
        if piece_a_bouger is None:
            print("Case de départ vide. Veuillez réessayer.")
            continue
        if piece_a_bouger.couleur != joueur_actuel.couleur:
            print("Ce n'est pas votre pièce. Veuillez réessayer.")
            continue

        # 2. Obtenir les déplacements possibles pour la pièce sélectionnée
        deplacements_possibles = piece_a_bouger.deplacement_possible(plateau)

        
        # 3. Vérifier si la destination choisie est parmi les déplacements possibles
        if destination not in deplacements_possibles:
            print("Mouvement illégal. Veuillez réessayer.")
            continue
        
        #3.1
            #copie des éléments
        copie_plateau = deepcopy(plateau)
        piece_simulee = deepcopy(piece_a_bouger)
            #simulation du mouvement dans la copie
        piece_simulee.position = destination
        copie_plateau.plateau[y_arrivee][x_arrivee] = piece_simulee
        copie_plateau.plateau[y_depart][x_depart] = None
        
            #vérifie si coup jouable ( donc pas de mise en echec )
        if joueur_actuel.est_en_echec(copie_plateau):
            print("Ce coup vous met en échec. Mouvement interdit")
            continue
                
        # 4. Effectuer le mouvement (mise à jour du plateau)
        piece_a_bouger.position = destination
        plateau.plateau[y_arrivee][x_arrivee] = piece_a_bouger
        plateau.plateau[y_depart][x_depart] = None
        
        #promotion
        if isinstance(piece_a_bouger, Pion) and (y_arrivee == 0 or y_arrivee == 7):
            while True :
                choix = input("Promotion ! Choisissez (d)ame, (t)our, (f)ou, (c)cavalier :").lower()
                if choix in "dtfc":
                    classes = {"d": Dame, 't': Tour, 'f': Fou, 'c': Cavalier}
                    plateau.plateau[y_arrivee][x_arrivee] = classes[choix](piece_a_bouger.couleur, (x_arrivee, y_arrivee))
                    break
                else :
                    print("Choix invalide.")

        print(plateau) # Afficher le plateau après le mouvement

        # 5. Vérifier les conditions de fin de partie (échec et mat, pat, etc.)
        # Cette partie nécessite une logique plus complexe à implémenter
        # Il faut vérifier si le roi adverse est en échec, et s'il a des mouvements légaux.

        # Pour l'instant, on se contente d'alterner les joueurs
        if joueur_actuel == joueur_blanc:
            joueur_actuel = joueur_noir
        else:
            joueur_actuel = joueur_blanc
            tour += 1 # Incrémenter le tour après le mouvement du joueur noir


        # Ajouter une condition de sortie temporaire pour éviter une boucle infinie lors des tests
        if tour > 100: # Par exemple, après 100 tours
            print("Nombre de tours maximum atteint (pour test).")
            break
        
        if joueur_actuel.est_en_echec(plateau):
            if not joueur_actuel.a_au_moins_un_coup_legal(plateau):
                print(f"Echec et mat ! {joueur_actuel} a perdu.")
                break
            else:
                print(f"{joueur_actuel} est en échec.")
        elif not joueur_actuel.a_au_moins_un_coup_legal(plateau):
            print("Pat ! Match nul.")
            break
        
    print("Fin de la partie.")
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    game()
    
    
    



