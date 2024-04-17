from concurrent import futures
import grpc
import os
import sys
import time
import threading
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

load_dotenv() # Load enviroment variables

channel_nameNode = grpc.insecure_channel(f'{os.getenv("NAMENODE_LEADER_IP")}:{os.getenv("NAMENODE_PORT")}') # Address of the nameNode Leader
nameNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_nameNode)

class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):

    def __init__(self):
        self.blocks = {}

    def InitialContact(self):
        initial_contact = Service_pb2.DataNodeID(id=os.getenv("PORT"))
        nameNode_stub.InitialContact(initial_contact)
       
    def SendHeartbeat(self):
        while True:
            heartbeat = Service_pb2.DataNodeID(id=os.getenv("PORT"))
            nameNode_stub.SendHeartbeat(heartbeat)
            print("Heartbeat sent")
            time.sleep(int(os.getenv("HEARTBEAT_INTERVAL")))  # Wait for n seconds before sending the next heartbeat
    
    def StoreBlock(self, request, context):
            block_id = request.id
            data = request.data
            self.blocks[block_id] = data  # Store the data block
            print(f"Block: {block_id} stored")
            return Service_pb2.Status(success=True, message=f"Block {block_id} stored successfully")

    def SendBlock(self, request, context):
            block_id = request.id
            # Busca el ID del bloque en el diccionario de bloques almacenados
            if block_id in self.blocks:
                data = self.blocks[block_id]
                # Si se encuentra, devuelve los datos del bloque
                print(f"Block: {block_id} found. Sending...")
                return Service_pb2.BlockData(id=block_id, data=data)
            else:
                # Si no se encuentra, establece un código de error y un mensaje
                print(f"Block: {block_id} not found")
                return Service_pb2.BlockData()
   
    def DeleteBlock(self, request, context):
        # Implementa la lógica para eliminar un bloque de datos del dataNode
         block_id = request.id
         if block_id in self.blocks:
               # Si el bloque existe, eliminarlo
               del self.blocks[block_id]
               print(f"Block {block_id} deleted successfully")
               return Service_pb2.Status(success=True, message=f"Block {block_id} deleted successfully")
         else:
               # Si el bloque no existe, retornar un mensaje de error
               print(f"Block {block_id} not found")
               return Service_pb2.Status(success=False, message=f"Block {block_id} not found")

    def ChangeOfLeader(self, request, context): # (new_leader)
        # Implementa la lógica para hacer el cambio de Leader
        pass

def serve():
    service_dataNode = DataNodeService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = int(os.getenv("MAX_WORKERS"))))
    Service_pb2_grpc.add_DataNodeServiceServicer_to_server(service_dataNode, server)
    server.add_insecure_port(f'[::]:{str(os.getenv("PORT"))}')
    server.start()
    service_dataNode.InitialContact()
    # Start the SendHeartbeat method in a separate thread
    heartbeat_thread = threading.Thread(target=service_dataNode.SendHeartbeat)
    heartbeat_thread.daemon = True  # heartbeat_thread as a daemon for it to terminate when the main program ends
    heartbeat_thread.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()