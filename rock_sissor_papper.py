# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 11:12:40 2021

@author: Gabriel  Angel
"""


import cv2
import numpy as np
import imutils
import random

opciones = ['ROCK','PAPER','SCISSORS']
magia =random.randint(0,2)
magia2= random.randint(0,2)
magia3 = random.randint(0,2)



cap = cv2.VideoCapture(0)
bg=None

color_start= (204,204,0)
color_end= (204,0,204)
color_far= (255,0,0)

color_start_far=(204,204,0)
color_far_end=(204,0,204)
color_start_end=(0,255,255)

color_contorno=(0,255,0)
color_ymin=(0,130,255)
color_angulo=(0,255,255)
color_d=(0,255,255)
color_fingers=(0,255,255)

color_win=(0,255,0)
color_lose=(0,0,255)
color_compu=(12,139,250)
color_draw =(255,0,0)

while True: 
    ret, frame = cap.read()
    
    frame = imutils.resize(frame, width=640)
    frame = cv2.flip(frame,1)
    frameAux= frame.copy()

    
    if bg is not None:
        #cv2.imshow('bg',bg)
        
        # Determinar la región de interés
      
        
        ROI = frame [50:300,380:600]
        cv2.rectangle(frame,(380-2,50-2),(600+2,300+2),color_fingers,1)
        grayROI = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
        
        bgROI = bg[50:300,380:600]
        
        #cv2.imshow('ROI', ROI)
        #cv2.imshow('grayROI', grayROI)
        #cv2.imshow('bgROI', bgROI)
        
        dif =cv2.absdiff(grayROI,bgROI)
        _, th = cv2.threshold(dif,30,255,cv2.THRESH_BINARY)
        th = cv2.medianBlur(th,7)
        
        #cv2.imshow('dif',dif)
        #cv2.imshow('th',th)
        
        cnts, _ = cv2.findContours(th,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key=cv2.contourArea,reverse=True)[:1]
        #cv2.drawContours(ROI,cnts,0,(0,255,0),1)
        
        
        
        for cnt in cnts:
            # Encontrar el centro del contorno
            M = cv2.moments(cnt)
            if M["m00"] == 0: M["m00"]=1
            x = int(M["m10"]/M["m00"])
            y = int(M["m01"]/M["m00"])
            cv2.circle(ROI,tuple([x,y]),5,(0,255,0),-1)
            # Punto más alto del contorno
            ymin = cnt.min(axis=1)
            cv2.circle(ROI,tuple(ymin[0]),5,color_ymin,-1)
            # Contorno encontrado a través de cv2.convexHull
            hull1 = cv2.convexHull(cnt)
            cv2.drawContours(ROI,[hull1],0,color_contorno,2)
            # Defectos convexos
            hull2 = cv2.convexHull(cnt,returnPoints=False)
            defects = cv2.convexityDefects(cnt,hull2)
      
            # Seguimos con la condición si es que existen defectos convexos
            if defects is not None:
                inicio = [] # Contenedor en donde se almacenarán los puntos iniciales de los defectos convexos
                fin = [] # Contenedor en donde se almacenarán los puntos finales de los defectos convexos
                fingers = 0 # Contador para el número de dedos levantados
               
                for i in range(defects.shape[0]):
                      s,e,f,d = defects[i,0]
                      start = cnt[s][0]
                      end = cnt[e][0]
                      far = cnt[f][0]
                      
                      # Encontrar el triángulo asociado a cada defecto convexo para determinar ángulo                    
                      a = np.linalg.norm(far-end)
                      b = np.linalg.norm(far-start)
                      c = np.linalg.norm(start-end)
                      
                      angulo = np.arccos((np.power(a,2)+np.power(b,2)-np.power(c,2))/(2*a*b))
                      angulo = np.degrees(angulo)
                      angulo = int(angulo)
                       
                      # Se descartarán los defectos convexos encontrados de acuerdo a la distnacia
                      # entre los puntos inicial, final y más alelago, por el ángulo y d
                      if np.linalg.norm(start-end) > 20 and angulo < 90 and d > 12000:
                               
                          # Almacenamos todos los puntos iniciales y finales que han sido
                          # obtenidos
                          inicio.append(start)
                          fin.append(end)
                           
                          # Visualización de distintos datos obtenidos
                          #cv2.putText(ROI,'{}'.format(angulo),tuple(far), 1, 1.5,color_angulo,2,cv2.LINE_AA)
                          #cv2.putText(ROI,'{}'.format(d),tuple(far), 1, 1.1,color_d,1,cv2.LINE_AA)
                          cv2.circle(ROI,tuple(start),5,color_start,2)
                          cv2.circle(ROI,tuple(end),5,color_end,2)
                          cv2.circle(ROI,tuple(far),7,color_far,-1)
                          #cv2.line(ROI,tuple(start),tuple(far),color_start_far,2)
                          #cv2.line(ROI,tuple(far),tuple(end),color_far_end,2)
                          #cv2.line(ROI,tuple(start),tuple(end),color_start_end,2)
                        # Si no se han almacenado puntos de inicio (o fin), puede tratarse de
                        # 0 dedos levantados o 1 dedo levantado
                if len(inicio)==0:
                
                    minY = np.linalg.norm(ymin[0]-[x,y])                    
                    if minY >= 110:
                        fingers = fingers +1
                        cv2.putText(ROI,'{}'.format(fingers),tuple(ymin[0]), 1, 1.7,(color_fingers),1,cv2.LINE_AA)

                for i in range(len(inicio)):
                    
                    fingers = fingers + 1
                    cv2.putText(ROI,'{}'.format(fingers),tuple(inicio[i]), 1, 1.7,(color_fingers),1,cv2.LINE_AA)
                    if i == len(inicio)-1:
                        fingers = fingers + 1
                        cv2.putText(ROI,'{}'.format(fingers),tuple(fin[i]), 1, 1.7,(color_fingers),1,cv2.LINE_AA)
    
                # Se visualiza el número de dedos levantados en el rectángulo izquierdo
                #cv2.putText(frame,'{}'.format(fingers),(390,45), 1, 4,(color_fingers),2,cv2.LINE_AA)
                if fingers == 0 or fingers == 1:
                
                    cv2.putText(frame, 'ROCK', (390, 45), 1, 4, (color_fingers), 2, cv2.LINE_AA)
                    yo1 = 'ROCK'
                    #computadora1= 'papel'
                    
                    # Mediante un rand seleccionamos la opcion de la computadora
                    
                    compu= opciones[magia]
                    print('eleccion computadora',compu)
                    
                    cv2.putText(frame, 'VS', (330, 45), 1, 2, (color_compu), 2, cv2.LINE_AA)
                    cv2.putText(frame, 'COMPUTER', (40, 80), 1, 2, (color_compu), 2, cv2.LINE_AA)
                    cv2.putText(frame, compu, (40, 45), 1, 3.5, (color_compu), 2, cv2.LINE_AA)
                    
                    # Realizamos la logica del juego piedra papel tijera
                    if (yo1 == compu):
                        cv2.putText(frame, 'DRAW', (200, 400), 1, 3.5, (color_draw), 2, cv2.LINE_AA)
                        print('empate')
                    if (yo1 == 'ROCK'):
                        if (compu == 'SCISSORS'):
                            cv2.putText(frame, 'YOU WIN', (170, 400), 1, 3.5, (color_win), 2, cv2.LINE_AA)
                            print('Ganaste')
                        if (compu == 'PAPER'):
                            cv2.putText(frame, 'YOU LOSE', (170, 400), 1, 3.5, (color_lose), 2, cv2.LINE_AA)
                            print('perdiste')
                        
                    
                    
                else:
                    if fingers == 2 or fingers == 3:
                        cv2.putText(frame, 'SCISSORS', (390, 45), 1, 3.5, (color_fingers), 2, cv2.LINE_AA)
                        
                        yo2 = 'SCISSORS'
                        compu= opciones[magia2]
                        print('eleccion computadora',compu)
                        
                        cv2.putText(frame, 'VS', (330, 45), 1, 2, (color_compu), 2, cv2.LINE_AA)
                        cv2.putText(frame, 'COMPUTADORA', (40, 80), 1, 2, (color_compu), 2, cv2.LINE_AA)
                        cv2.putText(frame, compu, (40, 45), 1, 3.5, (color_compu), 2, cv2.LINE_AA)
                        
                        if (yo2 == compu):
                            cv2.putText(frame, 'DRAW', (200, 400), 1, 3.5, (color_draw), 2, cv2.LINE_AA)
                            print('empate')
                        if (yo2 == 'SCISSORS'):
                            if (compu == 'ROCK'):
                                cv2.putText(frame, 'YOU LOSE', (170, 400), 1, 3.5, (color_lose), 2, cv2.LINE_AA)
                                print('perdiste')
                            if (compu == 'PAPER'):
                                cv2.putText(frame, 'YOU WIN', (170, 400), 1, 3.5, (color_win), 2, cv2.LINE_AA)
                                print('Ganaste')
                        
                        
                    else:
                        if fingers == 4 or fingers == 5:
                            cv2.putText(frame, 'PAPER', (390, 45), 1, 3.5, (color_fingers), 2, cv2.LINE_AA)
                            
                            yo3 = 'PAPER'
                            compu= opciones[magia3]
                            print('eleccion computadora',compu)
                            
                            cv2.putText(frame, 'VS', (330, 45), 1, 2, (color_compu), 2, cv2.LINE_AA)
                            cv2.putText(frame, 'COMPUTADORA', (40, 80), 1, 2, (color_compu), 2, cv2.LINE_AA)
                            cv2.putText(frame, compu, (40, 45), 1, 3.5, (color_compu), 2, cv2.LINE_AA)
                    
                            if (yo3 == compu):
                                cv2.putText(frame, 'DRAW', (200, 400), 1, 3.5, (color_draw), 2, cv2.LINE_AA)
                                print('empate')
                            if (yo3 == 'PAPER'):
                                if (compu == 'ROCK'):
                                    cv2.putText(frame, 'YOU WIN', (170, 400), 1, 3.5, (color_win), 2, cv2.LINE_AA)
                                    print('perdiste')
                                if (compu == 'SCISSORS'):
                                    cv2.putText(frame, 'YOU LOSE', (170, 400), 1, 3.5, (color_lose), 2, cv2.LINE_AA)
                                    print('Ganaste')
                    
        cv2.imshow('th',th)
    # Display the frame
    cv2.imshow('frame',frame)
    
    k= cv2.waitKey(20)
    if k == ord("i"):
        bg = cv2.cvtColor(frameAux,cv2.COLOR_BGR2GRAY)

    #if cv2.waitKey(1) & 0xFF == ord('q'):
        #break
    
    if k == 27:
        break

# Close the camera connection and all windows
cap.release()
cv2.destroyAllWindows()

# BIOGRAPHY
# Example5.py, Edwin R. Salcedo
# https://www.youtube.com/watch?v=nVkX7wC25g4&list=PLQPS-rf5qhUp331AU96gGYfB2Qy5EH5Iz&index=7&t=14s
# https://www.youtube.com/watch?v=v-XcmsYlzjA&t=0s
# https://pierfrancesco-soffritti.medium.com/handy-hands-detection-with-opencv-ac6e9fb3cec1
# https://www.superprof.es/apuntes/escolar/matematicas/trigonometria/4-resolver-un-triangulo-conociendo-los-tres-lados.html
# https://customers.pyimagesearch.com/lesson-sample-advanced-contour-properties/


        