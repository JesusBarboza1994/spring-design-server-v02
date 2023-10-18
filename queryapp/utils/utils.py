import math

def sumMatrix(bigMatrix,matrix,indexROW,indexCOL): 
    """Suma los elementos una matriz (matrix) dentro de la matriz mayor (bigMatrix), desde unos índices iniciales (indexROW, indexCOL)."""
    m=0   
    for i in range(indexROW,indexROW+len(matrix)):
        n=0
        for j in range(indexCOL,indexCOL+len(matrix)):
            bigMatrix[i][j] = bigMatrix[i][j]+ matrix[m][n]
            n = n+1
        m=m+1
  
    return bigMatrix

def elementsStiffnessMatrix(longitud, youngModulus, inercia, area, shearModulus, inerciapolar, kappa):
  phi_z = 12*youngModulus*inercia/(kappa*shearModulus*area*math.pow(longitud,2))
  phi_y = 12*youngModulus*inercia/(kappa*shearModulus*area*math.pow(longitud,2))
  phi_bar_z = 1/(1+phi_z)
  phi_bar_y = 1/(1+phi_y)

  k1 = youngModulus*area/longitud
  k2 = 12*phi_bar_z*youngModulus*inercia/math.pow(longitud,3)
  k3 = 6*phi_bar_z*youngModulus*inercia/math.pow(longitud,2)
  k4 = 12*phi_bar_y*youngModulus*inercia/math.pow(longitud,3)
  k5 = 6*phi_bar_y*youngModulus*inercia/math.pow(longitud,2)
  k6 = shearModulus*inerciapolar/longitud
  k7 = (4+phi_y)*phi_bar_y*youngModulus*inercia/longitud
  k8 = (4+phi_z)*phi_bar_z*youngModulus*inercia/longitud
  k9 = (2-phi_y)*phi_bar_y*youngModulus*inercia/longitud
  k10 = (2-phi_z)*phi_bar_z*youngModulus*inercia/longitud

  return [k1, k2, k3, k4, k5, k6, k7, k8, k9, k10]