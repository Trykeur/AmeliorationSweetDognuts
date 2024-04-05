import math
import numpy as np

# ---------------------------------------- TOOLS ----------------------------------------
def truncate(f, n):
    assert f != 0 or n != 0, "truncate les parametres sont égales à 0" 
    return np.floor(f * 10 ** n) / 10 ** n

# ---------------------------------------- SIMILARITE ----------------------------------------
def Sim_Jacc(V1,V2):

    """
    Sim_Jacc(V1, V2)= |V1 ∩ V2| / |V1 ∪ V2|
                    = A / B
    """
    assert len(V1) == len(V2), "Sim_Jacc la taille des 2 vecteurs est différentes" 

    A,B = 0,0
    for i in range(len(V1)):
        if (V1[i]*V2[i] !=0):
            A += 1
        if (V1[i]+V2[i] !=0): 
            B += 1
    assert B != 0, "Sim_Jacc le dénominateur est égale a 0"

    return A/B

def Sim_Cos(V1,V2):
    """
    SimCos(V1, V2)  = (V1.V2) / ( |V1| ∗ |V2| )
                    = A / (B x C)
    """

    assert len(V1) == len(V2), "Sim_Cos la taille des 2 vecteurs est différentes" 

    A,B,C = 0,0,0
    for i in range(len(V1)):
        A += V1[i]*V2[i]
        B += V1[i]**2
        C += V2[i]**2

    assert B != 0 or C != 0, "Sim_Cos les variables B et C sont égales à 0"

    return A/(math.sqrt(B)*math.sqrt(C))

def Sim_euclidienne(V1,V2):
    """
    Sim_Jacc(V1, V2)    =   1 / SQRT( (V1_1 − V1_1)² + (V1_2 − V2_2)² + ... + (V1_n − V2_n)²)
    """
    A = math.sqrt(sum([(V1[i]-V2[i])**2 for i in range(len(V1))]))
    assert A != 0, "Sim_euclidienne le dénominateur est égale a 0"
    return 1/A

# ---------------------------------------- Functions recommandation ----------------------------------------
def enjoyIndex(note):
    assert note > 0, "La note doit être strictement positive"  
    return (note ** 2.7) / (10 ** 2.7)

def distance(x1, y1, x2, y2):
    xd = x2 - x1
    yd = y2 - y1
    
    # assert xd != 0 or yd != 0, "Les points sont identiques donc la distance est nulle"
    
    return math.sqrt((xd ** 2) + (yd ** 2))


# ---------------------------------------- TEST ----------------------------------------

"""VECTEUR_MOVIE = [1,1,0,1,1,1,1,1,0]
VECTEUR_USER = [1,1,1,0,1,2,0,0,2]

assert truncate(Sim_Jacc(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.444
assert truncate(Sim_Cos(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.545
assert truncate(Sim_euclidienne(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.333"""


# Fonction pour gérer les erreurs d'assertion
def test_error_handling(func, *args):
    try:
        result = func(*args)
        print("Résultat:", result)
    except AssertionError as e:
        print("Erreur AssertionError:", e)
    except ValueError as e:
        print("Erreur ValueError:", e)

# ---------------------------------------- SIMILARITE ----------------------------------------

print("Test qui vont fonctionner : \n")

# Test de Sim_Jacc
print("\nTest de Sim_Jacc:")
V1 = [1, 0, 1, 0]
V2 = [0, 1, 1, 0]
test_error_handling(Sim_Jacc, V1, V2)

# Test de Sim_Cos
print("\nTest de Sim_Cos:")
V1 = [1, 2]
V2 = [3, 4]
test_error_handling(Sim_Cos, V1, V2)

# Test de Sim_euclidienne
print("\nTest de Sim_euclidienne:")
V1 = [1, 2, 3]
V2 = [4, 5, 6]
test_error_handling(Sim_euclidienne, V1, V2)

# ---------------------------------------- Functions recommandation ----------------------------------------

# Test de enjoyIndex
print("\nTest de enjoyIndex:")
test_error_handling(enjoyIndex, 5)  # Note positive

# Test de distance
print("\nTest de distance:")
test_error_handling(distance, 1, 1, 3, 3)  # Points distincts

print("\nTest qui vont provoquer une erreur : \n")

# Test de Sim_Jacc
print("\nTest de Sim_Jacc:")
V1 = [1, 0, 1, 0]
V2 = [0, 1, 1]
test_error_handling(Sim_Jacc, V1, V2)

# Test de Sim_Cos
print("\nTest de Sim_Cos:")
V1 = [1, 2]
V2 = [3, 4, 5]
test_error_handling(Sim_Cos, V1, V2)

# Test de Sim_euclidienne
print("\nTest de Sim_euclidienne:")
V1 = [1, 2, 3]
V2 = [1, 2, 3]
test_error_handling(Sim_euclidienne, V1, V2)

# ---------------------------------------- Functions recommandation ----------------------------------------

# Test de enjoyIndex
print("\nTest de enjoyIndex:")
test_error_handling(enjoyIndex, -5)  # Note négative

# Test de distance
print("\nTest de distance:")
test_error_handling(distance, 0, 0, 0, 0)  # Points identiques
