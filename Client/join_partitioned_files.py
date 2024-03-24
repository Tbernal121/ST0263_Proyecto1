import os

def join_partitioned_files(split_directory, destination_file_name):    
    parts = sorted(os.listdir(split_directory))
    with open(destination_file_name, 'wb') as destination_file:
        for part in parts:
            part_path = os.path.join(split_directory, part)
            with open(part_path, 'rb') as part_file:
                destination_file.write(part_file.read())

def main():
    split_directory = input("Enter the directory: ")
    destination_file_name = f"reconstructed_{split_directory}.txt"
    join_partitioned_files(split_directory, destination_file_name)

main()