package com.autoever.poc.parser.can;

import org.w3c.dom.Element;

import com.streambase.sb.Tuple;

abstract class Evaluable {
	public TriggerParser trigger = null;
	public Evaluable(TriggerParser trigger) {
		this.trigger = trigger;
	}
	public Element GetNode() {
		return trigger.mNode;
	}
	
	public Object Evaluate(Tuple message) {
		if(trigger == null) return null;
		return EvalData(trigger, message);
	}

	abstract public Object EvalData(TriggerParser trigger, Tuple message);
}


