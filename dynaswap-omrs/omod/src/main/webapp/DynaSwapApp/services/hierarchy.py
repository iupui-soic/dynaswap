from collections import defaultdict
from DynaSwapApp.models import Roles
from DynaSwapApp.models import RoleEdges


class Hierarchy:

    def __init__(self):
        self.children = defaultdict(list)
        self.parent = defaultdict(list)
        self.edgeKey = defaultdict(list)
        self.roleDict = dict()
        self.roleKey = dict()
        self.roleID = dict()
        self.roleNum = 0


    #add edge from database
    def addEdge(self, u, v, uvkey):
        self.children[self.roleDict[u]].append(self.roleDict[v])
        self.parent[self.roleDict[v]].append(self.roleDict[u])
        self.edgeKey[self.roleDict[u]][self.roleDict[v]].append(uvkey)


    #add role from database
    def addRole(self, u, uid, ukey):
        self.roleDict.setdefault(u, ++self.roleNum)
        self.roleID.setdefault(self.roleNum, uid)
        self.roleKey.setdefault(self.roleNum, ukey)


    #create the DAG for check and access
    def createGraph(self):
        for roles in Roles.objects.all():
            addRole(roles.role, roles.uuid, roles.role_key)
        for roleEdge in RoleEdges.objects.all():
            addEdge(roleEdge.parent_role, roleEdge.child_role, roleEdge.edge_key)


    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.children[v]:
            if !visited[neighbour]:
                if self.isCyclicUtil(neighbour, visited, recStack):
                    return True
            elif recStack[neighbour]:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        recStack[v] = False
        return False


    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = [False] * self.roleNum
        recStack = [False] * self.roleNum
        for node in range(self.roleNum):
            if !visited[node]:
                if self.isCyclicUtil(node, visited, recStack):
                    return True
        return False
    

    def addNewEdge(self, u, v):
        if !self.children[self.roleDict[u]][self.roleDict[v]]:
            #compute edge key
            #cur_key = self.roleKey[self.roleDict[v]] ^ H(H(self.roleKey[self.roleDict[u]], roleID[self.roleDict[u]]), roleID[self.roleDict[v]])
            self.addEdge(u, v, cur_key)
            if !self.isCyclic():
                #save to database
                #newEdge = RoleEdge(parent_role = u, child_role = v, edge_key = cur_key)
                #newEdge.save()
                return True


    def delEdge(self, u, v):
        #generate a new ID for parent and compute new k
        #delete record in database
        #RoleEdge.objects.filter(parent_role=u, child_role=v).delete()


    def addNewRole(self, u):
        self.roleDict[u] = ++self.roleNum
        #generate ID, private key

        #save to database
        #newrole = ()
        #newrole.save()


    def delRole(self, u):
        for parent in self.parent[self.roleDict[u]]:
            delEdge(self.roleDict.key()[self.roleDict.value().index(parent)], u)
        for children in self.children[self.roleDict[u]]:
            delEdge(u, self.roleDict.key()[self.roleDict.value().index(children)])
        #del the record in database
        #Roles.objects.filter(role=u).delete()

    def accessRole(self, u, v):
        #DFS to the role wanted
        #either find the role first then compare keys along the path, or compare keys in DFS

        