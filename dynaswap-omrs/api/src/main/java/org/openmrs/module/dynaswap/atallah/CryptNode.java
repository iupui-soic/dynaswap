package org.openmrs.module.dynaswap.atallah;

import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

import javax.persistence.CascadeType;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.JoinColumn;
import javax.persistence.JoinTable;
import javax.persistence.OneToMany;
import javax.persistence.Table;

import org.apache.commons.codec.digest.DigestUtils;
import org.openmrs.util.Security;

@Entity
@Table(name = "cryptnode")
public class CryptNode {
	
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(name = "id", updatable = false, nullable = false, unique = true)
	private int id;
	
	@Column(name = "name")
	public String name;
	
	@Column(name = "label")
	public String label;
	
	@Column(name = "secret")
	private String secret;
	
	@OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
	@JoinTable(name = "cryptnode_cryptedge", joinColumns = { @JoinColumn(name = "cryptnode_id") }, inverseJoinColumns = { @JoinColumn(name = "cryptedge_id") })
	public List<CryptEdge> edges;
	
	/**
	 * constructor
	 */
	public CryptNode(String name) {
		this.name = name;
		this.label = this.getRandHexStr();
		this.updateSecret();
		this.edges = new ArrayList<CryptEdge>();
	}
	
	private String getRandHexStr() {
		// returns a 64 char random hex string
		return DigestUtils.sha256Hex(Security.getRandomToken());
	}
	
	public void updateSecret() {
		this.secret = this.getRandHexStr();
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
	
	public int getId() {
		return this.id;
	}
	
	public String getName() {
		return this.name;
	}
}
