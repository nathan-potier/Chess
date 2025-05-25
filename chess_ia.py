import pygame
import sys
import time




# --- Constants ---
TAILLE_CASE = 80
LARGEUR = TAILLE_CASE * 8
HAUTEUR = TAILLE_CASE * 8

# --- Chess Engine Classes and Functions ---

class Plateau:
    def __init__(self):
        self.plateau = [[None for _ in range(8)] for _ in range(8)]
        #self.initialiser_plateau()
        self.roque_blanc_droit = True
        self.roque_blanc_gauche = True
        self.roque_noir_droit = True
        self.roque_noir_gauche = True
        self.en_passant = None
        self.historique = []
        self.coups_sans_capture = 0
        
        self.plateau[0][4] = Roi("noir", (4, 0))
        self.plateau[2][5] = Roi("blanc", (5, 2))
        self.plateau[1][4] = Dame("blanc", (4, 1))  # Dame blanche pour mettre en échec et mat




    def initialiser_plateau(self):
        ordre_piece = [Tour, Cavalier, Fou, Dame, Roi, Fou, Cavalier, Tour]
        for i in range(8):
            self.plateau[1][i] = Pion("noir", (i, 1))
            self.plateau[6][i] = Pion("blanc", (i, 6))
            self.plateau[0][i] = ordre_piece[i]("noir", (i, 0))
            self.plateau[7][i] = ordre_piece[i]("blanc", (i, 7))

    def case_est_vide(self, position):
        x, y = position
        return self.plateau[y][x] is None

    def case_occupe_par_adversaire(self, position, couleur):
        x, y = position
        piece = self.plateau[y][x]
        return piece is not None and piece.couleur != couleur

    def deplacer_piece(self, pos_depart, pos_arrivee, promotion=None):
        x0, y0 = pos_depart
        x1, y1 = pos_arrivee
        piece = self.plateau[y0][x0]

        # Sauvegarder l'état actuel plus complètement
        coup = {
            'pos_depart': pos_depart,
            'pos_arrivee': pos_arrivee,
            'piece_deplacee': piece,
            'piece_capturee': self.plateau[y1][x1],
            'roque_blanc_droit': self.roque_blanc_droit,
            'roque_blanc_gauche': self.roque_blanc_gauche,
            'roque_noir_droit': self.roque_noir_droit,
            'roque_noir_gauche': self.roque_noir_gauche,
            'en_passant': self.en_passant,
            'coups_sans_capture': self.coups_sans_capture,
            'roi_blanc_deplace': any(isinstance(p, Roi) and p.couleur == "blanc" and p.position != (4,7) for row in self.plateau for p in row if p),
            'roi_noir_deplace': any(isinstance(p, Roi) and p.couleur == "noir" and p.position != (4,0) for row in self.plateau for p in row if p),
            'tour_blanc_droite_deplacee': any(isinstance(p, Tour) and p.couleur == "blanc" and p.position != (7,7) for row in self.plateau for p in row if p),
            'tour_blanc_gauche_deplacee': any(isinstance(p, Tour) and p.couleur == "blanc" and p.position != (0,7) for row in self.plateau for p in row if p),
            'tour_noir_droite_deplacee': any(isinstance(p, Tour) and p.couleur == "noir" and p.position != (7,0) for row in self.plateau for p in row if p),
            'tour_noir_gauche_deplacee': any(isinstance(p, Tour) and p.couleur == "noir" and p.position != (0,0) for row in self.plateau for p in row if p),
        }
        self.historique.append(coup)

        # Gestion du compteur de coups sans capture/promotion
        if isinstance(piece, Pion) or not self.case_est_vide(pos_arrivee):
            self.coups_sans_capture = 0
        else:
            self.coups_sans_capture += 1

        # Roque
        if isinstance(piece, Roi):
            if piece.couleur == "blanc" and y0 == 7:
                if (x0, y0) == (4, 7) and (x1, y1) == (6, 7):  # Petit roque blanc
                    self.plateau[7][7], self.plateau[7][5] = None, self.plateau[7][7]
                    self.plateau[7][5].position = (5, 7)
                elif (x0, y0) == (4, 7) and (x1, y1) == (2, 7):  # Grand roque blanc
                    self.plateau[7][0], self.plateau[7][3] = None, self.plateau[7][0]
                    self.plateau[7][3].position = (3, 7)
            elif piece.couleur == "noir" and y0 == 0:
                if (x0, y0) == (4, 0) and (x1, y1) == (6, 0):  # Petit roque noir
                    self.plateau[0][7], self.plateau[0][5] = None, self.plateau[0][7]
                    self.plateau[0][5].position = (5, 0)
                elif (x0, y0) == (4, 0) and (x1, y1) == (2, 0):  # Grand roque noir
                    self.plateau[0][0], self.plateau[0][3] = None, self.plateau[0][0]
                    self.plateau[0][3].position = (3, 0)

        # Prise en passant
        if isinstance(piece, Pion):
            if (x1, y1) == self.en_passant:
                direction = -1 if piece.couleur == "blanc" else 1
                self.plateau[y1 - direction][x1] = None

        # Déplacement normal
        self.plateau[y1][x1] = piece
        self.plateau[y0][x0] = None
        piece.position = (x1, y1)

        # Promotion
        if isinstance(piece, Pion):
            if (piece.couleur == "blanc" and y1 == 0) or (piece.couleur == "noir" and y1 == 7):
                if promotion is None:
                    promotion = Dame  # Par défaut on promeut en Dame
                self.plateau[y1][x1] = promotion(piece.couleur, (x1, y1))

        # Mise à jour des droits au roque
        if isinstance(piece, Roi):
            if piece.couleur == "blanc":
                self.roque_blanc_droit = False
                self.roque_blanc_gauche = False
            else:
                self.roque_noir_droit = False
                self.roque_noir_gauche = False

        if isinstance(piece, Tour):
            if piece.couleur == "blanc":
                if (x0, y0) == (7, 7):
                    self.roque_blanc_droit = False
                elif (x0, y0) == (0, 7):
                    self.roque_blanc_gauche = False
            else:
                if (x0, y0) == (7, 0):
                    self.roque_noir_droit = False
                elif (x0, y0) == (0, 0):
                    self.roque_noir_gauche = False

        # Mise à jour de la prise en passant
        self.en_passant = None
        if isinstance(piece, Pion):
            if abs(y1 - y0) == 2:
                self.en_passant = (x1, (y0 + y1) // 2)

    def annuler_dernier_coup(self):
        if not self.historique:
            return
        coup = self.historique.pop()
        x0, y0 = coup['pos_depart']
        x1, y1 = coup['pos_arrivee']
        
        # Restaurer les pièces
        self.plateau[y0][x0] = coup['piece_deplacee']
        self.plateau[y1][x1] = coup['piece_capturee']
        coup['piece_deplacee'].position = (x0, y0)
        
        # Restaurer tous les états
        self.roque_blanc_droit = coup['roque_blanc_droit']
        self.roque_blanc_gauche = coup['roque_blanc_gauche']
        self.roque_noir_droit = coup['roque_noir_droit']
        self.roque_noir_gauche = coup['roque_noir_gauche']
        self.en_passant = coup['en_passant']
        self.coups_sans_capture = coup['coups_sans_capture']
        
        # Si c'était un roque, il faut aussi restaurer la tour
        if isinstance(coup['piece_deplacee'], Roi) and abs(x1 - x0) == 2:
            if coup['piece_deplacee'].couleur == "blanc":
                if x1 == 6:  # Petit roque
                    self.plateau[7][5], self.plateau[7][7] = None, self.plateau[7][5]
                    if self.plateau[7][7]:
                        self.plateau[7][7].position = (7, 7)
                elif x1 == 2:  # Grand roque
                    self.plateau[7][3], self.plateau[7][0] = None, self.plateau[7][3]
                    if self.plateau[7][0]:
                        self.plateau[7][0].position = (0, 7)
            else:
                if x1 == 6:  # Petit roque
                    self.plateau[0][5], self.plateau[0][7] = None, self.plateau[0][5]
                    if self.plateau[0][7]:
                        self.plateau[0][7].position = (7, 0)
                elif x1 == 2:  # Grand roque
                    self.plateau[0][3], self.plateau[0][0] = None, self.plateau[0][3]
                    if self.plateau[0][0]:
                        self.plateau[0][0].position = (0, 0)

class Joueur:
    def __init__(self, nom, couleur):
        self.nom = nom
        self.couleur = couleur

    def est_en_echec(self, plateau):
        roi_pos = None
        for y in range(8):
            for x in range(8):
                piece = plateau.plateau[y][x]
                if isinstance(piece, Roi) and piece.couleur == self.couleur:
                    roi_pos = (x, y)
                    break
            if roi_pos:
                break
        if roi_pos is None:
            return False

        for y in range(8):
            for x in range(8):
                piece = plateau.plateau[y][x]
                if piece and piece.couleur != self.couleur:
                    if roi_pos in piece.deplacements_possibles(plateau):
                        return True
        return False

    def a_au_moins_un_coup_legal(self, plateau):
        for y in range(8):
            for x in range(8):
                piece = plateau.plateau[y][x]
                if piece and piece.couleur == self.couleur:
                    for move in piece.deplacements_possibles(plateau):
                        if coup_legal(plateau, piece, move, self):
                            return True
        return False

class Piece:
    def __init__(self, couleur, position):
        self.couleur = couleur
        self.position = position

    def __str__(self):
        return self.__class__.__name__[0] + ("B" if self.couleur == "blanc" else "N")

class Pion(Piece):
    def deplacements_possibles(self, plateau):
        x, y = self.position
        direction = -1 if self.couleur == "blanc" else 1
        deplacements = []

        # Avance d'une case
        if 0 <= y + direction < 8 and plateau.case_est_vide((x, y + direction)):
            deplacements.append((x, y + direction))

            # Avance de deux cases depuis la position initiale
            if ((self.couleur == "blanc" and y == 6) or (self.couleur == "noir" and y == 1)) and plateau.case_est_vide((x, y + 2 * direction)):
                deplacements.append((x, y + 2 * direction))

        # Prise diagonale
        for dx in [-1, 1]:
            nx = x + dx
            ny = y + direction
            if 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                # Prise en passant
                if plateau.en_passant == (nx, ny):
                    deplacements.append((nx, ny))

        return deplacements

class Tour(Piece):
    def deplacements_possibles(self, plateau):
        x, y = self.position
        deplacements = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)):
                    deplacements.append((nx, ny))
                elif plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return deplacements

class Cavalier(Piece):
    def deplacements_possibles(self, plateau):
        x, y = self.position
        deplacements = []
        mouvements = [(1, 2), (2, 1), (2, -1), (1, -2),
                      (-1, -2), (-2, -1), (-2, 1), (-1, 2)]

        for dx, dy in mouvements:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)) or plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
        return deplacements

class Fou(Piece):
    def deplacements_possibles(self, plateau):
        x, y = self.position
        deplacements = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)):
                    deplacements.append((nx, ny))
                elif plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return deplacements

class Dame(Piece):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1,1), (1,-1), (-1,1), (-1,-1)]

    def deplacements_possibles(self, plateau):
        x, y = self.position
        deplacements = []
        for dx, dy in self.directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)):
                    deplacements.append((nx, ny))
                elif plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return deplacements

class Roi(Piece):
    def deplacements_possibles(self, plateau):
        x, y = self.position
        deplacements = []
        mouvements = [(1, 0), (1, 1), (0, 1), (-1, 1),
                      (-1, 0), (-1, -1), (0, -1), (1, -1)]

        for dx, dy in mouvements:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)) or plateau.case_occupe_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))

        # Roque - version avec vérification d'échec
        if self.couleur == "blanc" and y == 7 and x == 4:
            if plateau.roque_blanc_droit and plateau.case_est_vide((5, 7)) and plateau.case_est_vide((6, 7)):
                # Vérifier si le roi n'est pas en échec et ne passe pas par une case attaquée
                if not cases_attaquees_par_adversaire(plateau, [(4, 7)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(5, 7)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(6, 7)], self.couleur):
                    deplacements.append((6, 7))
            if plateau.roque_blanc_gauche and plateau.case_est_vide((3, 7)) and plateau.case_est_vide((2, 7)) and plateau.case_est_vide((1, 7)):
                if not cases_attaquees_par_adversaire(plateau, [(4, 7)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(3, 7)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(2, 7)], self.couleur):
                    deplacements.append((2, 7))
        elif self.couleur == "noir" and y == 0 and x == 4:
            if plateau.roque_noir_droit and plateau.case_est_vide((5, 0)) and plateau.case_est_vide((6, 0)):
                if not cases_attaquees_par_adversaire(plateau, [(4, 0)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(5, 0)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(6, 0)], self.couleur):
                    deplacements.append((6, 0))
            if plateau.roque_noir_gauche and plateau.case_est_vide((3, 0)) and plateau.case_est_vide((2, 0)) and plateau.case_est_vide((1, 0)):
                if not cases_attaquees_par_adversaire(plateau, [(4, 0)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(3, 0)], self.couleur) and \
                   not cases_attaquees_par_adversaire(plateau, [(2, 0)], self.couleur):
                    deplacements.append((2, 0))

        return deplacements


def cases_attaquees_par_adversaire(plateau, cases, couleur):
    adversaire = "noir" if couleur == "blanc" else "blanc"
    cases_a_verifier = set(cases)

    for y in range(8):
        for x in range(8):
            piece = plateau.plateau[y][x]
            if piece and piece.couleur == adversaire:
                # Gestion spéciale pour le roi (pour éviter la récursion)
                if isinstance(piece, Roi):
                    for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 8 and 0 <= ny < 8 and (nx, ny) in cases_a_verifier:
                            return True
                else:
                    for move in piece.deplacements_possibles(plateau):
                        if move in cases_a_verifier:
                            return True
    return False

def charger_images():
    types = ['p', 'k', 'n', 'b', 'q', 'r']
    couleurs = ['w', 'b']
    images = {}

    for t in types:
        for c in couleurs:
            chemin = f"assets/{c}{t}.png"
            try:
                image = pygame.image.load(chemin)
                image = pygame.transform.scale(image, (TAILLE_CASE, TAILLE_CASE))
                images[f"{c}{t}"] = image
            except pygame.error as e:
                raise FileNotFoundError(f"Erreur de chargement pour {chemin}: {e}")
    return images

def get_image_for_piece(piece, images):
    if piece is None:
        return None
    mapping = {
        'Pion': 'p',
        'Roi': 'k',
        'Cavalier': 'n',
        'Fou': 'b',
        'Dame': 'q',
        'Tour': 'r'
    }
    c = 'w' if piece.couleur == 'blanc' else 'b'
    t = mapping[piece.__class__.__name__]
    return images[f"{c}{t}"]

def dessiner_plateau(fenetre, plateau, images, selection, message, joueur_courant):
    couleurs = [(240, 217, 181), (181, 136, 99)]
    fenetre.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 28)

    # Dessiner les cases
    for y in range(8):
        for x in range(8):
            couleur_case = couleurs[(x + y) % 2]
            rect = pygame.Rect(x * TAILLE_CASE, y * TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            pygame.draw.rect(fenetre, couleur_case, rect)

            # Mettre en évidence la case sélectionnée
            if selection == (x, y):
                pygame.draw.rect(fenetre, (0, 255, 0), rect, 3)

            # Dessiner les pièces
            piece = plateau.plateau[y][x]
            image = get_image_for_piece(piece, images)
            if image:
                fenetre.blit(image, rect)

    # Afficher le joueur courant
    text_joueur = font.render(f"Tour du joueur: {joueur_courant.nom} ({joueur_courant.couleur})", True, (255, 255, 255))
    fenetre.blit(text_joueur, (10, HAUTEUR + 5))

    # Afficher les messages
    if message:
        text_msg = font.render(message, True, (255, 0, 0))
        fenetre.blit(text_msg, (10, HAUTEUR + 30))

    # Bouton pour le meilleur coup
    button_rect = pygame.Rect(LARGEUR - 150, HAUTEUR + 10, 140, 30)
    pygame.draw.rect(fenetre, (0, 200, 0), button_rect)
    button_text = font.render("Meilleur Coup", True, (255, 255, 255))
    fenetre.blit(button_text, (LARGEUR - 140, HAUTEUR + 15))

    return button_rect

def coordonnees_souris_vers_case(pos):
    x, y = pos
    return x // TAILLE_CASE, y // TAILLE_CASE


def coup_legal(plateau, piece, destination, joueur):
    if destination not in piece.deplacements_possibles(plateau):
        return False

    # Sauvegarde de l'état
    backup = {
        'roque': (plateau.roque_blanc_droit, plateau.roque_blanc_gauche,
                 plateau.roque_noir_droit, plateau.roque_noir_gauche),
        'en_passant': plateau.en_passant,
        'historique': plateau.historique.copy()
    }

    # Simulation du coup
    piece_capturee = plateau.plateau[destination[1]][destination[0]]
    plateau.deplacer_piece(piece.position, destination)
    en_echec = joueur.est_en_echec(plateau)

    # Annulation du coup
    plateau.annuler_dernier_coup()

    # Restauration de l'état
    plateau.roque_blanc_droit, plateau.roque_blanc_gauche = backup['roque'][0], backup['roque'][1]
    plateau.roque_noir_droit, plateau.roque_noir_gauche = backup['roque'][2], backup['roque'][3]
    plateau.en_passant = backup['en_passant']
    plateau.historique = backup['historique']
    plateau.plateau[destination[1]][destination[0]] = piece_capturee
    plateau.plateau[piece.position[1]][piece.position[0]] = piece

    return not en_echec

def evaluer_plateau(plateau):
    score = 0

    # Valeurs des pièces
    valeurs_pieces = {
        'Pion': 100,
        'Cavalier': 320,
        'Fou': 330,
        'Tour': 500,
        'Dame': 900,
        'Roi': 20000
    }

    # Tables de position pour chaque pièce
    tables_position = {
        'Pion': [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0]
        ],
        'Cavalier': [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ],
        'Fou': [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ],
        'Tour': [
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ],
        'Dame': [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ],
        'Roi_milieu': [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [ 20, 20,  0,  0,  0,  0, 20, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20]
        ],
        'Roi_fin': [
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-30,-30,-30,-30,-30,-30,-50]
        ]
    }

    # Compter le nombre de pièces pour déterminer si on est en milieu ou fin de partie
    nb_pieces = sum(1 for ligne in plateau.plateau for piece in ligne if piece is not None)
    fin_de_partie = nb_pieces <= 10

    for y in range(8):
        for x in range(8):
            piece = plateau.plateau[y][x]
            if piece:
                type_piece = piece.__class__.__name__
                valeur = valeurs_pieces.get(type_piece, 0)

                # Ajouter la valeur positionnelle
                if type_piece == 'Roi':
                    table = tables_position['Roi_fin'] if fin_de_partie else tables_position['Roi_milieu']
                else:
                    table = tables_position.get(type_piece, [[0]*8 for _ in range(8)])

                # Inverser la table pour les noirs
                if piece.couleur == 'noir':
                    y_table = 7 - y
                else:
                    y_table = y

                valeur += table[y_table][x]

                # Ajouter ou soustraire selon la couleur
                if piece.couleur == 'blanc':
                    score += valeur
                else:
                    score -= valeur

    # Bonus pour le contrôle du centre
    cases_centre = [(3, 3), (3, 4), (4, 3), (4, 4)]
    for x, y in cases_centre:
        piece = plateau.plateau[y][x]
        if piece and piece.couleur == 'blanc':
            score += 10
        elif piece and piece.couleur == 'noir':
            score -= 10

    # Bonus pour la mobilité
    blanc_mobilite = sum(len(p.deplacements_possibles(plateau)) for ligne in plateau.plateau for p in ligne if p and p.couleur == 'blanc')
    noir_mobilite = sum(len(p.deplacements_possibles(plateau)) for ligne in plateau.plateau for p in ligne if p and p.couleur == 'noir')
    score += (blanc_mobilite - noir_mobilite) * 0.1

    return score

def generer_coups_legaux(plateau, joueur):
    coups = []
    for y in range(8):
        for x in range(8):
            piece = plateau.plateau[y][x]
            if piece and piece.couleur == joueur.couleur:
                for dest in piece.deplacements_possibles(plateau):
                    if coup_legal(plateau, piece, dest, joueur):
                        coups.append(((x, y), dest))
    return coups

def partie_terminee(plateau, joueur):
    # Vérifie d'abord si le joueur a des coups légaux
    a_coups_legaux = False
    for y in range(8):
        for x in range(8):
            piece = plateau.plateau[y][x]
            if piece and piece.couleur == joueur.couleur:
                for dest in piece.deplacements_possibles(plateau):
                    if coup_legal(plateau, piece, dest, joueur):
                        a_coups_legaux = True
                        break
                if a_coups_legaux:
                    break
            if a_coups_legaux:
                break
    
    if not a_coups_legaux:
        if joueur.est_en_echec(plateau):
            return "échec et mat"
        else:
            return "pat"
    
    # Vérifie la règle des 50 coups
    if plateau.coups_sans_capture >= 50:
        return "50 coups sans capture"
    
    # Vérifie s'il y a suffisamment de matériel pour mater
    pieces_restantes = []
    for ligne in plateau.plateau:
        for piece in ligne:
            if piece:
                pieces_restantes.append(piece.__class__.__name__)
    
    # Cas où il ne reste que les rois
    if all(p in ['Roi', 'Roi'] for p in pieces_restantes):
        return "matériel insuffisant"
    
    # Cas où il ne reste qu'un roi et un fou ou un cavalier contre un roi
    if (len(pieces_restantes) == 3 and 
        sorted(pieces_restantes) in [['Fou', 'Roi', 'Roi'], ['Cavalier', 'Roi', 'Roi']]):
        return "matériel insuffisant"
    
    return None

def minimax(plateau, joueurs, profondeur, alpha, beta, maximisant):
    joueur_actuel = joueurs[0] if maximisant else joueurs[1]
    resultat = partie_terminee(plateau, joueur_actuel)
    if resultat is not None:
        if resultat == "échec et mat":
            return -100000 if maximisant else 100000
        elif resultat == "pat":
            return 0
        else:
            return evaluer_plateau(plateau)

    if profondeur == 0:
        return evaluer_plateau(plateau)

    if maximisant:
        max_eval = float('-inf')
        for coup in generer_coups_legaux(plateau, joueurs[0]):
            plateau.deplacer_piece(coup[0], coup[1])
            eval = minimax(plateau, joueurs, profondeur - 1, alpha, beta, False)
            plateau.annuler_dernier_coup()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for coup in generer_coups_legaux(plateau, joueurs[1]):
            plateau.deplacer_piece(coup[0], coup[1])
            eval = minimax(plateau, joueurs, profondeur - 1, alpha, beta, True)
            plateau.annuler_dernier_coup()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def meilleur_coup(plateau, joueurs, profondeur):
    meilleur_score = float('-inf')
    meilleur_coup_trouve = None
    coups_legaux = generer_coups_legaux(plateau, joueurs[0])

    # Trier les coups pour améliorer l'élagage alpha-bêta
    coups_legaux.sort(key=lambda coup: -evaluation_rapide(plateau, coup, joueurs[0]))

    for coup in coups_legaux:
        plateau.deplacer_piece(coup[0], coup[1])
        score = minimax(plateau, joueurs, profondeur - 1, float('-inf'), float('inf'), False)
        plateau.annuler_dernier_coup()

        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup_trouve = coup

    return meilleur_coup_trouve

def evaluation_rapide(plateau, coup, joueur):
    # Une évaluation rapide pour trier les coups
    x0, y0 = coup[0]
    x1, y1 = coup[1]
    piece = plateau.plateau[y0][x0]
    cible = plateau.plateau[y1][x1]

    score = 0

    # Valeur de la pièce capturée
    if cible:
        valeurs = {'Pion': 100, 'Cavalier': 320, 'Fou': 330, 'Tour': 500, 'Dame': 900, 'Roi': 20000}
        score += valeurs.get(cible.__class__.__name__, 0)

    # Valeur de la pièce qui capture (pour éviter de sacrifier des pièces plus fortes)
    valeurs = {'Pion': 100, 'Cavalier': 320, 'Fou': 330, 'Tour': 500, 'Dame': 900, 'Roi': 20000}
    score -= valeurs.get(piece.__class__.__name__, 0) * 0.1

    # Bonus pour les captures avec des pièces moins précieuses
    if cible and valeurs.get(cible.__class__.__name__, 0) > valeurs.get(piece.__class__.__name__, 0):
        score += 50

    # Bonus pour les échecs
    plateau.deplacer_piece(coup[0], coup[1])
    if joueur.est_en_echec(plateau):
        score += 50
    plateau.annuler_dernier_coup()

    return score




def main():
    pygame.init()
    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR + 60))
    pygame.display.set_caption("Jeu d'échecs")
    images = charger_images()
    plateau = Plateau()
    joueurs = [Joueur("Blanc", "blanc"), Joueur("Noir", "noir")]
    joueur_courant = 0
    selection = None
    clock = pygame.time.Clock()
    message = ""
    en_promotion = None
    running = True
    partie_finie = False

    def get_coups_legaux(joueur, plateau):
        """Retourne tous les coups légaux pour un joueur"""
        coups = []
        for y in range(8):
            for x in range(8):
                piece = plateau.plateau[y][x]
                if piece and piece.couleur == joueur.couleur:
                    for dest_y in range(8):
                        for dest_x in range(8):
                            if coup_legal(plateau, piece, (dest_x, dest_y), joueur):
                                coups.append(((x, y), (dest_x, dest_y)))
        return coups

    def verifier_fin_partie():
        """Vérifie si la partie est terminée et met à jour l'état"""
        nonlocal message, partie_finie, joueur_courant
        adversaire = joueurs[1 - joueur_courant]  # Le joueur qui vient de jouer
        
        if adversaire.est_en_echec(plateau):
            coups = get_coups_legaux(adversaire, plateau)
            if not coups:
                message = f"Échec et mat ! {joueurs[joueur_courant].nom} gagne."
                partie_finie = True
            else:
                message = "Échec !"
        else:
            coups = get_coups_legaux(adversaire, plateau)
            if not coups:
                message = "Pat ! Partie nulle."
                partie_finie = True
            else:
                message = ""

    def effectuer_deplacement(depart, arrivee, promotion=None):
        """Gère un déplacement et ses conséquences"""
        nonlocal joueur_courant, en_promotion
        plateau.deplacer_piece(depart, arrivee, promotion)
        verifier_fin_partie()
        joueur_courant = 1 - joueur_courant  # Changement de joueur
        

    def gerer_promotion(x):
        """Gère le choix de pièce pour la promotion"""
        nonlocal en_promotion
        if 0 <= x < 4:
            choix = [Dame, Tour, Fou, Cavalier][x]
            effectuer_deplacement(en_promotion[0], en_promotion[1], choix)
            en_promotion = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not partie_finie:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    case = coordonnees_souris_vers_case(event.pos)
                    x, y = case

                    # Bouton "Meilleur coup"
                    if y >= 8:
                        button_rect = pygame.Rect(LARGEUR - 150, HAUTEUR + 10, 140, 30)
                        if button_rect.collidepoint(event.pos):
                            meilleur_c = meilleur_coup(plateau, joueurs, 3)
                            if meilleur_c:
                                effectuer_deplacement(meilleur_c[0], meilleur_c[1])
                        continue

                    # Gestion de la promotion
                    if en_promotion is not None:
                        gerer_promotion(x)
                        continue

                    # Sélection/déplacement normal
                    piece = plateau.plateau[y][x] if y < 8 else None
                    
                    if selection is None:
                        if piece and piece.couleur == joueurs[joueur_courant].couleur:
                            selection = case
                            message = ""
                    else:
                        piece_sel = plateau.plateau[selection[1]][selection[0]]
                        if piece_sel and coup_legal(plateau, piece_sel, case, joueurs[joueur_courant]):
                            if isinstance(piece_sel, Pion) and ((piece_sel.couleur == "blanc" and case[1] == 0) or 
                                                              (piece_sel.couleur == "noir" and case[1] == 7)):
                                en_promotion = (selection, case)
                            else:
                                effectuer_deplacement(selection, case)
                        else:
                            message = "Coup illégal"
                        selection = None

        # Affichage
        dessiner_plateau(fenetre, plateau, images, selection, message, joueurs[joueur_courant])
        
        # Menu de promotion
        if en_promotion is not None:
            couleur = joueurs[joueur_courant].couleur
            for i, piece_type in enumerate([Dame, Tour, Fou, Cavalier]):
                rect = pygame.Rect(i * TAILLE_CASE, HAUTEUR, TAILLE_CASE, TAILLE_CASE)
                pygame.draw.rect(fenetre, (200, 200, 200), rect)
                piece = piece_type(couleur, (0, 0))
                fenetre.blit(get_image_for_piece(piece, images), rect)

        # Écran de fin
        if partie_finie:
            font = pygame.font.SysFont(None, 48)
            text = font.render(message, True, (255, 0, 0))
            text_rect = text.get_rect(center=(LARGEUR//2, HAUTEUR//2))
            pygame.draw.rect(fenetre, (255, 255, 255), (LARGEUR//2 - 200, HAUTEUR//2 - 50, 400, 100))
            fenetre.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
import unittest

class TestEchecs(unittest.TestCase):
    def setUp(self):
        self.plateau = Plateau()
        self.joueur_blanc = Joueur("Blanc", "blanc")
        self.joueur_noir = Joueur("Noir", "noir")

    def test_roque_avec_echec(self):
        # Configurer le plateau pour un test de roque avec échec
        self.plateau.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.plateau.plateau[0][4] = Roi("noir", (4, 0))
        self.plateau.plateau[0][7] = Tour("noir", (7, 0))
        self.plateau.plateau[7][4] = Roi("blanc", (4, 7))
        self.plateau.plateau[7][7] = Tour("blanc", (7, 7))
        self.plateau.plateau[3][5] = Tour("blanc", (5, 3))  # Tour blanche pour mettre en échec

        # Vérifier que le roque n'est pas possible car le roi passe par une case en échec
        roi_noir = self.plateau.plateau[0][4]
        deplacements = roi_noir.deplacements_possibles(self.plateau)
        self.assertNotIn((6, 0), deplacements)

    def test_echec_et_mat(self):
        # Configurer le plateau pour un échec et mat
        self.plateau.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.plateau.plateau[0][4] = Roi("noir", (4, 0))
        self.plateau.plateau[2][5] = Roi("blanc", (5, 2))
        self.plateau.plateau[1][4] = Dame("blanc", (4, 1))  # Dame blanche pour mettre en échec et mat

        # Vérifier que le roi noir est en échec et mat
        resultat = partie_terminee(self.plateau, self.joueur_noir)
        print(resultat)
        self.assertEqual(resultat, "échec et mat")

    def test_pat(self):
        # Configurer le plateau pour un pat
        self.plateau.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.plateau.plateau[0][4] = Roi("noir", (4, 0))
        self.plateau.plateau[7][4] = Roi("blanc", (4, 7))
        self.plateau.plateau[6][5] = Tour("blanc", (5, 6))  # Dame blanche pour mettre en pat
        self.plateau.plateau[6][3] = Tour("blanc", (3, 6))
        self.plateau.plateau[1][0] = Tour("blanc", (0, 1))

        # Vérifier que le roi noir est en pat
        resultat = partie_terminee(self.plateau, self.joueur_noir)
        self.assertEqual(resultat, "pat")

    def test_coup_legal_avec_echec(self):
        # Configurer le plateau pour un coup légal avec échec
        self.plateau.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.plateau.plateau[0][4] = Roi("noir", (4, 0))
        self.plateau.plateau[7][4] = Roi("blanc", (4, 7))
        self.plateau.plateau[0][3] = Dame("blanc", (3, 0))  # Dame blanche pour mettre en échec
        self.plateau.plateau[1][4] = Pion("noir", (4, 1))

        # Vérifier que le pion noir ne peut pas bouger car le roi est en échec
        pion_noir = self.plateau.plateau[1][4]
        self.assertFalse(coup_legal(self.plateau, pion_noir, (4, 2), self.joueur_noir))

if __name__ == "__main__":
    #unittest.main()
    main()