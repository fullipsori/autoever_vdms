package com.autoever.poc.parser;

public enum AutoKafkaField {
	TerminalID("TerminalID", 11, 0), 
	SequenceNo("SequenceNo", 4, 1), 
	BodyLength("BodyLength", 4, 2), 
	CIN("CIN", 8, 3), 
	VIN("VIN", 30, 4), 
	VehicleKeyID("VehicleKeyID", 4, 5), 
	PolicyVersion("PolicyVersion", 2, 6),
	RecordCount("RecordCount", 4, 7),
	RootCount("RootCount", 2, 8),
	SubmitSequenceNo("SubmitSequenceNo", 4, 9),
	SerialNo("SerialNo", 11, 10),
	BaseTime("BaseTime", 4, 11),
	MessageType("MessageType", 1, 12),
	FirstPID("FirstPID", 128, 13),
	MsgSrcKeyID("MsgSrcKeyID", 128, 14),
	SyncSerID("SyncSerID", 20, 15),
	LoadDTM("LoadDTM", 14, 16),
	XctRedisInpDTM("XctRedisInpDTM", 4, 17);

	private final String name;
    private final int size;
    private final int index;

    AutoKafkaField(String name, int size, int index) { 
    	this.name = name;
    	this.size= size; 
    	this.index = index;
    }

    public String getName() { return this.name; }
    public int getSize() { return this.size; }
    public int getIndex() { return this.index; }
}
