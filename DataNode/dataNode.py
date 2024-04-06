from concurrent import futures
import grpc
import os
import sys
import time
import threading
from dotenv import load_dotenv

load_dotenv() # Load enviroment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

channel_nameNode = grpc.insecure_channel(f'localhost:{os.getenv("NAMENODE_PORT")}')  # Address of the nameNode Leader
nameNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_nameNode)

class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):

    def __init__(self):
        self.blocks = {
            'block_id1': '1 ',
            'block_id2': '2 ',
            'block_id3': '3 ',
            'block_id4': '4 ',
            'block_id5': '5 ',
            'block_id6': '6 ',
            'block_id7': '7 ',
            'block_id8': '8 ',
            'block_id9': '9 ',
            'block_id10': '10 ',
            'block_id11': '11 ',
            'block_id12': '12 ',
        }        
       
    def SendHeartbeat(self):
        while True:
            heartbeat = Service_pb2.DataNodeID(id=os.getenv("PORT"))
            response = nameNode_stub.SendHeartbeat(heartbeat)
            print("Heartbeat sent")
            time.sleep(10)  # Wait for 10 seconds before sending the next heartbeat        
    
    def StoreBlock(self, request, context): # (block_id, data)
            block_id = request.id
            data = request.data
            self.blocks[block_id] = data  # Store the data block
            print(f"Block: {block_id} stored")
            return Service_pb2.Status(success=True, message=f"Block {block_id} stored successfully")

    def SendBlock(self, request, context): # (block_id, data, destination)
            block_id = request.id
            # Busca el ID del bloque en el diccionario de bloques almacenados
            if block_id in self.blocks:
                data = self.blocks[block_id]
                # Si se encuentra, devuelve los datos del bloque
                print(f"se encontró el bloque id: {block_id}. Sending...")
                return Service_pb2.BlockData(id=block_id, data=data)
            else:
                # Si no se encuentra, establece un código de error y un mensaje
                print(f"no se encontró el bloque id: {block_id}")
                return Service_pb2.BlockData()
   

    def DeleteBlock(self, request, context): # (block_id)
        # Implementa la lógica para eliminar un bloque de datos del dataNode
         block_id = request.id
         if block_id in self.blocks:
               # Si el bloque existe, eliminarlo
               del self.blocks[block_id]
               print(f"Block {block_id} deleted successfully.")
               return Service_pb2.Status(success=True, message=f"Block {block_id} deleted successfully")
         else:
               # Si el bloque no existe, retornar un mensaje de error
               print(f"Block {block_id} not found.")
               return Service_pb2.Status(success=False, message=f"Block {block_id} not found")

    def CleanStart(self, request, context):
        # Implementa la lógica para borrar todo lo que tiene y conectarse como un dataNode nuevo
        pass

    def ChangeOfLeader(self, request, context): # (new_leader)
        # Implementa la lógica para hacer el cambio de Leader
        pass

def serve():
    service_dataNode = DataNodeService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_DataNodeServiceServicer_to_server(service_dataNode, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    # Start the SendHeartbeat method in a separate thread
    heartbeat_thread = threading.Thread(target=service_dataNode.SendHeartbeat)
    heartbeat_thread.start()    
    server.wait_for_termination()

if __name__ == '__main__':
    port = str(os.getenv("PORT"))
    serve()