package org.openmrs.module.dynaswap.atallah;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "cryptedge")
public class CryptEdge {
	
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	@Column(name = "id", updatable = false, nullable = false, unique = true)
	private int id;
	
	@Column(name = "r_ij")
	private String r_ij;
	
	@Column(name = "y_ij")
	public String y_ij;
	
	@Column(name = "parent_id")
	public String parentName;
	
	@Column(name = "child_id")
	public String childName;
	
	/**
	 * Constructor for edge. Given the parent derive key, child label, child derive key and child
	 * decrypt key the edge will calculate the edge seed and the edge label.
	 * 
	 * @param t_i hex string of parent derive key
	 * @param l_j hex string of child label
	 * @param t_j hex string of child derive key
	 * @param k_j hex string of child decrypt key
	 */
	public CryptEdge(String parentName, String childName, String t_i, String l_j, String t_j, String k_j) {
		// Store the parent and child node name for ease of access.
		this.parentName = parentName;
		this.childName = childName;
		this.r_ij = CryptUtil.hashFunc(t_i, l_j);
		this.y_ij = CryptUtil.encrypt(this.r_ij, t_j, k_j);
	}
	
	public void update_r_ij(String t_i, String l_j) {
		this.r_ij = CryptUtil.hashFunc(t_i, l_j);
	}
	
	public void update_y_ij(String t_j, String k_j) {
		this.y_ij = CryptUtil.encrypt(this.r_ij, t_j, k_j);
	}
	
	public String get_r_ij() {
		return this.r_ij;
	}
	
}
