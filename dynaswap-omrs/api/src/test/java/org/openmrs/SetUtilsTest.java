package org.openmrs.module.dynaswap;

import org.junit.Test;
import static org.junit.Assert.*;
import org.openmrs.module.dynaswap.atallah.SetUtils;
import org.openmrs.test.BaseModuleContextSensitiveTest;
import java.util.Set;
import java.util.HashSet;
import java.util.Arrays;

public class SetUtilsTest extends BaseModuleContextSensitiveTest {
	
	// Build String set using ints as string {start, ..., end}
	// Note: end integer is not inclusive
	private Set<String> buildPrivSet(int start, int end) {
		Set<String> set = new HashSet<String>();
		for (int i = start; i < end; i++) {
			set.add(Integer.toString(i));
		}
		return set;
	}
	
	@Test
	public void SetUtils_getIntersect() {
		// {0, 1, 2, 3, 4}
		Set<String> setA = this.buildPrivSet(0, 5);
		// {2, 3, 4, 5, 6}
		Set<String> setB = this.buildPrivSet(2, 7);
		Set<String> setIntersect = SetUtils.getIntersect(setA, setB);
		// {2, 3, 4}
		Set<String> expectedSetIntersect = this.buildPrivSet(2, 5);
		
	}
	
	@Test
	public void SetUtils_getUnion() {
		// {0, 1, 2, 3, 4}
		Set<String> setA = this.buildPrivSet(0, 5);
		// {5, 6, 7, 8, 9}
		Set<String> setB = this.buildPrivSet(5, 10);
		Set<String> setUnion = SetUtils.getUnion(setA, setB);
		// {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
		Set<String> expectedSetUnion = this.buildPrivSet(0, 10);
		
	}
	
	@Test
	public void SetUtils_getDifference() {
		// {0, 1, 2, 3, 4}
		Set<String> setA = this.buildPrivSet(0, 5);
		// {3, 4}
		Set<String> setB = this.buildPrivSet(3, 5);
		Set<String> setDiff = SetUtils.getDifference(setA, setB);
		// {0, 1, 2}
		Set<String> expectedSetDiff = this.buildPrivSet(0, 3);
		assertEquals(expectedSetDiff, setDiff);
	}
	
	@Test
	public void SetUtils_isProperSubset() {
		Set<String> setA = new HashSet<String>(Arrays.asList("1", "3", "5"));
		Set<String> setB = new HashSet<String>(Arrays.asList("1", "5"));
		Set<String> setC = new HashSet<String>(Arrays.asList("1", "3", "5"));
		Set<String> setD = new HashSet<String>(Arrays.asList("1", "4"));
		boolean bIsProperSubOfA = SetUtils.isProperSubset(setB, setA);
		assertTrue(bIsProperSubOfA);
		boolean cIsProperSubOfA = SetUtils.isProperSubset(setC, setA);
		assertFalse(cIsProperSubOfA);
		boolean dIsProperSubOfA = SetUtils.isProperSubset(setD, setA);
		assertFalse(dIsProperSubOfA);
	}
}
