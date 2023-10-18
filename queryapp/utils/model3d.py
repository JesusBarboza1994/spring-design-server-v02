from re import X
# La premisa del código es dividir el resorte en 5 tramos. Se considera que el resorte al inicio comienza con un paso pequeño, el cual va aumentando hasta llegar a un paso
#constante, luego va disminuyendo ese paso hasta llegar al tramo final.

#Tramo 1: La primera vuelta
#Tramo 2: Desde la vuelta 1 hasta la vuelta donde inicia el paso constante 
#Tramo 3: Cantidad de vueltas de paso constante
#Tramo 4: Final del tramo constante hasta la penúltima vuelta
#Tramo 5: Vuelta final

#------------------------------------------------------------------------------------------------------------------------
#Importo librerías útiles
from numpy.core.fromnumeric import size #Probar 2200167
from numpy.ma.core import count
import math
import numpy as np
import json
#------------------------------------------------------------------------------------------------------------------------
#Defino funciones útiles

# Función para calcular número de vueltas en octavos, siendo una vuelta equivalente a 8
def vueltas_a_N_octavos(vr):
  num = 0
  if (vr > 0):
    num = 8 * vr
  else:
    num = 8
  return num

#Función para calcular longitud, siendo util para hallar las longitudes de la primera y última vuelta
def longitud_de_extremo(tipo_extrm,luz,d_al):
  long = 0
  if (tipo_extrm == "TASE" or tipo_extrm == "TAE"):
    long = luz + d_al
  elif (tipo_extrm == "TCSE" or tipo_extrm == "TCE"):
    long = d_al
  return long

#Función para calcular el ángulo pi*n, siendo una vuelta 2pi o lo que sería 8pi/4
# m es el numero de vueltas y t_ant es el angulo inicial
# t_max es el angulo final obtenido
def tramo_a_angulo(n_octavos, angulo_inicial):
  t = 0
  t_max = (math.pi/4)*n_octavos + angulo_inicial
  return t_max

#Función para ubicar el tramo. Dentro de los 5 mencionados al inicio de este codigo
def ubicar_en_tramos(angulo,cero,uno,dos,tres,cuatro,cinco):
  posicion = 0
  if(angulo > cero and angulo <= uno):
    posicion = 1
  if(angulo > uno and angulo <= dos):
    posicion = 2
  if(angulo > dos and angulo < tres):
    posicion = 3
  if(angulo >= tres and angulo < cuatro):
    posicion = 4
  if(angulo >= cuatro and angulo < cinco):
    posicion = 5
  return posicion 

#Función para setear cantidad de nodos. Siendo esta cantidad tal que se puedan separar los numeros cada pi/4 múltiplos. Es decir cada pi/4 o pi/8 o pi/16 , etc..
def n_nodos_multiploPi4(ang_fin,ang_inicio,grado):
  m = ang_fin - ang_inicio
  a = pow(2,grado + 2)
  n_previa = (m * a)/math.pi
  n = round(n_previa)
  return n          

#Función de la secante. Método de la secante, con esto se halla el x (i+1) de la serie
def f_secante(xi,xiprev,f_xi,f_xiprev):
  solucion = xi - ((f_xi * (xiprev - xi)) / (f_xiprev - f_xi))
  return solucion

def ord_burbuja(arreglo):
  arreglo_ord = []
  arreglo_ord = arreglo
  n = len(arreglo_ord)
  for i in range(n-1):       # <-- bucle padre
    for j in range(n-1-i): # <-- bucle hijo
      if arreglo_ord[j][1] > arreglo_ord[j+1][1]:
        arreglo_ord[j], arreglo_ord[j+1] = arreglo_ord[j+1], arreglo_ord[j]
  return arreglo_ord

#------------------------------------------------------------------------------------------------------------------------
#FUNCION DE GENERACION DE PUNTOS

def generatePoints(spring):


    d = spring.wire
    D = spring.diam_ext1
    d1 = spring.diam_int1
    d2 = spring.diam_int2
    L = spring.length
    N = spring.coils
    E1 = spring.end1
    E2 = spring.end2
    Luz_1 = spring.luz1
    Luz_2 = spring.luz2
    vr1 = spring.coils_red_1
    vr2 = spring.coils_red_2
    grade = spring.grade

    #------------------------------------------------------------------------------------------------------------------------
    #Obtención de valores útiles para los cálculos internos
    Lt = L - d #Longitud total, como marca en soliworks
    Mt = 8 * N #Numero total de vueltas, pasado a octavos

    #Longitud de tramos 
    L1 = longitud_de_extremo(E1,Luz_1,d) #1era vuelta (Extremo 1)
    L3 = longitud_de_extremo(E2,Luz_2,d) #Ultima vuelta (Extremo 2)
    L2 = Lt - L1 - L3        #Longitud del cuerpo

    #Diámetro medio
    Dm = D - d    #Diámetro constante  

    #Buscar iterar esto
    p0 = 0 #paso inicial, seteo (paso intantáneo en el que empieza el extremo inicial del resorte)
    pf = 5 # paso final, seteo (paso intantáneo en el que acaba el extremo final del resorte)
    paso_2 = 40 #seteo (limite inferior del rango para evaluar el paso constante del cuerpo del resorte)(Valor obtenido en base a la tendencia en fabricaciones TRANSMETA)
    paso_2_final = 60 #seteo (limite superior del rango para evaluar el paso constante del cuerpo del resorte)(Valor obtenido en base a la tendencia en fabricaciones TRANSMETA)(Puede llegar a 70, probar luego)
    p = 0 #parametro que da inicio a la iteracion
    #No se ha definido este dato, pero para fines prácticos se tomará media vuelta
    nc1 = 0.5 #numero de vueltas adicionales (> 1) antes del paso constante 
    nc2 = 0.5 #numero de vueltas despues del paso constante (< N - 1) 

    pi = round(math.pi,5)
    d_alambre = d

    #------------------------------------------------------------------------------------------------------------------------
    #Cálculo DIRECTO del paso ideal del cuerpo del Resorte

    x1 = 1
    x2 = nc1
    x4 = nc2
    x5 = 1
    x3 = N - x1 - x2 - x4 - x5

    Ncalculado = x1+x2+x3+x4+x5

    J = (L2 - (2*L3-pf+p0-2*L1)*nc1/2 - 2*(L1-p0)*nc1 - (2*L3-pf)*(N-2-nc1-nc2) - (2*L3-pf)*nc2)/(nc1*nc2 + 2*nc2*(N-2-nc1-nc2) + pow(nc2,2))
    I = (2*J*nc2 + 2*L3 - pf + p0 - 2*L1)/(2*nc1)
    K = 2*J*nc2+2*L3-pf

    P1 = 2*L1 - p0
    P2 = 2*I*nc1 + 2*L1 - p0
    P4 = 2*J*nc2 + 2*L3 - pf
    P5 = 2*L3 - pf

    y1 = (L1-p0)*x1*x1 + p0*x1
    y2 = I*x2*x2 + P1*x2
    y3 = K*x3
    y4 = J*x4*x4 + P5*x4
    y5 = (L3-pf)*x5*x5 + pf*x5

    y_total = y1+y2+y3+y4+y5

    #---------------------------------------------------------------------------------------------------------------------------
    #Defino mis ecuaciones de tramo, tomando como el paso constante el hallada mediante el método de la secante

    #Numero de vueltas en cada tramo, se cuentan cuantos 1/8 x vuelta hay
    M1 = vueltas_a_N_octavos(1) #Primera vuelta
    Mc1 = vueltas_a_N_octavos(nc1) #paso variable 1
    M3 = vueltas_a_N_octavos(1) #Última vuelta
    Mc2 = vueltas_a_N_octavos(nc2) #paso variable 2
    M2 = Mt - M1 - Mc1 - M3 - Mc2 #paso constante

    #Ángulo máximo de cada tramo
    t1_max = tramo_a_angulo(M1,0) #ángulo con el que termina la primera vuelta
    tMc1_max = tramo_a_angulo(Mc1,t1_max)#ángulo con el que termina el tramo de paso ascendente
    t2_max = tramo_a_angulo(M2,tMc1_max)#ángulo con el que termina el tramo de paso constante
    tMc2_max = tramo_a_angulo(Mc2,t2_max)#ángulo con el que termina el tramo de paso descendente
    t3_max = tramo_a_angulo(M3,tMc2_max)#ángulo con el que termina la última vuelta

    #Ecuaciones por tramo, partiendo del eje "Z"
    t1 = np.linspace(0,t1_max,100) #nodos x cada tramo
    tMc1 = np.linspace(t1_max,tMc1_max,100)
    t2 = np.linspace(tMc1_max,t2_max,400)
    tMc2 = np.linspace(t2_max,tMc2_max,100)
    t3 = np.linspace(tMc2_max,t3_max,100)

    #Vectores para las coordenadas
    coord_x1 = []
    coord_y1 = []
    coord_z1 = []
    coord_x2 = []
    coord_y2 = []
    coord_z2 = []
    coord_x3 = []
    coord_y3 = []
    coord_z3 = []
    coord_x4 = []
    coord_y4 = []
    coord_z4 = []
    coord_x5 = []
    coord_y5 = []
    coord_z5 = []

    paso0 = p0
    paso1_calc = 2*(L1-p0)*x1+p0
    altura1_calc = (L1-p0)*pow(1,2)+p0*1
    paso2_calc = 2*I*x2+paso1_calc
    altura2_calc = L1 + I*pow(x2,2)+paso1_calc*x2
    paso3_calc = K
    altura3_calc = altura2_calc + K*x3
    paso4_calc = K
    paso5_calc = 2*(L3-pf)*x5+pf
    altura4_calc = altura3_calc + J*pow(x4,2)+paso5_calc*x4

    t_1 = t1_max
    t_Mc1 = tMc1_max
    t_2 = t2_max
    t_Mc2 = tMc2_max
    t_3 = t3_max

    #--------------------------------------------------------------------------------
    #Vuelvo a definir las ecuaciones, tomando en cuentas las reducciones

    #Numero de vueltas de las vueltas reducidas
    if (d1 > 0):
        M_vr1 = vueltas_a_N_octavos(vr1)
        t_vr1 = round((math.pi/4)*M_vr1,5)
        Dm_vr1 = d1 + d 
        t_vr_1 = t_vr1 - math.pi
        C1 = (Dm - Dm_vr1) / (2 * t_vr_1)
    else:
        M_vr1 = 0
        Dm_vr1 = Dm
        C1 = 0
        t_vr1 = round(t_1,5)

    if (d2 > 0):
        M_vr2 = vueltas_a_N_octavos(vr2)
        t_vr2 = round(t_3 - (math.pi/4)*M_vr2,5)
        Dm_vr2 = d2 + d 
        t_vr_2 = (math.pi/4)*M_vr2 - math.pi 
        C2 = (Dm - Dm_vr2) / (2 * t_vr_2)

    else:
        M_vr2 = 0
        Dm_vr2 = Dm
        C2 = 0
        t_vr2 = round(t_Mc2,5)

    q = 0

    grado = float(grade)

    n_1 = n_nodos_multiploPi4(t_1,0,grado + 2) 
    n_2 = n_nodos_multiploPi4(t_Mc1,t_1,grado + 2)
    n_3 = n_nodos_multiploPi4(t_2,t_Mc1,grado + 2)
    n_4 = n_nodos_multiploPi4(t_Mc2,t_2,grado + 2)
    n_5 = n_nodos_multiploPi4(t_3,t_Mc2,grado + 2)

    nodos_totales = n_1 + 1 + n_2 + n_3 + n_4 + n_5

    print("Cantidad de nodos totales será de: ")
    print(nodos_totales)

    #Ecuaciones por tramo, partiendo el eje y en 5 tramos
    ang_t1 = np.linspace(0,t_1,n_1 + 1) #nodos x cada tramo
    ang_t1_2 = []
    for i in ang_t1:
        truncado = round(i,5)
        ang_t1_2.append(truncado)

    ang_tMc1 = np.linspace(t_1,t_Mc1,n_2 + 1)
    ang_tMc1_2 = []
    for i in ang_tMc1:
        truncado = round(i,5)
        ang_tMc1_2.append(truncado)

    ang_t2 = np.linspace(t_Mc1,t_2,n_3 + 1)
    ang_t2_2 = []
    for i in ang_t2:
        truncado = round(i,5)
        ang_t2_2.append(truncado)

    ang_tMc2 = np.linspace(t_2,t_Mc2,n_4 + 1)
    ang_tMc2_2 = []
    for i in ang_tMc2:
        truncado = round(i,5)
        ang_tMc2_2.append(truncado)

    ang_t3 = np.linspace(t_Mc2,t_3,n_5 + 1)
    ang_t3_2 = []
    for i in ang_t3:
        truncado = round(i,5)
        ang_t3_2.append(truncado)

    #print(ang_t1)
    #Lo pasamos a lista estos array, para poder obtener las posiciones de ciertos elementos
    list_t1 = ang_t1_2#.tolist()
    list_tMc1 = ang_tMc1_2#.tolist()
    list_t2 = ang_t2_2#.tolist()
    list_tMc2 = ang_tMc2_2#.tolist()
    list_t3 = ang_t3_2#.tolist()
    #print(list_t1)
    pos_1 = list_t1.index(pi) 
    ang_t0_5 = np.linspace(0,math.pi,pos_1 + 1) #primera media vuelta (0 a 0.5)
    ang_t1_5 = np.linspace(math.pi,t_1,pos_1 + 1) #resto de la primera vuelta (0.5 a 1)
    medio_final = round(t_3 - math.pi,5)
    pos_2 = list_t3.index(medio_final)
    ang_tN_0 = np.linspace(t_Mc2,medio_final,pos_2 + 1)#penúltima media vuelta (N - 1 a N - 0.5)
    ang_tN_5 = np.linspace(medio_final,t_3,pos_2 + 1)#última media vuelta(N - 0.5 a N)

    #Vectores para las coordenadas
    coord1_x1 = []
    coord1_y = []
    coord1_z1 = []
    coord1_x2 = []
    coord1_z2 = []
    coord1_x3 = []

    coord1_z3 = []
    coord1_x4 = []
    coord1_y4 = []
    coord1_z4 = []
    coord1_x5 = []
    coord1_z5 = []
    coord2_y = []

    #Vector de pasos
    Pi = []

    #Guardamos todo el recorrido de la altura en un array

    #Tramo 1 #vuelta 0 a vuelta 1 #y = ax2 + bx
    for a in ang_t1: 
        Ni_1 = a/(2*math.pi)
        Pi_1 = 2*(L1-p0)*Ni_1+p0
        y_1_decimal = (L1-p0)*pow(Ni_1,2)+p0*Ni_1
        y_1 = round(y_1_decimal,6)
        coord1_y.append(y_1)
        Pi.append(Pi_1)

    altura1 = coord1_y[len(coord1_y)-1]
    #print("altura1: ", altura1)
    paso1 = Pi[len(Pi)-1]

    #Tramo 2 #vuelta 1 a la vuelta donde comienza el paso constante #y = ax2 + bx
    for b in ang_tMc1:
        Ni_2 = (b-ang_t1[len(ang_t1)-1])/(2*math.pi)
        Pi_2 = 2*I*Ni_2+paso1
        y_2_decimal = altura1 + I*pow(Ni_2,2)+paso1*Ni_2
        y_2 = round(y_2_decimal,6)
        if (b > ang_tMc1[0]):
            coord1_y.append(y_2)
            Pi.append(Pi_2)

    altura2 = coord1_y[len(coord1_y)-1]
    #print("altura2: ", altura2)
    paso2 = Pi[len(Pi)-1]

    #Tramo 3 #el tramo donde el paso es constante y = mx + b
    for c in ang_t2:
        Ni_3 = (c-ang_tMc1[len(ang_tMc1)-1])/(2*math.pi)
        Pi_3 = paso2
        y_3_decimal = altura2 + paso2*(Ni_3)
        y_3 = round(y_3_decimal,6)
        if (c > ang_t2[0]):
            coord1_y.append(y_3)
            Pi.append(Pi_3)

    altura3 = coord1_y[len(coord1_y)-1]
    #print("altura3: ", altura3)
    paso3 = Pi[len(Pi)-1]

    #Tramo 5 #la vuelta N-1 a vuelta N # y = ax2 + bx
    arreglo_Pi_5_creciente = []
    arreglo_y_5_decimal_creciente = []
    for e in ang_t3:
        Ni_5 = (e - ang_tMc2[len(ang_tMc2)-1])/(2*math.pi)
        Pi_5_creciente = 2*(L3-pf)*Ni_5+pf
        y_5_decimal_creciente = (L3-pf)*pow(Ni_5,2)+pf*Ni_5
        if (e < ang_t3[len(ang_t3)-1]):
            arreglo_y_5_decimal_creciente.append(y_5_decimal_creciente)
            arreglo_Pi_5_creciente.append(Pi_5_creciente)

    paso5 = arreglo_Pi_5_creciente[len(arreglo_Pi_5_creciente)-1]

    #Tramo 4 #la vuelta donde termina el paso constante a la vuelta N-1 # y = ax2 + bx
    #paso4_abajo = J*pow(nc2,2)+L3*nc2
    arreglo_Pi_4_creciente = []
    arreglo_y_4_decimal_creciente = []
    for d in ang_tMc2:
        Ni_4 = (d- ang_t2[len(ang_t2)-1])/(2*math.pi)
        Pi_4_creciente = 2*J*Ni_4+paso5
        y_4_decimal_creciente = J*pow(Ni_4,2) + (2*L3 - pf) * Ni_4
        if (d < ang_tMc2[len(ang_tMc2)-1]):
            arreglo_y_4_decimal_creciente.append(y_4_decimal_creciente)
            arreglo_Pi_4_creciente.append(Pi_4_creciente)

    paso4 = arreglo_Pi_4_creciente[len(arreglo_Pi_4_creciente)-1]

    #Agregando el Tramo 4 al arreglo de coordenadas y (Se agrega de forma decreciente y se resta)
    v = 0
    altura_tramo4 = arreglo_y_4_decimal_creciente[len(arreglo_y_4_decimal_creciente)-1] - arreglo_y_4_decimal_creciente[0]
    altura3_toerico = y1+y2+y3
    dif_altura3 = altura3_toerico - altura3
    print("altura3_toerico - altura3: ", dif_altura3)

    while (v < len(arreglo_y_4_decimal_creciente)):
        y_4_decimal = Lt-L3-altura_tramo4 + (altura_tramo4 - arreglo_y_4_decimal_creciente[len(arreglo_y_4_decimal_creciente)-1-v])
        y_4 = round(y_4_decimal,6)
        coord1_y.append(y_4)
        Pi_4 = arreglo_Pi_4_creciente[len(arreglo_Pi_4_creciente)-1-v]
        Pi.append(Pi_4)
        v = v + 1

    altura4 = coord1_y[len(coord1_y)-1]
    
    #Agregando el Tramo 5 al arreglo de coordenadas y (Se agrega de forma decreciente y se resta)
    q = 0
    while (q < len(arreglo_y_5_decimal_creciente)):
        y_5_decimal = Lt-L3 + (L3 - arreglo_y_5_decimal_creciente[len(arreglo_y_5_decimal_creciente)-1-q])
        y_5 = round(y_5_decimal,6)
        coord1_y.append(y_5)
        Pi_5 = arreglo_Pi_5_creciente[len(arreglo_Pi_5_creciente)-1-q]
        Pi.append(Pi_5)
        q = q + 1

    final = len(coord1_y) 

    altura_final = coord1_y[len(coord1_y)-1]

    #---------------------------------------------------------------------------------------------------------------------------------

    #Tramos en base de coordenadas x , z

    #Tramo 0.5 (vuelta 0 a vuelta 0.5) 
    for a in ang_t0_5:
        x_1 = (Dm_vr1/2) * math.sin(a)
        z_1 = (Dm_vr1/2) * math.cos(a) * (-1)
        coord1_x1.append(x_1)
        coord1_z1.append(z_1) 
    ang_f1 = pi 

    posicion1 = list_t1.index(ang_f1) 
    hasta1 = posicion1 + 1
    coord2_y1 = coord1_y[0:hasta1] 

    #-------------------------------------------------------------------------------------------------------------------------------------

    #Tramo 0.5 al final de la vuelta reducida 1
    tramo_2 = ubicar_en_tramos(t_vr1,0,t_1,t_Mc1,t_2,t_Mc2,t_3)

    if (tramo_2 == 1):
        posicion2 = list_t1.index(t_vr1) 
        hasta2 = posicion2 
        coord2_y2 = coord1_y[posicion1:hasta2]
        dif1 = hasta2 - posicion1

    elif (tramo_2 == 2):
        posicion2 = list_tMc1.index(t_vr1) # 
        hasta2 = (n_1 + 1) + posicion2 
        coord2_y2 = coord1_y[posicion1:hasta2] #nro de elemtos, derecha - izquierda
        dif1 = hasta2 - posicion1

    elif (tramo_2 == 3):
        posicion2 = list_t2.index(t_vr1)
        hasta2 = (n_1 + n_2 + 1) + posicion2 
        coord2_y2 = coord1_y[posicion1:hasta2]
        dif1 = hasta2 - posicion1

    ang_t_red1 = np.linspace(math.pi,t_vr1,dif1) #hasta llegar al final de la vuelta reducida
    print(ang_t_red1)
    for b in ang_t_red1:
        x_2 = (Dm_vr1/2 + C1 * (b - math.pi)) * math.sin(b)
        z_2 = (Dm_vr1/2 + C1 * (b - math.pi)) * math.cos(b) * (-1)
        coord1_x2.append(x_2)
        coord1_z2.append(z_2)

    #-------------------------------------------------------------------------------------------------------------------------------------

    #Tramo cuerpo sin reducciones
    tramo3 = ubicar_en_tramos(t_vr2,0,t_1,t_Mc1,t_2,t_Mc2,t_3)

    if (tramo3 == 3):
        posicion3 = list_t2.index(t_vr2)
        hasta3 = (n_1 + n_2 + 1) + posicion3 
        inicio = hasta2 - 1 #indicar desde donde comenzar
        coord2_y3 = coord1_y[inicio:hasta3]
        dif2 = hasta3 - inicio

    elif (tramo3 == 4):
        posicion3 = list_tMc2.index(t_vr2)
        hasta3 = (n_1 + n_2 + n_3 + 1) + posicion3 
        inicio = hasta2 - 1 #indicar desde donde comenzar
        coord2_y3 = coord1_y[inicio:hasta3]
        dif2 = hasta3 - inicio

    elif (tramo3 == 5):
        posicion3 = list_t3.index(t_vr2)
        hasta3 = (n_1 + n_2 + n_3 + n_4 + 1) + posicion3 
        inicio = hasta2 - 1 #indicar desde donde comenzar
        coord2_y3 = coord1_y[inicio:hasta3]
        dif2 = hasta3 - inicio

    ang_t_red2 = np.linspace(t_vr1,t_vr2,dif2)
    for a in ang_t_red2:
        x_3 = (Dm/2) * math.sin(a)
        z_3 = (Dm/2) * math.cos(a) * (-1)
        coord1_x3.append(x_3)
        coord1_z3.append(z_3)


    #-------------------------------------------------------------------------------------------------------------------------------------

    #Tramo red2 a tramo N - 0.5
    tramo4 = ubicar_en_tramos(medio_final,0,t_1,t_Mc1,t_2,t_Mc2,t_3)

    posicion4 = list_t3.index(medio_final)
    hasta4 = (n_1 + n_2 + n_3 + n_4 + 1) + posicion4 
    inicio2 = hasta3 - 1
    coord2_y4 = coord1_y[inicio2:hasta4] 
    dif3 = hasta4 - inicio2

    ang_t_red3 = np.linspace(t_vr2,medio_final,dif3)
    for a in ang_t_red3:
        x_4 = (Dm/2 - C2 * (a - t_vr2)) * math.sin(a)
        z_4 = (Dm/2 - C2 * (a - t_vr2)) * math.cos(a) * (-1)
        coord1_x4.append(x_4)
        coord1_z4.append(z_4)

    #-------------------------------------------------------------------------------------------------------------------------------------

    #Tramo N - 0.5 a tramo N
    for a in ang_tN_5:
        x_5 = (Dm_vr2/2) * math.sin(a)
        z_5 = (Dm_vr2/2) * math.cos(a) * (-1)
        coord1_x5.append(x_5)
        coord1_z5.append(z_5)
    inicio3 = hasta4 - 1
    coord2_y5 = coord1_y[inicio3:final]

    #------------------------------------------------------------------------------------------------------------------------------------
    #Obtención de datos para el modelamiento del resorte en Solidworks

    tabla_solidworks = []

    #Punto 0 vueltas (0)
    vta_punto0_vueltas = 0.0
    paso_punto0_vueltas = p0
    y_punto0_vueltas = 0.0
    if (vr1 > 0):
        Dm_punto0_vueltas = d1 + d_alambre
    else:
        Dm_punto0_vueltas = Dm
    punto_solidworks = [paso_punto0_vueltas,y_punto0_vueltas,vta_punto0_vueltas,Dm_punto0_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto 0.5 vueltas (1)
    vta_punto1_vueltas = 0.5
    paso_punto1_vueltas = 2*(L1-p0)*vta_punto1_vueltas+p0
    y_punto1_vueltas = (L1-p0)*pow(vta_punto1_vueltas,2)+vta_punto1_vueltas*p0
    if (vr1 > 0):
        Dm_punto1_vueltas = d1 + d_alambre
    else:
        Dm_punto1_vueltas = Dm
    punto_solidworks = [paso_punto1_vueltas,y_punto1_vueltas,vta_punto1_vueltas,Dm_punto1_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto 1 vuelta (2)
    vta_punto2_vueltas = 1
    paso_punto2_vueltas = 2*(L1-p0)*vta_punto2_vueltas+p0
    y_punto2_vueltas = (L1-p0)*pow(vta_punto2_vueltas,2)+vta_punto2_vueltas*p0
    if (vr1 > 0):
        if (vta_punto2_vueltas <= vr1):
            Dm_punto2_vueltas = 2*(2*pi*C1*(vta_punto2_vueltas-0.5)+(d1+d_alambre)/2)
        else:
            Dm_punto2_vueltas = Dm
    else:
        Dm_punto2_vueltas = Dm
    punto_solidworks = [paso_punto2_vueltas,y_punto2_vueltas,vta_punto2_vueltas,Dm_punto2_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto 1+nc1 vueltas (3)
    vta_punto3_vueltas = 1+nc1
    paso_punto3_vueltas = paso2
    y_punto3_vueltas = altura1 + I*pow((vta_punto3_vueltas-1),2)+(vta_punto3_vueltas-1)*paso1
    if (vr1 > 0):
        if (vta_punto3_vueltas <= vr1):
            Dm_punto3_vueltas = 2*(2*pi*C1*(vta_punto3_vueltas-0.5)+(d1+d_alambre)/2)
        else:
            Dm_punto3_vueltas = Dm
    else:
        Dm_punto3_vueltas = Dm
    punto_solidworks = [paso_punto3_vueltas,y_punto3_vueltas,vta_punto3_vueltas,Dm_punto3_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto N-1-nc2 vueltas (4)
    vta_punto4_vueltas = N-1-nc2
    paso_punto4_vueltas = paso2
    y_punto4_vueltas = altura2 + (vta_punto4_vueltas-1-nc1)*paso2
    if (vr2 > 0):
        if ((N - vta_punto4_vueltas) <= vr2):
            Dm_punto4_vueltas = 2*(2*pi*C2*(N-vta_punto4_vueltas-0.5)+(d2+d_alambre)/2)
        else:
            Dm_punto4_vueltas = Dm
    else:
        Dm_punto4_vueltas = Dm
    punto_solidworks = [paso_punto4_vueltas,y_punto4_vueltas,vta_punto4_vueltas,Dm_punto4_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto N-1 vueltas (5)
    vta_punto5_vueltas = N-1
    paso_punto5_vueltas = 2*(L3-pf)*(N-vta_punto5_vueltas)+pf
    y_punto5_vueltas = Lt - ((L3-pf)*pow((N-vta_punto5_vueltas),2)+pf*(N-vta_punto5_vueltas))
    if (vr2 > 0):
        if ((N - vta_punto5_vueltas) <= vr2):
            Dm_punto5_vueltas = 2*(2*pi*C2*(N-vta_punto5_vueltas-0.5)+(d2+d_alambre)/2)
        else:
            Dm_punto5_vueltas = Dm
    else:
        Dm_punto5_vueltas = Dm
    punto_solidworks = [paso_punto5_vueltas,y_punto5_vueltas,vta_punto5_vueltas,Dm_punto5_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto N-0.5 vueltas (6)
    vta_punto6_vueltas = N-0.5
    paso_punto6_vueltas = 2*(L3-pf)*(N-vta_punto6_vueltas)+pf
    y_punto6_vueltas = Lt - ((L3-pf)*pow((N-vta_punto6_vueltas),2)+pf*(N-vta_punto6_vueltas))
    if (vr2 > 0):
        Dm_punto6_vueltas = d2 + d_alambre
    else:
        Dm_punto6_vueltas = Dm
    punto_solidworks = [paso_punto6_vueltas,y_punto6_vueltas,vta_punto6_vueltas,Dm_punto6_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto N vueltas (7)
    vta_punto7_vueltas = N
    paso_punto7_vueltas = pf
    y_punto7_vueltas = Lt
    if (vr2 > 0):
        Dm_punto7_vueltas = d2 + d_alambre
    else:
        Dm_punto7_vueltas = Dm
    punto_solidworks = [paso_punto7_vueltas,y_punto7_vueltas,vta_punto7_vueltas,Dm_punto7_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto fin vta red 1 (8)
    vta_punto8_vueltas = vr1
    if (vr1 == 0.0):
        paso_punto8_vueltas = p0
        y_punto8_vueltas = 0.0
    elif ((vr1 > 0) and (vr1 <= 1)):
        paso_punto8_vueltas = 2*(L1-p0)*vta_punto8_vueltas+p0
        y_punto8_vueltas = (L1-p0)*pow(vta_punto8_vueltas,2)+vta_punto8_vueltas*p0
    elif (vr1 <= (1+nc1)):
        paso_punto8_vueltas = 2*I*(vta_punto8_vueltas-1)+paso1
        y_punto8_vueltas = altura1 + I*pow((vta_punto8_vueltas-1),2)+(vta_punto8_vueltas-1)*paso1
    else:
        paso_punto8_vueltas = paso2
        y_punto8_vueltas = altura2 + (vta_punto8_vueltas-1-nc1)*paso2
    Dm_punto8_vueltas = Dm
    punto_solidworks = [paso_punto8_vueltas,y_punto8_vueltas,vta_punto8_vueltas,Dm_punto8_vueltas]
    tabla_solidworks.append(punto_solidworks)

    #Punto fin vta red 2 (9)
    vta_punto9_vueltas = N-vr2
    if (vr2 == 0.0):
        paso_punto9_vueltas = pf
        y_punto9_vueltas = Lt
    elif ((vr2 > 0) and (vr2 <= 1)):
        paso_punto9_vueltas = 2*(L3-pf)*(N-vta_punto9_vueltas)+pf
        y_punto9_vueltas = Lt - ((L3-pf)*pow((N-vta_punto9_vueltas),2)+pf*(N-vta_punto9_vueltas))
    elif (vr2 <= (1+nc1)):
        paso_punto9_vueltas = 2*J*(vr2-1)+(2*L3-pf)
        y_punto9_vueltas = y_punto5_vueltas - (J*pow((vr2-1),2)+(2*L3-pf)*(vr2-1))
    else:
        paso_punto9_vueltas = paso2
        y_punto9_vueltas = altura2 + (vta_punto9_vueltas-1-nc1)*paso2
    Dm_punto9_vueltas = Dm
    punto_solidworks = [paso_punto9_vueltas,y_punto9_vueltas,vta_punto9_vueltas,Dm_punto9_vueltas]
    tabla_solidworks.append(punto_solidworks)

    print("Paso 0 = ",paso0,"/","Altura 0 = ",0,"/","Vueltas = ",0,"/","Tramo angular = [0,",t_1,"]")
    print("Paso 1 = ",paso1,"/","Altura 1 = ",altura1,"/","Vueltas = ",1,"/","Tramo angular = [",t_1,",",t_Mc1,"]")
    print("Paso 2 = ",paso2,"/","Altura 2 = ",altura2,"/","Vueltas = ",1 + nc1,"/","Tramo angular = [",t_Mc1,",",t_2,"]")
    print("Paso 3 = ",paso3,"/","Altura 3 = ",altura3,"/","Vueltas = ",N - 1 - nc2,"/","Tramo angular = [",t_2,",",t_Mc2,"]")
    print("Paso 4 = ",paso5,"/","Altura 4 = ",altura4,"/","Vueltas = ",N - 1,"/","Tramo angular = [",t_Mc2,",",t_3,"]")
    print("Paso final = ",pf,"/","Altura final = ",altura_final,"/","Vueltas = ",N)
    print("Nc1 = ",nc1)
    print("Nc2 = ",nc2)

    tabla_solidworks_ord = []
    tabla_solidworks_ord = ord_burbuja(tabla_solidworks)

    #print("TABLA EN SOLIDWORKS")
    #index_puntos = 0
    #for i in tabla_solidworks_ord:
        #print("Punto ",index_puntos," : ", "Paso = ",i[0]," / ","Vueltas = ",i[2]," / ","Altura = ",i[1],"/","Diámetro = ",i[3])
        #index_puntos = index_puntos +1

    #----------------------------------------------------------------------------------------------------------------------------------------

    #SALIDA: Arreglo de puntos con coordenadas en 3D
    resorte = []

    ind1 = 0
    while (ind1 < len(coord1_x1)-1):
        punto = []
        punto.append(coord1_x1[ind1])
        punto.append(coord1_z1[ind1])
        punto.append(coord2_y1[ind1])
        resorte.append(punto)
        ind1 = ind1 + 1

    ind2 = 0
    while (ind2 < len(coord1_x2)-1):
        punto = []
        punto.append(coord1_x2[ind2])
        punto.append(coord1_z2[ind2])
        punto.append(coord2_y2[ind2])
        resorte.append(punto)
        ind2 = ind2 + 1

    ind3 = 0
    while (ind3 < len(coord1_x3)-1):
        punto = []
        punto.append(coord1_x3[ind3])
        punto.append(coord1_z3[ind3])
        punto.append(coord2_y3[ind3])
        resorte.append(punto)
        ind3 = ind3 + 1

    ind4 = 0
    while (ind4 < len(coord1_x4)-1):
        punto = []
        punto.append(coord1_x4[ind4])
        punto.append(coord1_z4[ind4])
        punto.append(coord2_y4[ind4])
        resorte.append(punto)
        ind4 = ind4 + 1

    ind5 = 0
    while (ind5 < len(coord1_x5)):
        punto = []
        punto.append(coord1_x5[ind5])
        punto.append(coord1_z5[ind5])
        punto.append(coord2_y5[ind5])
        resorte.append(punto)
        ind5 = ind5 + 1

    #print("Punto Inicial: X = ",resorte[0][0],", Y = ",resorte[0][1],", Z = ", resorte[0][2])
    #print("Punto Final: X = ",resorte[len(resorte)-1][0],", Y = ",resorte[len(resorte)-1][1],", Z = ", resorte[len(resorte)-1][2])

    #print(resorte)
    #print(".")

    #json_string = json.dumps(resorte)

    return resorte