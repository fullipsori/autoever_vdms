//
// Copyright 2004-2022 TIBCO Software Inc. All rights reserved.
//

package com.autoever.poc.adapters;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

import org.slf4j.Logger;

import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class KafkaFileSerializer implements org.apache.kafka.common.serialization.Serializer<Tuple> {

    private static final String CONFIG_SCHEMA = "schema";
    private static final String CONFIG_LOGGER = "logger";
    
    private Schema schema;
    private Logger logger;
    
    private Schema.Field filePathField;
    @Override
    public void close() {
    }

    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        if (configs.containsKey(CONFIG_SCHEMA)) {
            schema = (Schema)configs.get(CONFIG_SCHEMA);
			try {
				filePathField = schema.getField("filePath");
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
        
        try {
			String filePath = tuple.getString(filePathField);
			byte[] allBytes;
			try {
				allBytes = Files.readAllBytes(Paths.get(filePath));
				if(allBytes != null && allBytes.length > 0) {
					return allBytes;
				} else {
				}
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
				return null;
			}
		} catch (Exception e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
			return null;
		}
        return null;
    }

}
