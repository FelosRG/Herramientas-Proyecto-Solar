# Herramientas y librerías para el desarrollo del proyecto de predicción de recurso solar.

<b> !!! No hacer publico el código pues contiene credenciales privadas para algunas APIs !!!</b> <br> <br>
Recopilación de las herramientas adquiridas y desarrolladas para el proyecto solar, así como guías para su funcionamiento y uso.

### Contenido

<li type="circle"> <b> libGEOS </b> <br> 
  &emsp;  Contiene las funciones desarrolladas para trabajar con las imágenes satélitales. </li>
  
<li type="circle"> <b> libNSRDB </b> <br> 
  &emsp;  Contiene las funciones desarrolladas para descargar y trabajar con los datos del NSRDB.</li>
  
<li type="circle"> <b> Shapefiles </b> <br> 
  &emsp;  Contiene archivos con información geométrica reelevante para la generación de mapas y visualizaciónes. 
  
 
### Instalación de las liberías requeridas
Se requieren tener instaladas algunas librerías de python :
 
 <li type="circle"> Librería para la descarga de datos y archivos de documentos del GOES. <br>
  
 ```
pip3 install s3f3
```

 <li type="circle"> Libería para manejar archivos netCDF <br>
  
 ```
pip3 install netCDF4
```

Otras liberías requeridas:
pandas, numpy, matpotlib.

### Guía rápida libGOES

<li type="circle"> <b> Obtener la fecha de un netCDF4 Dataset  </b> <br>

 ```
libGOES.obtenerFecha_GOES(nc,return_datetime=False)
   
    """ Devuelve un string con la fecha de la imágen.
        
        return_datetime (bool): Si está en True, devuelve
        .. la fecha como objeto datetime. De lo contrario
        .. lo devuelve como string.
   
        !! Falta implementar que de la hora para otras zonas
        horarias.
    """
   
   return fecha
```
<br>

 <li type="circle"> <b>  Obtener a partir de la localización de coordenadas, la ubicación en pixeles en la imágen. </b> <br>

 ```
libGOES.coordinates2px_GOES(nc,latitud,longitud)
   
       """Pasa de coordenadas a localización en px.
          Returna una tupla con el índice que indica
          en que pixel estan las coordenadas descritas.
          
          !Es necesario proporcionar el netCDF4 Dataset como
          primera entrada
          
          ! La latitud y longitud deben de estar en número decimal.
       """
      
      return px_x , px_y
```
<br>

<li type="circle">  <b> Cortar y centrar una imágen del goes.  </b> <br>

 ```
libGOES.cortarYcentrar_GOES(array,x,y ,ventana=200)
    """
    Dado un par de pixeles (px_x , px_y),
    obtiene un subarray cuadrado, de radio (ventana),
    a partir del array introducido (array)
   
   returna el array recortado.
   
   ! La función se encarga de las siatuciones cuando la 
   ventana se sale de los límites del array original
   recortando la imágen.
    """
   
   return array
```
<br>
   
<li type="circle"> <b> Descarga del archivo más actual disponible para un producto. </b> <br>
   Para una lista de productos disponibles ver : https://docs.opendata.aws/noaa-goes16/cics-readme.html <br>
   Basado en la libería goes2go                : https://github.com/blaylockbk/goes2go/

 ```
libGOES.datosActualesGOES16(producto,
                        banda=None,
                        output_name="GOES-descarga.nc")
    """
    
    Descarga los datos más recientes de las categorias ingresadas, desde datos alojados en AWS.
    Los guarda en formato netCDF con el nombre ingresado en (output_name)
    
    Cuando el producto es de clase ABI-L1b-RadC es necesario introducir la bada
    que se desea descargar.
    
    LA FUNCIÓN SIGUE EN DESAROLLO, SOLO USAR CON PRODUCTOS EN EL DOMINIO DE CONUS.
    """
```
<br>
   
