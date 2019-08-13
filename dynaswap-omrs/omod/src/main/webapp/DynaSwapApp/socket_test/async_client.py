import asyncio
import websockets
import json
import hashlib
import time

# concat values together and then hash
def hash_multiple_to_one_int(list_of_values_to_hash):
    concated_hashes = ""
    for value in list_of_values_to_hash:
        concated_hashes += str(value)
    result = hashlib.md5(concated_hashes.encode('utf-8')).hexdigest()
    return int(result, 16)


class Client:
    def __init__(self, uri, user_id, SID=None, z=None, p=None, coefficient_list=None, secret_key=None, private_key=None, user_uuid=None):
        """Constructor"""
        # example uri of server: "ws://192.168.0.15:8765"
        self.uri = uri
        # For testing purposes the user_id will be hardcoded but ideally this should be provided by Django when logging in
        self.user_id = user_id
        # Ideally SID (as well as these other values) would be saved and loaded on device but will be hard coded for now
        self.SID = SID
        self.z = z
        self.p = p
        self.coefficient_list = coefficient_list
        self.secret_key = secret_key
        self.private_key = private_key
        self.user_uuid = user_uuid
        self.public_graph = None
        self.keys = {}

    async def connect(self):
        """Connect to websocket server"""
        self.connection = await websockets.client.connect(self.uri)
        # Maybe need error checking for connection before returning
        return self.connection

    async def send_message(self, websocket, message):
        """Take in a connection to the websocket and a message. Send message to server and print response"""
        print(f"Sending message: {message}")
        await websocket.send(message)
        key = await websocket.recv()
        print(f"Got key: {key}")

    async def receive_JSON(self, websocket):
        json_data = await websocket.recv()
        data = json.loads(json_data)
        action = data['action']
        if action == "receive_SID":
            await self.receive_SID(data)
        elif action == "receive_public_data":
            await self.receive_public_data(data)
        elif action == "receive_public_graph_data":
            await self.receive_public_graph_data(data)

    async def receive_SID(self, data):
        self.SID = data['SID']
        print(f"SID is now: {self.SID}")
    
    async def receive_public_data(self, data):
        self.z = int(data['z'])
        self.p = int(data['p'], 16)
        self.coefficient_list = json.loads(data['coefficient_list'])
        print(f"z is now: {self.z}\np is now: {self.p}\ncoefficient_list is now: {self.coefficient_list}")
    
    async def receive_public_graph_data(self, data):
        # print(data)
        # maybe should send this with the SID instead
        # This is the uuid of the role where the user starts at
        self.user_uuid = data['user_uuid']
        self.public_graph = data['public_graph']
        # print(f"graph: {data['public_graph']}")
        print("Now have public info from graph")
        self.calc_own_private_key()
        print(f"private_key is now: {self.private_key}")
        print(f"private_key as hex: {hex(self.private_key)}")
    
    async def send_action(self, websocket, action_message):
        message = {"action": action_message, "user_id": self.user_id}
        json_message = json.dumps(message)
        print(f"sending action: {action_message}")
        await websocket.send(json_message)
    
    def calc_secret_key(self, x):
        if self.coefficient_list == None:
            raise ValueError("Must have coefficient list to calculate the secret key")

        bigPrimeInt = self.p
        cur = 1
        res = 0
        for i in range(0, len(self.coefficient_list)):
            res = (res + cur * (self.coefficient_list[len(self.coefficient_list) - i - 1])) % bigPrimeInt
            cur *= x
        # print(f"result: {res}")
        # print(f"hex result: {hex(res)}")
        self.secret_key = res

    
    def calc_own_private_key(self):
        # print(f"client uuid: {self.user_uuid}")
        # print(f"client secret_key: {self.secret_key}")
        # The secret key that is used on the server side is formatted as a hex string without '0x' at the front
        # The client side secret key is stored as an int so the formatting must be changed
        formatted_secret_key = hex(self.secret_key)[2:]
        print(f"user_uuid: {self.user_uuid}")
        self.private_key = hash_multiple_to_one_int([formatted_secret_key, self.user_uuid])
        return self.private_key
    
    def calc_private_key(self, secret_key, uuid):
        # The secret key that is used on the server side is formatted as a hex string without '0x' at the front
        # The client side secret key is stored as an int so the formatting must be changed
        formatted_secret_key = hex(secret_key)[2:]
        private_key = hash_multiple_to_one_int([formatted_secret_key, uuid])
        return private_key
    
    # def access_role(self, cur_role_id, target_role_id):
    #     if cur_role_id == target_role_id:
    #         return True
    #     for child in self.public_graph[cur_role_id]:
    #         # hash of own private key and child's public uuid
    #         priv_key = hex(self.private_key)[2:]
    #         print(f"priv key: {priv_key}")
    #         hashed = hash_multiple_to_one_int([hex(self.private_key)[2:], child[0]])
    #         print(f"child_label: {child[0]}")
    #         edge_key = int(child[1])
    #         print(f"edge key {edge_key}")
    #         child_private_key = edge_key ^ hashed
    #         print(f"child private key hex: {hex(child_private_key)}")
    #         if self.access_role(child[0], target_role_id):
    #             return True
    #     return False

    def access_role_util(self, curr_role_uuid, target_role_uuid, curr_private_key):
        print(f"graph for {curr_role_uuid}, {self.public_graph[curr_role_uuid]}")
        for child in self.public_graph[curr_role_uuid]:
            child_uuid = child[0]
            edge_key = int(child[1])
            print(f"child_uuid: {child_uuid}")
            print(f"edge_key: {edge_key}")
            hashed = hash_multiple_to_one_int([hex(curr_private_key)[2:], child_uuid])
            child_private_key = edge_key ^ hashed
            self.keys[curr_role_uuid] = child_private_key

            if curr_role_uuid == target_role_uuid:
                return self.keys[curr_role_uuid]
            elif len(self.public_graph[child_uuid]) > 0:
                print(f"keys: {self.keys}")
                print(f"children: {self.public_graph[child_uuid]}")
                for child in self.public_graph[child_uuid]:
                    self.access_role_util(child[0], target_role_uuid, self.keys[curr_role_uuid])


    def access_role(self, target_role_id):
        self.keys = {}
        # calc private key for starting node
        cur_private_key = self.calc_own_private_key()
        target_priv_key = self.access_role_util(self.user_uuid, '0ac28f293426290c8e7827ece2bf406a', cur_private_key)
        print(f"target priv key {target_priv_key}")
    



if __name__ == "__main__":
    client = Client("ws://127.0.0.1:8000/ws/server_test/", 10)
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(client.connect())
    loop.run_until_complete(client.send_action(connection, "request_SID"))
    loop.run_until_complete(client.receive_JSON(connection))

    loop.run_until_complete(client.send_action(connection, "request_public_data"))
    loop.run_until_complete(client.receive_JSON(connection))
    my_hash = hash_multiple_to_one_int([client.SID, client.z])
    # print(f"hash value of SID and z: {my_hash}")
    client.calc_secret_key(my_hash)
    print(f"secret key is: {client.secret_key}")
    print(f"secret key as hex: {hex(client.secret_key)}")

    loop.run_until_complete(client.send_action(connection, "request_public_graph_data"))
    loop.run_until_complete(client.receive_JSON(connection))

    # client.access_role('0ac28f293426290c8e7827ece2bf406a')
