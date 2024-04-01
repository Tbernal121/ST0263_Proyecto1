
def send_heartbeat():
    print("sending heartbeat")


def store_block(block_id, data):
    print(f"storing {block_id} block")


def delete_block(block_id):
    print(f"deleting {block_id} block")


def send_block(block_id, data, destination):
    print(f"sending {block_id} to {destination}")


# borra todo lo que tiene para conectarse como un nodo nuevo 
def clean_start():
    print("Clean start")


def change_of_leader (new_leader):
    print(f"changing to {new_leader} Leader")