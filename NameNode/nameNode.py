from concurrent import futures
import grpc
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

index_DB = {
    "file1": {"datanode_id": "datanode_id1", "blocks": ["block_id1", "block_id2", "block_id3", "block_id4", "block_id5", "block_id6", "block_id7", "block_id8", "block_id9", "block_id10", "block_id11", "block_id12"]},
    "file2": {"datanode_id": "datanode_id2", "blocks": ["block_id4", "block_id5", "block_id6"]},
    "file3": {"datanode_id": "datanode_id3", "blocks": ["block_id7", "block_id8", "block_id9"]},
    "file4": {"datanode_id": "datanode_id4", "blocks": ["block_id10", "block_id11", "block_id12"]},
    "file5": {"datanode_id": "datanode_id5", "blocks": ["block_id13", "block_id14", "block_id15"]},
}

class ClientService(Service_pb2_grpc.ClientServiceServicer):
    
    def ListFiles(self, request, context):
        file_names = list(index_DB.keys())
        return Service_pb2.FileList(files=file_names)
    
    def CreateFile(self, request, context):
        file_name = request.name
        blocks_id = request.blocks_id
        if file_name in index_DB:
            print(f"File {file_name} already exists")
            return Service_pb2.DataNodeID(id=None)
        data_node_id = "datanode_id1"  # Replace with the address of the DataNode --> bootstrap
        index_DB[file_name] = {"datanode_id": data_node_id, "blocks": blocks_id}
        # Return the DataNode assignment to the client
        return Service_pb2.DataNodeID(id=file_name)
    
    def GetBlockLocations(self, request, context):
        file_name = request.name
        if file_name in index_DB:
            file_info = index_DB[file_name]
            block_locations = []
            for block_id in file_info['blocks']:
                dataNode_id = file_info['datanode_id']
                block_location = Service_pb2.BlockLocation(block_id=block_id, dataNode_id=dataNode_id)
                block_locations.append(block_location)
            return Service_pb2.BlockLocations(locations=block_locations)
        else:
            return Service_pb2.Status(success=False, message=f"File {file_name} not found")

    def Open(self, request, context):
        return super().Open(request, context)
    
    def Close(self, request, context):
        return super().Close(request, context)
    
    def Read(self, request, context):
        return super().Read(request, context)
    
    def Write(self, request, context):
        file_name = request.name
        data = request.data  # Asumimos que los datos vienen como bytes
        num_blocks = len(data) // (1024*1024) + (1 if len(data) % (1024*1024) > 0 else 0)  # 1MB por bloque

        data_node_id = "datanode_id1"

        if file_name not in index_DB:
            # Crear entrada para el nuevo archivo en el índice
            index_DB[file_name] = {"datanode_id": data_node_id, "blocks": [f"{file_name}_block_{i}" for i in range(num_blocks)]}
            return Service_pb2.Status(success=True, message="File created and ready for block storage.")
        else:
            # Manejar caso donde el archivo ya existe
            return Service_pb2.Status(success=False, message="File already exists.")


class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):

    def __init__(self):
        self.data_nodes = {}  # Dictionary to store the status of DataNodes
    
    def SendHeartbeat(self, request, context):
        data_node_id = request.id
        self.data_nodes[data_node_id] = time.time()  # Update the last heartbeat time
        print(f"Heartbeat received from {data_node_id}")
        return Service_pb2.Status(success=True, message=f"Heartbeat from {data_node_id} successfully recieved")


class NameNodeService(Service_pb2_grpc.NameNodeServiceServicer):
        
    def allocate_blocks(file):
        pass

    def append(file, data):
        pass

    def get_block_locations(file):
        pass

    def register_datanode(datanode_id):
        pass

    def datanode_heartbeat(datanode_id):
        pass

    # cuando un DataNode se cae y toca reasignar todos los bloques que este tenía. 
    def relocate_blocks (datanode_id):
        pass



def serve():
    service_dataNode = DataNodeService()
    service_client = ClientService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_ClientServiceServicer_to_server(service_client, server)
    Service_pb2_grpc.add_DataNodeServiceServicer_to_server(service_dataNode, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()