package com.autoever.poc.parser.ccp;

import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.client.CustomFunctionResolver;

public class CCPCustomUtils {

	public static long GetFieldValue(Tuple tuple, int index) {
		try {
			return tuple.getLong(index);
		} catch (Exception e) {
			return 0;
		}
	}

	@CustomFunctionResolver("GetDeltaValueCustomUtilsResolver0")
	public static long GetDeltaValue(List<Tuple> datas){
		if(datas == null) return 0;
		return datas.stream().mapToLong(tuple -> CCPCustomUtils.GetFieldValue(tuple, 1)).max().getAsLong()
				- datas.stream().mapToLong(tuple -> CCPCustomUtils.GetFieldValue(tuple, 1)).min().getAsLong();
	}

	public static CompleteDataType GetDeltaValueCustomUtilsResolver0(CompleteDataType datas) {
		return CompleteDataType.forLong();
	}
	
	@CustomFunctionResolver("GetMaxValueCustomUtilsResolver0")
	public static long GetMaxValue(List<Tuple> datas){
		if(datas == null) return 0;
		return datas.stream().mapToLong(tuple -> CCPCustomUtils.GetFieldValue(tuple, 1)).max().getAsLong();
	}

	public static CompleteDataType GetMaxValueCustomUtilsResolver0(CompleteDataType datas) {
		return CompleteDataType.forLong();
	}

	@CustomFunctionResolver("GetMinValueCustomUtilsResolver0")
	public static long GetMinValue(List<Tuple> datas){
		if(datas == null) return 0;
		return datas.stream().mapToLong(tuple -> CCPCustomUtils.GetFieldValue(tuple, 1)).min().getAsLong();
	}

	public static CompleteDataType GetMinValueCustomUtilsResolver0(CompleteDataType datas) {
		return CompleteDataType.forLong();
	}

	@CustomFunctionResolver("GetDVolCustomUtilsResolver0")
	public static List<Double> GetDVol(List<Tuple> cellDatas){
		// TODO Implement function here
		if(cellDatas == null) return null;
		double[] cellDiffs = new double[cellDatas.size()];
		for(int i=0; i < cellDatas.size(); i++) {
			if(i==0) { 
				cellDiffs[i] = 0;
			} else { 
				cellDiffs[i] = GetFieldValue(cellDatas.get(i), 1) - GetFieldValue(cellDatas.get(i-1), 1); 
			}
		}
		
		double mean = Math.round(Arrays.stream(cellDiffs).average().orElse(0.0) * 10.0)/10.0;
		return Arrays.stream(cellDiffs).map(v -> v-mean).boxed().collect(Collectors.toList());
	}
	
	public static CompleteDataType GetDVolCustomUtilsResolver0(CompleteDataType cellDatas) {
		return CompleteDataType.forList(CompleteDataType.forDouble());
	}

	public static final Schema FieldDoubleSchema = new Schema(null, List.of(
			new Schema.Field("field", CompleteDataType.forString()), 
			new Schema.Field("value", CompleteDataType.forDouble())));

	@CustomFunctionResolver("GetMaxDVolCustomUtilsResolver0")
	public static Tuple GetMaxDVol(List<Double> dVols){
		if(dVols == null) return null;
		Tuple volTuple = FieldDoubleSchema.createTuple();
		int maxIndex = IntStream.range(0, dVols.size()).boxed().max(Comparator.comparingDouble(i -> Math.abs(dVols.get(i)))).get();
		try {
			volTuple.setString(0, "cell_"+ (maxIndex+1));
			volTuple.setDouble(1, dVols.get(maxIndex));
			return volTuple;
		}catch(Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	
	public static CompleteDataType GetMaxDVolCustomUtilsResolver0(CompleteDataType dVols) {
		return CompleteDataType.forTuple(FieldDoubleSchema);
	}

	@CustomFunctionResolver("GetMaxDVolValCustomUtilsResolver0")
	public static Double GetMaxDVolVal(List<Double> dVols){
		if(dVols == null || dVols.isEmpty()) return 0.0;
		return dVols.stream().max(Comparator.comparingDouble(Math::abs)).map(Math::abs).get();
	}
	
	public static CompleteDataType GetMaxDVolValCustomUtilsResolver0(CompleteDataType dVols) {
		return CompleteDataType.forDouble();
	}

	@CustomFunctionResolver("GetMaxDVolCellsCustomUtilsResolver0")
	public static String GetMaxDVolCells(List<Double> dVols, Double value){
		if(dVols == null || dVols.isEmpty()) return "";
		return IntStream.range(0, dVols.size()).filter(i -> Math.abs(dVols.get(i)) == value.doubleValue()).mapToObj(i -> String.valueOf(i+1)).collect(Collectors.joining(","));
	}
	
	public static CompleteDataType GetMaxDVolCellsCustomUtilsResolver0(CompleteDataType dVols, CompleteDataType value) {
		return CompleteDataType.forString();
	}

	@CustomFunctionResolver("GetMaxCDiffValCustomUtilsResolver0")
	public static Long GetMaxCDiffVal(List<Long> cellDiffs){
		if(cellDiffs == null || cellDiffs.isEmpty()) return (long)0;
		return cellDiffs.stream().max(Comparator.comparingLong(Math::abs)).map(Math::abs).get();
	}
	
	public static CompleteDataType GetMaxCDiffValCustomUtilsResolver0(CompleteDataType cellDiffs) {
		return CompleteDataType.forLong();
	}

	@CustomFunctionResolver("GetMaxCDiffCellsCustomUtilsResolver0")
	public static String GetMaxCDiffCells(List<Long> cellDiffs, Long value){
		if(cellDiffs == null || cellDiffs.isEmpty()) return "";
		return IntStream.range(0, cellDiffs.size()).filter(i -> Math.abs(cellDiffs.get(i)) == value.longValue()).mapToObj(i -> String.valueOf(i+1)).collect(Collectors.joining(","));
	}
	
	public static CompleteDataType GetMaxCDiffCellsCustomUtilsResolver0(CompleteDataType cellDiffs, CompleteDataType value) {
		return CompleteDataType.forString();
	}

	@CustomFunctionResolver("JoinFromCellTuplesCustomUtilsResolver0")
	public static String JoinFromCellTuples(List<Tuple> cellDatas){
		if(cellDatas == null) return "";
		return cellDatas.stream().map(tuple -> GetFieldValue(tuple, 1)).map(String::valueOf).collect(Collectors.joining(","));
	}

	public static CompleteDataType JoinFromCellTuplesCustomUtilsResolver0(CompleteDataType cellDatas) {
		return CompleteDataType.forString();
	}

	@CustomFunctionResolver("GetCellTupleDataCustomUtilsResolver0")
	public static List<Long> GetCellTupleData(List<Tuple> cellDatas){
		if(cellDatas == null) return null;
		return cellDatas.stream().map(tuple -> GetFieldValue(tuple, 1)).collect(Collectors.toList());
	}

	public static CompleteDataType GetCellTupleDataCustomUtilsResolver0(CompleteDataType cellDatas) {
		return CompleteDataType.forList(CompleteDataType.forLong());
	}

	@CustomFunctionResolver("JoinFromMsrTBTuplesCustomUtilsResolver0")
	public static String JoinFromMsrTBTuples(List<Tuple> msrTBDatas){
		if(msrTBDatas== null) return "";
		return msrTBDatas.stream().map(tuple -> GetFieldValue(tuple, 1)).map(l -> Math.round(l)/10.0).map(String::valueOf).collect(Collectors.joining(","));
	}

	public static CompleteDataType JoinFromMsrTBTuplesCustomUtilsResolver0(CompleteDataType msrTBDatas) {
		return CompleteDataType.forString();
	}

	@CustomFunctionResolver("GetMsrTBTupleDataCustomUtilsResolver0")
	public static List<Double> GetMsrTBTupleData(List<Tuple> msrTBDatas){
		if(msrTBDatas== null) return null;
		return msrTBDatas.stream().map(tuple -> GetFieldValue(tuple, 1)).map(l -> Math.round(l)/10.0).collect(Collectors.toList());
	}

	public static CompleteDataType GetMsrTBTupleDataCustomUtilsResolver0(CompleteDataType msrTBDatas) {
		return CompleteDataType.forList(CompleteDataType.forDouble());
	}

	@CustomFunctionResolver("JoinFromNumberListCustomUtilsResolver0")
	public static String JoinFromNumberList(List<? extends Number> datas){
		if(datas == null || datas.size() == 0) return "none";
		return datas.stream().map(v-> String.valueOf(v)).collect(Collectors.joining(","));
	}

	public static CompleteDataType JoinFromNumberListCustomUtilsResolver0(CompleteDataType datas) {
		return CompleteDataType.forString();
	}
	
	
	@CustomFunctionResolver("getMatchedTupleByIntervalCustomUtilsResolver0")
	public static Tuple getMatchedTupleByInterval(Tuple kafkaMessage, Tuple dataTuple, double realTime, double minInterval, double maxInterval) {
		ODTParser odtParser = ODTRepository.getInstance().getMapper(kafkaMessage);
		if(odtParser != null) return odtParser.getMatchedTupleByInterval(dataTuple, realTime, minInterval, maxInterval);
		return null;
	}
	
	public static CompleteDataType getMatchedTupleByIntervalCustomUtilsResolver0(CompleteDataType kafkaMessage, CompleteDataType dataTuple, CompleteDataType realTime, CompleteDataType minInterval, CompleteDataType maxInterval) {
		return CompleteDataType.forTuple(CCPPreProcessor.RawParsed);
	}
	
	@CustomFunctionResolver("getCellDiffCustomUtilsResolver0")
	public static List<Long> getCellDiff(Tuple kafkaMessage, List<Tuple> curCells, List<Tuple> prevCells) {
		ODTParser odtParser = ODTRepository.getInstance().getMapper(kafkaMessage);
		if(odtParser != null) return odtParser.getCellDiff(curCells, prevCells);
		return null;
	}
	
	public static CompleteDataType getCellDiffCustomUtilsResolver0(CompleteDataType kafkaMessage, CompleteDataType curCells, CompleteDataType prevCells) {
		return CompleteDataType.forList(CompleteDataType.forLong());
	}

}
