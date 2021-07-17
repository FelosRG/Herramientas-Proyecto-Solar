import pandas as pd
import numpy  as np

import lib.geo as geo

def NormaInf(x1,x2,y1,y2):
    "Obteine la norma infinito,compatible con listas en numpy."
    
    norma1 = np.stack([np.abs(x1-x2),np.abs(y1-y2)])
    return np.max(norma1,axis=0)


def obtenerLocalidades(px_x,px_y,df,ventana=200,coordenadas_desde_ventana=False):
    "Obtiene las localidades cercanas a unas coordenadas."
    # Obtener los valores de los pixeles de la localidad.
    lista_px_x  = df["px_x"].values
    lista_px_y  = df["px_y"].values
    # Obtiene las norma infinito de todas las localidades respecto al centro de la imágen.
    lista_normInf = NormaInf(px_x,lista_px_x,px_y,lista_px_y)
    # Encontramos las localidades dentro de la ventana de la imágen.
    Indexes   = np.where(lista_normInf < ventana)
    # Obtenemos las localidades del dataframe.
    df_localidades = df.iloc[Indexes]
    # Obtenemos los valores de los pixeles.
    lista_px_x = df_localidades["px_x"].values
    lista_px_y = df_localidades["px_y"].values
    # Si queremos las coordenadas con origen en la ventana recortada.
    if coordenadas_desde_ventana:
        lista_px_x = lista_px_x - px_x + ventana
        lista_px_y = lista_px_y - px_y + ventana
        
    return lista_px_x , lista_px_y 
    
