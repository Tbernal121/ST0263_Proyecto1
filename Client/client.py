import grpc
import os
import sys
import tempfile
import partitionManagement


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

# this dictionary will be in nameNode Class
dataNode_addresses = {
    "datanode1": "localhost:50052",
    "datanode2": "localhost:50053",
    "datanode3": "localhost:50054",
    "datanode4": "localhost:50055",
    "datanode5": "localhost:50056",
}

# Takes a DataNode address and returns a stub to communicate with that DataNode
def get_dataNode_stub(dataNode_id):
    dataNode_address = dataNode_addresses[dataNode_id]
    channel = grpc.insecure_channel(dataNode_address)
    stub = Service_pb2_grpc.DataNodeServiceStub(channel)
    return stub


def run():
    channel_nameNode = grpc.insecure_channel('localhost:50051') # Replace with the address of your nameNode Leader bootstrap
    nameNode_stub = Service_pb2_grpc.ClientServiceStub(channel_nameNode)
    #dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)

    while True:
        print("\nMenu:")
        print("1. List files") # mostrar todos los nombres de los archivos que hay en el sistema
        print("2. Create file") # es como hacer mkdir. (file_name, data)
        print("3. Open file to read or write") # es como hacer cd directory_name. (directory_name)
        print("4. Close file") # es como hacer cd..  (directory_name)
        print("5. Read file") # (file_name)
        print("6. Write file") # (file_name)
        print("7. Exit")     

        choice = input("Enter your choice: ")

        if choice == '1':
            response = nameNode_stub.ListFiles(Service_pb2.Empty())
            print("Client received: " + ', '.join(response.files))

        elif choice == '2':
            channel_dataNode = grpc.insecure_channel('localhost:50052') # Replace with the address of your nameNode Leader bootstrap
            dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)
            file_name = input("Enter the name of the file to create: ")    

            # Open the file in read mode
            '''with open(f'files/{file_name}', 'r') as file:
                file_content = file.read()
            blocks = partitionManagement.file_partition(file_content)'''
            blocks = partitionManagement.file_partition(f'files/{file_name}')
            file_data = Service_pb2.FileInfo(name=file_name, num_blocks=len(blocks))        
            response = nameNode_stub.CreateFile(file_data)

            # Send each block to the DataNode
            for i, block in enumerate(blocks):
                block_data = Service_pb2.BlockData(id=block, data=f"{block} data")
                response = dataNode_stub.StoreBlock(block_data)
                print(response.message)
            # then delete the block's directory

        elif choice == '3':        
            while (True):
                file_name = input("Enter the name of the file: ")
                # check if the file exist
                action = input("Press 1 to read, 2 to write and 3 to return: ")
                if action == '1':
                    blocks = []
                    block_locations_map = nameNode_stub.GetBlockLocations(Service_pb2.FileName(name=file_name))
                    for block_id, dataNode_id in block_locations_map.locations.items():
                        dataNode_stub = get_dataNode_stub(dataNode_id) # takes a DataNode address and returns a stub to communicate with that DataNode
                        block_request = Service_pb2.BlockId(id=block_id)
                        block = dataNode_stub.SendBlock(block_request)
                        blocks.append(block.data)
                    file_data = partitionManagement.join_partitioned_files(blocks)
                    print(file_data)

                    # Create a temporary directory to store the blocks
                    with tempfile.TemporaryDirectory() as temp_dir:
                        for i, block_location in enumerate(block_locations.locations):
                            dataNode_stub = get_dataNode_stub(block_location.dataNode)  # takes a DataNode address and returns a stub to communicate with that DataNode
                            block_request = Service_pb2.BlockId(id=block_location.block_id)
                            block = dataNode_stub.SendBlock(block_request)
                            # Write each block to a file in the temporary directory
                            with open(os.path.join(temp_dir, f'block_{i}'), 'w') as block_file:
                                block_file.write(block.data)
                        # pass the temporary directory to join_partitioned_files
                        file_data = partitionManagement.join_partitioned_files(temp_dir, f'reconstructed_{file_name}.txt')
                        #print(file_data)
                
                elif action == '2':
                    # Write logic
                    pass
                elif action == '3':
                    break
                else:   
                    print("Invalid choice. Please enter a number between 1 and 3")
                

        elif choice == '4':
            # Call Close here
            pass
        elif choice == '5':
            # Call Read here
            pass
        elif choice == '6':
            # Call Write here
            pass
        elif choice == '7':
            break         
        else:
            print("Invalid choice. Please enter a number between 1 and 7")

if __name__ == '__main__':
    run()