package org.openmrs.module.dynaswap;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptDAG;
import org.openmrs.test.BaseModuleContextSensitiveTest;
import static org.junit.Assert.*;

public class CryptDAGTest extends BaseModuleContextSensitiveTest {
	
	@Test
	public void CryptDAG_constructor() {
		CryptDAG dag = new CryptDAG();
		String dagFormatted = dag.getFormattedGraph();
		// The empty test database will by default only contain nodes for Anonymous, Authenticated, Provider, and System Developer
		String expectedDagFormatted = "{\"elements\":{\"nodes\":[{\"data\":{\"id\":\"Anonymous\",\"label\":\"Anonymous\"}},{\"data\":{\"id\":\"Authenticated\",\"label\":\"Authenticated\"}},{\"data\":{\"id\":\"Provider\",\"label\":\"Provider\"}},{\"data\":{\"id\":\"System Developer\",\"label\":\"System Developer\"}}],\"edges\":[]}}";
		assertEquals(dagFormatted, expectedDagFormatted);
	}
}
