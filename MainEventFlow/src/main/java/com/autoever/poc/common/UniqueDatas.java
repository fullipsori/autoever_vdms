package com.autoever.poc.common;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.IntStream;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Tuple;
import com.streambase.sb.client.CustomFunctionResolver;
import com.streambase.sb.operator.AggregateWindow;

public class UniqueDatas extends AggregateWindow {

	public static final long serialVersionUID = 1690338405269L;
	private List<Tuple> accDatas = new ArrayList<>();

	/**
	* Called before each new use of the aggregate window object.
	*/
	public void init() {
		accDatas.clear();
	}

	public List<?> calculate() {
		return accDatas;
	}

	public static String getStringField(Tuple tuple, int index) {
		try {
			return tuple.getString(index);
		} catch(Exception e) {
			return "";
		}
	}

	@CustomFunctionResolver("accumulateCustomFunctionResolver0")
	public void accumulate(Tuple inData, boolean isFirst) {
		if(inData == null) return;
		String fieldName = getStringField(inData, 0);
		if(fieldName == null) return;
		IntStream.range(0, accDatas.size()).filter(i -> fieldName.equals(getStringField(accDatas.get(i), 0)))
			.findFirst().ifPresentOrElse(i -> { if(!isFirst) accDatas.set(i, inData);}, () -> accDatas.add(inData));
	}

	public static CompleteDataType accumulateCustomFunctionResolver0(CompleteDataType inData,
			CompleteDataType isFirst) {
		return CompleteDataType.forList(inData);
	}

	public void release() {
		accDatas.clear();
	}

}
