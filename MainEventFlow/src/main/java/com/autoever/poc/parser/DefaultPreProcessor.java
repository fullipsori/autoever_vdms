package com.autoever.poc.parser;

import java.util.List;

import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class DefaultPreProcessor implements PreProcessable {

	public DefaultPreProcessor() {
		// TODO Auto-generated constructor stub
	} 

	public static void addSchemaField(List<Schema.Field> outputSchemaField) {
		return;
	}

	@Override
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData) {
		// TODO Auto-generated method stub
		return true;
	}

	@Override
	public void initialize(Tuple kafkaMessage) {
	}

}
