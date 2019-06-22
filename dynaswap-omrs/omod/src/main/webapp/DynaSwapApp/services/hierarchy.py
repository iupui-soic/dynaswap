from collections import defaultdict
from DynaSwapApp.models import Roles
from DynaSwapApp.models import RoleEdges

#class of roles
class Node:

    def __init__(self, roleName, roleDesc, rolePublicID, privateKey):
        self.roleName = roleName
        self.roleDesc = roleDesc
        self.rolePublicID = rolePublicID
        self.privateKey = privateKey
        #compute the second key
        self.edges = dict()


#class of edges
class Edge:

    def __init__(self, edgeKey):
        self.__edgeKey = edgeKey

    #get the edge_key
    def tryEdgeEquation(self):

class HierarchyGraph:

    def __init__(self, curRole):
        self.roleNum = 0
        #counter for assign roleID, or just get rid of it and use roleName
        self.curRole = curRole
        self.nodes = dict()
        

    #add edge to the graph
    def addEdge(self, parentRoleID, childRoleID, edgeKey):
        #we may want a dict for the relationship between roleName and roleID to simplify adding edge from the database
        #or just use the name of the role as roleID

    #add a new role
    def addRole(self, roleName, roleDesc, rolePublicID, privateKey):


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

        