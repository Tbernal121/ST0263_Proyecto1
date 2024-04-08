import shutil
import grpc
import os
import sys
import tempfile
import partitionManagement
import time
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Protobufs import Service_pb2
from Protobufs import Service_pb2_grpc

load_dotenv() # Load enviroment variables

def run():
    channel_nameNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{os.getenv("NAMENODE_PORT")}') # Address of the nameNode Leader
    nameNode_stub = Service_pb2_grpc.NameNodeServiceStub(channel_nameNode) # verify

    while True:
        print("\nMenu:")
        print("1. List files")
        print("2. Create file")
        print("3. Open file to read or write")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            response = nameNode_stub.ListFiles(Service_pb2.Empty())
            print("Files list: " + ', '.join(response.files))
        
        elif choice == '2':
            file_name = input("Enter the name of the file to create: ")
            blocks = partitionManagement.file_partition(f'{os.getenv("DIR_PATH")}{file_name}')
            file_data = Service_pb2.FileInfo(name=file_name, blocks_id=blocks)
            dataNode_id = nameNode_stub.CreateFile(file_data)
            channel_dataNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{dataNode_id.id}')
            dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)
            # Send each block to the DataNode
            for i, block in enumerate(blocks):
                block_file_path = os.path.join(f'{file_name}_dir{block}')
                with open(block_file_path, 'rb') as block_file:
                    block_content = block_file.read()
                block_data = Service_pb2.BlockData(id=block, data=block_content)
                response = dataNode_stub.StoreBlock(block_data)
            # Delete the block's directory
            shutil.rmtree(f"{file_name}_dir")
        
        elif choice == '3':
            while (True):
                file_name = input("Enter the name of the file: ")
                # check if the file exist
                action = input("Press 1 to read, 2 to write and 3 to close file: ")
                # Obtener la ubicación de los bloques actuales del archivo
                block_locations_map = nameNode_stub.GetBlockLocations(Service_pb2.FileName(name=file_name))

                # Read Logic
                if action == '1':
                    blocks = []
                    # Create a temporary directory to store the blocks
                    with tempfile.TemporaryDirectory() as temp_dir:
                        i = 0
                        for block_locations in block_locations_map.locations:
                            block_id = block_locations.block_id
                            dataNode_id = block_locations.dataNode_id
                            channel_dataNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{dataNode_id}')
                            dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)
                            block_request = Service_pb2.BlockId(id=block_id)
                            block = dataNode_stub.SendBlock(block_request)
                            # Write each block to a file in the temporary directory
                            with open(os.path.join(temp_dir, str(i).zfill(4)), 'w') as block_file:
                                block_file.write(block.data)
                            i+=1
                        
                        file_data = partitionManagement.join_partitioned_files(temp_dir, f'reconstructed_{file_name}{os.getenv("DEFAULT_FILE_EXTENSION")}')
                 
                # Write Logic
                elif action == '2':
                    new_text = input("Enter the text to add: ")
                    new_text_bytes = new_text.encode('utf-8')
                    if not block_locations_map.locations:
                         print("File not found")
                         continue  # back to the menu
                    
                    last_dataNode_id = block_locations_map.locations[-1].dataNode_id
                    channel_dataNode = grpc.insecure_channel(f'{os.getenv("HOST_ADDRESS")}:{last_dataNode_id}')
                    dataNode_stub = Service_pb2_grpc.DataNodeServiceStub(channel_dataNode)

                    # Get the last block
                    last_block_id = block_locations_map.locations[-1].block_id
                    last_block_data = dataNode_stub.SendBlock(Service_pb2.BlockId(id=last_block_id))
                    
                    # Verificar si el último bloque tiene espacio para más datos
                    if len(last_block_data.data) + len(new_text.encode('utf-8')) <= int(os.getenv("BLOCK_SIZE")): # max block size 
                        # Si hay espacio, añadir el nuevo texto al último bloque
                        updated_block_data = Service_pb2.BlockData(id=last_block_id, data=last_block_data.data + new_text)
                        response = dataNode_stub.StoreBlock(updated_block_data)
                        if not response.success:
                            print("Failed to update the last block")
                            continue
                    
                    else:
                        # Genera un nuevo ID de bloque basado en un esquema de nomenclatura o un identificador único
                        new_block_id = f"new_block_{int(time.time())}"  # Ejemplo de generación de un nuevo block_id
                        #new_block_id = f'/part-{block_num:04d}'  # Generación de un nuevo block_id
                        
                        # Add the new block to block_locations_map
                        block_location = Service_pb2.BlockLocation(block_id=new_block_id, dataNode_id=last_dataNode_id)
                        block_locations_map.locations.append(block_location)

                        # Almacenar el nuevo bloque en el DataNode seleccionado
                        block_data = Service_pb2.BlockData(id=new_block_id, data=new_text)
                        response = dataNode_stub.StoreBlock(block_data)
                        
                    if not response.success:
                        print("Failed to store the new block")
                        continue
                    # Actualizar la lista de bloques del archivo en el NameNode
                    blocks_id = [location.block_id for location in block_locations_map.locations]
                    
                    update_response = nameNode_stub.UpdateFileBlocks(Service_pb2.FileInfo(name=file_name, blocks_id=blocks_id))
                    if not update_response.success:
                        print("Failed to update the file's block list in the NameNode")
                    else:
                        print("Text added successfully to the file")
                    
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