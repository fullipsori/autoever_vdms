package com.autoever.poc.parser;

import com.streambase.sb.Tuple;

public interface PreProcessable {
	public void initialize(Tuple kafkaMessage);
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData);
}
