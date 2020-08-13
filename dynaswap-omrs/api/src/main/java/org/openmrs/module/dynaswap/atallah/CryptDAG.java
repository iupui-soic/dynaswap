package org.openmrs.module.dynaswap.atallah;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Set;
import java.util.Comparator;

import org.openmrs.api.context.Context;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.node.ArrayNode;
import org.codehaus.jackson.node.ObjectNode;
import org.openmrs.Privilege;
import org.openmrs.Role;

/**
 * CryptDAG
 */
public class CryptDAG {
	
	private String formattedGraph;
	
	/**
	 * constructor
	 */
	public CryptDAG() {
		this.createGraph();
	}
	
	public void createGraph() {
		List<Role> roles = Context.getUserService().getAllRoles();
		ArrayList<Set<Privilege>> nodePrivs = new ArrayList<Set<Privilege>>();
		// Maybe change role key to use uuid (unique)?
		ArrayList<ImmutablePair<String, Set<Privilege>>> rolePrivMappings = new ArrayList<ImmutablePair<String, Set<Privilege>>>();
		for (Role role : roles) {
			// Get a list of all the possible privileges.
			nodePrivs.add(role.getPrivileges());
			// Build role/privilege mapping.
			String roleName = role.getName();
			Set<Privilege> privs = role.getPrivileges();
			ImmutablePair<String, Set<Privilege>> mapping = new ImmutablePair<String, Set<Privilege>>(roleName, privs);
			rolePrivMappings.add(mapping);
		}
		// Find all intersections between privileges and generate dummy nodes.
		int d = 0;
		for (int i = 0; i < nodePrivs.size(); i++) {
			for (int j = i + 1; j < nodePrivs.size(); j++) {
				Set<Privilege> privs1 = nodePrivs.get(i);
				Set<Privilege> privs2 = nodePrivs.get(j);
				Set<Privilege> intersect = SetUtils.getIntersect(privs1, privs2);
				if ((intersect.size() < Math.min(privs1.size(), privs2.size())) && (intersect.size() > 0)
				        && (nodePrivs.contains(intersect) == false)) {
					String dummyName = "Placeholder" + Integer.toString(d);
					ImmutablePair<String, Set<Privilege>> mapping = new ImmutablePair<String, Set<Privilege>>(dummyName,
					        intersect);
					rolePrivMappings.add(mapping);
					nodePrivs.add(intersect);
					d += 1;
				}
			}
		}
		// Sort rolePrivMappings by number of privileges in descending order.
		Collections.sort(rolePrivMappings, new Comparator<ImmutablePair<String, Set<Privilege>>>() {
			
			public int compare(ImmutablePair<String, Set<Privilege>> p1, ImmutablePair<String, Set<Privilege>> p2) {
				return p2.getValue().size() - p1.getValue().size();
			}
		});
		// Place node names in an ArrayList in the same descending order of privileges.
		ArrayList<String> nodeNames = new ArrayList<String>();
		for (ImmutablePair<String, Set<Privilege>> p : rolePrivMappings) {
			nodeNames.add(p.getKey());
		}
		// Sort nodePrivs by number of privileges in descending order.
		Collections.sort(nodePrivs, new Comparator<Set<Privilege>>() {
			
			public int compare(Set<Privilege> p1, Set<Privilege> p2) {
				return p2.size() - p1.size();
			}
		});
		// Init adjacency matrix.
		ArrayList<ArrayList<Integer>> adj_mat = new ArrayList<ArrayList<Integer>>(nodePrivs.size());
		// Init ArrayList with empty ArrayLists for use later in dfs.
		for (int i = 0; i < nodePrivs.size(); i++) {
			adj_mat.add(new ArrayList<Integer>());
		}
		ArrayList<Set<Privilege>> tot = new ArrayList<Set<Privilege>>(nodePrivs.size());
		// Init ArrayList with empty sets for use later in dfs.
		for (int i = 0; i < nodePrivs.size(); i++) {
			tot.add(Collections.<Privilege> emptySet());
		}
		// Use depth first search to build the adjacency matrix.
		this.dfs(adj_mat, nodePrivs, tot, 0);
		// Try to store special json formatted version of the graph.
		try {
			this.formatGraphAsJson(adj_mat, nodePrivs, nodeNames);
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		
		// Create CryptNode objects and store in HashMap.
		HashMap<String, CryptNode> nodeMapping = new HashMap<String, CryptNode>();
		for (int i = 0; i < nodePrivs.size(); i++) {
			String name = nodeNames.get(i);
			CryptNode node = new CryptNode(name);
			nodeMapping.put(name, node);
		}
		// Create CryptEdge objects and assign to proper CryptNode objects.
		for (int i = 0; i < adj_mat.size(); i++) {
			int row = i;
			for (int j = 0; j < adj_mat.get(i).size(); j++) {
				int val = adj_mat.get(i).get(j);
				String parentName = nodeNames.get(row);
				CryptNode parentNode = nodeMapping.get(parentName);
				String childName = nodeNames.get(val);
				CryptNode childNode = nodeMapping.get(childName);
				CryptEdge edge = new CryptEdge(parentNode.getDeriveKey(), childNode.getLabel(), childNode.getDeriveKey(),
				        childNode.getDecryptKey());
				nodeMapping.get(parentName).edges.put(childName, edge);
			}
		}
		System.out.println("\nnodeMapping: " + nodeMapping.toString());
		
	}
	
	private void dfs(ArrayList<ArrayList<Integer>> adj_mat, ArrayList<Set<Privilege>> nodePrivs,
	        ArrayList<Set<Privilege>> tot, int cur) {
		if (cur == nodePrivs.size()) {
			return;
		}
		if (tot.get(cur).size() > 0) {
			this.dfs(adj_mat, nodePrivs, tot, cur + 1);
			return;
		}
		
		for (int i = cur + 1; i < nodePrivs.size(); i++) {
			this.dfs(adj_mat, nodePrivs, tot, i);
			boolean nodePrivIsSubset = SetUtils.isProperSubset(nodePrivs.get(cur), tot.get(i));
			boolean totIsSubset = SetUtils.isProperSubset(tot.get(cur), tot.get(i));
			if (nodePrivIsSubset && (!totIsSubset)) {
				if (!adj_mat.get(cur).contains(i)) {
					adj_mat.get(cur).add(i);
				}
				// union of tot[cur] and tot[i]
				Set<Privilege> newSet = SetUtils.getIntersect(tot.get(cur), tot.get(i));
				tot.set(cur, newSet);
			}
		}
		Set<Privilege> diffSet = SetUtils.getDifference(nodePrivs.get(cur), tot.get(cur));
		nodePrivs.set(cur, diffSet);
		Set<Privilege> unionSet = SetUtils.getUnion(tot.get(cur), nodePrivs.get(cur));
		tot.set(cur, unionSet);
	}
	
	public void formatGraphAsJson(ArrayList<ArrayList<Integer>> adj_mat, ArrayList<Set<Privilege>> nodePrivs,
	        ArrayList<String> nodeNames) throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		ObjectNode info = mapper.createObjectNode();
		ObjectNode nodeEdge = mapper.createObjectNode();
		ArrayNode nodes = mapper.createArrayNode();
		ArrayNode edges = mapper.createArrayNode();
		
		for (int i = 0; i < adj_mat.size(); i++) {
			String nodeName = nodeNames.get(i);
			// Create json node object.
			ObjectNode node = mapper.createObjectNode();
			node.put("id", nodeName);
			node.put("label", nodeName);
			// Create json nodeData to hold node.
			ObjectNode nodeData = mapper.createObjectNode();
			nodeData.put("data", node);
			nodes.add(nodeData);
			for (int j = 0; j < adj_mat.get(i).size(); j++) {
				// Create json edge object.
				ObjectNode edge = mapper.createObjectNode();
				int val = adj_mat.get(i).get(j);
				String idName = String.format("e%s%s", i, val);
				edge.put("id", idName);
				String srcName = nodeNames.get(i);
				edge.put("source", srcName);
				String targetName = nodeNames.get(val);
				edge.put("target", targetName);
				// Create json edgeData to hold edge.
				ObjectNode edgeData = mapper.createObjectNode();
				edgeData.put("data", edge);
				edges.add(edgeData);
			}
		}
		
		nodeEdge.put("nodes", nodes);
		nodeEdge.put("edges", edges);
		info.put("elements", nodeEdge);
		this.formattedGraph = mapper.writeValueAsString(info);
	}
	
	public String getFormattedGraph() {
		return this.formattedGraph;
	}
}
