from Crypto.Util import number
from DynaSwapApp.models import Roles, RoleEdges, User, UsersRoles
from DynaSwapApp.services.hierarchy import Node, Edge, KeyManagement, HierarchyGraph
import os

def hashMultipleToOne(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += value
    result = int(hashlib.sha256(concatedHashes.encode('utf-8')).hexdigest(), 0)
    return result

#I'm assuming that the User model has a new field 'SID', and it's assigned during the registration for now.
#And UsersRoles model has new fields 'big_prime', 'random_number' indicating the prime and random number used in the function
#The construction of accessControlPoly class will request the target role
class accessControlPoly:

    def __init__(self, curRole, bigPrime, randomNum):
        self.curRole = curRole
        self.bigPrime = Roles.objects.get(role=curRole).big_prime
        self.randomNum = Roles.objects.get(role=curRole).random_num


    def updatePrime(self):
        self.bigPrime = number.getPrime(128)
        Roles.objects.get(role=curRole).update(big_prime=self.bigPrime)


    def updateACP(self):
        self.randomNum = os.urandom(128)
        keyManage = KeyManagement(128)
        newSecretKey = keyManage.generateSecretKey()
        Roles.objects.get(role=userRole).update(random_num=self.randomNum, role_key=newSecretKey)


    #depend on the registration
    def assignSID(self):
        pass


    #add an existing user in the Users model to the target Roles
    def addUser(self, userID):
        try:
            user = User.objects.get(user_id=userID)
            res = UsersRoles.objects.get(user_id=user)
        except SomeModel.DoesNotExist:
            res = None
        if res not None:
            userObj = User.objects.get(user_id=userID)
            roleObj = Roles.objects.get(role=curRole)
            UsersRoles(user_id=userObj, role=roleObj).save()
        #send message to all the users(only random number needed now)


    def revokeUser(self, userID):
        userObj = User.objects.get(user_id=userID)
        UsersRoles.objects.get(user_id=userObj).delete()
        self.updateACP()
        #send to all users
        #update keys in the graph
        graph = HierarchyGraph(curRole)
        graph.updateSecretKey(curRole)


    def calcAccess(self, hashedValue):
        res = 0
        for userObj in UsersRoles.objects.filter(role=curRole):
            res = res * (hashMultipleToOne([userObj.SID, self.randomNum]) - hashedValue) % self.bigPrime
        return res + Roles.objects.get(role=curRole).role_key

        