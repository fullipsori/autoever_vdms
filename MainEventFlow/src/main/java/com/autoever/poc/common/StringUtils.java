package com.autoever.poc.common;

import java.io.UnsupportedEncodingException;

import com.streambase.sb.util.Base64;

public class StringUtils {

	public static String convertbytesToHex(byte[] bytes, int sIndex, int size){
        StringBuilder sb = new StringBuilder();
        int maxSize= (bytes.length-sIndex) < size? (bytes.length-sIndex): size;
        for(int i=0; i< maxSize; i++) {
        	sb.append(String.format("%02x", bytes[i+sIndex]&0xff));
        }
        return sb.toString();
    }
	
	public static String convertStrToHex(String data) {
		if(data == null) return "";
		return convertbytesToHex(data.getBytes(), 0, data.length());
	}
	
	public static String convertStrToHexWithCharset(String data, String charset) {
		if(data == null) return "";
		try {
			return convertbytesToHex(data.getBytes(charset), 0, data.length());
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return "";
		}
	}

	public static byte[] convertHexTobytes(String s) {
	    int len = s.length();
	    byte[] data = new byte[len / 2];
	    for (int i = 0; i < len; i += 2) {
	        data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
	                             + Character.digit(s.charAt(i+1), 16));
	    }
	    return data;
	}

	public static String convertHexToStr(String hexData) {
		if(hexData == null) return "";
		return Base64.encodeBytes(convertHexTobytes(hexData));
	}
	
	public static int indexOf(byte[] bytes, byte[] pattern, int start) {
		if(pattern.length == 0) return start;
		if(start > bytes.length) return -1;
		int last = bytes.length - pattern.length + 1;
		next: for(; start < last; start++) {
			for(int i = 0; i < pattern.length; i++) {
				if(bytes[start+i] != pattern[i]) {
					continue next;
				}
			}
			return start;
		}
		return -1;
	}

	public static byte[] mergeByteArray(byte[] first, byte[] second) {
		byte[] combined = new byte[first.length + second.length];
		System.arraycopy(first, 0, combined, 0, first.length);
		System.arraycopy(second,0,combined, first.length, second.length);
		return combined;
	}

}
