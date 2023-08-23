package com.autoever.poc.parser.can;

import java.util.List;

@FunctionalInterface
public interface EventCallback {
	public List<String> OnCalled(double time, Boolean status, String value);
}
