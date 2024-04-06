import shutil
import grpc
import os
import sys
import tempfile
import partitionManagement
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

# this dictionary will be in nameNode Class
dataNode_addresses = {
    "datanode_id1": "localhost:50052",
    "datanode_id2": "localhost:50053",
    "datanode_id3": "localhost:50054",
    "datanode_id4": "localhost:50055",
    "datanode_id5": "localhost:50056",
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
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            response = nameNode_stub.ListFiles(Service_pb2.Empty())
            print("Files list: " + ', '.join(response.files))

        elif choice == '2':
            channel_dataNode = grpc.insecure_channel('localhost:50052') # Replace with the address of your nameNode Leader bootstrap
            dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)
            file_name = input("Enter the name of the file to create: ")
            blocks = partitionManagement.file_partition(f'files/{file_name}')
            file_data = Service_pb2.FileInfo(name=file_name, blocks_id=blocks)
            response = nameNode_stub.CreateFile(file_data)

            # Send each block to the DataNode         
            for i, block in enumerate(blocks):
                block_file_path = os.path.join(f'{file_name}_dir{block}')                
                with open(block_file_path, 'rb') as block_file:
                    block_content = block_file.read()
                block_data = Service_pb2.BlockData(id=block, data=block_content)
                response = dataNode_stub.StoreBlock(block_data)
            # then delete the block's directory
            shutil.rmtree(f"{file_name}_dir")

        elif choice == '3':
            while (True):
                file_name = input("Enter the name of the file: ")
                # check if the file exist
                action = input("Press 1 to read, 2 to write and 3 to close file: ")
                if action == '1':
                    blocks = []
                    block_locations_map = nameNode_stub.GetBlockLocations(Service_pb2.FileName(name=file_name))
                    # Create a temporary directory to store the blocks
                    with tempfile.TemporaryDirectory() as temp_dir:
                        i = 0
                        for block_locations in block_locations_map.locations:
                            block_id = block_locations.block_id
                            dataNode_id = block_locations.dataNode_id
                            dataNode_stub = get_dataNode_stub(dataNode_id) # takes a DataNode address and returns a stub to communicate with that DataNode
                            block_request = Service_pb2.BlockId(id=block_id)
                            block = dataNode_stub.SendBlock(block_request)
                            # Write each block to a file in the temporary directory
                            with open(os.path.join(temp_dir, str(i).zfill(4)), 'w') as block_file:
                                block_file.write(block.data)
                            i+=1
                        
                        # pass the temporary directory to join_partitioned_files
                        file_data = partitionManagement.join_partitioned_files(temp_dir, f'reconstructed_{file_name}.txt')#f'reconstructed_{temp_dir}.txt'
                
                elif action == '2':
                    data_to_write = input("Enter the content to write into the file: ").encode()  
                    temp_dir = tempfile.mkdtemp()
                    temp_file_path = os.path.join(temp_dir, "temp_file_to_write")
                    with open(temp_file_path, 'wb') as temp_file:
                        temp_file.write(data_to_write)
                    blocks = partitionManagement.file_partition(temp_file_path)

    # Solicitar al NameNode que cree el archivo y determine la ubicación de los bloques
                    try:
                        file_info = Service_pb2.FileInfo(name=file_name, num_blocks=len(blocks))
                        dataNodeID = nameNode_stub.CreateFile(file_info)
                        if dataNodeID.id == "":
                            print(f"Failed to create file {file_name}")
                            continue

        # Asignar cada bloque a un DataNode según la respuesta del NameNode
                        for i, block in enumerate(blocks):
                        # Asumiendo que cada bloque es enviado al mismo DataNode para simplificar. En un caso real, podrías tener diferentes DataNodes para cada bloque.
                            dataNode_stub = get_dataNode_stub(dataNodeID.id)

            # Crear un mensaje BlockData con el ID y los datos
                        block_data_msg = Service_pb2.BlockData(id=f"{file_name}_block_{i}", data=block)

            # Envía el bloque al DataNode
                        response = dataNode_stub.StoreBlock(block_data_msg)
                        if response.success:
                            print(f"Block {i} stored successfully.")
                        else:
                            print(f"Failed to store block {i}.")
                    except grpc.RpcError as e:
                        print(f"GRPC error: {e}")
    
                    shutil.rmtree(temp_dir)
                    
                elif action == '3':
                    break
                else:   
                    print("Invalid choice. Please enter a number between 1 and 3")
                break
                

        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4")

if __name__ == '__main__':
    run()