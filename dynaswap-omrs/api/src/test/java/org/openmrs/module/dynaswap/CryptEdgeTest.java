package org.openmrs.module.dynaswap;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptEdge;
import org.openmrs.module.dynaswap.atallah.CryptNode;
import org.openmrs.module.dynaswap.atallah.CryptUtil;

import static org.junit.Assert.*;

public class CryptEdgeTest {
	
	@Test
	public void CryptEdge_constructor() {
		CryptNode n1 = new CryptNode("n1");
		CryptNode n2 = new CryptNode("n2");
		String parentDeriveKey = n1.getDeriveKey();
		String childLabel = n2.getLabel();
		String childDeriveKey = n2.getDeriveKey();
		String childDecryptKey = n2.getDecryptKey();
		CryptEdge edge = new CryptEdge(n1.getName(), n2.getName(), parentDeriveKey, childLabel, childDeriveKey,
		        childDecryptKey);
		String edge_r = edge.get_r_ij();
		String expectedEdge_r = CryptUtil.hashFunc(parentDeriveKey, childLabel);
		assertEquals(edge_r, expectedEdge_r);
		String edge_y = edge.y_ij;
		String expectedEdge_y = CryptUtil.encrypt(edge_r, childDeriveKey, childDecryptKey);
		assertEquals(edge_y, expectedEdge_y);
	}
}
