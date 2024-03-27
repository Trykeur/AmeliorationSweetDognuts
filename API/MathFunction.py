import math
import numpy as np

# ---------------------------------------- TOOLS ----------------------------------------
def truncate(f, n):
    return np.floor(f * 10 ** n) / 10 ** n

# ---------------------------------------- SIMILARITE ----------------------------------------
def Sim_Jacc(V1,V2):
    """
    Sim_Jacc(V1, V2)= |V1 ∩ V2| / |V1 ∪ V2|
                    = A / B
    """
    A,B = 0,0
    for i in range(len(V1)):
        if (V1[i]*V2[i] !=0): A += 1
        if (V1[i]+V2[i] !=0): B += 1
    return A/B

def Sim_Cos(V1,V2):
    """
    SimCos(V1, V2)  = (V1.V2) / ( |V1| ∗ |V2| )
                    = A / (B x C)
    """
    L = len(V1)
    A,B,C= 0,0,0
    for i in range(len(V1)):
        A += V1[i]*V2[i]
        B += V1[i]**2
        C += V2[i]**2
    return A/(math.sqrt(B)*math.sqrt(C))

def Sim_euclidienne(V1,V2):
    """
    Sim_Jacc(V1, V2)    =   1 / SQRT( (V1_1 − V1_1)² + (V1_2 − V2_2)² + ... + (V1_n − V2_n)²)
    """
    A = math.sqrt(sum([(V1[i]-V2[i])**2 for i in range(len(V1))]))
    if(A == 0):return 1
    return 1/A
    

# ---------------------------------------- Functions recommandation ----------------------------------------
def enjoyIndex(note):
    return (note**2.7)/(10**2.7)

def distance(x1, y1, x2, y2):
    xd = x2 - x1
    yd = y2 - y1 
    return math.sqrt((xd**2)+(yd**2))


# ---------------------------------------- TEST ----------------------------------------

"""VECTEUR_MOVIE = [1,1,0,1,1,1,1,1,0]
VECTEUR_USER = [1,1,1,0,1,2,0,0,2]

assert truncate(Sim_Jacc(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.444
assert truncate(Sim_Cos(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.545
assert truncate(Sim_euclidienne(VECTEUR_USER,VECTEUR_MOVIE),3) == 0.333"""




