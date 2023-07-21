import numpy
import pygame
import random
import time
from datetime import datetime
import os



def colocar_poros(estados_casillas, porosidad, largo_tierra,  casillas_x, casillas_y):
    for i in range(int(int(casillas_x*largo_tierra)*casillas_y*porosidad)): #se itera en el area de la tierra, pero en y solo en proporcion a la porosidad
        x = random.randrange(int(casillas_x*largo_tierra)) #se generan numeros aleatoros en el rango del terreno poroso
        y = random.randrange(casillas_y) #se generan numeros aleatorios de nuevo
        while estado_casillas[x][y] == 2: #mientras que el estado de las casillas sea dos
            x = random.randrange(int(casillas_x*largo_tierra)) #se generan numeros aleatorios en los cuales poner los poros
            y = random.randrange(casillas_y)#se generan numeros aleatorios en los cuales poner los poros
        estado_casillas[x][y] = 2 #se le asignan la condicion de poros a los numeros anteriormente mencionados
    return estado_casillas

def encontrar_llave(diccionario, valor_buscado): 
    for llave, valor in diccionario.items(): #reconoce un valor en una lista y devuelve lo que encuentra o nada
        if valor_buscado == valor:
            return llave
    return None                                          

pygame.init()

reloj = pygame.time.Clock() #mide los tiempos

#densidad de poros
contador_generaciones = 0 #lleva la cuenta de la generaciones que pasaron (inicia en 0)
porosidad = 0.5 #cantidad de poros en proporcion de area de tierra
largo_tierra = 0.6 #porcentaje de ancho de casillas destinada a la tierra
probabilidad_lateral = 0.6 #probabilidad de que el contaminante se mueva lateralmente
probabilidad_tierra_agua = 0.7 #probabilidad de pasar de la tierra al agua
probabilidad_difusion = 0.3
velocidad_agua = 3 # cada n generaciones el contaminante se mueve a la derecha (entero)
concentracion_contaminante = 0.5 #concentracion inicial del contaminante
concentracion_min = 0.1 #concentracion minima del contaminante en el agua
saltos = (concentracion_contaminante-concentracion_min)/5 # saltados entre concentraciones


#colores--------------------------
colores = {
    "tierra" : (78,59,49),
    "poro": (43, 128, 0),
    "blanco":(255,255,255),
    "agua": (0, 20, 200),
    "contaminante" : (221,215,0),
    "negro" : (0,0,0)
}

#tipos casillas---------------------
estados = {
    "tierra" : 1,
    "poro": 2,
    "agua": 3,
    "contaminante" : 4
}

#creacion de ventana
dimension_cuadricula = 20
alto = 600 + dimension_cuadricula
ancho = 1200

casillas_x = ancho//dimension_cuadricula
casillas_y = (alto//dimension_cuadricula)-1

ventana = pygame.display.set_mode((ancho, alto)) 
ventana.fill(colores["blanco"])

#titulo para la ventana
pygame.display.set_caption("Difusion")

#icono para la ventana
try:
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_imagen_icono = os.path.join(directorio_actual, "icono_difusion.png")
    icono = pygame.image.load(ruta_imagen_icono)
    pygame.display.set_icon(icono)
except:
    print("No se ha podido cargar la imagen")

#otras variables
gameOver = False
pausa = True
velocidad_generacion = 1 #esto es el "tiempo en que va iterando"
fuente = pygame.font.SysFont(name="Arial", size=14, bold=False, italic=False)

#creacion cuadriculas---------------------------------------
estado_casillas = numpy.zeros((casillas_x, casillas_y)) #matriz para la creacion de poros
concentraciones_agua = numpy.zeros((casillas_x, casillas_y)) #matriz para la difusion en el agua

for x in range(int(casillas_x*largo_tierra)):
    for y in range(casillas_y):
        estado_casillas[x][y] = estados["tierra"] #se crea la tierra

for x in range(int(casillas_x*largo_tierra), casillas_x):
    for y in range(casillas_y):
        estado_casillas[x][y] = estados["agua"] #se crea la zona del agua

estado_casillas = colocar_poros(estado_casillas, porosidad, largo_tierra, casillas_x, casillas_y) #se crea el medio poroso con la función de arriba

instante = datetime.now()

#bucle del juego
while not gameOver:
    # eventos------------------------------------
    for evento in pygame.event.get():

        # terminar el juego-----------------------
        if evento.type == pygame.QUIT:
            gameOver = True

        # evento de presionar teclas---------------
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE: #pausa con espacio
                pausa = not pausa

            if evento.key == pygame.K_RIGHT: #disminuye el tiempo de iteracion, entonces se aumenta la velocidad
                if (velocidad_generacion <= 0.05):
                    velocidad_generacion = 0
                else:
                    velocidad_generacion -= 0.05

            if evento.key == pygame.K_LEFT:   #aumenta el tiempo de iteracion, entonces se disminuye la velocidad
                if (velocidad_generacion >= 1):
                    velocidad_generacion = 1
                else:
                    velocidad_generacion += 0.05

        #evento de mouse--------------------------
        mouseClick = pygame.mouse.get_pressed()
        if (mouseClick[0]or mouseClick[2]):
            posx, posy = pygame.mouse.get_pos()
            x = int(numpy.floor(posx/dimension_cuadricula)) #al hacer click se agrega el contaminante solo en la primera fila
            if(estado_casillas[x][0] == 2):
                estado_casillas[x][0] = 4




    if (not pausa and (datetime.now()-instante).total_seconds() >= velocidad_generacion):

        #reglas para el limite tierra - agua
        for i in range(casillas_y):
            if(estado_casillas[int(casillas_x*largo_tierra)-1][i] == estados["contaminante"] and estado_casillas[int(casillas_x*largo_tierra)][i] == estados["agua"]):
                if(random.random() < probabilidad_tierra_agua):                                         #si el contaminante llega al limite de tierra y la casilla siguiente es
                    estado_casillas[int(casillas_x*largo_tierra)-1][i] = estados["poro"]                #agua
                    estado_casillas[int(casillas_x*largo_tierra)][i] = estados["contaminante"]
                    concentraciones_agua[int(casillas_x*largo_tierra)][i] = concentracion_contaminante #adquiere la concentración del contaminante

        #reglas para el contaminante en el suelo
        contador_generaciones += 1
        instante = datetime.now()
        for y in range(casillas_y-1, -1, -1): #de arriba a abajo
            for x in range(int(casillas_x*largo_tierra)): #solo en la tierra
                if(estado_casillas[x][y]==estados["contaminante"] and (y+1)<casillas_y): # si es un contaminante y esta dentro del rango de y
                    if(estado_casillas[x][y+1]==estados["poro"]): # movimiento a la casilla de abajo
                        estado_casillas[x][y]=estados["poro"]
                        estado_casillas[x][y+1]=estados["contaminante"]

                    elif(estado_casillas[x-1][y+1] == estados["poro"] or estado_casillas[x+1][y+1] == estados["poro"]): #esquina izquiera y derecha
                        list_temp = [] #lista vacia en el cual pondremos la esquina izquierda y derecha]
                        if(estado_casillas[x-1][y+1] == estados["poro"]):
                            list_temp.append(x-1)
                        if(estado_casillas[x+1][y+1] == estados["poro"]):
                            list_temp.append(x+1)

                        estado_casillas[x][y] = estados["poro"]
                        estado_casillas[random.choice(list_temp)][y+1] = estados["contaminante"] #esta funcion escoje una de las opciones de la lista al azar

                    elif(estado_casillas[x-1][y] == estados["poro"] or estado_casillas[x+1][y] == estados["poro"]): #se repite el proceso anterior pero con las casillas de
                        list_temp = []                                                                              # los lados
                        if(estado_casillas[x-1][y] == estados["poro"]):
                            list_temp.append(x-1)
                        if(estado_casillas[x+1][y] == estados["poro"]):
                            list_temp.append(x+1)

                        if(probabilidad_lateral > random.random()): # se le agrega una probabilidad ademas
                            estado_casillas[x][y] = estados["poro"]
                            estado_casillas[random.choice(list_temp)][y] = estados["contaminante"]

                elif(estado_casillas[x][y] == estados["contaminante"] and (estado_casillas[x-1][y] == estados["poro"] or estado_casillas[x+1][y] == estados["poro"])):
                        list_temp = []
                        if(estado_casillas[x-1][y] == estados["poro"]): #proceso para el movimiento lateral cuando no hay poros abajo
                            list_temp.append(x-1)
                        if(estado_casillas[x+1][y] == estados["poro"]):
                            list_temp.append(x+1)

                        if(probabilidad_lateral > random.random()):
                            estado_casillas[x][y] = estados["poro"]
                            estado_casillas[random.choice(list_temp)][y] = estados["contaminante"] 


        #movimiento lateral en el agua
        if(contador_generaciones%velocidad_agua == 0):
            for y in range(casillas_y):
                for x in range(casillas_x-1, int(casillas_x*largo_tierra)-1, -1):
                    if(estado_casillas[x][y] == estados["contaminante"]): #si es un contaminante
                        if( x+1 >= casillas_x): #si es o es el siguiente  un numero en el limite de la pantalla
                            estado_casillas[x][y] = estados["agua"]  #cambia su estado a agua
                            concentraciones_agua[x][y] = 0 #se baja la concentración a cero
                        else:
                            estado_casillas[x][y] = estados["agua"] #agua
                            estado_casillas[x+1][y] = estados["contaminante"] #la siguiente es contaminante
                            concentraciones_agua[x+1][y] = concentraciones_agua[x][y] #la siguiente adquiere la concentración de la anterior
                            concentraciones_agua[x][y] = 0 #la actual disminuye su concentración a cero


        #reglas para la difusion del contaminante en el agua
        temp_estados = numpy.copy(estado_casillas)
        temp_concentraciones = numpy.copy(concentraciones_agua)
        for y in range(casillas_y):
            for x in range(int(casillas_x*largo_tierra) ,casillas_x): #delimita a la zona del agua
                if(estado_casillas[x][y] == estados["contaminante"]): #si hay contaminante
                    if(x-1> int(casillas_x*largo_tierra) and random.random() < probabilidad_difusion and temp_concentraciones[x][y] > concentracion_min): #condiciones
                        temp_estados[x-1][y] = estados["contaminante"] #se contamina la casilla
                        temp_concentraciones[x][y] = max(temp_concentraciones[x][y]-saltos, concentracion_min) #la concentración sera el maximo entre maximo entre la concentracion minima y la presente en esa casilla menos el salto
                        if (temp_concentraciones[x-1][y]==0):
                            temp_concentraciones[x-1][y] = concentracion_min #si es igual a cero, la cambiamos  a la concentración minima
                        else:
                            temp_concentraciones[x-1][y] = min(temp_concentraciones[x-1][y]+saltos, concentracion_contaminante) #el minimo entre la anterior mas el salto y el normal


                    if(y+1 < casillas_y and random.random() < probabilidad_difusion and temp_concentraciones[x][y] > concentracion_min): #para y
                        temp_estados[x][y+1] = estados["contaminante"]#si hay contaminante
                        temp_concentraciones[x][y] = max(temp_concentraciones[x][y]-saltos, concentracion_min)
                        if (temp_concentraciones[x][y+1]==0):
                            temp_concentraciones[x][y+1] = concentracion_min
                        else:
                            temp_concentraciones[x][y+1] = min(temp_concentraciones[x][y+1]+saltos, concentracion_contaminante) #se repite para un movimiento en y

                    if(y-1 >= 0 and random.random() < probabilidad_difusion and temp_concentraciones[x][y] > concentracion_min): #se repite para el anterior
                        temp_estados[x][y-1] = estados["contaminante"]
                        temp_concentraciones[x][y] = max(temp_concentraciones[x][y]-saltos, concentracion_min)
                        if (temp_concentraciones[x][y-1]==0):
                            temp_concentraciones[x][y-1] = concentracion_min
                        else:
                            temp_concentraciones[x][y-1] = min(temp_concentraciones[x][y-1]+saltos, concentracion_contaminante)

                    if(x+1< casillas_x and random.random() < probabilidad_difusion and temp_concentraciones[x][y] > concentracion_min): #se hace para la casilla anterior en x
                        temp_estados[x+1][y] = estados["contaminante"]
                        temp_concentraciones[x][y] = max(temp_concentraciones[x][y]-saltos, concentracion_min)
                        if (temp_concentraciones[x+1][y]==0):
                            temp_concentraciones[x+1][y] = concentracion_min
                        else:
                            temp_concentraciones[x+1][y] = min(temp_concentraciones[x+1][y]+saltos, concentracion_contaminante)

        estado_casillas = numpy.copy(temp_estados)
        concentraciones_agua = numpy.copy(temp_concentraciones) #se actualizan los estados

    ventana.fill(colores["blanco"])

    # dibujar la cuadricula----------------------
    for x in range(casillas_x):
        for y in range(casillas_y):
            polygono = [(x*dimension_cuadricula, (y+1)*dimension_cuadricula),
                        ((x+1)*dimension_cuadricula, (y+1)*dimension_cuadricula),
                        ((x+1)*dimension_cuadricula, (y+2)*dimension_cuadricula),
                        (x*dimension_cuadricula, (y+2)*dimension_cuadricula)] #puntos a colorear

            if(x<=int(casillas_x*largo_tierra)):
                llave = encontrar_llave(estados, estado_casillas[x][y])
                pygame.draw.polygon(ventana, colores[llave], polygono, 0) #colorea sobre una superficie
            else:
                if(estado_casillas[x][y] == estados["contaminante"]):
                    c = concentraciones_agua[x][y]
                    c_min = concentracion_min
                    c_max = concentracion_contaminante
                    R =int(221*(c-c_min)/(c_max - c_min)) #cambia la intensidad segun la concentración
                    G = int(35*(c-c_min)/(c_max - c_min) + 150)
                    B = int((200*(c_min-c))/(c_max-c_min) + 200)

                    pygame.draw.polygon(ventana,(R, G, B), polygono, 0)
                else:
                    pygame.draw.polygon(ventana,colores["agua"], polygono, 0)




    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------
    #-------------------------texto superior-------------------------------------
    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------

    texto_colocar = "Estado: " + ("Pausado" if pausa else "Ejecutandose") 



    texto = fuente.render(texto_colocar, True, colores["negro"]) #genera la fuente apartir del texto y su color 
    ventana.blit(texto, (1, 3))#este coloca el texto en la posicion correcta en la ventana 
    
    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------
    #----------------------------------------------------------------------------

    pygame.display.flip()
    reloj.tick(30)

pygame.quit()
