from collections import defaultdict
from DynaSwapApp.models import Roles, RoleEdges, Users, UsersRoles
import hashlib
import sys
import os
import time
from .acp import hashMultipleToOneInt, accessControlPoly

start_time = time.time()


"""
Note about notation: 
    private key is 'k' in the paper
    secret key is 'k^' is k hat or k prime
"""

# concat values together and then hash
def hashMultipleToOne(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += value
    result = hashlib.md5(concatedHashes.encode('utf-8')).hexdigest()
    return result


def hashMultipleToOneInt(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += str(value)
    result = hashlib.md5(concatedHashes.encode('utf-8')).hexdigest()
    return int(result, 16)


def xor_two_strings(str1, str2):
    return "".join(chr(ord(a) ^ ord(b)) for a,b in zip(str1,str2))


#class of roles
class Node:
    def __init__(self, roleName, roleDesc, rolePublicID, secretKey=None, privateKey=None):
        self.roleName = roleName
        self.roleDesc = roleDesc
        self.rolePublicID = rolePublicID
        self.secretKey = secretKey
        self.privateKey = privateKey
        self.edges = dict()
        self.access_control_poly = accessControlPoly(self.roleName)


#class of edges
class Edge:
    def __init__(self, edgeKey):
        self.edgeKey = edgeKey


class KeyManagement:
    def __init__(self, keyLength):
        self.keyLength = keyLength

    def calcEdgeKey(self, parentPrivateKey, childPrivateKey, childLabel):
        print(f"parent: {parentPrivateKey}, child: {childPrivateKey}, childlabel: {childLabel}")
        hashed = hashMultipleToOneInt([parentPrivateKey, childLabel])
        # edgeKey = xor_two_strings(childPrivateKey, hashed)
        edgeKey = int(childPrivateKey, 16) ^ hashed
        return edgeKey 
    
    def generatePublicId(self):
        publicIDHex = hashlib.md5(os.urandom(self.keyLength)).hexdigest()
        return publicIDHex
    
    def generateSecretKey(self):
        secretKeyHex = hashlib.md5(os.urandom(self.keyLength)).hexdigest()
        return secretKeyHex
    
    def generatePrivateKey(self):
        # Right now this is pretty much the same as generateSecretKey but
        # they have been made different functions with the expectation that the logic may differ in the future.
        # If not they should be combined at some point
        privateKeyHex = hashlib.md5(os.urandom(self.keyLength)).hexdigest()
        return privateKeyHex


class HierarchyGraph:
    def __init__(self):
        self.nodes = dict()
        self.KeyManagement = KeyManagement(128)

    #add edge to the graph
    def addEdge(self, parentRoleName, childRoleName):
        # Need to make sure edge doesn't already exist in database before doing anything
        if not RoleEdges.objects.filter(parent_role=parentRoleName, child_role=childRoleName).exists():
            # Need to edit this function so that it uses isCyclic to make sure that adding an edge doesn't violate DAG
            parentRole = Roles.objects.get(role=parentRoleName)
            childRole = Roles.objects.get(role=childRoleName)
            parentPrivateKey = parentRole.role_second_key
            childPrivateKey = childRole.role_second_key
            childLabel = childRole.uuid
            edgeKey = self.KeyManagement.calcEdgeKey(parentPrivateKey, childPrivateKey, childLabel)
            # print(f"parentPrivateKey: {parentPrivateKey}\nchildPrivateKey: {childPrivateKey}\nchildLabel: {childLabel}\nedgeKey: {edgeKey}")
            # Create new edge object for local graph
            newEdge = Edge(edgeKey)
            print(f"parent: {parentRole}, child: {childRole}, edge key: {edgeKey}")
            # Use the names of parent and child roles for key names
            self.nodes[parentRole.role].edges[childRole.role] = newEdge
            # After adding edge check to make sure it isn't cylic (this graph should be a DAG)
            if not self.isCyclic():
                # If it isn't cyclic then it can be saved to the database
                RoleEdges(parent_role=parentRole, child_role=childRole, edge_key=edgeKey).save()
            # Otherwise it's cyclic and we need to remove it
            else:
                del self.nodes[parentRole.role].edges[childRole.role]
                raise CyclicError
            #calculate elapsed time
            elapsed = time.time() - start_time
            print(elapsed)

    #add a new role
    # def addRole(self, roleName, roleDesc, pubid, secretKey):
    #     privateKey = hashMultipleToOne([pubid, secretKey])
    #     # Is accessKey the correct parameter here? What is secondKey supposed to be in Node
    #     newNode = Node(roleName, roleDesc, pubid, secretKey, privateKey)
    #     # Add new node to local graph
    #     self.nodes[roleName] = newNode
    #     # Save node information to the database
    #     Roles(role=roleName, description=roleDesc, uuid=pubid, role_key=secretKey, role_second_key=privateKey).save()
    #     #calculate time elapsed
    #     elapsed = time.time() - start_time
    #     print(elapsed)

    def addRole(self, roleName, roleDesc):
        pubid = self.KeyManagement.generatePublicId()
        secret_key = self.KeyManagement.generateSecretKey()
        # privateKey = self.KeyManagement.generatePrivateKey()
        # newNode = Node(roleName, roleDesc, pubid, None, privateKey)
        print(f"SERVER uuid: {pubid}")
        print(f"SERVER secret_key: {secret_key}")
        private_key = hashMultipleToOne([secret_key, pubid])
        print(f"SERVER private_key: {private_key}")
        newNode = Node(roleName, roleDesc, pubid, secret_key, private_key)
        self.nodes[roleName] = newNode
        # Save node information to the database
        Roles(role=roleName, description=roleDesc, uuid=pubid, role_key=secret_key, role_second_key=private_key).save()
        # Cant update acp before Role is created in database because updateACP saves additional info to Role
        newNode.access_control_poly.updateACP(secret_key)
        #calculate time elapsed
        elapsed = time.time() - start_time
        print(elapsed)
    

    #read data from database and add roles and edges
    def createGraph(self):
        for roles in Roles.objects.all():
            self.nodes[roles.role] = Node(roles.role, roles.description, roles.uuid, roles.role_key, roles.role_second_key)
        for edges in RoleEdges.objects.all():
            self.nodes[edges.parent_role.role].edges[edges.child_role.role] = Edge(edges.edge_key)

    #DFS from the specific role
    def isCyclicUtil(self, roleID, visited, recStack):
        # Mark current node as visited and  
        # adds to recursion stack 
        visited[roleID] = True
        recStack[roleID] = True

        # Recur for all neighbours 
        # if any neighbour is visited and in recStack then graph is cyclic 
        for neighbour in self.nodes[roleID].edges.keys():
            if visited[neighbour] == False:
                if self.isCyclicUtil(neighbour, visited, recStack):
                    return True
            elif recStack[neighbour]:
                return True

        # The node needs to be poped from  
        # recursion stack before function ends 
        recStack[roleID] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = dict() 
        recStack = dict() 
        for roleID in self.nodes.keys():
            visited[roleID] = False
        recStack = visited.copy()
        for roleID in self.nodes.keys(): 
            if visited[roleID] == False: 
                if self.isCyclicUtil(roleID,visited,recStack): 
                    return True
        return False

    #update the public ID and access key of the role
    def updatePublicID(self, roleID):
        newUUID = self.KeyManagement.generatePublicId()
        self.nodes[roleID].uuid = newUUID
        self.nodes[roleID].privateKey = hashMultipleToOne([self.nodes[roleID].uuid, self.nodes[roleID].secretKey])
        Roles.objects.filter(role=roleID).update(uuid=self.nodes[roleID].uuid, role_second_key=self.nodes[roleID].privateKey)

    def updateSecretKey(self, roleID):
        #update the secret key first, then compute the new private key for the role
        newSecretKey = self.KeyManagement.generateSecretKey()
        self.nodes[roleID].secretKey = newSecretKey
        self.nodes[roleID].privateKey = hashMultipleToOne([self.nodes[roleID].uuid, self.nodes[roleID].secretKey])
        Roles.objects.filter(role=roleID).update(role_second_key=self.nodes[roleID].privateKey, role_key=self.nodes[roleID].secretKey)
        #for edges connected to the role, change edge keys 
        for parentRole in self.findPred(roleID).keys():
            self.nodes[parentRole].edges[roleID].edgeKey = self.KeyManagement.calcEdgeKey(self.nodes[parentRole].secondKey, self.nodes[roleID].secondKey, self.nodes[roleID].rolePublicID)
            parent = Roles.objects.get(role=parentRole)
            child = Roles.objects.get(role=roleID)
            RoleEdges.objects.filter(parent_role=parent, child_role=child).update(edge_key=self.nodes[parentRole].edges[roleID].edgeKey)
        #for edges from this role, change edge keys
        for children in self.nodes[roleID].edges.keys():
            self.nodes[roleID].edges[children].edgeKey = self.KeyManagement.calcEdgeKey(self.nodes[roleID].secondKey, self.nodes[children].secondKey, self.nodes[children].rolePublicID)
            parent = Roles.objects.get(role=roleID)
            child = Roles.objects.get(role=children)
            RoleEdges.objects.filter(parent_role=parent, child_role=child).update(edge_key=self.nodes[roleID].edges[children].edgeKey)

    def delEdge(self, parentRoleID, childRoleID):
            #generate a new ID for parent and compute new k
            self.nodes[parentRoleID].edges.pop(childRoleID)
            #update publicID for all the decs of role
            #for all the roles involved, find the pred sets and update the edge keys
            for roles in self.findDesc(childRoleID).keys():
                self.updatePublicID(roles)
                for rolePred in self.findPred(roles).keys():
                    self.nodes[rolePred].edges[roles].edgeKey = self.KeyManagement.calcEdgeKey(self.nodes[rolePred].secondKey, self.nodes[roles].secondKey, self.nodes[roles].rolePulicID)
                    parentRole = Roles.objects.get(role=rolePred)
                    childRole = Roles.objects.get(role=roles)
                    RoleEdges.objects.filter(parent_role=parentRole, child_role=childRole).update(edge_key=self.nodes[rolePred].edges[roles].edgeKey)
            #delete record in database
            parentRole = Roles.objects.get(role=parentRoleID)
            childRole = Roles.objects.get(role=childRoleID)
##            print(parentRole.role)
##            print(childRole.role)
##            print (RoleEdges.objects.filter(parent_role=parentRole, child_role=childRole))
            RoleEdges.objects.filter(parent_role=parentRole, child_role=childRole).delete()
            #calculate elapsed time
            elapsed = time.time() - start_time
            print(elapsed)
            

    def delRole(self, inputRoleId):
        for roleID, roleObj in self.nodes.items():
            if roleID == inputRoleId:
                #del all children edges
                for childrenRole in list(roleObj.edges):
                    self.delEdge(roleID, childrenRole)
            if inputRoleId in roleObj.edges:
                #del all parent edges
                self.delEdge(roleID, inputRoleId)
        self.nodes.pop(inputRoleId)
        Roles.objects.filter(role=inputRoleId).delete()
        #calculate time elapsed
        elapsed = time.time() - start_time
        print(elapsed)


    def accessRole(self, curRoleID, targetRoleID):
        #DFS to the role wanted with key decoding
        if curRoleID == targetRoleID:
            return True
        for children in self.nodes[curRoleID].edges.keys():
            if xor_two_strings(self.nodes[curRoleID].edges[children].edgeKey, hashMultipleToOne(self.nodes[curRoleID].privateKey, self.nodes[children].rolePublicID)) == self.nodes[children].privateKey:
                if self.accessRole(children, targetRoleID):
                    return True
        return False
        
    #determine if there is a path from origin to the target role
    def havePath(self, originRoleID, targetRoleID):
        if originRoleID == targetRoleID:
            return True
        for children in self.nodes[originRoleID].edges.keys():
            if self.havePath(children, targetRoleID):
                return True
        return False
    
    #return the list of descendants of the role
    def findDesc(self, originRoleID):
        desc = dict()
        for roles in self.nodes.keys():
            if (roles not in desc) and (self.havePath(originRoleID, roles)):
                desc[roles] = False
        return desc
    
    #return the list of immediate predecessors of the role
    def findPred(self, originRoleID):
        pred = dict()
        for roles in self.nodes.keys():
            if (roles not in pred) and (originRoleID in self.nodes[roles].edges):
                pred[roles] = False
        return pred
    
    def addUser(self, userID, roleID):
        # only do something if there isn't already an entry in UsersRoles
        if not UsersRoles.objects.filter(user_id=userID).exists():
            useObj = Users.objects.get(user_id=userID)
            roleObj = Roles.objects.get(role=roleID)
            UsersRoles(user_id=useObj, role=roleObj).save()
            # Not sure if this actually needs to be done here
            # self.nodes[roleID].access_control_poly.updateACP(self.KeyManagement.generateSecretKey())
    
    def assignSID(self, userID):
        SID = self.KeyManagement.generateSecretKey()
        Users.objects.filter(user_id=userID).update(SID=SID)
        return SID
    
    def revokeUser(self, userID, roleID):
        userObj = Users.objects.get(user_id=userID)
        UsersRoles.objects.get(user_id=userObj).delete()
        self.updateSecretKey(roleID)

        return self.nodes[roleID].access_control_poly.updateACP()
        

# Should be moved to a file for exceptions at some point
class CyclicError(Exception):
    pass
