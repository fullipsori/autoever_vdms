package com.autoever.poc.common;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Timestamp;
import com.streambase.sb.client.CustomFunctionResolver;

public class TimeUtils {

	@CustomFunctionResolver("GetTimestampCustomFunctionResolver0")
	public static Timestamp GetTimestamp(long timeMillis){
		return new Timestamp(new Date(timeMillis));
	}

	public static CompleteDataType GetTimestampCustomFunctionResolver0(CompleteDataType timeMillis) {
		return CompleteDataType.forTimestamp();
	}


	public static String GetLocalTimeString(long timeMillis, String format){
	    // TODO Implement function here
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(timeMillis), ZoneId.of("Asia/Seoul"));
		if(format == null || format.isEmpty())
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		return realTime.format(DateTimeFormatter.ofPattern(format));
	}

	public static String GetCurrUTCTimeString(String format){
	    // TODO Implement function here
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.now(), ZoneId.of("UTC"));
		if(format == null || format.isEmpty()) {
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		} else {
			return realTime.format(DateTimeFormatter.ofPattern(format));
		}
	}

	public static String getUTCTimeString(long timeMillis, String format) {
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(timeMillis), ZoneId.of("UTC"));
		if(format == null || format.isEmpty()) {
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		} else {
			return realTime.format(DateTimeFormatter.ofPattern(format));
		}
	}

	
	public static void main(String[] args) {
		System.out.println("time:" + GetCurrUTCTimeString("yyyyMMDD'T'HHmmss'Z'"));
	}
}
