from concurrent import futures
import grpc
import os
import sys
import time
import threading
import json

from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

load_dotenv() # Load enviroment variables

index_DB = {"file1": {"datanode_id": "50052", "blocks": ["block_id1", "block_id2", "block_id3", "block_id4", "block_id5", "block_id6", "block_id7", "block_id8", "block_id9", "block_id10", "block_id11", "block_id12"]},
            "file2": {"datanode_id": "50052", "blocks": ["block_id11", "block_id12", "block_id13", "block_id14", "block_id15", "block_id16", "block_id17", "block_id18", "block_id19", "block_id20", "block_id12", "block_id22"]},
            }
    # "file1": {"datanode_id": "50052", "blocks": ["block_id1", "block_id2", "block_id3", "block_id4", "block_id5", "block_id6", "block_id7", "block_id8", "block_id9", "block_id10", "block_id11", "block_id12"]},

# live NameNodes (first one always is the Leader)
nameNodes_connected = []

# live dataNodes
dataNode_addresses = {}

last_assigned = 0
nameNode_first_heartbeat = 0
    
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
        global last_assigned
        while True:
            current_time = time.time()
            inactive_nodes = []

            # Check each DataNode
            for data_node_id, last_heartbeat in dataNode_addresses.items():
                # If the DataNode hasn't sent a heartbeat for a long time
                if current_time - last_heartbeat > int(os.getenv('HEARTBEAT_TIMEOUT')):
                    # Add it to the list of inactive nodes
                    inactive_nodes.append(data_node_id)
                else:
                    print(f"vivo: {data_node_id}")

            # Handle the inactive nodes
            for data_node_id in inactive_nodes:
                # Find the files that have blocks on the inactive node
                for file_name, file_info in index_DB.items():
                    if data_node_id in file_info['datanode_id']:
                        # Get the next DataNode in Round Robin order                        
                        while True:
                            new_data_node_id = list(dataNode_addresses.keys())[last_assigned % len(dataNode_addresses.keys())]
                            last_assigned = (last_assigned + 1) % len(dataNode_addresses)
                            if new_data_node_id not in inactive_nodes:
                                break                            
                        
                        # Replicate the blocks on the new node
                        for block_id in file_info['blocks']:
                            # Find the active DataNode that has the block
                            for dataNode_id in file_info['datanode_id']:
                                if dataNode_id != data_node_id and dataNode_id in dataNode_addresses:
                                    # Create a stub for the active DataNode
                                    print(f"dataNode_id to create the stub: {dataNode_id}")
                                    channel_active_dataNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{dataNode_id}')
                                    active_dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_active_dataNode)

                                    # Read the block from the active node
                                    block_request = Service_pb2.BlockId(id=block_id)
                                    block_data = active_dataNode_stub.SendBlock(block_request)

                                    # Create a stub for the new DataNode
                                    channel_new_dataNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{new_data_node_id}')
                                    new_dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_new_dataNode)

                                    # Write the block to the new node
                                    response = new_dataNode_stub.StoreBlock(block_data)

                                    if not response.success:
                                        print(f"Failed to replicate block {block_id} to DataNode {new_data_node_id}")
                                    break  # Break after finding the first active DataNode that has the block

                        # Replace the inactive node with the new node in the file info
                        index_DB[file_name]['datanode_id'] = [new_data_node_id if id == data_node_id else id for id in index_DB[file_name]['datanode_id']]

                # Remove the inactive node from the dictionary
                del dataNode_addresses[data_node_id]
                print(f"DataNode {data_node_id} removed due to inactivity")

            time.sleep(int(os.getenv("CHECK_LIVE_DATANODES_TIMEOUT")))


class NameNodeService(Service_pb2_grpc.NameNodeServiceServicer):

    def leader_heartbeat(self, nameNode_leader):
        global nameNodes_connected
        global last_assigned
        global nameNode_first_heartbeat
        global index_DB
        global dataNode_addresses
        while True:
            if nameNode_first_heartbeat == 0 and nameNode_leader != str(os.getenv("NAMENODE_PORT")):
                nameNodes_connected.insert(0 , nameNode_leader)
                nameNode_first_heartbeat = 1
            print(f"nameNodes_connected: {nameNodes_connected}")
            nameNode_leader = nameNodes_connected[0]
            
            if nameNode_leader != str(os.getenv("NAMENODE_PORT")):
                channel_nameNode_leader = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{nameNode_leader}') # Address of the nameNode Leader
                nameNode_leader_stub = Service_pb2_grpc.NameNodeServiceStub(channel_nameNode_leader)
                heartbeat = Service_pb2.NameNodeID(id=str(os.getenv("NAMENODE_PORT")))                
                try:
                    nameNodes_info= nameNode_leader_stub.LeaderHeartbeat(heartbeat)
                    nameNodes_connected = nameNodes_info.id_list
                    last_assigned = nameNodes_info.last_assigned
                    nameNode_first_heartbeat = nameNodes_info.nameNode_first_heartbeat
                    print(f"Heartbeat sent to nameNode Leader : {nameNode_leader}")
                    dictionary = json.loads(nameNodes_info.dictionary)
                    index_DB = dictionary.copy()
                
                except Exception as e:
                    # change of Leader because the current one just failed
                    del nameNodes_connected[0]
                    print(f"new leader: {nameNodes_connected[0]}")
                    print(f"Uploaded nameNodes_connected: {nameNodes_connected}")

            else:
                for nameNode in nameNodes_connected[:]:  # Iterate over a copy of the list
                    channel = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{nameNode}')
                    stub = Service_pb2_grpc.NameNodeServiceStub(channel)
                    heartbeat = Service_pb2.NameNodeID(id=str(os.getenv("NAMENODE_PORT")))
                    try:
                        stub.LeaderHeartbeat(heartbeat)  # Send a heartbeat
                    except Exception as e:
                        # If the heartbeat fails, remove the node from the list
                        nameNodes_connected.remove(nameNode)
                        print(f"Node {nameNode} is not alive. Removed from the list.")
            
            time.sleep(int(os.getenv("HEARTBEAT_INTERVAL")))  # Wait for n seconds before sending the next heartbeat
            
        
    def LeaderHeartbeat(self, request, context): # should return the nameNodes_connected
        global nameNodes_connected
        global last_assigned
        global nameNode_first_heartbeat
        global index_DB
        global dataNode_addresses
        name_node_id = request.id
        leader_info = Service_pb2.LeaderInfo()
        if name_node_id not in nameNodes_connected:
            nameNodes_connected.append(name_node_id)
        for nameNode in nameNodes_connected:
            leader_info.id_list.append(nameNode)
        leader_info.last_assigned = last_assigned
        leader_info.nameNode_first_heartbeat = nameNode_first_heartbeat
        leader_info.dictionary = json.dumps(index_DB)        
        return leader_info
    
    def ListFiles(self, request, context):
        file_names = list(index_DB.keys())
        print(f"index_DB: {index_DB}")
        return Service_pb2.FileList(files=file_names)
    
    def CreateFile(self, request, context):
        global last_assigned
        data_node_ids = []
        file_name = request.name
        blocks_id = request.blocks_id
        if file_name in index_DB:
            print(f"File {file_name} already exists")
            return Service_pb2.DataNodeID(id_list=[])
        
        # Get the next DataNode (or DataNodes) in Round Robin order
        print(f"datanode keys: {dataNode_addresses.keys()}")
        
        for _ in range(int(os.getenv("REPLICATION_NUMBER"))):             
            data_node_id = list(dataNode_addresses.keys())[last_assigned% len(dataNode_addresses.keys())]
            data_node_ids.append(data_node_id)
            last_assigned = (last_assigned + 1) % len(dataNode_addresses)

        print(f"DataNodes assigned by Round Robin: {data_node_ids}")
        index_DB[file_name] = {"datanode_id": data_node_ids, "blocks": blocks_id}
        # Return the DataNode assignments to the client
        print(f"index_DB{index_DB}")
        return Service_pb2.DataNodeIDS(id_list=index_DB[file_name]["datanode_id"]) 
        
    def GetBlockLocations(self, request, context):
        file_name = request.name
        if file_name in index_DB:
            file_info = index_DB[file_name]
            block_locations = []
            for block_id in file_info['blocks']:                
                for dataNode_id in file_info['datanode_id']:
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
    nameNode_leader = input("Enter the NameNode Leader address: ")
    nameNodes_connected.append(str(os.getenv("NAMENODE_PORT")))
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
    # Start the leader_heartbeat method in a separate thread 
    leader_heartbeat_thread = threading.Thread(target=service_nameNode.leader_heartbeat, args=(nameNode_leader,))
    leader_heartbeat_thread.daemon = True  # leader_heartbeat as a daemon for it to terminate when the main program ends
    leader_heartbeat_thread.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()