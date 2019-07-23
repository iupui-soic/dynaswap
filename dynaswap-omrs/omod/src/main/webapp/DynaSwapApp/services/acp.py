from Crypto.Util import number
from DynaSwapApp.models import Roles, RoleEdges, User, UsersRoles
from DynaSwapApp.services.hierarchy import Node, Edge, KeyManagement, HierarchyGraph
from itertools import combinations
import os

def hashMultipleToOne(listOfValuesToHash):
    # concatedHashes = ""
    # for value in listOfValuesToHash:
    #     concatedHashes += value
    # result = int(hashlib.sha256(concatedHashes.encode('utf-8')).hexdigest(), 0)
    # return result
    return pow(2, (listOfValuesToHash[0] ^ listOfValuesToHash[1]), listOfValuesToHash[2])


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
        newSecretKey = int(keyManage.generateSecretKey())

        SIDList = []
        ACP = []
        
        ACP.append(self.randomNum)
        ACP.append(self.bigPrime)
        ACP.append(1)

        for user in UsersRoles.objects.filter(role=self.curRole):
            SIDList.append(hashMultipleToOne([user.user_id.SID, self.randomNum, self.bigPrime]))

        for i in range(1, len(SIDList)):
            SIDComb = combinations(SIDList, i)
            polyTerm = 0
            multip = 1
            for everyComb in SIDComb:
                for everyTerm in everyComb:
                    multip = multip * everyComb % self.bigPrime
                polyTerm = (polyTerm + multip) % self.bigPrime
            ACP.append(polyTerm)
        ACP[len(ACP) - 1] = (ACP[len(ACP) - 1] + newSecretKey) % self.bigPrime
        #ACP is a list contains all the poly terms, maybe return this in Json objects to the client side to compute the secret key
        #ACP[0] = random number, ACP[1] = big prime
        #maybe also store the list to the database for queries later
        Roles.objects.get(role=userRole).update(random_num=self.randomNum, role_key=newSecretKey)
        return ACP


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
            
        return self.updateACP()


    def revokeUser(self, userID):
        userObj = User.objects.get(user_id=userID)
        UsersRoles.objects.get(user_id=userObj).delete()
        graph = HierarchyGraph(curRole)
        graph.updateSecretKey(curRole)

        return self.updateACP()


    #should move to client side?
    # def calcAccess(self, hashedValue):
    #     res = 0
    #     for userObj in UsersRoles.objects.filter(role=curRole):
    #         res = res * (hashMultipleToOne([userObj.SID, self.randomNum]) - hashedValue) % self.bigPrime
    #     return res + Roles.objects.get(role=curRole).role_key