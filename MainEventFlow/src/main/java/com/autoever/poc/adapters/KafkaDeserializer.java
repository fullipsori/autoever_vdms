//
// Copyright 2004-2022 TIBCO Software Inc. All rights reserved.
//

package com.autoever.poc.adapters;

import java.util.Arrays;
import java.util.Map;

import org.slf4j.Logger;

import com.autoever.poc.common.NumUtils;
import com.autoever.poc.parser.AutoKafkaField;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.util.Base64;

public class KafkaDeserializer implements org.apache.kafka.common.serialization.Deserializer<Tuple> {

    private static final String CONFIG_SCHEMA = "schema";
    private static final String CONFIG_LOGGER = "logger";
    
    private Schema schema;
    private Logger logger;
    
    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        schema = (Schema) configs.get(CONFIG_SCHEMA);
        logger = (Logger) configs.get(CONFIG_LOGGER);
    }

    @Override
    public Tuple deserialize(String topic, byte[] data) {
        Tuple tuple = schema.createTuple();
        int curIndex = 0;
        int size;

        if(data == null) {
        	return null;
        }

        try {
        	size = AutoKafkaField.TerminalID.getSize();
			tuple.setString(AutoKafkaField.TerminalID.getIndex(), new String(Arrays.copyOfRange(data, curIndex, size)));
			curIndex += size;
        	size = AutoKafkaField.SequenceNo.getSize();
			tuple.setLong(AutoKafkaField.SequenceNo.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.BodyLength.getSize();
			tuple.setLong(AutoKafkaField.BodyLength.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.CIN.getSize();
			tuple.setString(AutoKafkaField.CIN.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.VIN.getSize();
			tuple.setString(AutoKafkaField.VIN.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.VehicleKeyID.getSize();
			tuple.setLong(AutoKafkaField.VehicleKeyID.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.PolicyVersion.getSize();
			tuple.setInt(AutoKafkaField.PolicyVersion.getIndex(), NumUtils.getIntFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.RecordCount.getSize();
			tuple.setLong(AutoKafkaField.RecordCount.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.RootCount.getSize();
			tuple.setInt(AutoKafkaField.RootCount.getIndex(), NumUtils.getIntFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.SubmitSequenceNo.getSize();
			tuple.setLong(AutoKafkaField.SubmitSequenceNo.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.SerialNo.getSize();
			tuple.setString(AutoKafkaField.SerialNo.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.BaseTime.getSize();
			tuple.setLong(AutoKafkaField.BaseTime.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
        	size = AutoKafkaField.MessageType.getSize();
			tuple.setInt(AutoKafkaField.MessageType.getIndex(),NumUtils.getIntFromBig(data, curIndex, size));
			curIndex += size;

        	size = AutoKafkaField.FirstPID.getSize();
			tuple.setString(AutoKafkaField.FirstPID.getIndex(), Base64.encodeBytes(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;

        	size = AutoKafkaField.MsgSrcKeyID.getSize();
			tuple.setString(AutoKafkaField.MsgSrcKeyID.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.SyncSerID.getSize();
			tuple.setString(AutoKafkaField.SyncSerID.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.LoadDTM.getSize();
			tuple.setString(AutoKafkaField.LoadDTM.getIndex(), new String(Arrays.copyOfRange(data, curIndex, curIndex+size)));
			curIndex += size;
        	size = AutoKafkaField.XctRedisInpDTM.getSize();
			tuple.setLong(AutoKafkaField.XctRedisInpDTM.getIndex(), NumUtils.getLongFromBig(data, curIndex, size));
			curIndex += size;
			return tuple;
        } catch (Exception e) {
            logger.error("Error deserializing topic '" + topic + "': " + e.getMessage(), e);
            return null;
        }
    }

    @Override
    public void close() {
    }

}
