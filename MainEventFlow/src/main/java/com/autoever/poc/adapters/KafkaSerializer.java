//
// Copyright 2004-2022 TIBCO Software Inc. All rights reserved.
//

package com.autoever.poc.adapters;

import java.io.ByteArrayOutputStream;
import java.util.Map;

import org.slf4j.Logger;

import com.autoever.poc.common.NumUtils;
import com.autoever.poc.parser.AutoKafkaField;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class KafkaSerializer implements org.apache.kafka.common.serialization.Serializer<Tuple> {

    private static final String CONFIG_SCHEMA = "schema";
    private static final String CONFIG_LOGGER = "logger";
    
    private Schema schema;
    private Logger logger;
    
    private Schema.Field TerminalID;
    private Schema.Field SequenceNo;
    private Schema.Field BodyLength;
    private Schema.Field CIN;
    private Schema.Field VIN;
    private Schema.Field VehicleKeyID;
    private Schema.Field PolicyVersion;
    private Schema.Field RecordCount;
    private Schema.Field RootCount;
    private Schema.Field SubmitSequenceNo;
    private Schema.Field SerialNo;
    private Schema.Field BaseTime;
    private Schema.Field MessageType;

    private Schema.Field FirstPID;
    private Schema.Field MsgSrcKeyId;
    private Schema.Field SyncSerID;
    private Schema.Field LoadDTM;
    private Schema.Field XctRedisInpDTM;

    @Override
    public void close() {
    }

    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        if (configs.containsKey(CONFIG_SCHEMA)) {
            schema = (Schema)configs.get(CONFIG_SCHEMA);
			try {
				TerminalID = schema.getField(AutoKafkaField.TerminalID.getName());
				SequenceNo = schema.getField(AutoKafkaField.SequenceNo.getName());
				BodyLength = schema.getField(AutoKafkaField.BodyLength.getName());
				CIN = schema.getField(AutoKafkaField.CIN.getName());
				VIN = schema.getField(AutoKafkaField.VIN.getName());
				VehicleKeyID = schema.getField(AutoKafkaField.VehicleKeyID.getName());
				PolicyVersion = schema.getField(AutoKafkaField.PolicyVersion.getName());
				RecordCount = schema.getField(AutoKafkaField.RecordCount.getName());
				RootCount = schema.getField(AutoKafkaField.RootCount.getName());
				SubmitSequenceNo = schema.getField(AutoKafkaField.SubmitSequenceNo.getName());
				SerialNo = schema.getField(AutoKafkaField.SerialNo.getName());
				BaseTime = schema.getField(AutoKafkaField.BaseTime.getName());
				MessageType = schema.getField(AutoKafkaField.MessageType.getName());

				FirstPID = schema.getField(AutoKafkaField.FirstPID.getName());
				MsgSrcKeyId = schema.getField(AutoKafkaField.MsgSrcKeyID.getName());
				SyncSerID = schema.getField(AutoKafkaField.SyncSerID.getName());
				LoadDTM = schema.getField(AutoKafkaField.LoadDTM.getName());
				XctRedisInpDTM = schema.getField(AutoKafkaField.XctRedisInpDTM.getName());

			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
        }
        if (configs.containsKey(CONFIG_LOGGER)) {
            logger = (Logger) configs.get(CONFIG_LOGGER);
        }
    }

    @Override
    public byte[] serialize(String topic, Tuple tuple) {
        if (schema == null || schema.getFieldCount() <= 0) {
            logger.warn("No schema");
            return null;
        }
        if (logger != null && logger.isDebugEnabled()) {
            logger.debug("Converting tuple: " + tuple.toString());
        }
        
        int size = 0;
        try (ByteArrayOutputStream oStream = new ByteArrayOutputStream()) {
        	size = AutoKafkaField.TerminalID.getSize();
        	oStream.write(tuple.getString(TerminalID).getBytes(), 0, size);
        	size = AutoKafkaField.SequenceNo.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(SequenceNo), size), 0, size);
        	size = AutoKafkaField.BodyLength.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(BodyLength), size), 0, size);
        	size = AutoKafkaField.CIN.getSize();
        	oStream.write(tuple.getString(CIN).getBytes(), 0, size);
        	size = AutoKafkaField.VIN.getSize();
        	oStream.write(tuple.getString(VIN).getBytes(), 0, size);
        	size = AutoKafkaField.VehicleKeyID.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(VehicleKeyID), size), 0, size);
        	size = AutoKafkaField.PolicyVersion.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromInt(tuple.getInt(PolicyVersion), size), 0, size);
        	size = AutoKafkaField.RecordCount.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(RecordCount), size), 0, size);
        	size = AutoKafkaField.RootCount.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromInt(tuple.getInt(RootCount), size), 0, size);
        	size = AutoKafkaField.SubmitSequenceNo.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(SubmitSequenceNo), size), 0, size);
        	size = AutoKafkaField.SerialNo.getSize();
        	oStream.write(tuple.getString(SerialNo).getBytes(), 0, size);
        	size = AutoKafkaField.BaseTime.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(BaseTime), size), 0, size);
        	size = AutoKafkaField.MessageType.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromInt(tuple.getInt(MessageType), size), 0, size);
        	
			/** Variable sized Message */
			size = AutoKafkaField.FirstPID.getSize();
        	oStream.write(tuple.getString(FirstPID).getBytes(), 0, size);
        	size = AutoKafkaField.MsgSrcKeyID.getSize();
        	oStream.write(tuple.getString(MsgSrcKeyId).getBytes(), 0, size);
        	size = AutoKafkaField.SyncSerID.getSize();
        	oStream.write(tuple.getString(SyncSerID).getBytes(), 0, size);
        	size = AutoKafkaField.LoadDTM.getSize();
        	oStream.write(tuple.getString(LoadDTM).getBytes(), 0, size);
        	size = AutoKafkaField.XctRedisInpDTM.getSize();
        	oStream.write(NumUtils.getLittleByteArrayFromLong(tuple.getLong(XctRedisInpDTM), size), 0, size);
        	
        	return oStream.toByteArray();
        	
        } catch (Exception e) {
            logger.error("Error serializing topic '" + topic + "': " + e.getMessage(), e);
            return null;
        }
    }

}
