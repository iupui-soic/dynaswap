from channels.generic.websocket import WebsocketConsumer
import json
from DynaSwapApp.services.hierarchy import HierarchyGraph
from DynaSwapApp.models import Users, UsersRoles, Roles, RoleEdges
from channels.db import database_sync_to_async
import time

graph = HierarchyGraph()
graph.createGraph()
 
graph.addRole('test1', 'testing 1')
graph.addRole('test2', 'testing 2')
graph.addEdge('test1', 'test2')
graph.addRole('test3', 'testing 3')
graph.addEdge('test2', 'test3')
graph.addUser(10, 'test1')

# graph.assignSID(5)
# graph.nodes['Organizational: Doctor'].access_control_poly.updateACP(graph.KeyManagement.generateSecretKey())
# print(graph.nodes)

class ServerConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass
    
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        user_id = text_data_json['user_id']

        if action == "request_public_data":
            self.publicize_data(user_id)
        elif action == "request_SID":
            self.send_SID(user_id)
        elif action == "request_public_graph_data":
            self.publicize_graph_data(user_id)
    
    def publicize_data(self, user_id):
        role_for_user = str(UsersRoles.objects.get(user_id=user_id).role)
        z = str(Roles.objects.get(role=role_for_user).random_num)
        p = str(Roles.objects.get(role=role_for_user).big_prime)
        coefficient_list = graph.nodes[role_for_user].access_control_poly.coefficientList
        coefficient_list_JSON = json.dumps(coefficient_list)

        self.send(text_data=json.dumps({
            'action': 'receive_public_data',
            'z': z,
            'coefficient_list': coefficient_list_JSON,
            'p': p

        }))
    
    def publicize_graph_data(self, user_id):
        user_role = UsersRoles.objects.get(user_id=user_id).role
        user_uuid = user_role.uuid
        print(f"SERVER user_uuid: {user_uuid}")
        public_graph = {}
        for roles in Roles.objects.all():
            public_graph[roles.uuid] = []
        for edges in RoleEdges.objects.all():
            parent_uuid = edges.parent_role.uuid
            child_uuid = edges.child_role.uuid
            public_graph[parent_uuid].append((child_uuid, edges.edge_key))
        # print(nodes)
        self.send(text_data=json.dumps({
            'action': 'receive_public_graph_data',
            'user_uuid': user_uuid,
            'public_graph': public_graph
        }))
    
    def send_SID(self, user_id):
        """Right now the user login functionality is not working. Ideally if a user could log in
        then this function would take a user_id as an input and be able to detemine if this user already
        has an SID or needs to be assigned a new one."""
        SID = Users.objects.get(user_id=user_id).SID
        # if there isn't an SID already in the database assign one
        if SID is None:
            SID = graph.assignSID(user_id)
        self.send(text_data=json.dumps({
            'action': 'receive_SID',
            'SID': SID
        }))
