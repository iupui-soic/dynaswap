package org.openmrs.module.dynaswap.atallah;

import java.util.HashMap;
import org.openmrs.util.Security;

public class CryptNode {
	
	public String name;
	
	// maybe use uuid for label when actually using in database
	public String label;
	
	private String secret;
	
	public HashMap<String, CryptEdge> edges;
	
	/**
	 * constructor
	 */
	public CryptNode(String name) {
		this.name = name;
		this.label = Security.getRandomToken();
		this.updateSecret();
		this.edges = new HashMap<String, CryptEdge>();
	}
	
	public void updateSecret() {
		this.secret = Security.getRandomToken();
	}
	
	public String getSecret() {
		return this.secret;
	}
	
	public String getLabel() {
		return this.label;
	}
	
	public String getDeriveKey() {
		return CryptUtil.hashFunc(this.secret, this.label, "0");
	}
	
	public String getDecryptKey() {
		return CryptUtil.hashFunc(this.secret, this.label, "1");
	}
}
