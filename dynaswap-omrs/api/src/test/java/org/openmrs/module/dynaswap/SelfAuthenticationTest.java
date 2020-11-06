package org.openmrs.module.dynaswap;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Random;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptDAG;
import org.openmrs.module.dynaswap.atallah.CryptNode;
import org.openmrs.module.dynaswap.atallah.SelfAuthentication;
import org.openmrs.test.BaseModuleContextSensitiveTest;
import org.openmrs.module.dynaswap.CryptDAGTest;
import org.openmrs.module.dynaswap.atallah.CryptUtil;
import org.openmrs.util.Security;

public class SelfAuthenticationTest extends BaseModuleContextSensitiveTest {
	
	// For now some simple test data values will be copied over and hard coded.
	public ArrayList<ArrayList<String>> getSimpleData() {
		int rows = 30;
		ArrayList<ArrayList<String>> data = new ArrayList<ArrayList<String>>(rows);
		for (int i = 0; i < rows; i++) {
			data.add(new ArrayList<String>(Arrays.asList("no-recurrence-events", "30-39", "premeno", "30-34", "0-2", "no",
			    "3", "left", "left_low", "no")));
		}
		return data;
	}
	
	// For now some simple test data values will be copied over and hard coded.
	public ArrayList<String> getSimpleDataColumns() {
		ArrayList<String> columnNames = new ArrayList<String>(Arrays.asList("Object 1", "Object 2", "Object 3", "Object 4",
		    "Object 5", "Object 6", "Object 7", "Object 8", "Object 9", "Object 1"));
		return columnNames;
	}
	
	public HashMap<String, ArrayList<String>> getSimpleRoleFieldMapping() {
		HashMap<String, ArrayList<String>> roleFieldMapping = new HashMap<String, ArrayList<String>>();
		// For now try simple 1-1 mapping.
		// What about placeholders?
		roleFieldMapping.put("[CRYPT]admin", new ArrayList<String>(Arrays.asList("Object 1")));
		roleFieldMapping.put("[CRYPT]doctor", new ArrayList<String>(Arrays.asList("Object 2")));
		roleFieldMapping.put("[CRYPT]clerk", new ArrayList<String>(Arrays.asList("Object 3")));
		roleFieldMapping.put("[CRYPT]nurse", new ArrayList<String>(Arrays.asList("Object 4")));
		roleFieldMapping.put("Placeholder0", new ArrayList<String>(Arrays.asList("Object 5")));
		roleFieldMapping.put("Placeholder1", new ArrayList<String>(Arrays.asList("Object 6")));
		return roleFieldMapping;
	}
	
	@Test
	public void SelfAuthentication_constructor() {
		System.out.println("Self Auth test");
		CryptDAGTest.setupSimpleModel();
		CryptDAG dag = new CryptDAG();
		dag.createGraph();
		System.out.println(dag.getFormattedGraph());
		HashMap<String, CryptNode> nodeMapping = dag.getNodeMapping();
		SelfAuthentication selfAuth = new SelfAuthentication();
		ArrayList<ArrayList<String>> data = this.getSimpleData();
		System.out.println("Original Data: ");
		this.print2dArrayList(data);
		ArrayList<String> columns = this.getSimpleDataColumns();
		HashMap<String, ArrayList<String>> roleFieldMapping = this.getSimpleRoleFieldMapping();
		ArrayList<ArrayList<String>> encryptedData = SelfAuthentication
		        .encrypt(nodeMapping, roleFieldMapping, data, columns);
		System.out.println("Encrypted data:");
		this.print2dArrayList(encryptedData);
		// Choose random starting node.
		Random rand = new Random();
		int numOfNodes = nodeMapping.keySet().size();
		String[] possibleNodes = new String[numOfNodes];
		possibleNodes = nodeMapping.keySet().toArray(possibleNodes);
		String sourceNode = possibleNodes[rand.nextInt(possibleNodes.length - 1)];
		// What about when there are multiple valid target cols?
		String randTargetCol = columns.get(rand.nextInt(columns.size() - 1));
		String targetCol = SelfAuthentication.getValidTargetCol(roleFieldMapping, sourceNode, randTargetCol, nodeMapping,
		    columns);
		System.out.println("sourceNode: " + sourceNode);
		System.out.println("Target column: " + targetCol);
		System.out.println("sourceNode mapped to field: " + roleFieldMapping.get(sourceNode).contains(targetCol));
		ArrayList<ArrayList<String>> decryptedData = SelfAuthentication.decrypt(nodeMapping, encryptedData, columns,
		    sourceNode, targetCol);
		System.out.println("Decrypted data:");
		this.print2dArrayList(decryptedData);
	}
	
	public void print2dArrayList(ArrayList<ArrayList<String>> arr) {
		String arrStr = "";
		for (int i = 0; i < arr.size(); i++) {
			for (int j = 0; j < arr.get(i).size(); j++) {
				arrStr += arr.get(i).get(j);
				arrStr += " ";
			}
			arrStr += "\n";
		}
		System.out.println(arrStr);
	}
}
