#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 08:33:13 2021

@author: felos
"""
import datetime
import math
import numpy as np

def degree2rad(degree):
    """Pasa de grados a radianes."""
    k   = math.pi / 180
    rad = degree*k
    return rad

def rad2degree(rad):
    """pasa de radianes a grados."""
    k     = 180 / math.pi
    degree = rad*k 
    return degree


def obtenerFecha(nc):
    "Devuelve un string con la fecha de la imágen"
    
    # Obtiene los segundos desde 2000-01-01 12:00
    t = float(np.array(nc.variables["t"]))
    
    # Con ayuda de la librería "datetime" obtenemos la fecha actual.
    fecha_inicio = datetime.datetime(2000,1,1,0,0,0)
    time_delta   = datetime.timedelta(seconds=t)

    fecha        = fecha_inicio + time_delta
    formato      = "%Y-%m-%d_%H-%M"
    return fecha.strftime(formato)

def obtenerBanda(nc):
    "Obtiene de que banda es el archivo nc "
    id_banda = np.array(nc.variables["band_id"])
    id_banda = int(id_banda)
    return id_banda


def irradiancia2temperatura(array,nc):
    """Pasa de los valores de irradiancia a grados 
    centígrados para las bandas emisoras"""
    
    fk1 = float(np.array(nc.variables["planck_fk1"]))
    fk2 = float(np.array(nc.variables["planck_fk2"]))
    bc1 = float(np.array(nc.variables["planck_bc1"]))
    bc2 = float(np.array(nc.variables["planck_bc2"]))
    
    a = np.log(1 + (fk1 / array))
    b = (fk2 / a - bc1)
    
    resultado  = b / bc2
    
    return resultado


def px2coordinates(nc,px_x,px_y):
    """Pasa de pixeles en la imágen a coordenadas."""
    # Parámetros del satélite.
    
    # Fixed Grid scanning angles.
    X = nc.variables["x"]
    Y = nc.variables["y"]
    # Longitud of proyection of the origin
    lambda_o = nc.variables["goes_imager_projection"].longitude_of_projection_origin
    lambda_o = degree2rad(lambda_o)
    # Semi major axis value
    r_eq   = 6378137          # [m]
    # Semi minor axis value
    r_pool = 6356752.31414    # [m]
    # Satellite Hight from center of earth [m]
    H      = 42164160         # [m]
    
    # Cálculos previos.
    frac_r = r_eq / r_pool
    
    coef1  = frac_r**2
    
    x = X[px_x]
    y = Y[px_y]
    
    cosx = math.cos(x)
    cosy = math.cos(y)
    sinx = math.sin(x)
    siny = math.sin(y)
    
    a = sinx**2 + (cosx**2)*(cosy**2 + coef1*siny**2)
    b = -2*H*cosx*cosy
    c = H**2 - r_eq**2
    
    r_s = (-b-math.sqrt(b**2 - 4*a*c)) / 2*a
    
    s_x =  r_s*cosx*cosy
    s_y = -r_s*sinx
    s_z =  r_s*cosx*siny
    
    coef2 = s_z / math.sqrt((H-s_x)**2 + s_y**2)
    
    coef3 = s_y / (H-s_x)
    
    latitud  = math.atan(coef1*coef2)
    longitud = lambda_o  - math.atan(coef3)
    
    # Pasamos de rads a grados.
    latitud  = rad2degree(latitud )
    longitud = rad2degree(longitud)
    
    return latitud , longitud

def coordinates2px(nc,latitud,longitud):
    """Pasa de coordenadas a localización en px."""
    # Parámetros del satélite.
    
    # Fixed Grid scanning angles.
    X = nc.variables["x"]
    Y = nc.variables["y"]
    # Longitud of proyection of the origin
    lambda_o = nc.variables["goes_imager_projection"].longitude_of_projection_origin
    lambda_o = degree2rad(lambda_o)
    # Semi major axis value
    r_eq   = 6378137          # [m]
    # Semi minor axis value
    r_pool = 6356752.31414    # [m]
    # Satellite Hight from center of earth [m]
    H      = 42164160         # [m]
    # exentricidad 
    e = 0.0818191910435
    
    # Pasamos de grados a radianes
    latitud  = degree2rad(latitud )
    longitud = degree2rad(longitud)
    
    # Cálculos intermedios
    coef1 = (r_pool / r_eq)**2
    
    phi_c = math.atan(coef1*math.tan(latitud))
    r_c   = r_pool / math.sqrt(1-(e*math.cos(phi_c))**2)
    
    s_x   = H - r_c*math.cos(phi_c)*math.cos(longitud-lambda_o)
    s_y   = -r_c*math.cos(phi_c)*math.sin(longitud -lambda_o)
    s_z   = r_c*math.sin(phi_c)
    
    # Revisamos la visiblidad desde el satélite.
    inequality1 = H*(H-s_x)
    inequality2 = s_y**2 + (s_z**2)*(r_eq/r_pool)**2
    message = "Coordenada no visibles desde el satélite."
    if inequality1 < inequality2:
        raise ValueError(message)
    
    # Obtenemos los ángulos delevación y escaneo N/S E/W.
    y = math.atan(s_z/s_x)
    x = math.asin(-s_y/math.sqrt(s_x**2 + s_y**2 + s_z**2))
    
    # De los ángulos de escaneo obtemos el pixel.
    
    # Si el array que contiene la variable X del .nc nos inidica que ángulo de escaneo le
    # ..  corresponde a cada pixel. ahora tenemos que encontrar "una situación inversa" , 
    # .. donde dado un ángulo de  escaneo en particular tenemos que encontrar su pixel. 
    # .. Esto no se puede hacer directo puesto que los ángulos de escaneo son números reales y la
    # .. posición de los pixeles se representa con enteros.
    # Para resolver este problema resto el ángulo de escaneo de nuestro interes con el array X, y
    # .. encuentro la posición o index del valor menor de esta diferencia.
    
    X_array = np.array(X)
    X_array = np.abs(X_array - x)
    px_x    = np.argmin(X_array)
    
    Y_array = np.array(Y)
    Y_array = np.abs(Y_array - y)
    px_y    = np.argmin(Y_array)
    
    return px_x , px_y
