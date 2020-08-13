package org.openmrs.module.dynaswap.atallah;

import java.util.Set;
import org.openmrs.Privilege;
import java.util.HashSet;

public class SetUtils {
	
	public static Set<Privilege> getIntersect(Set<Privilege> setA, Set<Privilege> setB) {
		// retainAll modifies the set so we must use a copy to preserve it.
		Set<Privilege> copySetA = new HashSet<Privilege>(setA);
		// Retain elements that intersect.
		copySetA.retainAll(setB);
		return copySetA;
	}
	
	public static Set<Privilege> getUnion(Set<Privilege> setA, Set<Privilege> setB) {
		// addAll modifies the set so we must use a copy to preserve it
		Set<Privilege> copySetA = new HashSet<Privilege>(setA);
		// Return union of sets.
		copySetA.addAll(setB);
		return copySetA;
	}
	
	public static Set<Privilege> getDifference(Set<Privilege> setA, Set<Privilege> setB) {
		// removeAll modifies the set so we must use a copy to preserve it.
		Set<Privilege> copySetA = new HashSet<Privilege>(setA);
		// Return union of sets.
		copySetA.removeAll(setB);
		return copySetA;
	}
	
	// Check if setA is a proper subset of setB.
	public static boolean isProperSubset(Set<Privilege> setA, Set<Privilege> setB) {
		// Proper subsets can't be equal.
		if (setA.equals(setB)) {
			return false;
		}
		return setA.containsAll(setB);
	}
}
