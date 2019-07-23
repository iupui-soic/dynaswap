from channels.generic.websocket import WebsocketConsumer
import json

class ServerConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        # message = text_data_json['message']

        # self.send(text_data=json.dumps({
        #     'message': message
        # }))

        if action == "request_public_data":
            self.publicize_data()
        elif action == "request_SID":
            self.sendSID()
    
    def publicize_data(self):
        # These are dummy variables hardcoded in. It is assumed that the ACP class will be able to supply
        # these either by returning through function calls or passing in to this function as parameters
        z = 5
        coefficientList = json.dumps([1, -5, 2])
        p = 13
        self.send(text_data=json.dumps({
            'action': 'receive_public_data',
            'z': z,
            'coefficientList': coefficientList,
            'p': p

        }))
    
    def sendSID(self):
        """Right now the user login functionality is not working. Ideally if a user could log in
        then this function would take a user_id as an input and be able to detemine if this user already
        has an SID or needs to be assigned a new one."""
        # dummy SID for now, ideally this should use the KeyManagement class from hierarchy.py to get SID
        SID = 7
        self.send(text_data=json.dumps({
            'action': 'receive_SID',
            'SID': SID
        }))
