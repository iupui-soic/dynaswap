package org.openmrs;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptNode;
import static org.junit.Assert.*;

public class CryptNodeTest {
	
	@Test
	public void CryptNode_constructor() {
		CryptNode node = new CryptNode("n1");
		System.out.println(node.name);
		assertEquals(node.name, "n1");
	}
}
