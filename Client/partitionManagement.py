import os

def file_partition(file_name):  
    blocks = [] # List to store the  blocks
    block_size = 256 # int(os.getenv("BLOCK_SIZE"))
    base_file_name = os.path.splitext(os.path.basename(file_name))[0] + os.path.splitext(os.path.basename(file_name))[1]
    print(f"base_file_name: {base_file_name}")
    destination_directory = f"{base_file_name}_dir"
    
    # Create the directory
    os.makedirs(destination_directory, exist_ok=True)

    block_num = 1
    with open(file_name, 'rb') as file:
        block = file.read(block_size)
        while block:
            block_name = f'/{base_file_name}-part-{block_num:04d}'
            part_name = f"{destination_directory}{block_name}"
            with open(part_name, 'wb') as part_file:
                part_file.write(block)
            blocks.append(block_name)
            block_num += 1
            block = file.read(block_size)
    
    return blocks


def join_partitioned_files(split_directory, destination_file_name):
    parts = sorted(os.listdir(split_directory))
    with open(destination_file_name, 'wb') as destination_file:
        for part in parts:
            part_path = os.path.join(split_directory, part)
            with open(part_path, 'rb') as part_file:
                destination_file.write(part_file.read())