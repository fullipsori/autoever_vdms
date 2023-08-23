package com.autoever.poc.common;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

/* java is default BIG_ENDIAN */
public class NumUtils {

	private static final int INT_SIZE = 4;
	private static final int LONG_SIZE = 8;

	public static int getIntFromBig(byte[] data, int sIndex, int size) {
		ByteBuffer byteBuffer = ByteBuffer.allocate(INT_SIZE).order(ByteOrder.BIG_ENDIAN);
		byteBuffer.clear();
		int start = INT_SIZE - size;
		for(int i=0;i<size; i++) {
			byteBuffer.put(start+i, data[sIndex+i]);
		}
		return byteBuffer.rewind().getInt();
	}
	
	public static int getIntFromLittle(byte[] data, int sIndex, int size) {

		ByteBuffer byteBuffer = ByteBuffer.allocate(INT_SIZE).order(ByteOrder.LITTLE_ENDIAN);
		byteBuffer.clear();
		for(int i=0;i<size; i++) {
			byteBuffer.put(i, data[sIndex+i]);
		}
		return byteBuffer.rewind().getInt();
	}

	public static long getLongFromBig(byte[] data, int sIndex, int size) {
		ByteBuffer byteBuffer = ByteBuffer.allocate(LONG_SIZE).order(ByteOrder.BIG_ENDIAN);
		byteBuffer.clear();
		int start = LONG_SIZE - size;
		for(int i=0;i<size; i++) {
			byteBuffer.put(start+i, data[sIndex+i]);
		}
		return byteBuffer.rewind().getLong();
	}
	
	public static long getLongFromLittle(byte[] data, int sIndex, int size) {
		ByteBuffer byteBuffer = ByteBuffer.allocate(LONG_SIZE).order(ByteOrder.LITTLE_ENDIAN);
		for(int i=0;i<size; i++) {
			byteBuffer.put(i, data[sIndex+i]);
		}
		return byteBuffer.rewind().getLong();
	}

	public static byte[] getBigByteArrayFromInt(int data, int size) {
		byte[] byteBuffer = ByteBuffer.allocate(INT_SIZE).order(ByteOrder.BIG_ENDIAN).putInt(data).array();
		if(INT_SIZE == size)
			return byteBuffer;
		else
			return Arrays.copyOfRange(byteBuffer, INT_SIZE-size, byteBuffer.length);
	}
	
	public static byte[] getLittleByteArrayFromInt(int data, int size) {
		byte[] byteBuffer = ByteBuffer.allocate(INT_SIZE).order(ByteOrder.LITTLE_ENDIAN).putInt(data).array();
		if(INT_SIZE == size)
			return byteBuffer;
		else
			return Arrays.copyOfRange(byteBuffer, 0, size);
	}

	public static byte[] getBigByteArrayFromLong(long data, int size) {
		byte[] byteBuffer = ByteBuffer.allocate(LONG_SIZE).order(ByteOrder.BIG_ENDIAN).putLong(data).array();
		if(LONG_SIZE == size)
			return byteBuffer;
		else
			return Arrays.copyOfRange(byteBuffer, LONG_SIZE-size, byteBuffer.length);
	}
	
	public static byte[] getLittleByteArrayFromLong(long data, int size) {
		byte[] byteBuffer = ByteBuffer.allocate(LONG_SIZE).order(ByteOrder.BIG_ENDIAN).putLong(data).array();
		if(LONG_SIZE == size)
			return byteBuffer;
		else
			return Arrays.copyOfRange(byteBuffer, 0, size);
	}
	
	public static int getIntFromHexString(String hexString) {
		return Integer.parseInt(hexString, 16);
	}
	
	public static long convertlongFromUnsignedInt(int n) {
		return n & 0xFFFFFFFFL;
	}

	public static double getDoubleFromStr(String value, double defaultValue) {
		try {
			return Double.valueOf(value);
		}catch(Exception e) {
			return defaultValue;
		}
	}

	public static long getLongFromStr(String value, long defaultValue) {
		try {
			return Long.valueOf(value);
		}catch(Exception e) {
			return defaultValue;
		}
	}
}
