class Plateau:
    def __init__(self):
        self.plateau = [[None for _ in range(8)] for _ in range(8)]
        self.initialiser_plateau()

    def initialiser_plateau(self):
        """Initialise les pièces sur l'échiquier."""
        # Placement des pions
        for i in range(8):
            self.plateau[1][i] = Pion("Blanc", (1, i))
            self.plateau[6][i] = Pion("Noir", (6, i))

        # Placement des autres pièces
        pieces = [Tour, Cavalier, Fou, Dame, Roi, Fou, Cavalier, Tour]
        for i, piece in enumerate(pieces):
            self.plateau[0][i] = piece("Blanc", (0, i))
            self.plateau[7][i] = piece("Noir", (7, i))

    def afficher_plateau(self):
        """Affiche le plateau sous forme de grille."""
        for row in self.plateau:
            print(" | ".join(str(piece) if piece else "." for piece in row))
            print("-" * 40)

    def case_est_vide(self, position: tuple):
        """Vérifie si une case est vide."""
        x, y = position
        return self.plateau[y][x] is None

    def case_occupee_par_adversaire(self, position: tuple, couleur: str):
        """Vérifie si la case est occupée par une pièce adverse."""
        x, y = position
        piece = self.plateau[x][y]
        return piece is not None and piece.couleur != couleur

    def deplacer_piece(self, piece, nouvelle_position):
        """Déplace une pièce si le déplacement est valide."""
        if nouvelle_position in piece.deplacement_possible(self):
            x, y = piece.position
            self.plateau[x][y] = None  # Retirer la pièce de sa position actuelle
            piece.position = nouvelle_position
            nx, ny = nouvelle_position
            self.plateau[nx][ny] = piece  # Déplacer la pièce
            return True
        return False


class Joueur:
    def __init__(self, nom, couleur):
        self.nom = nom
        self.couleur = couleur

    def __str__(self):
        return f"{self.nom} ({self.couleur})"


class Piece:
    def __init__(self, couleur, position):
        self.couleur = couleur
        self.position = position

    def __str__(self):
        return self.__class__.__name__[0] + ("B" if self.couleur == "Blanc" else "N")

    def deplacement_possible(self, plateau: Plateau):
        """Renvoie la liste des déplacements possibles (à implémenter dans chaque sous-classe)."""
        return []


class Pion(Piece):
    def deplacement_possible(self, plateau: Plateau):
        x, y = self.position
        deplacements = []
        direction = -1 if self.couleur == "Blanc" else 1  # Blanc avance vers le haut, Noir vers le bas

        # Avancer d'une case
        nouvelle_position = (x + direction, y)
        if 0 <= nouvelle_position[0] < 8 and plateau.case_est_vide(nouvelle_position):
            deplacements.append(nouvelle_position)

        # Avancer de deux cases au premier coup
        nouvelle_position = (x ,  y +  2 * direction)
        if (self.couleur == "Blanc" and y == 6) or (self.couleur == "Noir" and y == 1):
            if plateau.case_est_vide(nouvelle_position):
                deplacements.append(nouvelle_position)

        # Captures diagonales
        for dx in [-1, 1]:
            nouvelle_position = (x + dx, y + direction)
            if 0 <= nouvelle_position[0] < 8 and 0 <= nouvelle_position[1] < 8:
                if plateau.case_occupee_par_adversaire(nouvelle_position, self.couleur):
                    deplacements.append(nouvelle_position)

        return deplacements



class Tour(Piece):
    def deplacement_possible(self, plateau: Plateau):
        x, y = self.position
        deplacements = []

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)):
                    deplacements.append((nx, ny))
                elif plateau.case_occupee_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy

        return deplacements


class Cavalier(Piece):
    def deplacement_possible(self, plateau: Plateau):
        x, y = self.position
        deplacements = []

        mouvements = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for dx, dy in mouvements:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and (plateau.case_est_vide((nx, ny)) or plateau.case_occupee_par_adversaire((nx, ny), self.couleur)):
                deplacements.append((nx, ny))

        return deplacements


class Fou(Piece):
    def deplacement_possible(self, plateau: Plateau):
        x, y = self.position
        deplacements = []

        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if plateau.case_est_vide((nx, ny)):
                    deplacements.append((nx, ny))
                elif plateau.case_occupee_par_adversaire((nx, ny), self.couleur):
                    deplacements.append((nx, ny))
                    break
                else:
                    break
                nx, ny = nx + dx, ny + dy

        return deplacements


class Dame(Piece):
    def deplacement_possible(self, plateau: Plateau):
        return Tour(self.couleur, self.position).deplacement_possible(plateau) + Fou(self.couleur, self.position).deplacement_possible(plateau)


class Roi(Piece):
    def deplacement_possible(self, plateau: Plateau):
        x, y = self.position
        deplacements = []

        for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1), (0, 1),
                       (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and (plateau.case_est_vide((nx, ny)) or plateau.case_occupee_par_adversaire((nx, ny), self.couleur)):
                deplacements.append((nx, ny))

        return deplacements


class Game:
    def __init__(self, joueur1, joueur2):
        self.plateau = Plateau()
        self.joueurs = [joueur1, joueur2]
        self.tour_actuel = 0  # 0 pour le joueur1, 1 pour le joueur2

    def jouer(self):
        """Boucle de jeu simple."""
        while True:
            self.plateau.afficher_plateau()
            joueur = self.joueurs[self.tour_actuel]
            print(f"Tour de {joueur.nom} ({joueur.couleur})")

            x, y = map(int, input("Entrez les coordonnées de la pièce à déplacer (x y) : ").split())
            piece = self.plateau.plateau[x][y]

            if piece and piece.couleur == joueur.couleur:
                print(f"Déplacements possibles : {piece.deplacement_possible(self.plateau)}")
                nx, ny = map(int, input("Entrez la nouvelle position (x y) : ").split())

                if self.plateau.deplacer_piece(piece, (nx, ny)):
                    self.tour_actuel = 1 - self.tour_actuel  # Changer de joueur
                else:
                    print("Déplacement invalide.")
            else:
                print("Sélection invalide.")


# Lancer une partie
joueur1 = Joueur("Alice", "Blanc")
joueur2 = Joueur("Bob", "Noir")
jeu = Game(joueur1, joueur2)
jeu.jouer()
