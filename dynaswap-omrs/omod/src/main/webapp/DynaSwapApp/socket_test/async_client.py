import asyncio
import websockets
import json
import hashlib

# concat values together and then hash
def hashMultipleToOneInt(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += str(value)
    result = hashlib.md5(concatedHashes.encode('utf-8')).hexdigest()
    return int(result, 16)


class Client:
    def __init__(self, uri, user_id, SID=None, z=None, p=None, coefficientList=None, secret_key=None, private_key=None, user_uuid=None):
        """Constructor"""
        # example uri of server: "ws://192.168.0.15:8765"
        self.uri = uri
        # For testing purposes the user_id will be hardcoded but ideally this should be provided by Django when logging in
        self.user_id = user_id
        # Ideally SID (as well as these other values) would be saved and loaded on device but will be hard coded for now
        self.SID = SID
        self.z = z
        self.p = p
        self.coefficientList = coefficientList
        self.secret_key = secret_key
        self.private_key = private_key
        self.user_uuid = user_uuid
        self.public_graph = None

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
        self.coefficientList = json.loads(data['coefficientList'])
        print(f"z is now: {self.z}\np is now: {self.p}\ncoefficientList is now: {self.coefficientList}")
    
    async def receive_public_graph_data(self, data):
        # print(data)
        # maybe should send this with the SID instead
        # This is the uuid of the role where the user starts at
        self.user_uuid = data['user_uuid']
        self.public_graph = data['public_graph']
        print(f"graph: {data['public_graph']}")
        print("Now have public info from graph")
        self.calc_own_private_key()
        print(f"private_key is now: {self.private_key}")
        print(f"private_key as hex: {hex(self.private_key)}")
    
    async def send_action(self, websocket, action_message):
        message = {"action": action_message, "user_id": self.user_id}
        json_message = json.dumps(message)
        print(f"sending action: {action_message}")
        await websocket.send(json_message)
    
    def calc_secret_key(self, x, p):
        if self.coefficientList == None:
            raise ValueError("Must have coefficient list to calculate the secret key")

        # startingExponentNum = len(self.coefficientList)-1
        # sumTotal = 0
        # for coefficient in self.coefficientList:
        #     coefficientNum = int(coefficient)
        #     if startingExponentNum > 0:
        #         sumTotal += (coefficientNum * (x ** startingExponentNum))
        #     else:
        #         sumTotal += coefficientNum
        #     startingExponentNum -= 1
        # self.secret_key = (sumTotal % p)

        bigPrimeInt = self.p
        cur = 1
        res = 0
        for i in range(0, len(self.coefficientList)):
            res = (res + cur * (self.coefficientList[len(self.coefficientList) - i - 1])) % bigPrimeInt
            cur *= x
        # print(f"result: {res}")
        # print(f"hex result: {hex(res)}")
        self.secret_key = res

    
    def calc_own_private_key(self):
        print(f"client uuid: {self.user_uuid}")
        print(f"client secret_key: {self.secret_key}")
        # The secret key that is used on the server side is formatted as a hex string without '0x' at the front
        # The client side secret key is stored as an int so the formatting must be changed
        formatted_secret_key = hex(self.secret_key)[2:]
        self.private_key = hashMultipleToOneInt([formatted_secret_key, self.user_uuid])
    
    # def access_role(self, cur_role_id, target_role_id):
    #     if cur_role_id == target_role_id:
    #         return True
    #     for child in self.public_graph[cur_role_id]:
    #         # hash of own private key and child's public uuid
    #         priv_key = hex(self.private_key)[2:]
    #         print(f"priv key: {priv_key}")
    #         hashed = hashMultipleToOneInt([hex(self.private_key)[2:], child[0]])
    #         print(f"child_label: {child[0]}")
    #         edge_key = int(child[1])
    #         print(f"edge key {edge_key}")
    #         child_private_key = edge_key ^ hashed
    #         print(f"child private key hex: {hex(child_private_key)}")
    #         if self.access_role(child[0], target_role_id):
    #             return True
    #     return False


if __name__ == "__main__":
    client = Client("ws://127.0.0.1:8000/ws/server_test/", 10)
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(client.connect())
    loop.run_until_complete(client.send_action(connection, "request_SID"))
    loop.run_until_complete(client.receive_JSON(connection))
    loop.run_until_complete(client.send_action(connection, "request_public_data"))
    loop.run_until_complete(client.receive_JSON(connection))
    # my_hash = (hashMultipleToOneInt([client.SID, client.z]) % client.p)
    my_hash = hashMultipleToOneInt([client.SID, client.z])
    print(f"hash value of SID and z: {my_hash}")
    client.calc_secret_key(my_hash, client.p)
    print(f"secret key is: {client.secret_key}")
    print(f"secret key as hex: {hex(client.secret_key)}")
    loop.run_until_complete(client.send_action(connection, "request_public_graph_data"))
    loop.run_until_complete(client.receive_JSON(connection))
    # client.access_role(client.user_uuid, 'test3')
