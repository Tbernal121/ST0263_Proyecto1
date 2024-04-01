
index_DB = {
    "file1": {"datanode_id": "datanode1", "blocks": ["block1", "block2", "block3"]},
    "file2": {"datanode_id": "datanode2", "blocks": ["block4", "block5", "block6"]},
    "file3": {"datanode_id": "datanode3", "blocks": ["block7", "block8", "block9"]},
    "file4": {"datanode_id": "datanode4", "blocks": ["block10", "block11", "block12"]},
    "file5": {"datanode_id": "datanode5", "blocks": ["block13", "block14", "block15"]},
}

def create(file):
    if file in index_DB:
        print(f"File {file} already exists.")
        return
    index_DB[file] = {"datanode_id": None, "blocks": []}
    print(f"File {file} created successfully")


def allocate_blocks(file):
    print()


def append(file, data):
    print()


def get_block_locations(file):
    print()


def register_datanode(datanode_id):
    print()


def datanode_heartbeat(datanode_id):
    print()


# cuando un DataNode se cae y toca reasignar todos los bloques que este tenía. 
def relocate_blocks (datanode_id):
    print()