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
        # Need to create a test node before edges can be added to it
        roleName = "doctor"
        roleDesc = "doc description"
        pubid = "123"
        privateKey = "456"
        secondKey = "789"
        Roles(role=roleName, description=roleDesc, uuid=pubid, role_key=privateKey, role_second_key=secondKey).save()
        Roles(role="nurse", description="nurse desc", uuid="456", role_key="456", role_second_key=secondKey).save()
        self.HierarchyGraph.nodes[roleName] = Node(roleName, roleDesc, pubid, privateKey, secondKey)
        # Just using the sha256 hash of 'test' string for edge key right now
        self.HierarchyGraph.addEdge("doctor", "nurse", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")
        # edge =  RoleEdges.objects.get(parent_role="doctor")
        # print(edge.child_role)
        # newEdge = self.HierarchyGraph.nodes["doctor"].edges["nurse"]
        # newEdgeKey = newEdge.edgeKey
        # self.assertEquals(newEdgeKey, "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")

    # def test_addEdge_key_error(self):
        # """If the node we are trying to add an edge to doesn't exist we should get a keyerror"""
        # with self.assertRaises(KeyError):
            # self.HierarchyGraph.addEdge("doctor", "nurse", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")

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

    # def test_createGraph(self):
    #     """Test basic case of createGraph"""
    #     # create some test roles and edges with fake values to build the graph
    #     self.HierarchyGraph.addRole("test1", "test1 description", "1", "testPrivateKey1")
    #     self.HierarchyGraph.addRole("test2", "test2 description", "2", "testPrivateKey2")
    #     self.HierarchyGraph.addRole("test3", "test3 description", "3", "testPrivateKey3")
    #     self.HierarchyGraph.addEdge("test1", "test2", "test1to2edgeKey")
    #     self.HierarchyGraph.addEdge("test1", "test3", "test1to3edgeKey")
    #     self.HierarchyGraph.createGraph()

