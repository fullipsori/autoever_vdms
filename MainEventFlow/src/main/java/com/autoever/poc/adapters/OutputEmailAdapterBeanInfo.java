package com.autoever.poc.adapters;

import java.beans.*;

import com.streambase.sb.operator.parameter.*;

/**
* A BeanInfo class controls what properties are exposed, add 
* metadata about properties (such as which properties are optional), and access 
* special types of properties that can't be automatically derived via reflection. 
* If a BeanInfo class is present, only the properties explicitly declared in
* this class will be exposed by StreamBase.
*/
public class OutputEmailAdapterBeanInfo extends SBSimpleBeanInfo {

	/*
	* The order of properties below determines the order they are displayed within
	* the StreamBase Studio property view. 
	*/
	public SBPropertyDescriptor[] getPropertyDescriptorsChecked() throws IntrospectionException {
		SBPropertyDescriptor[] p = {
				new SBPropertyDescriptor("SMTP_HOST", OutputEmailAdapter.class).displayName("SMTP HOST")
						.description(""),
				new SBPropertyDescriptor("SMTP_ID", OutputEmailAdapter.class).displayName("SMTP ID").description(""),
				new SBPropertyDescriptor("SMTP_PASS", OutputEmailAdapter.class).displayName("SMTP PASS")
						.description(""),
				new SBPropertyDescriptor("SMTP_ADDR", OutputEmailAdapter.class).displayName("SMTP_ADDRESS")
						.description(""), };
		return p;
	}

}
