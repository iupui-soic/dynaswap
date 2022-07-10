package org.openmrs.module.dynaswap;

import java.util.List;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptDAG;
import org.openmrs.test.BaseModuleContextSensitiveTest;
import org.openmrs.Role;
import org.openmrs.Privilege;
import org.openmrs.api.context.Context;
import org.openmrs.api.UserService;
import static org.junit.Assert.*;

public class CryptDAGTest extends BaseModuleContextSensitiveTest {
	
	public static void setupSimpleModel() {
		UserService us = Context.getUserService();
		// Add a simple model generation test case consisting of
		// the following role-priv object mappings described in a JSON-like
		// format below. For now, values will be hard coded.
		// In the future it may be useful to create a method to parse JSON into a mapping.
		// {"admin": [0, 1, 2], "nurse": [1, 2], "clerk": [2, 3, 4], "doctor": [1, 2, 4]}
		List<Privilege> privs = new ArrayList<Privilege>();
		for (int i = 0; i < 5; i++) {
			Privilege priv = new Privilege(Integer.toString(i));
			privs.add(priv);
			us.savePrivilege(priv);
		}
		
		Role admin = new Role("[CRYPT]admin");
		admin.addPrivilege(privs.get(0));
		admin.addPrivilege(privs.get(1));
		admin.addPrivilege(privs.get(2));
		us.saveRole(admin);
		
		Role nurse = new Role("[CRYPT]nurse");
		nurse.addPrivilege(privs.get(1));
		nurse.addPrivilege(privs.get(2));
		us.saveRole(nurse);
		
		Role clerk = new Role("[CRYPT]clerk");
		clerk.addPrivilege(privs.get(2));
		clerk.addPrivilege(privs.get(3));
		clerk.addPrivilege(privs.get(4));
		us.saveRole(clerk);
		
		Role doctor = new Role("[CRYPT]doctor");
		doctor.addPrivilege(privs.get(1));
		doctor.addPrivilege(privs.get(2));
		doctor.addPrivilege(privs.get(4));
		us.saveRole(doctor);
		
	}
	
	@Test
	public void CryptDAG_model_gen_simple_mapping() {
		CryptDAGTest.setupSimpleModel();
		CryptDAG dag = new CryptDAG();
		dag.createGraph();
		System.out.println(dag.getFormattedGraph());
	}
	
	@Test
	public void CryptDAG_getRoleDataMapFromTxtFile() {
		CryptDAGTest.setupSimpleModel();
		CryptDAG dag = new CryptDAG();
		try {
			HashMap<String, HashMap<String, ArrayList<String>>> mapping = dag.getRoleDataMapFromTxtFile();
			System.out.println("Printing test mapping values:");
			for (HashMap.Entry<String, HashMap<String, ArrayList<String>>> entry : mapping.entrySet()) {
				System.out.println("role:");
				System.out.println(entry.getKey());
				for (HashMap.Entry<String, ArrayList<String>> subEntry : entry.getValue().entrySet()) {
					System.out.println("table:");
					System.out.println(subEntry.getKey());
					System.out.println("fields:");
					for (String field : subEntry.getValue()) {
						System.out.println(field);
					}
				}
			}
		}
		catch (FileNotFoundException e) {
			e.printStackTrace();
		}
		catch (IOException e) {
			e.printStackTrace();
		}
		catch (URISyntaxException e) {
			e.printStackTrace();
		}
	}
	
	@Test
	public void CryptDAG_setupRolePrivMapFromRoleDataMap() {
		// Need to add assert.
		System.out.println("Testing role-priv setup from role-data mapping...");
		CryptDAG dag = new CryptDAG();
		try {
			HashMap<String, HashMap<String, ArrayList<String>>> roleDataMap = dag.getRoleDataMapFromTxtFile();
			dag.setupRolePrivMapFromRoleDataMap(roleDataMap);
			List<Role> roles = Context.getUserService().getAllRoles();
			for (Role role : roles) {
				System.out.println("Role:" + role.getRole());
				System.out.println("Privs:");
				for (Privilege priv : role.getPrivileges()) {
					System.out.println(priv.getPrivilege());
				}
			}
			System.out.println("ALL PRIVS");
			for (Privilege priv : Context.getUserService().getAllPrivileges()) {
				System.out.println(priv.getPrivilege());
			}
		}
		catch (Exception e) {
			System.out.println(e.getStackTrace());
		}
	}
}
