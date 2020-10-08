package org.openmrs.module.dynaswap.atallah;

import org.apache.commons.codec.digest.DigestUtils;
import org.openmrs.util.Security;

public class CryptUtil {
	
	public static String hashFunc(String val1, String val2) {
		String message = new String();
		message = val1 + val2;
		// return Security.encodeString(message, "SHA-256");
		return DigestUtils.sha256Hex(message);
	}
	
	public static String hashFunc(String val1, String val2, String valOpt) {
		String message = new String();
		message = val1 + valOpt + val2;
		// return Security.encodeString(message, "SHA-256");
		return DigestUtils.sha256Hex(message);
	}
	
	public static String encrypt(String r_ij, String t_j, String k_j) {
		byte[] init = Security.getSavedInitVector();
		String message = t_j + k_j;
		byte[] key = hexStringToByteArray(r_ij);
		String ciphertext = Security.encrypt(message, init, key);
		return ciphertext;
	}
	
	public static String decrypt(String ciphertext, String keyHexStr) {
		byte[] init = Security.getSavedInitVector();
		byte[] key = hexStringToByteArray(keyHexStr);
		String plaintext = Security.decrypt(ciphertext, init, key);
		return plaintext;
	}
	
	// String must be an even length to be valid hex string.
	public static byte[] hexStringToByteArray(String str) {
		int len = str.length();
		byte[] data = new byte[len / 2];
		for (int i = 0; i < len; i += 2) {
			data[i / 2] = (byte) ((Character.digit(str.charAt(i), 16) << 4) + Character.digit(str.charAt(i + 1), 16));
		}
		return data;
	}
	
}
