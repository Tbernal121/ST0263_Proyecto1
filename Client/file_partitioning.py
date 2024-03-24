import os

def file_partition(file_name):  
    block_size=1024*1024 #1mb
    base_file_name = os.path.splitext(os.path.basename(file_name))[0] + os.path.splitext(os.path.basename(file_name))[1]
    destination_directory = f"{base_file_name}_dir"
    
    # Create the directory
    os.makedirs(destination_directory, exist_ok=True)

    block_num = 1
    with open(file_name, 'rb') as file:
        block = file.read(block_size)
        while block:
            part_name = f"{destination_directory}/part-{block_num:04d}"
            with open(part_name, 'wb') as part_file:
                part_file.write(block)
            print(f"Block {part_name} created")
            block_num += 1
            block = file.read(block_size)

def main():
    file_name = input("Enter file name to partition: ")  # Replace this with the file name
    file_partition(file_name)

main()