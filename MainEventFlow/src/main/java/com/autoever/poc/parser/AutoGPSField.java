package com.autoever.poc.parser;

public enum AutoGPSField {
	Latitude("Latitude", 4), 
	Longitude("Longitude", 4), 
	Heading("Heading", 2),
	Velocity("Velocity", 1),
	Altitude("Altitude", 3);

	private final String name;
    private final int size;

    AutoGPSField(String name, int size) { 
    	this.name = name;
    	this.size= size; 
    }

    public String getName() { return this.name; }
    public int getsize() { return this.size; }

}
