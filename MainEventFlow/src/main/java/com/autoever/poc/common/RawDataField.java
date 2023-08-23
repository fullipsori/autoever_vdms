package com.autoever.poc.common;

import java.util.List;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;

public enum RawDataField {

	DLC(1, 0),
	DeltaTime(4, 1),
	MSGInfo(1, 2),
	DataChannel(1, 3),
	DataID(4, 4),
	DATA(0, 5),
	BaseTime(4, 6);

	public static Schema RawDataSchema = new Schema( "BaseRawData", 
			List.of(
				new Schema.Field("DLC", CompleteDataType.forInt()),
				new Schema.Field("DeltaTime", CompleteDataType.forDouble()),
				new Schema.Field("MSGInfo", CompleteDataType.forInt()),
				new Schema.Field("DataChannel", CompleteDataType.forInt()),
				new Schema.Field("DataID", CompleteDataType.forInt()),
				new Schema.Field("DATA", CompleteDataType.forString()),
				new Schema.Field("BaseTime", CompleteDataType.forLong())
			)
	);
	final private int size;
	final private int index;
	
	private RawDataField(int size, int index) {
		this.size = size;
		this.index = index;
	}
	
	public int getSize() {
		return this.size;
	}
	public int getIndex() {
		return this.index;
	}
	
}
