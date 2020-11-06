package org.openmrs.module.dynaswap.atallah;

import org.apache.commons.codec.digest.DigestUtils;
import org.openmrs.util.Security;
import org.openmrs.util.OpenmrsConstants;
import org.openmrs.api.APIException;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

public class CryptUtil {
	
	public static String hashFunc(String val1, String val2) {
		String message = new String();
		message = val1 + val2;
		return DigestUtils.md5Hex(message);
	}
	
	public static String hashFunc(String val1, String val2, String valOpt) {
		String message = new String();
		message = val1 + valOpt + val2;
		return DigestUtils.md5Hex(message);
	}
	
	public static String encrypt(String r_ij, String t_j, String k_j) {
		String message = t_j + k_j;
		String ciphertext = CryptUtil.encrypt(r_ij, message);
		return ciphertext;
	}
	
	// More general form of encryption, rather than specific atallah formatted encryption
	public static String encrypt(String keyStr, String message) {
		byte[] init = Security.getSavedInitVector();
		byte[] key = hexStringToByteArray(keyStr);
		String ciphertext = CryptUtil.encryptHelper(message, init, key);
		return ciphertext;
	}
	
	// Encryption without using base64 encoding like in the OpenMRS Security class.
	public static String encryptHelper(String message, byte[] initVector, byte[] secretKey) {
		IvParameterSpec initVectorSpec = new IvParameterSpec(initVector);
		SecretKeySpec secret = new SecretKeySpec(secretKey, OpenmrsConstants.ENCRYPTION_KEY_SPEC);
		byte[] encrypted;
		String result;
		
		try {
			Cipher cipher = Cipher.getInstance(OpenmrsConstants.ENCRYPTION_CIPHER_CONFIGURATION);
			cipher.init(Cipher.ENCRYPT_MODE, secret, initVectorSpec);
			encrypted = cipher.doFinal(message.getBytes(StandardCharsets.UTF_8));
			// results in hex str
			result = CryptUtil.bytesToHex(encrypted);
		}
		catch (GeneralSecurityException e) {
			throw new APIException("could.not.encrypt.text", e);
		}
		
		return result;
	}
	
	public static String decryptHelper(String message, byte[] initVector, byte[] secretKey) {
		IvParameterSpec initVectorSpec = new IvParameterSpec(initVector);
		SecretKeySpec secret = new SecretKeySpec(secretKey, OpenmrsConstants.ENCRYPTION_KEY_SPEC);
		String decrypted = "";
		
		try {
			Cipher cipher = Cipher.getInstance(OpenmrsConstants.ENCRYPTION_CIPHER_CONFIGURATION);
			cipher.init(Cipher.DECRYPT_MODE, secret, initVectorSpec);
			byte[] bMessage = CryptUtil.hexStringToByteArray(message);
			byte[] original = cipher.doFinal(bMessage);
			decrypted = new String(original, StandardCharsets.UTF_8);
		}
		catch (GeneralSecurityException e) {
			// throw new APIException("could.not.decrypt.text", e);
			System.out.println(e.getStackTrace());
		}
		
		return decrypted;
	}
	
	public static String decrypt(String keyHexStr, String ciphertext) {
		byte[] init = Security.getSavedInitVector();
		byte[] key = hexStringToByteArray(keyHexStr);
		String plaintext = CryptUtil.decryptHelper(ciphertext, init, key);
		return plaintext;
	}
	
	// String must be an even length to be valid hex string.
	public static byte[] hexStringToByteArray(String hex) {
		int byteNum = hex.length() / 2;
		byte[] key = new byte[byteNum];
		// Using i as the distance from the END of the string.
		for (int i = 0; i < hex.length() && (i / 2) < byteNum; i++) {
			// Pull out the hex value of the character.
			int nibble = Character.digit(hex.charAt(hex.length() - 1 - i), 16);
			if ((i & 1) != 0) {
				// When i is odd we shift left 4.
				nibble = nibble << 4;
			}
			// Use OR to avoid sign issues.
			key[byteNum - 1 - (i / 2)] |= (byte) nibble;
		}
		return key;
	}
	
	public static String bytesToHex(byte[] bArr) {
		String result = "";
		for (byte b : bArr) {
			result += String.format("%02x", b);
		}
		return result;
	}
	
	public static String strToHexStr(String str) {
		return String.format("%x", new BigInteger(1, str.getBytes(StandardCharsets.UTF_8)));
	}
}
