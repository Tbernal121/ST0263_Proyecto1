## ST-0263 Topicos en Telemática

## Estudiantes:
-Daniel Pineda(dpinedav@eafit.edu.co)

-Tomas Bernal Zuluaga(tberalz@eafit.edu.co)

-Andres leonardo Rojas Peña(alrojasp@eafit.edu.co)

## Profesor: Edwin Nelson Montoya(emontoya@eafit.edu.co)

## 1.Breve descripción del proyecto:
El proyecto abarca la creación de un sistema de almacenamiento distribuido, el cual opera bajo una estructura de  cliente-servidor. Este sistema empleará Python para programar tanto los datanodes como el cliente, y Docker para el manejo del NameNode. La estructura del sistema se fundamenta en un NameNode central y varios DataNodes que interactúan a través del protocolo gRPC, dedicados a almacenar y organizar archivos de forma distribuida. La meta de este proyecto fue desarrollar las capacidades esenciales de un sistema de este tipo, tales como la replicación de datos, aseguramiento de la disponibilidad de los nodos y el correcto manejo de fallos.

### 1.1 Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
- Implementacion de la función write y read de un archivo realidada por cliente
- Correcto Particionamiento de los archivos
- Presencia de bloques en al menos 2 dataNodes
- Cambio de leader si en algún momento este falla

### 1.2 Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

## 2.Información general de diseño de alto nivel, arquitectura, patrones.
### 2.1 Componentes:
- Client: Aplicación desarollada en el lenguaje Pyhton
- Namenode: Servidor que da respuesta a peticiones de cliente
- Datanode: Nodos que almacenan los archivos en bloques
  
### 2.2 Patrones:

-Cliente-servidor: Se usa este modelo ya que el cliente es el que realiza las peticiones a un servidor, en este caso es el Namenode y este se conecta con los datanodes, para realizar todas las tareas.

-gRPC: Para la comunicación entre componentes se utilizará el protocolo gRPC. Este protocolo no solo garantiza que los datos lleguen a su destino, sino que también proporciona un alto rendimiento. Es por eso que no se optó por MOM, ya que se requiere una comunicación más estrecha y en tiempo real entre sus componentes, además de que no se necesitas garantizar la entrega de mensajes incluso en caso de fallos de red o de componentes.

![diseño](https://github.com/Tbernal121/ST0263_Proyecto1/assets/92877092/437e0e9c-14a2-406a-9a36-ff6072a5f87b)

## 2.3 Partición y manejo de archivos

Nuestro proyecto incluye una funcionalidad que permite dividir archivos grandes en segmentos de 256 bytes y almacenarlos en un directorio designado, facilitando así su manejo y transferencia. Cuando se requiere, estas partes se pueden reensamblar para reconstruir el archivo original. Este proceso de partición y unión asegura una gestión eficaz de archivos de gran tamaño, optimizando el uso del espacio de almacenamiento y mejorando la eficiencia en la transferencia de datos.

## 2.4 Mantenimiento de la Red
El mantenimiento de la red en nuestro proyecto esta centrado en la configuración y el  despliegue de servicios que interactúan entre sí. Los servicios como Client, DataNode y NameNode se implementan sobre una infraestructura de red diseñada para comunicarse eficientemente.

## 2.5 Mantenimiento del Directorio y Uso de Docker
El proyecto utiliza Docker para manejar el mantenimiento de los directorios de DataNode y NameNode, como se evidencia en los archivos docker-compose-datanode.yml y docker-compose-namenode.yml. Estos archivos contienen configuraciones para desplegar estos nodos de forma aislada y manejable, esta práctica nos ayuda a simplificar la configuración del proyecto.

## 3 Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.
NameNode:
- lenguaje de programación: Python
- librerias y paquetes: Especificados en requirements.txt en carpeta NameNode
- Como se compila y ejecuta: Primero se deben instalar las dependencias de NameNode/requirements.txt, para despues ejecutar este comando NameNode/nameNode.py

DataNode:
- lenguaje de programación: Python
- librerias y paquetes: Especificados en requirements.txt en carpeta DataNode
- Como se compila y ejecuta: Primero se deben instalar las dependencias de DataNode/requirements.txt, para despues ejecutar este comando DataNode/dataNode.py

Client:
- lenguaje de programación: Python
- librerias y paquetes: Especificados en requirements.txt en carpeta 
- Como se compila y ejecuta: Primero se deben instalar las dependencias de /requirements.txt, para despues ejecutar este comando Client/client.py

### descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)
-Para configurar parametros del proyecto, se tiene que modificar el archivo.env
## Detalles de la organización del código por carpetas o descripción de algún archivo.
```
D:.
|   .gitignore
|   docker-compose-datanode.yml
|   docker-compose-namenode.yml
|   README.md
|
+---Client
|   |   .env
|   |   client.py
|   |   partitionManagement.py
|   |   __init__.py
|   |
|   \---files
|           1mb.txt
|           20mb.txt
|           himno.txt
|           prueba.txt
|
+---DataNode
|       .env
|       dataNode.py
|       dockerfile
|       requirements.txt
|       __init__.py
|
+---NameNode
|       .env
|       dockerfile
|       nameNode.py
|       requirements.txt
|       __init__.py
|
\---Protobufs
    |   makefile
    |   Service.proto
    |   Service_pb2.py
    |   Service_pb2_grpc.py
    |   __init__.py
    |
    \---__pycache__
            Service_pb2.cpython-311.pyc
            Service_pb2_grpc.cpython-311.pyc
            __init__.cpython-311.pyc

```
# Instructions for Running the DFS (Distributed File System)

Follow this order to run the files:

1. `NameNode/nameNode.py`
2. `DataNode/dataNode.py`
3. `Client/client.py`

## How to Run a File?

To run a file, use the following command in your terminal:

```bash
python fileName.py
