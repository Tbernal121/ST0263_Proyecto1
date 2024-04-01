import os

# mostrar todos los nombres de los archivos que hay en el sistema
def list_files(): 
    print("All files")


# es como hacer mkdir
def create_file(file_name, data): 
    print(f"{file_name} file created")


# es como hacer cd directory_name
def open(directory_name):
    print(f"{directory_name} file opened")


# es como hacer cd..
def close(directory_name):
    print(f"{directory_name} file closed")


def read(file_name):
    print(f"show content of {file_name}")


def write(file_name):
    print(f"writing in {file_name}")


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

            '''def main():
                file_name = input("Enter file name to partition: ")  # Replace this with the file name
                file_partition(file_name)'''


def join_partitioned_files(split_directory, destination_file_name):    
    parts = sorted(os.listdir(split_directory))
    with open(destination_file_name, 'wb') as destination_file:
        for part in parts:
            part_path = os.path.join(split_directory, part)
            with open(part_path, 'rb') as part_file:
                destination_file.write(part_file.read())

            '''def main():
                split_directory = input("Enter the directory: ")
                destination_file_name = f"reconstructed_{split_directory}.txt"
                join_partitioned_files(split_directory, destination_file_name)'''