from Crypto.Util import number
from DynaSwapApp.models import Roles, RoleEdges, Users, UsersRoles
# from DynaSwapApp.services.hierarchy import Node, Edge, KeyManagement, HierarchyGraph
from itertools import combinations
import os
import hashlib
import struct

# concat values together and then hash
def hashMultipleToOneInt(listOfValuesToHash):
    concatedHashes = ""
    for value in listOfValuesToHash:
        concatedHashes += str(value)
    result = hashlib.md5(concatedHashes.encode('utf-8')).hexdigest()
    return int(result, 16)

#I'm assuming that the User model has a new field 'SID', and it's assigned during the registration for now.
#And UsersRoles model has new fields 'big_prime', 'random_number' indicating the prime and random number used in the function
#The construction of accessControlPoly class will request the target role
class accessControlPoly:

    def __init__(self, curRole):
        self.curRole = curRole
        self.updatePrime()
        self.updateRandNum()

    def updatePrime(self):
        # Models says that integer can go up to 128 but MYSQL caps ints at (2^32)-1? So just use 30 for now
        self.bigPrime = number.getPrime(30)
        Roles.objects.filter(role=self.curRole).update(big_prime=self.bigPrime)
    
    def updateRandNum(self):
        # Just using an unsigned short for now because it fits in MYSQL.
        # Maybe change MYSQL INT to BIGINT later?
        self.randomNum = struct.unpack('H', os.urandom(2))[0]
        Roles.objects.filter(role=self.curRole).update(random_num=self.randomNum)

    def updateACP(self, newSecretKey):
        # self.randomNum = os.urandom(128)
        self.updateRandNum()
        # keyManage = KeyManagement(128)
        # newSecretKey = int(keyManage.generateSecretKey())
        newSecretKeyHex = int(newSecretKey, 16)

        SIDList = []
        ACP = []
        
        ACP.append(self.randomNum)
        ACP.append(self.bigPrime)
        ACP.append(1)

        for entry in UsersRoles.objects.filter(role=self.curRole):
            # The models are setup kind of weird.
            # entry is a UsersRoles object. There is a User object stored under user_id on this object
            # On the User object the user_id is stored as an int under the property user_id
            # So to actually get the user_id number you must access the user_id property twice. This should be cleaned up later.
            user_id_num = entry.user_id.user_id
            # use the user_id_num from the user_role table mapping to get the user object
            # and grab the SID from the user object
            SID = Users.objects.filter(user_id=user_id_num)[0].SID
            SIDList.append(hashMultipleToOneInt([SID, self.randomNum, self.bigPrime]))

        for i in range(1, len(SIDList)):
            SIDComb = combinations(SIDList, i)
            polyTerm = 0
            multip = 1
            for everyComb in SIDComb:
                for everyTerm in everyComb:
                    multip = multip * everyComb % self.bigPrime
                polyTerm = (polyTerm + multip) % self.bigPrime
            ACP.append(polyTerm)
        ACP[len(ACP) - 1] = (ACP[len(ACP) - 1] + newSecretKeyHex) % self.bigPrime
        #ACP is a list contains all the poly terms, maybe return this in Json objects to the client side to compute the secret key
        #ACP[0] = random number, ACP[1] = big prime
        #maybe also store the list to the database for queries later
        Roles.objects.filter(role=self.curRole).update(role_key=newSecretKey)
        return ACP


    #depend on the registration
    def assignSID(self):
        pass


    #add an existing user in the Users model to the target Roles
    # def addUser(self, userID):
    #     try:
    #         user = Users.objects.get(user_id=userID)
    #         res = UsersRoles.objects.get(user_id=user)
    #     except UsersRoles.DoesNotExist:
    #         res = None

    #     if res:
    #         userObj = Users.objects.get(user_id=userID)
    #         roleObj = Roles.objects.get(role=curRole)
    #         UsersRoles(user_id=userObj, role=roleObj).save()
            
    #     return self.updateACP()


    # def revokeUser(self, userID):
    #     userObj = Users.objects.get(user_id=userID)
    #     UsersRoles.objects.get(user_id=userObj).delete()
    #     graph = HierarchyGraph(curRole)
    #     graph.updateSecretKey(curRole)

    #     return self.updateACP()

