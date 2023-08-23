package com.autoever.poc.parser.ccp;

import java.util.ArrayList;
import java.util.List;

import com.autoever.poc.common.NumUtils;
import com.autoever.poc.parser.AutoKafkaField;
import com.autoever.poc.parser.PreProcessable;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.util.Pair;


public class CCPPreProcessor implements PreProcessable {

	private int prevCmd = 0;
	public static final int ccpStartCmd = 0x0a;
	public static final int ccpEndCmd = 0x3b;
	private RawParsedData rawParsedData = null;
	private final int sizeCellData = 90;
	private final int sizeMsrTBData = 9;

	public CCPPreProcessor() {
	}

	private class RawParsedData {
		private List<Tuple> rawCellData = new ArrayList<>();
		private List<Tuple> rawMsrTBData = new ArrayList<>();
		private Double rawSOC = null;
		private Double rawIBM = null;
		private Long rawChargingNow = null;
		private Long rawISOL = null;
		private Long rawFaultCode = null;
		
		private boolean validate() {
			if(rawCellData.size() != sizeCellData) return false;
			if(rawMsrTBData.size() != sizeMsrTBData) return false;
			if(rawSOC == null) return false;
			if(rawIBM == null) return false;
			if(rawChargingNow == null) return false;
			if(rawISOL == null) return false;
			if(rawFaultCode == null) return false;
			return true;
		}
		
		public void addFieldData(int command, Pair<String, Long> data) {
			try {
				if(data.first.startsWith("cell_")) {
					Tuple field = FieldType.createTuple();
					field.setString(0, data.first);
					field.setLong(1, data.second);
					rawCellData.add(field);
				}else if(data.first.startsWith("msr_tb_")) {
					Tuple field = FieldType.createTuple();
					field.setString(0, data.first);
					field.setLong(1, data.second);
					rawMsrTBData.add(field);
				}else if("SOC".equals(data.first)) {
					rawSOC = data.second * 1.0;
				}else if("msr_data.ibm".equals(data.first)) {
					rawIBM = data.second * 1.0;
				}else if("chg_charging_now".equals(data.first)) {
					rawChargingNow = data.second;
				}else if("msr_data.r_isol".equals(data.first)) {
					rawISOL =  data.second;
				}else if("fault_code".equals(data.first)) {
					rawFaultCode = data.second;
				}
			}catch(Exception e) {
				e.printStackTrace();
			}
		}
		
		public Tuple GetTuple() {
			try {
				if(validate()) {
					Tuple ccpTuple = CCPPreProcessor.RawParsed.createTuple();
					ccpTuple.setList("rawCellData", rawCellData);
					ccpTuple.setList("rawMsrTBData", rawMsrTBData);
					ccpTuple.setDouble("rawSOC", rawSOC);
					ccpTuple.setDouble("rawIBM", rawIBM);
					ccpTuple.setLong("rawChargingNow", rawChargingNow);
					ccpTuple.setLong("rawISOL", rawISOL);
					ccpTuple.setLong("rawFaultCode", rawFaultCode);
					return ccpTuple;
				}
				return null;
			}catch(Exception e) {
				return null;
			}
		}
	}

	public final static Schema FieldType = new Schema("FieldType", List.of(
			new Schema.Field("fieldName", CompleteDataType.forString()),
			new Schema.Field("fieldValue", CompleteDataType.forLong())));

	public final static Schema RawParsed = new Schema("RawParsed", 
		List.of(
			new Schema.Field("rawCellData", CompleteDataType.forList(CompleteDataType.forTuple(FieldType))),
			new Schema.Field("rawMsrTBData", CompleteDataType.forList(CompleteDataType.forTuple(FieldType))),
			new Schema.Field("rawSOC", CompleteDataType.forDouble()),
			new Schema.Field("rawIBM", CompleteDataType.forDouble()),
			new Schema.Field("rawChargingNow", CompleteDataType.forLong()),
			new Schema.Field("rawISOL", CompleteDataType.forLong()),
			new Schema.Field("rawFaultCode", CompleteDataType.forLong())
		));
	
	public static void addSchemaField(List<Schema.Field> outputSchemaField) {
		outputSchemaField.add(new Schema.Field("RawParsed", CompleteDataType.forTuple(RawParsed)));
		return;
	}

	@Override
	public boolean preProcess(Tuple inputTuple, Tuple dataTuple, int msgInfo, int channel, int id, byte[] rawData) {
		// TODO Auto-generated method stub
		if(rawData == null || rawData.length == 0) return false;
		if(prevCmd != 0 ) {
			if(prevCmd != 255 && ((rawData[0]&0xff) >= ccpStartCmd) && ((rawData[0]&0xff) <= ccpEndCmd)) {
				prevCmd = rawData[0] & 0xff;
				try {
					Tuple kafkaMessage = inputTuple.getTuple("kafkaMessage");
					ODTParser odtParser = ODTRepository.getInstance().getMapper(kafkaMessage);
					List<Pair<String, Long>> odtParsed = parseData(rawData, odtParser);
					if(odtParsed != null) {
						if(rawParsedData == null) rawParsedData = new RawParsedData();
						odtParsed.stream().forEach(pair -> rawParsedData.addFieldData(prevCmd, pair));
					}

					if(prevCmd >= odtParser.ccpRawEndCmd && rawParsedData != null) {
						Tuple resTuple = rawParsedData.GetTuple();
						rawParsedData = null;
						if(resTuple != null) {
							dataTuple.setTuple("RawParsed", resTuple); 
							return true;
						}
						return false;
					}
					return false;
				}catch(Exception e) {
					e.printStackTrace();
					rawParsedData = null;
					return false;
				}
			}
		}
		prevCmd = rawData[0] & 0xff;
		return false;
	}

	@Override
	public void initialize(Tuple kafkaMessage) {
		// TODO Auto-generated method stub
		prevCmd = 0;
		rawParsedData = null;
		try {
			int rootCount = kafkaMessage.getInt(AutoKafkaField.RootCount.getIndex());
			ODTParser odtParser = ODTRepository.getInstance().getMapper(kafkaMessage);
			if(odtParser != null) odtParser.InitParams(rootCount);
		}catch(Exception e) {}
	}


	@SuppressWarnings("unchecked")
	public static List<Pair<String, Long>> parseData(byte[] rawdata, ODTParser evtParser) {

		if(evtParser == null) return null;

		int cmd = rawdata[0] & 0xff;
		List<Pair<String,Long>> resultList = new ArrayList<>();
		Object[] odt = evtParser.odt_map.get(cmd-10);
		if(odt == null || ((List<?>)odt[0]).isEmpty()) return null;

		int index = 1;
		for(int i=0; i<((List<String>)odt[0]).size(); i++) {
			switch(((String)odt[2]).charAt(i)) {
				case 'L' :
					resultList.add(new Pair<String,Long>(
							(String)((List<String>)odt[0]).get(i), 
							NumUtils.getLongFromLittle(rawdata, index, 4)));
					index += 4;
					break;
				case 'H' :
					resultList.add(new Pair<String,Long>(
							(String)((List<String>)odt[0]).get(i), 
							NumUtils.getLongFromLittle(rawdata, index, 2)));
					index += 2;
					break;
				case 'B' :
					resultList.add(new Pair<String,Long>(
							(String)((List<String>)odt[0]).get(i), 
							NumUtils.getLongFromLittle(rawdata, index, 1)));
					index += 1;
					break;
			}
		}
		return resultList;
	}
}
