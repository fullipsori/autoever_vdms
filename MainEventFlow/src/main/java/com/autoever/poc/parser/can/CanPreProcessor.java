package com.autoever.poc.parser.can;


import java.util.List;

import com.autoever.poc.parser.AutoKafkaField;
import com.autoever.poc.parser.PreProcessable;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class CanPreProcessor implements PreProcessable {

	public CanPreProcessor() {
		// TODO Auto-generated constructor stub
	}

	public static void addSchemaField(List<Schema.Field> outputSchemaField) {
		return;
	}

	@Override
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData) {
		try {
			Tuple kafkaMessage = inputTuple.getTuple("kafkaMessage");
			PolicyParser policy = PolicyRepository.getInstance().getMapper(kafkaMessage);
			if(policy == null) return false;
			return policy.IsAvailable(channel, id);
		}catch(Exception e) {
			e.printStackTrace();
			return false;
		}
	}
	
	@Override
	public void initialize(Tuple kafkaMessage) {
		try {
			int rootCount = kafkaMessage.getInt(AutoKafkaField.RootCount.getIndex());
			PolicyParser policyParser = PolicyRepository.getInstance().getMapper(kafkaMessage);
			if(policyParser != null) policyParser.InitParams(rootCount);
		}catch(Exception e) {}
	}

}
