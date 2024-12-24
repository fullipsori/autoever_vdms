package com.autoever.poc.parser.gps;

import java.util.List;

import com.autoever.poc.common.NumUtils;
import com.autoever.poc.parser.AutoGPSField;
import com.autoever.poc.parser.PreProcessable;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class GPSPreProcessor implements PreProcessable {

	public static final Schema RawParsed = new Schema("RawParsed", 
		List.of(
			new Schema.Field("Latitude", CompleteDataType.forDouble()),
			new Schema.Field("Longitude", CompleteDataType.forDouble()),
			new Schema.Field("Heading", CompleteDataType.forInt()),
			new Schema.Field("Velocity", CompleteDataType.forDouble()),
			new Schema.Field("Altitude", CompleteDataType.forDouble()),
			new Schema.Field("NS", CompleteDataType.forString()),
			new Schema.Field("EW", CompleteDataType.forString())
		));

	public static void addSchemaField(List<Schema.Field> outputSchemaField) {
		outputSchemaField.add(new Schema.Field("RawParsed", CompleteDataType.forTuple(RawParsed)));
		return;
	}

	@Override
	public void initialize(Tuple kafkaMessage) {
		// TODO Auto-generated method stub
		
	}

	public static double getGPSX(int longitude) {
		return (longitude & 0xfffffffe) * 0.0000001;
	}
	
	public static double getGPSY(int latitude) {
		return (latitude & 0xfffffffe) * 0.0000001;
	}
	
	public static boolean getNS(int latitude) {
		return (latitude & 0x01000000) == 0x01000000;
	}
	
	public static boolean getEW(int longitude) {
		return (longitude & 0x01000000) == 0x01000000;
	}
	
	@Override
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData) {
		// TODO Auto-generated method stub
		if(rawData == null || rawData.length == 0) return false;

		try {
			Tuple rawParsed = RawParsed.createTuple();

			int curIndex = 0;
			int size = AutoGPSField.Latitude.getsize();
			int latitude = NumUtils.getIntFromBig(rawData,curIndex,size);
			double dLatitude = getGPSY(latitude);
			if(dLatitude<-90 || dLatitude>90) return false; 
			rawParsed.setDouble("Latitude", dLatitude);
			curIndex += size;
			size = AutoGPSField.Longitude.getsize();
			int longitude = NumUtils.getIntFromBig(rawData,curIndex,size);
			double dLongitude = getGPSX(longitude);
			if(dLongitude<-180||dLongitude>180) return false;
			rawParsed.setDouble("Longitude", dLongitude);
			curIndex += size;
			size = AutoGPSField.Heading.getsize();
			rawParsed.setInt("Heading", NumUtils.getIntFromBig(rawData,curIndex,size));
			curIndex += size;
			size = AutoGPSField.Velocity.getsize();
			rawParsed.setDouble("Velocity", (double)NumUtils.getIntFromBig(rawData,curIndex,size));
			curIndex += size;
			size = AutoGPSField.Altitude.getsize();
			rawParsed.setDouble("Altitude", (double)NumUtils.getIntFromBig(rawData, curIndex, size));
			curIndex += size;
			rawParsed.setString("NS", getNS(latitude)? "S" : "N");					
			rawParsed.setString("EW", getEW(longitude)? "E" : "W");
			
			dataTuple.setTuple("RawParsed", rawParsed);
			return true;
		}catch(Exception e) {
			e.printStackTrace();
			return false;
		}
	}

}
