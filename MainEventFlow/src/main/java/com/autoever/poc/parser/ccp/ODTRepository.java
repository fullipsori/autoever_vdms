package com.autoever.poc.parser.ccp;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import com.autoever.poc.parser.AutoKafkaField;
import com.streambase.sb.Tuple;

public class ODTRepository {

	public Map<String, ODTParser> mODTMap = null;

	private static ODTRepository mInstance = new ODTRepository();
	public static ODTRepository getInstance() {
		return mInstance;
	}
	
	public ODTParser getMapper(Tuple kafkaMessage) {
		try {
			long vehicleKeyID = kafkaMessage.getLong(AutoKafkaField.VehicleKeyID.getIndex());
			return ODTRepository.getInstance().mODTMap.get(String.valueOf(vehicleKeyID));
		}catch(Exception e) {
			return null;
		}
	}

	public void setODT(Map<String,ODTParser> map) {
		mODTMap  = map;
	}
	
	public boolean LoadEVT(String dirPath, String ext) {
		if(dirPath == null || dirPath.isBlank()) return false;
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder documentBuilder;

		try {
			documentBuilder = factory.newDocumentBuilder();
			ODTRepository.getInstance().setODT( 
				Files.list(Paths.get(dirPath))
				.filter(path -> path.toString().endsWith(ext))
				.parallel()
				.map(path -> new ODTParser(path, documentBuilder))
				.collect(Collectors.toConcurrentMap(ODTParser::GetFilename, Function.identity())) 
			);
			return true;
		} catch (Exception e) {
			System.out.println("LoadEVT Excep:" + e.getMessage());
			return false;
		}
	}

}