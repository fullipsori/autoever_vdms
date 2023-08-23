package com.autoever.poc.parser;

import com.streambase.sb.Schema;

public interface DataSavable {
	public void initData(int param);
	public Schema getSaveSchema();
	public Object toSave();
	public void fromSave(Object saved);
}
