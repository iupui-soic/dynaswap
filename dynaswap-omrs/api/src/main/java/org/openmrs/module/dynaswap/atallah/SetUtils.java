package org.openmrs.module.dynaswap.atallah;

import java.util.Set;
import org.openmrs.Privilege;
import java.util.HashSet;

public class SetUtils {
	
	public static Set<String> getIntersect(Set<String> setA, Set<String> setB) {
		// retainAll modifies the set so we must use a copy to preserve it
		Set<String> copySetA = new HashSet<String>(setA);
		// Retain elements that intersect.
		copySetA.retainAll(setB);
		return copySetA;
	}
	
	public static Set<String> getUnion(Set<String> setA, Set<String> setB) {
		// addAll modifies the set so we must use a copy to preserve it
		Set<String> copySetA = new HashSet<String>(setA);
		// Return union of sets.
		copySetA.addAll(setB);
		return copySetA;
	}
	
	public static Set<String> getDifference(Set<String> setA, Set<String> setB) {
		// removeAll modifies the set so we must use a copy to preserve it.
		Set<String> copySetA = new HashSet<String>(setA);
		// Return union of sets.
		copySetA.removeAll(setB);
		return copySetA;
	}
	
	// Check if setA is a proper subset of setB.
	public static boolean isProperSubset(Set<String> setA, Set<String> setB) {
		// Proper subsets can't be equal.
		if (setA.equals(setB)) {
			return false;
		}
		// If A is a subset of B, then B has all of A's elements.
		return setB.containsAll(setA);
	}
}
