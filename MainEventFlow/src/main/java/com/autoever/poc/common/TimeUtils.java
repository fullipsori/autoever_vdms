package com.autoever.poc.common;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

public class TimeUtils {

	public static String GetLocalTime(long timeSeconds, String format){
	    // TODO Implement function here
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.ofEpochSecond(timeSeconds), ZoneId.of("Asia/Seoul"));
		if(format == null || format.isEmpty())
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		return realTime.format(DateTimeFormatter.ofPattern(format));
	}

	public static String GetCurrUTCTime(String format){
	    // TODO Implement function here
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.now(), ZoneId.of("UTC"));
		if(format == null || format.isEmpty()) {
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		} else {
			return realTime.format(DateTimeFormatter.ofPattern(format));
		}
	}

	public static String getUTCTime(long timeSeconds, String format) {
		LocalDateTime realTime = LocalDateTime.ofInstant(Instant.ofEpochSecond(timeSeconds), ZoneId.of("UTC"));
		if(format == null || format.isEmpty()) {
			return realTime.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
		} else {
			return realTime.format(DateTimeFormatter.ofPattern(format));
		}
	}

	
	public static void main(String[] args) {
		System.out.println("time:" + GetCurrUTCTime("yyyyMMDD'T'HHmmss'Z'"));
	}
}
