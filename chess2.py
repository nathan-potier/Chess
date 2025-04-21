"""
Joueur
Plateau
Game


Pieces:
    Pion
    Cavalier
    Tour
    Fou
    Roi
    Dame
"""


class Plateau:
    
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        
    def initialisation_plateau(self):
        pass
    
    def case_vide(self, position):
        pass
    
    def afficher_plat(self):
        pass
    
    def __repr__(self):
        pass
    
    
class Pieces:
    def __init__(self, couleur, position):
        pass
    def __repr__(self):
        pass
    
    def move_possible(self):
        pass
    
    