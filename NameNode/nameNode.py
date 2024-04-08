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

index_DB = {
    "file1": {"datanode_id": "50052", "blocks": ["block_id1", "block_id2", "block_id3", "block_id4", "block_id5", "block_id6", "block_id7", "block_id8", "block_id9", "block_id10", "block_id11", "block_id12"]},
    "file2": {"datanode_id": "datanode_id2", "blocks": ["block_id4", "block_id5", "block_id6"]},
    "file3": {"datanode_id": "datanode_id3", "blocks": ["block_id7", "block_id8", "block_id9"]},
    "file4": {"datanode_id": "datanode_id4", "blocks": ["block_id10", "block_id11", "block_id12"]},
    "file5": {"datanode_id": "datanode_id5", "blocks": ["block_id13", "block_id14", "block_id15"]},
}

# live dataNodes
dataNode_addresses = {}

last_assigned = 0
    
class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):

    def InitialContact(self, request, context):
        data_node_id = request.id
        dataNode_addresses[data_node_id] = time.time() # Add the new DataNode to the dictionary
        print(f"Initial contact from {data_node_id}")
        
        # check if the dataNode it´s already registered (if yes, it means that the datanode was restarted and lost all its blocks)
        # if yes --> start the DataNode Fail Protocol

         # Delete the dataNode's entries from index_DB if it's already registered
        #index_DB = {filename: fileinfo for filename, fileinfo in index_DB.items() if fileinfo["datanode_id"] != data_node_id}
    
        return Service_pb2.Status(success=True, message=f"Initial contact from {data_node_id} successfully recieved")
    
    def SendHeartbeat(self, request, context):
        data_node_id = request.id
        dataNode_addresses[data_node_id] = time.time() # Update the last heartbeat time
        print(f"Heartbeat received from {data_node_id}")
        return Service_pb2.Status(success=True, message=f"Heartbeat from {data_node_id} successfully recieved")
    
    def CheckLiveDataNodes(self):
        global last_heartbeat
        while True:
            current_time = time.time()
            inactive_nodes = []

            # Check each DataNode
            for data_node_id, last_heartbeat in dataNode_addresses.items():
                # If the DataNode hasn't sent a heartbeat for a long time
                if current_time - last_heartbeat > int(os.getenv('HEARTBEAT_TIMEOUT')):
                    # Add it to the list of inactive nodes
                    inactive_nodes.append(data_node_id)

            # Remove the inactive nodes from the dictionary
            for data_node_id in inactive_nodes:
                del dataNode_addresses[data_node_id]
                print(f"DataNode {data_node_id} removed due to inactivity")

            time.sleep(int(os.getenv("CHECK_LIVE_DATANODES_TIMEOUT")))


class NameNodeService(Service_pb2_grpc.NameNodeServiceServicer):

    def ListFiles(self, request, context):
        file_names = list(index_DB.keys())
        return Service_pb2.FileList(files=file_names)
    
    def CreateFile(self, request, context):
        global last_assigned
        file_name = request.name
        blocks_id = request.blocks_id
        if file_name in index_DB:
            print(f"File {file_name} already exists")
            return Service_pb2.DataNodeID(id=None)
        
        # Get the next DataNode in Round Robin order
        print(f"datanode keys: {dataNode_addresses.keys()}")
        data_node_id = list(dataNode_addresses.keys())[last_assigned]
        print(f"DataNode assigned by Round Robin: {data_node_id}")
        last_assigned = (last_assigned + 1) % len(dataNode_addresses)

        index_DB[file_name] = {"datanode_id": data_node_id, "blocks": blocks_id}
        # Return the DataNode assignment to the client
        return Service_pb2.DataNodeID(id=index_DB[file_name]["datanode_id"])
    
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
    
    def UpdateFileBlocks(self, request, context):
        file_name = request.name
        new_blocks_id = request.blocks_id
        if file_name in index_DB:
            # Actualiza la lista de bloques para el archivo existente
            index_DB[file_name]['blocks'] = new_blocks_id
            print(f"Updated blocks for file: {file_name}")
            return Service_pb2.Status(success=True, message="File blocks updated successfully.")
        else:
            return Service_pb2.Status(success=False, message="File does not exist.")
   
    # When the node crashes and it is necessary to reallocate all the blocks that it had
    def RegisterDataNode (self, request, context):
        pass


def serve():
    service_dataNode = DataNodeService()
    service_nameNode = NameNodeService()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = int(os.getenv("MAX_WORKERS")))) 
    Service_pb2_grpc.add_DataNodeServiceServicer_to_server(service_dataNode, server)
    Service_pb2_grpc.add_NameNodeServiceServicer_to_server(service_nameNode, server)
    server.add_insecure_port(f'[::]:{str(os.getenv("NAMENODE_PORT"))}')
    server.start()
    # Start the SendHeartbeat method in a separate thread
    check_live_datanodes_thread = threading.Thread(target=service_dataNode.CheckLiveDataNodes)
    check_live_datanodes_thread.daemon = True  # check_live_datanodes_thread as a daemon for it to terminate when the main program ends
    check_live_datanodes_thread.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()