from collections import defaultdict
from DynaSwapApp.models import Roles
from DynaSwapApp.models import RoleEdges
import hashlib
import sys
import os

# concat values together and then hash
def hashMultipleToOne(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += value
    result = hashlib.sha256(concatedHashes.encode('utf-8')).hexdigest()
    return result


def xor_two_strings(str1, str2):
    return "".join(chr(ord(a) ^ ord(b)) for a,b in zip(str1,str2))


#class of roles
class Node:
    def __init__(self, roleName, roleDesc, rolePublicID, privateKey, secondKey):
        self.roleName = roleName
        self.roleDesc = roleDesc
        self.rolePublicID = rolePublicID
        self.privateKey = privateKey
        self.secondKey = secondKey
        self.edges = dict()


#class of edges
class Edge:
    def __init__(self, edgeKey):
        self.edgeKey = edgeKey


class KeyManagement:
    def __init__(self, keyLength):
        self.keyLength = keyLength

    def calcEdgeKey(self, parentPrivateKey, childPrivateKey, childLabel):
        hashed = hashMultipleToOne([parentPrivateKey, childLabel])
        edgeKey = xor_two_strings(childPrivateKey, hashed)
        # maybe take the rightmost 128 bits of edgeKey instead of using mod part of equation from paper
        return edgeKey 
    
    def generatePublicId(self):
        publicIDHex = hashlib.md5(os.urandom(self.keyLength)).hexdigest()
        pubid = publicIDHex.decode('hex')
        return pubid
    
    def generatePrivateId(self):
        privateKeyHex = hashlib.md5(os.urandom(self.keyLength)).hexdigest()
        privateKey = privateKeyHex.decode('hex')
        return privateKey


class HierarchyGraph:
    def __init__(self, curRole):
        self.roleNum = 0
        #counter for assign roleID, or just get rid of it and use roleName
        self.curRole = curRole
        self.nodes = dict()

    #add edge to the graph
    def addEdge(self, parentRoleName, childRoleName, edgeKey):
        # Save the role edge to the database
        # An Edge object will be created later when createGraph is called
        RoleEdges(parent_role=parentRoleName, child_role=childRoleName, edge_key=edgeKey).save()

    #add a new role
    def addRole(self, roleName, roleDesc, pubid, privateKey):
        accessKey = hashMultipleToOne([pubid, privateKey])
        # Not sure if this is actually saving correctly because of our weird test database setup
        Roles(role=roleName, description=roleDesc, uuid=pubid, role_key=privateKey, role_second_key=accessKey).save()

    #read data from database and add roles and edges
    def createGraph(self):
        for roles in Roles.objects.all():
            self.nodes[roles.role] = Node(roles.role, roles.description, roles.uuid, roles.role_key, roles.role_second_key)
        for edges in RoleEdges.objects.all():
            self.nodes[edges.parent_role].edges[edges.child_role] = Edge(edges.edge_key)

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
    def updatePublicID(self, roleID, rolePublicId):
        self.nodes[roleID].secondKey = hashMultipleToOne([self.nodes[roleID].rolePublicID, self.nodes[roleID].privateKey])
        Roles.objects.filter(role=roleID).update(uuid=self.nodes[roleID].rolePublicID, role_second_key=self.nodes[roleID].secondKey)

    def delEdge(self, parentRoleID, childRoleID):
        #generate a new ID for parent and compute new k
        self.nodes[parentRoleID].edges.pop(childRoleID)
        #update publicID for all the decs of role
        #for all the roles involved, find the pred sets and update the edge keys
        for roles in self.findDesc(childRoleID).keys():
            self.updatePublicID(roles)
            for rolePred in self.findPred(roles).keys():
                self.nodes[rolePred].edges[roles].edgeKey = self.calcEdgeKey(self.nodes[rolePred].secondKey, self.nodes[roles].secondKey, self.nodes[roles].rolePulicID)
                RoleEdges.objects.filter().update(edge_key=self.nodes[rolePred].edges[roles].edgeKey)
        #delete record in database
        RoleEdge.objects.filter(parent_role=parentRoleID, child_role=childRoleID).delete()

    def delRole(self, RoleID):
        #we may want another dict to store the parents of each role to make del easier
        for (roleID, roleObj) in self.nodes.items():
            if roleID == RoleID:
                #del all children edges
                for childrenRole in roleObj.edges.keys():
                    self.delEdge(roleID, childrenRole)
            if roleObj.edges.has_key(RoleID):
                #del all parent edges
                self.delEdge(roleID, RoleID)
        self.nodes.pop(RoleID)
        Roles.objects.filter(role=RoleID).delete()

    def accessRole(self, curRoleID, targetRoleID):
        #DFS to the role wanted with key decoding
        if curRoleID == targetRoleID:
            return True
        for children in self.nodes[curRoleID].edges.keys():
            if xor_two_strings(self.nodes[curRoleID].edges[children].edgeKey, hashMultipleToOne(self.nodes[curRoleID].secondKey, self.nodes[children].rolePublicID)) == self.nodes[children].secondKey:
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
            if ((desc.has_key(roles) == False) and (self.havePath(originRoleID, roles))):
                desc[roles] = False
        return desc
    
    #return the list of immediate predecessors of the role
    def findPred(self, originRoleID):
        pred = dict()
        for roles in self.nodes.keys():
            if ((pred.has_key(roles) == False) and (self.nodes[roles].edges.has_key(originRoleID))):
                pred[roles] = False
        return pred
        
