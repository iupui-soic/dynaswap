package org.openmrs.module.dynaswap;

import org.junit.Test;
import org.openmrs.module.dynaswap.atallah.CryptUtil;
import org.openmrs.util.Security;
import static org.junit.Assert.*;

import org.apache.commons.codec.digest.DigestUtils;

/**
 * This is a unit test, which verifies logic in DynaSWAPBaseModuleService. It doesn't extend
 * BaseModuleContextSensitiveTest, thus it is run without the in-memory DB and Spring context.
 */
public class CryptUtilTest {
	
	@Test
	public void hashFunc_shouldConcateOption() {
		String val1 = Security.getRandomToken();
		String val2 = Security.getRandomToken();
		String valOpt = "0";
		String hash1 = CryptUtil.hashFunc(val1, val2);
		String hash2 = CryptUtil.hashFunc(val1, val2, valOpt);
		boolean hashEqual = hash1.equals(hash2);
		assertFalse(hashEqual);
	}
	
	@Test
	public void encrypt_decrypt() {
		String str1 = "hello";
		String str2 = "world";
		String keyHexStr = DigestUtils.sha256Hex("myKey");
		String ciphertext = CryptUtil.encrypt(keyHexStr, str1, str2);
		String plaintext = CryptUtil.decrypt(ciphertext, keyHexStr);
		final String expectedPlaintext = str1 + str2;
		assertEquals(expectedPlaintext, plaintext);
	}
}
