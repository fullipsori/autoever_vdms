package com.autoever.poc.parser.can;

import java.util.List;

import com.autoever.poc.parser.PreProcessable;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class CanDBCPreProcessor implements PreProcessable {

	public CanDBCPreProcessor() {
	}

	public static void addSchemaField(List<Schema.Field> outputSchemaField) {
		return;
	}

	@SuppressWarnings("unchecked")
	@Override
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData) {
		try {
			List<Long> dbcIDs = (List<Long>)inputTuple.getList("dbcIDs");
			if(dbcIDs == null || dbcIDs.isEmpty()) return false;
			long maskedID = ((msgInfo & 0x1)==0x1)? (id & 0x00FFFFFF) : (id & 0x7FF);
			return dbcIDs.contains(maskedID);
		}catch(Exception e) {
			e.printStackTrace();
			return false;
		}
	}
	
	@Override
	public void initialize(Tuple kafkaMessage) {
	}

}
