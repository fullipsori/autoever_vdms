package com.autoever.poc.parser;

import java.util.List;
import java.util.Optional;
import java.util.function.BiFunction;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

@FunctionalInterface
public interface Parseable {
	void parse();
	public static BiFunction<NodeList, String, Optional<Element>> GetElement = (nodelist, name) -> IntStream.range(0, nodelist.getLength())
			.mapToObj(nodelist::item)
			.filter(n-> n.getNodeType() == Node.ELEMENT_NODE && n.getNodeName().equals(name))
			.map(n -> (Element)n)
			.findFirst();

	public static BiFunction<NodeList, String, List<Element>> GetElements = (nodelist, name) -> IntStream.range(0, nodelist.getLength())
			.mapToObj(nodelist::item)
			.filter(n-> n.getNodeType() == Node.ELEMENT_NODE && n.getNodeName().equals(name))
			.map(n -> (Element)n)
			.collect(Collectors.toList());
}
