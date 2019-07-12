from django.test import TestCase
from DynaSwapApp.services.hierarchy import *
from DynaSwapApp.models import Roles

# Create your tests here.
class HelperFunctionTests(TestCase):
    def setUp(self):
        pass
    
    def test_xor_two_strings(self):
        """Test basic case of xoring two short strings"""
        xored = xor_two_strings("abc", "def")
        expectedResult = "\x05\x07\x05"
        self.assertEquals(xored, expectedResult)

    def test_xor_two_strings_type_error(self):
        """Check to make sure function raises error when inputs are not strings"""
        with self.assertRaises(TypeError):
            xor_two_strings("abc", 3)
            xor_two_strings(3, "abc")
            xor_two_strings(3, 3)


class KeyManagementTests(TestCase):
    def setUp(self):
        self.KeyManagement = KeyManagement(128)


class HierarchyGraphTests(TestCase):
    def setUp(self):
        self.HierarchyGraph = HierarchyGraph("doctor")

    def tearDown(self):
        # If there are any node values get rid of them for the next test
        if self.HierarchyGraph.nodes:
            self.HierarchyGraph.nodes.clear

    def test_addEdge(self):
        """Test basic case of adding an edge"""
        # Need to create two test nodes before edges can be added to it
        # Values for first node
        roleName1 = "doctor"
        roleDesc1 = "doc desc"
        pubid1 = "123"
        privateKey1 = "456"
        secondKey1 = "789"
        # Values for second node
        roleName2 = "nurse"
        roleDesc2 = "nurse desc"
        pubid2 = "456"
        privateKey2 = "654"
        secondKey2 = "999"
        
        newEdgeKey = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

        Roles(role=roleName1, description=roleDesc1, uuid=pubid1, role_key=privateKey1, role_second_key=secondKey1).save()
        Roles(role=roleName2, description=roleDesc2, uuid=pubid2, role_key=privateKey2, role_second_key=secondKey2).save()
        self.HierarchyGraph.nodes[roleName1] = Node(roleName1, roleDesc1, pubid1, privateKey1, secondKey1)
        self.HierarchyGraph.nodes[roleName2] = Node(roleName2, roleDesc2, pubid2, privateKey2, secondKey2)
        # Just using the sha256 hash of 'test' string for edge key right now
        self.HierarchyGraph.addEdge(roleName1, roleName2, newEdgeKey)
        # Grab the new edge from the database
        newEdgeDatabase = RoleEdges.objects.get(parent_role="doctor")
        # Make sure that we are also able to get the edge from the local graph
        newEdgeLocal = self.HierarchyGraph.nodes[roleName1].edges[roleName2]
        # Make sure that database saved correctly
        self.assertEquals(newEdgeDatabase.edge_key, newEdgeKey)
        # Make sure that local and database match
        self.assertEquals(newEdgeDatabase.edge_key, newEdgeLocal.edgeKey)

    #Test Deleting Edges
    def test_delEdge(self):
        """Delete an existing edge"""
        roleName1 = "doctor"
        roleDesc1 = "doc desc"
        pubid1 = "123"
        privateKey1 = "456"
        secondKey1 = "789"
        # Values for second node
        roleName2 = "nurse"
        roleDesc2 = "nurse desc"
        pubid2 = "456"
        privateKey2 = "654"
        secondKey2 = "999"
        #Create new edge same as test add Edge
        newEdgeKey = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"

        Roles(role=roleName1, description=roleDesc1, uuid=pubid1, role_key=privateKey1, role_second_key=secondKey1).save()
        Roles(role=roleName2, description=roleDesc2, uuid=pubid2, role_key=privateKey2, role_second_key=secondKey2).save()
        self.HierarchyGraph.nodes[roleName1] = Node(roleName1, roleDesc1, pubid1, privateKey1, secondKey1)
        self.HierarchyGraph.nodes[roleName2] = Node(roleName2, roleDesc2, pubid2, privateKey2, secondKey2)
        self.HierarchyGraph.addEdge(roleName1, roleName2, newEdgeKey)
        newEdgeDatabase = RoleEdges.objects.get(parent_role="doctor")
        newEdgeLocal = self.HierarchyGraph.nodes[roleName1].edges[roleName2]
        #del Edge between roles
        self.HierarchyGraph.delEdge(roleName1, roleName2)
        self.assertEquals(newEdgeDatabase.edge_key, newEdgeLocal.edgeKey)
##        
        
    def test_addEdge_doesnt_exist(self):
        """If the node we are trying to add an edge to doesn't exist we should get a DoesNotExist error"""
        with self.assertRaises(Roles.DoesNotExist):
            self.HierarchyGraph.addEdge("doctor", "nurse", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")

    # Because of how we have the testing database setup I am not sure if this is actually saving correctly
        
    
    def test_addRole(self):
        """Test basic case of addRole"""
        self.HierarchyGraph.addRole("nurse", "nurse description", "123", "456")
        newRole = Roles.objects.get(role="nurse")
        self.assertEquals(newRole.role, "nurse")
        self.assertEquals(newRole.description, "nurse description")
        self.assertEquals(newRole.uuid, "123")
        self.assertEquals(newRole.role_key, "456")
        # Not sure what this value should be right now so just check if there is something there
        self.assertTrue(newRole.role_second_key)

    def test_updatePublicID(self):
        """Add role then update its public id"""
        self.HierarchyGraph.addRole("nurse", "nurse description", "123", "456")
        newRole = Roles.objects.get(role="nurse")
        self.assertEquals(newRole.role, "nurse")
        self.assertEquals(newRole.description, "nurse description")
        self.assertEquals(newRole.uuid, "123")
        self.assertEquals(newRole.role_key, "456")
        self.assertTrue(newRole.role_second_key)
        #update the public ID for the new role
        self.HierarchyGraph.updatePublicID(newRole.role)
        newRole = Roles.objects.get(role = "nurse")
        #test if the new uuid is not equal to the old one
        self.assertNotEqual(newRole.uuid, "123")

    def test_createGraph(self):
        """Test basic case of createGraph"""
        # create some test roles and edges with fake values to build the graph
        self.HierarchyGraph.createGraph() 
        # Should be greater than zero because as of now there are some entries already in the dataase
        nodes = self.HierarchyGraph.nodes
        numberOfNodes = len(nodes)
        # Right now there are not any existing edge connections in the database
        # But if we were to put some in then we could just check the number of edges
        numberOfEdges = sum([len(v.edges) for k,v in nodes.items()])
        # Right now the structure of the original database is subject to change so it is difficult to test if the structure is exactly as intended. So instead for right now I will just check to make sure that nodes have been created
        self.assertGreater(numberOfNodes, 0)
        # self.assertGreater(numberOfEdges, 0)


    def test_createGraph_and_build_on_it(self):
        """Should be able to build graph correctly from database and then add on to it"""
        self.HierarchyGraph.createGraph() 
        self.HierarchyGraph.addRole("test1", "test1 description", "1", "testPrivateKey1")
        self.HierarchyGraph.addRole("test2", "test2 description", "2", "testPrivateKey2")
        self.HierarchyGraph.addRole("test3", "test3 description", "3", "testPrivateKey3")
        self.HierarchyGraph.addEdge("test1", "test2", "test1to2edgeKey")
        self.HierarchyGraph.addEdge("test1", "test3", "test1to3edgeKey")


    def test_delRole(self):
        """Should be able to create a role with edges and then delete that role along with it's edges"""
        self.HierarchyGraph.createGraph()
        self.HierarchyGraph.addRole("test1", "test1 desc", "1", "testPrivateKey1")
        self.HierarchyGraph.addRole("test2", "test2 desc", "2", "testPrivateKey2")
        self.HierarchyGraph.addRole("test3", "test3 description", "3", "testPrivateKey3")
        self.HierarchyGraph.addEdge("test1", "test2", "test1to2edgeKey")
        self.HierarchyGraph.addEdge("test1", "test3", "test1to3edgeKey")
        # role id to be deleted
        roleId = "test1"
        self.HierarchyGraph.delRole(roleId)
        localRoles = self.HierarchyGraph.nodes
        # the local role should be deleted so the node should not exist anymore
        nodeExists = False
        if roleId in localRoles:
            nodeExists = True
        self.assertEquals(nodeExists, False)
        with self.assertRaises(Roles.DoesNotExist):
            databaseRoles = Roles.objects.get(role=roleId)
        with self.assertRaises(RoleEdges.DoesNotExist):
            # After the role is deleted it's edges should also be deleted
            roleEdges = RoleEdges.objects.get(parent_role=roleId)
