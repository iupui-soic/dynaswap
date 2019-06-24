from collections import defaultdict
from DynaSwapApp.models import Roles
from DynaSwapApp.models import RoleEdges
import hashlib

# Not sure if there is a way to hash using multiple inputs
# So I am just creating a helper function to hash multiple values into one hash
def hashMultipleToOne(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += hashlib.sha256(value.encode('utf-8')).hexdigest()
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


class HierarchyGraph:

    def __init__(self, curRole, keyLength):
        self.roleNum = 0
        #counter for assign roleID, or just get rid of it and use roleName
        self.curRole = curRole
        self.nodes = dict()
        self.keyLength = keyLength
    
    def calcEdgeKey(self, parentPrivateKey, childPrivateKey, childLabel):
        hashed = hashMultipleToOne([parentPrivateKey, childLabel])
        edgeKey = xor_two_strings(childPrivateKey, hashed)
        # maybe take the rightmost 128 bits of edgeKey instead of using mod part of equation from paper
        return edgeKey       

    #add edge to the graph
    def addEdge(self, parentRoleName, childRoleName, edgeKey):
        newEdge = Edge(edgeKey)
        self.nodes[parentRoleName].edges[childRoleName] = newEdge

    #add a new role
    def addRole(self, roleName, roleDesc, rolePublicID, privateKey, secondKey):


    #read data from database and add roles and edges
    def createGraph(self):


    #DFS from the specific role
    def isCyclicUtil(self, roleID, visited, recStack):


    # Returns true if graph is cyclic else false
    def isCyclic(self):


    def delEdge(self, parentRoleID, childRoleID):
        #generate a new ID for parent and compute new k
        #delete record in database
        #RoleEdge.objects.filter(parent_role=u, child_role=v).delete()

    
    def delRole(self, RoleID):
        #we may want another dict to store the parents of each role to make del easier

    def accessRole(self, curRoleID, targetRoleID):
        #DFS to the role wanted
        #either find the role first then compare keys along the path, or compare keys in DFS
        