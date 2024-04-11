#Proyecto 1 Telemática

##Integrantes:
-Daniel Pineda(dpinedav@eafit.edu.co)
-Tomas Bernal Zuluaga(tberalz@eafit.edu.co)
-Andres leonardo Rojas Peña(alrojasp@eafit.edu.co)

## 1.Breve descripción del proyecto:
El proyecto abarca la creación de un sistema de almacenamiento distribuido, el cual opera bajo una estructura de  cliente-servidor. Este sistema empleará Python para programar tanto los datanodes como el cliente, y Docker para el manejo del NameNode. La estructura del sistema se fundamenta en un NameNode central y varios DataNodes que interactúan a través del protocolo gRPC, dedicados a almacenar y organizar archivos de forma distribuida. La meta de este proyecto fue desarrollar las capacidades esenciales de un sistema de este tipo, tales como la replicación de datos, aseguramiento de la disponibilidad de los nodos y el correcto manejo de fallos.

### 1.1 Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
- Implementacion de la función write y read de un archivo realidada por cliente
- Correcto Particionamiento de los archivos
- Presencia de bloques en al menos 2 dataNodes
- Cambio de leader si en algún momento este falla

## 2.Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.
Componentes:
- Client: Aplicación desarollada en el lenguaje Pyhton
- Namenode: Servidor que da respuesta a peticiones de cliente
- Datanode: Nodos que almacenan los archivos en bloques

# Instructions for Running the DFS (Distributed File System)

Follow this order to run the files:

1. `NameNode/nameNode.py`
2. `DataNode/dataNode.py`
3. `Client/client.py`

## How to Run a File?

To run a file, use the following command in your terminal:

```bash
python fileName.py
