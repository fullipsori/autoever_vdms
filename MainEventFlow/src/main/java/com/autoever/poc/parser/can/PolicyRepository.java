package com.autoever.poc.parser.can;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import com.autoever.poc.parser.AutoKafkaField;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class PolicyRepository {

	public Map<String, PolicyParser> mPolicyMap = null;

	private static PolicyRepository mInstance = new PolicyRepository();
	public static PolicyRepository getInstance() {
		return mInstance;
	}
	
	public PolicyParser getMapper(Tuple kafkaMessage) {
		
		try {
			String terminalID = kafkaMessage.getString(AutoKafkaField.TerminalID.getIndex());
			return PolicyRepository.getInstance().mPolicyMap.get(terminalID);
		}catch(Exception e) {
			return null;
		}
	}
	
	public static Schema trigDataSchema = new Schema(
			"TRIGDATA",
			new Schema.Field("preTime", CompleteDataType.forDouble()),
			new Schema.Field("postTime", CompleteDataType.forDouble()),
			new Schema.Field("deltaTime", CompleteDataType.forDouble()),
			new Schema.Field("eventName", CompleteDataType.forString()),
			new Schema.Field("category", CompleteDataType.forString()),
			new Schema.Field("status", CompleteDataType.forString()),
			new Schema.Field("value", CompleteDataType.forString())
			);

	public boolean LoadPolicy(String dirPath, String ext) {
		if(dirPath == null || dirPath.isBlank()) return false;
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder documentBuilder;
		
		try {
			documentBuilder = factory.newDocumentBuilder();
			mPolicyMap = Files.list(Paths.get(dirPath))
				.filter(path -> path.toString().endsWith(ext))
				.parallel()
				.map(path -> new PolicyParser(path, documentBuilder))
				.collect(Collectors.toConcurrentMap(PolicyParser::GetFileName, Function.identity())) ;
			
			return true;
		} catch (Exception e) {
			System.out.println("LoadPolicy Exp:" + e.getMessage());
			return false;
		}
	}

}