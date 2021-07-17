# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from ftplib import FTP
import time

url_base = "ftp.avl.class.noaa.gov"
user     = "felos"


def obtenerLista(ftp_object):
    " Obtiene una lista con los archivos en el directorio actual del ftp."

    lista_detalles_archivos  = []

    def añadirLista(string):
        "callback para ftp.retrlines,añade a una lista el nombre de cada archivo."

        lista_detalles_archivos.append(string)
    # mediante el callback añadimos ls nombres de cada archivo a la lista
    ftp_object.retrlines('LIST',callback=añadirLista)
    # la lista contiene ademas de los nombres, detalles extra como permisos o fecha, filtramos el nombre.
    lista_nombres = []
    for detalle in lista_detalles_archivos:
        nombre_archivo = detalle.split(" ")[-1]
        lista_nombres.append(nombre_archivo)
    
    return lista_nombres

def descargaDato(ftp_object,nombre_archivo,nombre_output,verbose=False):
    " Realiza la descarga desde el servidor FTP dado el nombre del archivo. "
    with open(nombre_output,"wb") as archivo:
        if verbose:
            print(ftp_object.retrbinary('RETR ' + nombre_archivo, archivo.write))
        else:
            ftp_object.retrbinary('RETR ' + nombre_archivo, archivo.write)



def descargarOrden(num_orden,verbose=False,path_salida=""):
    " Descarga una orden soliciada al sitio CLASS de la NOAA"
    
    url_base = "ftp.avl.class.noaa.gov"
    # Iniciamos conexión
    ftp      = FTP(url_base)
    ftp.login()
    # Entramos al directorio
    path = str(num_orden) + "/001"
    ftp.cwd(path)
    # Obtenemos lista de los archivos
    lista_nombres = obtenerLista(ftp)
    # Iniciando descarga de los archivos.
    for nombre_archivo in lista_nombres:
        descarga_correcta = False
        while descarga_correcta == False:
            try:
                descargaDato(ftp,nombre_archivo,path_salida + nombre_archivo,verbose=verbose)
            except:
                print("Descarga incorrecta volviendolo a intentar ...")
                time.sleep(5)
            else:
                descarga_correcta = True
    print("Descarga completada!")


    
