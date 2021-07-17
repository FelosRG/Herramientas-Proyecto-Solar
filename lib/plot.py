#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 08:48:42 2021

@author: felos
"""
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

def Contraste(array,contraste):
     array = array / 255                           # Normalizamos pixeles
     array = np.exp(-array*contraste)              # Aplicamos función del contraste
     array = abs(array - 1)                        # Arregleamos el flip 
     array = array*255    
     return array

def plot(array,contraste,dir_guardado=""):
    "Apicación del contraste y guardado."
    
    if contraste != 0:                      
       array = Contraste(array,contraste)                      # Reescalamos
       
    plt.figure(figsize=(10,10))
    plt.imshow(array,cmap="gray")
    #plt.axis("on")
    plt.grid(True)
    
    if dir_guardado != "":
        plt.savefig(dir_guardado, bbox_inches=0)
        plt.close()
    

def cmap_banda13():
    "Obtiene un custom c_map adecuato para la banda 13"
    
    inicio = -110
    final  = 57
    dt     = final - inicio
    
    ini_gist_yarg = -110
    fin_gist_yarg = -68
    dy            = fin_gist_yarg - ini_gist_yarg
    
    ini_hsv = -68
    fin_hsv = -52
    dh = fin_hsv - ini_hsv
    
    ini_ocean = -52
    fin_ocean = -43
    do = fin_ocean - ini_ocean
    
    long_yarg = int(256*dy/dt)
    long_hsv  = int(256*dh/dt)
    long_do   = int(256*do/dt)
    long_db   = 256 - long_yarg - long_hsv - long_do
    
    gist_yarg = cm.get_cmap('gist_yarg', 256 )
    hsv       = cm.get_cmap('hsv'      , 256 )
    ocean     = cm.get_cmap("ocean"    , 256 )
    binary    = cm.get_cmap('binary'   , 256 )
    
    gist_yarg_parte  = gist_yarg(np.linspace(0,1,long_yarg  ))
    hsv_parte        =       hsv(np.linspace(0,0.29,long_hsv ))
    ocean_parte      =     ocean(np.linspace(0,1,long_do    ))
    binary_parte     =    binary(np.linspace(0,1,long_db    ))
    
    custom_cmap_array = np.concatenate([gist_yarg_parte,hsv_parte,ocean_parte,binary_parte])
    
    custom_cmap = ListedColormap(custom_cmap_array)
    
    return custom_cmap
    
def cortarYcentrar(topo,x,y ,ventana=200):
    "Hace el recorte de la comunidad."
    
    # Revisa que se respete los límites de la imágen.
    lim_izquierdo = max(x-ventana,0)
    lim_derecho   = min(x+ventana,topo.shape[1])
    lim_inferior = max(y-ventana,0)
    lim_superior = min(y+ventana,topo.shape[0])
    
    if lim_izquierdo == 0:
        lim_derecho = lim_izquierdo + ventana
        print("WARNING")
        
    if lim_derecho == topo.shape[1]:
        lim_izquierdo = lim_derecho - ventana
        print("WARNING")
    if lim_inferior == 0:
        lim_superior = lim_inferior + ventana
        print("WARNING")
    if lim_superior == topo.shape[0]:
        lim_inferior == lim_superior - ventana
        print("WARNING")
    if len(topo.shape) == 3:
    	array = topo[ lim_inferior:lim_superior ,lim_izquierdo:lim_derecho,:]
    else:
    	array = topo[ lim_inferior:lim_superior ,lim_izquierdo:lim_derecho]
    return array

def plotComunidad(array,centro_px,centro_py,ventana=200,contraste=5,dir_guardado=""):
    "Recorte y centrado de la comunidad "
    array = cortarYcentrar(array,centro_px,centro_py,ventana)
    plot(array,contraste,dir_guardado)
    
  
def guardarComunidad(array,centro_px,centro_py,dir_guardado,ventana=200,contraste=5):
    array = cortarYcentrar(array,centro_px,centro_py,ventana)
    array = Contraste(array,contraste)
    
    # Estiramos linealmente.
    #min_value = np.min(array)
    #max_value = np.max(array)
    #scale = 255 / (max_value - min_value)
    #array = scale*(array - min_value)
    
    
    array = array.astype(dtype='uint8')  
    img = Image.fromarray(array)
    img.save(dir_guardado)
    
      
    
    
    
