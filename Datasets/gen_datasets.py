"""
README

Script de combinación de datasets.

El objetivo de este  script es combinar las  diferentes fuentes 
de  datos (datos satélitales y datos  de radiación solar)  para
generar un único dataset con toda la información. Esto se logra
emparejando  cada dato de todas las fuentes de datos de acuerdo 
a la fecha  y hora  de cada uno deesos datos. Además se realiza
un procesado final a los datos.

IMPORTANTE!

* Es necesario haber ejecutado los scripts de "descarga_GOES.py"
  y "descarga_NSRDB.py".
"""

# CONFIGURACIONES
# ---------------

# Datos satélitales que conformarán el dataset final.
VENTANA = 5     # --> Ventana de recorte.
BANDAS  = [4,6]   # --> Bandas que conformarán el dataset.

# Configuración de sincronización
LONGITUD_SECUENCIA    = 1  
UMBRAL_SINCRONIZACIÓN = 3  # minutos (recomendado 2).
UMBRAL_SERIE          = 7  # minutos (recomendado 7), se ignora si LONGITUD_SECUENCIA = 1. 

DATOS_NSRDB = ["GHI","Solar Zenith Angle","Clearsky GHI"]
# Guarda el datset final completo en un único archivo.
UNIR_BATCHES = True

# -------------------------------------------------------------------

import os
import sys

from numpy.core.numeric import indices
_path_script    = os.path.realpath(__file__) 
_path_script    = "/".join(_path_script.split("/")[:-1])
sys.path.append(_path_script + "/../")

import h5py
import config
import datetime
import numpy  as np
import pandas as pd 
import lib.libGOES as goes
import lib.libSinc as Sinc
import lib.f_generales as general

from   pathlib import Path

# Abrimos el archivo de pre-configuración.
print("Cargando archivo de configuración...")
días_descarga = config.cargar_mask_temporal()
Lat,Lon,mask  = config.cargar_mask_espacial()
Path(config.PATH_DATASET_FINAL).mkdir(parents=True,exist_ok=True)

# Revisamos que las bandas puestas estén descargada.
print("Revisando la existencia de todos los archivos a usar...")
for num_banda in BANDAS:
    if os.path.exists(config.PATH_DATASET_GOES + "4/") == False: raise FileNotFoundError(f"No se encontro el dataset de la banda {num_banda}")


def nombre_dataset():
    nombre = ""
    nombre += f"Ventana_{VENTANA}-"
    nombre += f"Bandas_"
    for banda in BANDAS:
        nombre += f"{banda}_"
    nombre += f"-Secuencia_{LONGITUD_SECUENCIA}-"
    nombre += f"Resolucion_{config.RESOLUCIÓN}-NSRDB"
    return nombre + ".h5"

# Definimos los callbacks para obtener la lista de datetime.
def datetime_bandas(T):
    "Obtenemos lista de objetos datetime de las bandas."
    lista_datetime = [goes.obtenerFecha_GOES(int(t),return_datetime=True) for t in T]
    return lista_datetime
def datetime_NSRDB(df):
    "Obtenemos lista de objetos datetime del NSRDB"
    año = df["Year"].values
    mes = df["Month"].values
    dia = df["Day"].values
    hora = df["Hour"].values
    minu = df["Minute"].values
    lista_datetime = [datetime.datetime(año[i],mes[i],dia[i],hora[i],minu[i]) for i  in range(len(año))]
    return lista_datetime

# Scritpt de procesado de batch
def procesar_batch(nombre_batch):

    # Generamos un dato con temporalidad por cada banda.
    datos_temporales = []
    for banda in BANDAS:
        # Abrimos batch.
        with h5py.File(config.PATH_DATASET_GOES + f"{banda}/"+ nombre_batch+ "h5","r") as batch:
            Arrays = batch["Datos"][()]
            DQF    = batch["DQF"][()]
            T      = batch["T"][()]
        lista_datetime = datetime_bandas(T)

        Datos = np.stack([Arrays,DQF]).reshape(-1,2,config.VENTANA_RECORTE*2,config.VENTANA_RECORTE*2)
        Datos = list(Datos)
        datos_temporales.append(Sinc.DatosTemporales(lista_datos=Datos,lista_datetime=lista_datetime))

    print("\nGenerando objeto temporal de archivo csv del NSRDB...")
    # Le añadimos el dato temporal de los datos de NSRDB.
    df = pd.read_csv(config.PATH_DESCARGA_NSRDB + nombre_batch + "csv")
    lista_datetime = datetime_NSRDB(df)
    datos_temporales.append(Sinc.DatosTemporales(lista_datos=df,lista_datetime=lista_datetime))

    # Iniciamos sincronización
    print("Sincronizando datos...")
    sincronizador = Sinc.Sincronizador(datos_temporales,verbose=True)
    serie_tiempo  = sincronizador.generarSerieTiempo(UMBRAL_SINCRONIZACIÓN*60,UMBRAL_SERIE*60,longitud=LONGITUD_SECUENCIA)
    serie_tiempo  = np.array(serie_tiempo)
    num_series    = serie_tiempo.shape[0]

    print("Extrayendo los datos de la sincronización.")
    # Obtenemos los datos asociados a las bandas.
    datos_GOES = {}
    for i,banda in zip(range(len(BANDAS)),BANDAS):
        datos_GOES[str(banda)] = np.take(np.array(datos_temporales[i].lista_datos),serie_tiempo[:,i],axis=0)
    # Obtenemos los datos asociados a NSRDB
    datos_NSRDB = {} 
    for columna in DATOS_NSRDB:
        datos_NSRDB[columna] = df[columna].iloc[serie_tiempo[:,-1]].values

    print("Iniciando procesamiento final...")
    print("Recortando los arrays a la ventana especificada...")
    for banda in BANDAS:
        array = datos_GOES[str(banda)]
        array = array[:,:,config.VENTANA_RECORTE - VENTANA:config.VENTANA_RECORTE + VENTANA,config.VENTANA_RECORTE - VENTANA:config.VENTANA_RECORTE + VENTANA]
        datos_GOES[str(banda)] = array
    
    print("Realizando los checks con los flags de los datos satelitales...")

    # Revisamos datos inválidos.
    indices_validos  = []
    for i in range(datos_GOES[str(BANDAS[0])].shape[0]):
        puntos_invalidos = 0
        for banda in BANDAS:
            for flag in config.FLAGS_GOES:
                puntos_invalidos += np.sum(datos_GOES[str(banda)][i,1,:,:] == flag)
        if puntos_invalidos == 0:
            indices_validos.append(i)
    
    # Extraemos datos válidos.
    for banda in BANDAS:
        datos = datos_GOES[str(banda)][:,0,:,:]
        datos = datos[indices_validos,:,:]
        datos_GOES[str(banda)] = datos
    for columna in DATOS_NSRDB:
        datos_NSRDB[columna] = datos_NSRDB[columna][indices_validos]
    
    return datos_GOES,datos_NSRDB

if __name__ == "__main__":
    num_batch_procesados = 0
    num_batch_totales    = np.sum(mask)

    # diccionarios para concatenar datos
    datos_GOES,datos_NSRDB = {} , {}
    for banda in BANDAS:
        datos_GOES[str(banda)] = []
    for columna in DATOS_NSRDB:
        datos_NSRDB[columna] = []
    
    # Obtenemos el nombre del batch (sin la extención).
    for i in range(config.RESOLUCIÓN):
        for j in range(config.RESOLUCIÓN):
            if mask[i,j]:
                lat , lon = Lat[i,j],Lon[i,j]
                nombre_batch = general.asignarNombreArchivo(lat=lat,lon=lon,extensión="")
                batch_datos_GOES,batch_datos_NSRDB = procesar_batch(nombre_batch)
                if UNIR_BATCHES:
                    # Juntamos todo en un diccionario.
                    for banda in BANDAS:
                        datos_GOES[str(banda)].append(batch_datos_GOES[str(banda)])
                    for columna in DATOS_NSRDB:
                        datos_NSRDB[columna].append(batch_datos_NSRDB[columna])
                else:
                    raise NotImplementedError("Aun no implemento el caso de no unir batches.")

                num_batch_procesados += 1
                print(f"Batch procesados {num_batch_procesados} de {num_batch_totales}")
    
    # Concatenamos y guardamos.
    print("\nGuardando datos...")
    nombre_dataset_final =  config.PATH_DATASET_FINAL +  nombre_dataset()
    with h5py.File(nombre_dataset_final,"w") as dataset:
        for banda in BANDAS:
            datos_GOES[str(banda)] = np.concatenate(datos_GOES[str(banda)],axis=0)
            print(f"shape  datos banda {banda}: {datos_GOES[str(banda)].shape}")
            dataset.create_dataset(name=str(banda),data=datos_GOES[str(banda)])
        for columna in DATOS_NSRDB:
            datos_NSRDB[columna] = np.concatenate(datos_NSRDB[columna],axis=0)
            print(f"shape columna {columna}: {datos_NSRDB[columna].shape}")
            dataset.create_dataset(name=columna,data=datos_NSRDB[columna])





