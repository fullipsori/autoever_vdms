package com.autoever.poc.parser.can;

import com.streambase.sb.Tuple;

public class CanEvaluable extends Evaluable {

	public CanEvaluable(TriggerParser trigger) {
		super(trigger);
	}

	@Override
	public Object EvalData(TriggerParser trigger, Tuple message) {
		return TriggerParser.EvalCAN(trigger, message);
	}
	
}
