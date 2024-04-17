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

index_DB = {"file1": {"datanode_ip": "192.168.68.116", "blocks": ["block_id1", "block_id2", "block_id3", "block_id4", "block_id5", "block_id6", "block_id7", "block_id8", "block_id9", "block_id10", "block_id11", "block_id12"]},
            "file2": {"datanode_ip": "aaaa", "blocks": ["block_id11", "block_id12", "block_id13", "block_id14", "block_id15", "block_id16", "block_id17", "block_id18", "block_id19", "block_id20", "block_id12", "block_id22"]},
            }

# live NameNodes (first one always is the Leader)
nameNodes_connected = []
nameNodes_ip_port = {}

# live dataNodes
dataNode_addresses = {}

last_assigned = 0
nameNode_first_heartbeat = 0
    
class DataNodeService(Service_pb2_grpc.DataNodeServiceServicer):

    def InitialContact(self, request, context):
        data_node_port = request.id
        data_node_ip = context.peer().split(':')[1]  # Get the IP address of the DataNode
        dataNode_addresses[data_node_ip] = {'timestamp': time.time(), 'port': data_node_port}
        print(f"Initial contact from DataNode: {data_node_ip}")
        
        # check if the dataNode it´s already registered (if yes, it means that the datanode was restarted and lost all its blocks)
        # if yes --> start the DataNode Fail Protocol

         # Delete the dataNode's entries from index_DB if it's already registered
        #index_DB = {filename: fileinfo for filename, fileinfo in index_DB.items() if fileinfo["datanode_id"] != data_node_id}
    
        return Service_pb2.Status(success=True, message=f"Initial contact from {data_node_ip} successfully recieved")
    
    def SendHeartbeat(self, request, context):
        data_node_port = request.id
        data_node_ip = context.peer().split(':')[1]  # Get the IP address of the DataNode
        dataNode_addresses[data_node_ip] = {'timestamp': time.time(), 'port': data_node_port}
        print(f"Heartbeat received from DataNode: {data_node_ip}")
        return Service_pb2.Status(success=True, message=f"Heartbeat from {data_node_ip} successfully recieved")
    
    def CheckLiveDataNodes(self):
        global last_assigned
        while True:
            current_time = time.time()
            inactive_nodes = []
            # Check each DataNode
            for data_node_ip, data_node_ip_info in dataNode_addresses.items():
                # If the DataNode hasn't sent a heartbeat for a long time
                if current_time - data_node_ip_info["timestamp"] > int(os.getenv('HEARTBEAT_TIMEOUT')):
                    # Add it to the list of inactive nodes
                    inactive_nodes.append(data_node_ip)
                    print(f"The DataNode {data_node_ip} is not alive anymore")

            # Handle the inactive nodes
            for data_node_ip_inactive in inactive_nodes:
                # Find the files that have blocks on the inactive node
                for file_name, file_info in index_DB.items():
                    if data_node_ip_inactive in file_info['datanode_ip']:
                        # Get the next DataNode in Round Robin order
                        for i_ in dataNode_addresses:
                            new_data_node_ip = list(dataNode_addresses.keys())[last_assigned % len(dataNode_addresses.keys())]
                            last_assigned = (last_assigned + 1) % len(dataNode_addresses)
                            if new_data_node_ip not in inactive_nodes:
                                break
                        print(f"inactive_nodes: {inactive_nodes}")
                        
                        # Replicate the blocks on the new node
                        for block_id in file_info['blocks']:
                            # Find the active DataNode that has the block
                            for dataNode_ip_file in file_info['datanode_ip']:
                                if dataNode_ip_file != data_node_ip_inactive and dataNode_ip_file in dataNode_addresses:
                                    # Create a stub for the active DataNode
                                    channel_active_dataNode = grpc.insecure_channel(f'{dataNode_ip_file}:{dataNode_addresses[dataNode_ip_file]["port"]}')
                                    active_dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_active_dataNode)

                                    # Read the block from the active node
                                    block_request = Service_pb2.BlockId(id=block_id)
                                    block_data = active_dataNode_stub.SendBlock(block_request)

                                    # Create a stub for the new DataNode
                                    channel_new_dataNode = grpc.insecure_channel(f'{new_data_node_ip}:{dataNode_addresses[new_data_node_ip]["port"]}')
                                    new_dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_new_dataNode)

                                    # Write the block to the new node
                                    response = new_dataNode_stub.StoreBlock(block_data)

                                    if not response.success:
                                        print(f"Failed to replicate block {block_id} to DataNode {new_data_node_ip}")
                                    break  # Break after finding the first active DataNode that has the block

                        # Replace the inactive node with the new node in the file info
                        index_DB[file_name]['datanode_ip'] = [new_data_node_ip if id == data_node_ip_inactive else id for id in index_DB[file_name]['datanode_ip']]

                # Remove the inactive node from the dictionary
                del dataNode_addresses[data_node_ip_inactive]
                print(f"DataNode {data_node_ip_inactive} removed due to inactivity")

            time.sleep(int(os.getenv("CHECK_LIVE_DATANODES_TIMEOUT")))


class NameNodeService(Service_pb2_grpc.NameNodeServiceServicer):

    def leader_heartbeat(self):
        global nameNodes_connected
        global nameNodes_ip_port
        global last_assigned
        global nameNode_first_heartbeat
        global index_DB
        global dataNode_addresses
        while True:
            # When a NameNode connects for the first time
            if nameNode_first_heartbeat == 0 and nameNodes_connected[0] != os.getenv("NAMENODE_IP"):
                nameNodes_connected.append(os.getenv("NAMENODE_IP"))
                nameNode_first_heartbeat = 1
                print("Initial nameNode heartbeat from", os.getenv("NAMENODE_IP"))
            print(f"NameNodes connected: {nameNodes_connected}")

            # When a NameNode needs to heartbeat the Leader
            if nameNodes_connected[0] != str(os.getenv("NAMENODE_IP")) :               
                channel_nameNode_leader = grpc.insecure_channel(f'{nameNodes_connected[0]}:{nameNodes_ip_port[nameNodes_connected[0]]}') # Address of the nameNode Leader
                nameNode_leader_stub = Service_pb2_grpc.NameNodeServiceStub(channel_nameNode_leader)
                heartbeat = Service_pb2.NameNodeInfo(ip=str(os.getenv("NAMENODE_IP")), port=str(os.getenv("NAMENODE_PORT")))
                try:
                    nameNodes_info = nameNode_leader_stub.LeaderHeartbeat(heartbeat)
                    nameNodes_connected = nameNodes_info.id_list
                    last_assigned = nameNodes_info.last_assigned
                    print(f"Heartbeat sent to nameNode Leader: {nameNodes_connected[0]}")
                    dictionaryIndexDB = json.loads(nameNodes_info.dictionaryIndexDB)
                    dictionaryDataNode_addresses = json.loads(nameNodes_info.dictionaryDataNode_addresses)
                    dictionaryNameNodes_ip_port = json.loads(nameNodes_info.dictionaryNameNodes_ip_port)
                    index_DB = dictionaryIndexDB.copy()
                    dataNode_addresses = dictionaryDataNode_addresses.copy()
                    nameNodes_ip_port = dictionaryNameNodes_ip_port.copy()
                
                except Exception as e:
                    # change of Leader because the current one just failed
                    del nameNodes_connected[0]
                    print(f"New leader: {nameNodes_connected[0]}")
                    print(f"Uploaded NameNodes connected: {nameNodes_connected}")

            # When the actual nameNode is the Leader
            else:
                for nameNode in nameNodes_connected[:]:  # Iterate over a copy of the list
                    channel_nameNode = grpc.insecure_channel(f'{nameNode}:{nameNodes_ip_port[nameNode]}')  
                    nameNode_stub = Service_pb2_grpc.NameNodeServiceStub(channel_nameNode)
                    heartbeat = Service_pb2.NameNodeInfo(ip=nameNode, port=nameNodes_ip_port[nameNode])
                    try:
                        nameNode_stub.LeaderHeartbeat(heartbeat)  # Send a heartbeat
                    except Exception as e:
                        print(e)
                        # If the heartbeat fails, remove the node from the list
                        nameNodes_connected.remove(nameNode)
                        print(f"Node {nameNode} is not alive. Removed from the list")
            
            time.sleep(int(os.getenv("HEARTBEAT_INTERVAL")))  # Wait for n seconds before sending the next heartbeat
            
        
    def LeaderHeartbeat(self, request, context): # should return the nameNodes_connected
        try:
            global nameNodes_connected
            global last_assigned
            global index_DB
            global dataNode_addresses
            global nameNodes_ip_port
            name_node_ip = request.ip
            name_node_port = request.port
            leader_info = Service_pb2.LeaderInfo()
            if name_node_ip not in nameNodes_connected:
                nameNodes_connected.append(name_node_ip)
            if name_node_ip not in nameNodes_ip_port:
                nameNodes_ip_port[name_node_ip] = name_node_port
            for nameNode in nameNodes_connected:
                leader_info.id_list.append(nameNode)
            leader_info.last_assigned = last_assigned
            leader_info.dictionaryIndexDB = json.dumps(index_DB) ########
            leader_info.dictionaryDataNode_addresses = json.dumps(dataNode_addresses)
            leader_info.dictionaryNameNodes_ip_port = json.dumps(nameNodes_ip_port)
            return leader_info
        except Exception as e:
            print(f"Exception occurred in LeaderHeartbeat: {e}")
            import traceback
            traceback.print_exc()

    
    def ListFiles(self, request, context):
        file_names = list(index_DB.keys())
        return Service_pb2.FileList(files=file_names)
    
    def CreateFile(self, request, context):
        global last_assigned
        data_node_ip_port = {}
        file_name = request.name
        blocks_id = request.blocks_id
        if file_name in index_DB:
            print(f"File {file_name} already exists")
            return Service_pb2.DataNodeID(dict_addresses=[])
        
        # Get the next DataNode (or DataNodes) in Round Robin order
        for _ in range(int(os.getenv("REPLICATION_NUMBER"))):
            data_node_ip = list(dataNode_addresses.keys())[last_assigned% len(dataNode_addresses.keys())]
            data_node_ip_port[data_node_ip] = dataNode_addresses[data_node_ip]['port']
            last_assigned = (last_assigned + 1) % len(dataNode_addresses)

        print(f"DataNodes assigned by Round Robin: {data_node_ip_port}")
        blocks_id_list = [block for block in blocks_id]
        index_DB[file_name] = {"datanode_ip": list(data_node_ip_port.keys())[0], "blocks": blocks_id_list}
        json_string = json.dumps(data_node_ip_port)
        # Return the DataNode assignments to the client
        return Service_pb2.DataNodeIDS(dict_addresses=json_string) 
        
    def GetBlockLocations(self, request, context):
        try:
            file_name = request.name
            if file_name in index_DB:
                file_info = index_DB[file_name]
                block_locations = []
                for block_id in file_info['blocks']:
                    dataNode_ip = file_info['datanode_ip']
                    dataNode_port = dataNode_addresses[dataNode_ip]['port']
                    block_location = Service_pb2.BlockLocation(block_id=block_id, dataNode_ip=dataNode_ip, dataNode_port=dataNode_port)
                    block_locations.append(block_location)
                return Service_pb2.BlockLocations(locations=block_locations)
            else:
                return Service_pb2.Status(success=False, message=f"File {file_name} not found")
            
        except Exception as e:
            print(f"Exception occurred in GetBlockLocations: {e}")
            import traceback
            traceback.print_exc()
    
    def UpdateFileBlocks(self, request, context):
        file_name = request.name
        new_blocks_id = list(request.blocks_id)  # Convert to list
        if file_name in index_DB:
            # Actualiza la lista de bloques para el archivo existente
            index_DB[file_name]['blocks'] = new_blocks_id
            print(f"Updated blocks for file: {file_name}")
            return Service_pb2.Status(success=True, message="File blocks updated successfully")
        else:
            return Service_pb2.Status(success=False, message="File does not exist")

    # When the node crashes and it is necessary to reallocate all the blocks that it had
    def RegisterDataNode (self, request, context):
        pass


def serve():
    nameNodes_connected.append(str(os.getenv("NAMENODE_LEADER_IP")))
    nameNodes_ip_port[os.getenv("NAMENODE_IP")] = str(os.getenv("NAMENODE_PORT"))
    nameNodes_ip_port[os.getenv("NAMENODE_LEADER_IP")] = str(os.getenv("NAMENODE_LEADER_PORT"))
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
    leader_heartbeat_thread = threading.Thread(target=service_nameNode.leader_heartbeat,)
    leader_heartbeat_thread.daemon = True  # leader_heartbeat as a daemon for it to terminate when the main program ends
    leader_heartbeat_thread.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()