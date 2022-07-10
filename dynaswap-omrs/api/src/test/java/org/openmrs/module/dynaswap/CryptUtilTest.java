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
	public void general_encrypt_decrypt() {
		String str = "Hello World!";
		String keyHexStr = DigestUtils.md5Hex("myKey");
		String ciphertext = CryptUtil.encrypt(keyHexStr, str);
		String plaintext = CryptUtil.decrypt(keyHexStr, ciphertext);
		final String expectedPlaintext = str;
		assertEquals(expectedPlaintext, plaintext);
	}
	
	@Test
	public void encrypt_decrypt() {
		String str1 = "hello";
		String str2 = "world";
		String keyHexStr = DigestUtils.md5Hex("myKey");
		String ciphertext = CryptUtil.encrypt(keyHexStr, str1, str2);
		String plaintext = CryptUtil.decrypt(keyHexStr, ciphertext);
		final String expectedPlaintext = str1 + str2;
		assertEquals(expectedPlaintext, plaintext);
	}
	
	@Test
	public void hexStrToByteArrayAndBack() {
		String hexStr1 = "21fc9a4ee52169b0613f591bfd2cb8b6";
		byte[] bArr1 = CryptUtil.hexStringToByteArray(hexStr1);
		String newHexStr1 = CryptUtil.bytesToHex(bArr1);
		assertEquals(hexStr1, newHexStr1);
	}
}
