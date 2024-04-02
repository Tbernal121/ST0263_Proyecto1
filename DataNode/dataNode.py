from concurrent import futures
import grpc
import os
import sys
import time
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')  # Replace with the address of your nameNode Leader bootstrap
nameNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel)

class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):
       
    def SendHeartbeat(self):
        while True:
            heartbeat = Service_pb2.DataNodeID(id="dataNode1") # replace dataNode1 bootstrap            
            response = nameNode_stub.SendHeartbeat(heartbeat)
            print("Heartbeat sent")
            time.sleep(10)  # Wait for 10 seconds before sending the next heartbeat        
            
    def StoreBlock(self, request, context): # (block_id, data)
        # Implementa la lógica para almacenar un bloque de datos en el dataNode
        pass

    def SendBlock(self, request, context): # (block_id, data, destination) 
        # Implementa la lógica para almacenar un bloque de datos en el dataNode
        pass    

    def DeleteBlock(self, request, context): # (block_id)
        # Implementa la lógica para eliminar un bloque de datos del dataNode
        pass

    def CleanStart(self, request, context):
        # Implementa la lógica para borrar todo lo que tiene y conectarse como un dataNode nuevo
        pass

    def ChangeOfLeader(self, request, context): # (new_leader)
        # Implementa la lógica para hacer el cambio de Leader
        pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_DataNodeServiceServicer_to_server(DataNodeService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    # Start the SendHeartbeat method in a separate thread
    heartbeat_thread = threading.Thread(target=DataNodeService().SendHeartbeat)
    heartbeat_thread.start()    
    #DataNodeService().SendHeartbeat()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()