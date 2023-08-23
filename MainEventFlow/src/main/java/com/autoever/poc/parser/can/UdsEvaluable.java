package com.autoever.poc.parser.can;

import com.streambase.sb.Tuple;

public class UdsEvaluable extends Evaluable {

	public UdsEvaluable(TriggerParser trigger) {
		super(trigger);
	}

	@Override
	public Object EvalData(TriggerParser trigger, Tuple message) {
		return TriggerParser.EvalUDS(trigger, message);
	}

}
