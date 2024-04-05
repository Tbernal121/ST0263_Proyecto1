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
    "file1": {"datanode_id": "datanode1", "blocks": ["block1", "block2", "block3"]},
    "file2": {"datanode_id": "datanode2", "blocks": ["block4", "block5", "block6"]},
    "file3": {"datanode_id": "datanode3", "blocks": ["block7", "block8", "block9"]},
    "file4": {"datanode_id": "datanode4", "blocks": ["block10", "block11", "block12"]},
    "file5": {"datanode_id": "datanode5", "blocks": ["block13", "block14", "block15"]},
}

class ClientService(Service_pb2_grpc.ClientServiceServicer):
    
    def ListFiles(self, request, context):
        file_names = list(index_DB.keys())
        return Service_pb2.FileList(files=file_names)
    
    def CreateFile(self, request, context):
        file_name = request.name
        num_blocks = request.num_blocks
        if file_name in index_DB:
            print(f"File {file_name} already exists")
            return Service_pb2.DataNodeID(id=None)
        data_node_id = "dataNode_id1"  # Replace with the address of the DataNode --> bootstrap
        index_DB[file_name] = {"datanode_id": data_node_id, "blocks": list(range(num_blocks))}
        # Return the DataNode assignment to the client
        return Service_pb2.DataNodeID(id=file_name)
    
    def GetBlockLocations(self, request, context):
        print("pasa por aquí #1")
        file_name = request.name        
        if file_name in index_DB: 
            print("pasa por aquí #2")
            file_info = index_DB[file_name]
            block_locations = []
            for block_id in file_info['blocks']:
                dataNode_id = file_info['datanode_id']
                print("pasa por aquí #3")
                block_location = Service_pb2.BlockLocation(block_id=block_id, dataNode_id=dataNode_id)
                print("pasa por aquí #4")
                block_locations.append(block_location)
                print(f'locations: {block_locations}')                
            print("pasa por aquí #5")
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
        return super().Write(request, context)


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