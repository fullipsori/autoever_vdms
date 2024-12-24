package com.autoever.poc.parser.can;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.TupleException;
import com.streambase.sb.client.CustomFunctionResolver;

public class TrigData {

	public static Schema trigDataSchema = new Schema(
			"TRIGDATA",
			new Schema.Field("preTime", CompleteDataType.forDouble()),
			new Schema.Field("postTime", CompleteDataType.forDouble()),
			new Schema.Field("deltaTime", CompleteDataType.forDouble()),
			new Schema.Field("eventName", CompleteDataType.forString()),
			new Schema.Field("category", CompleteDataType.forString()),
			new Schema.Field("status", CompleteDataType.forString()),
			new Schema.Field("value", CompleteDataType.forDouble())
			);

	@CustomFunctionResolver("MergeTrigEventsCustomFunctionResolver0")
	public static List<Tuple> MergeTrigEvents(List<Tuple> eventList, List<Tuple> events) {
		try {
			if(eventList == null || eventList.isEmpty()) {
				return events;
			}else {
				events.stream().forEach(event->{
					try {
						String eventName = event.getString("eventName");
						IntStream.range(0, eventList.size())
						.filter(n-> {
							try {
								return eventName.equals(eventList.get(n).getString("eventName"));
							} catch (Exception e) {
								e.printStackTrace();
								return false;
							}
						})
						.findFirst().ifPresentOrElse(n->eventList.set(n, event), ()->eventList.add(event));
					} catch (Exception e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				});

				return eventList;
			}
		}catch(Exception e) {
			return null;
		}
	}
	
	public static CompleteDataType MergeTrigEventsCustomFunctionResolver0(CompleteDataType eventList, CompleteDataType events) {
		return eventList;
	}

	@CustomFunctionResolver("GetChangedTrigEventsCustomFunctionResolver0")
	public static List<Tuple> GetChangedTrigEvents(List<Tuple> eventList, List<Tuple> events) {
		try {
			if(eventList == null || eventList.isEmpty()) {
				return events;
			}else {
				return events.stream().filter(event-> {
					try {
						String eventName = event.getString("eventName");
						Double value = event.getDouble("value");
						Double matchValue = eventList.stream().filter(e->{
							try {
								return eventName.equals(e.getString("eventName"));
							} catch (Exception e1) {
								return false;
							}
						}).map(e->{
							try {
								return e.getDouble("value");
							} catch (Exception e1) {
								return null;
							}
						}).findFirst().orElse(null);

						return (matchValue==null)? true :  Double.compare(value,matchValue)!=0;
					} catch (TupleException e1) {
						return true;
					}
				}).collect(Collectors.toList());
			}

		}catch(Exception e) {
			return events;
		}
	}
	
	public static CompleteDataType GetChangedTrigEventsCustomFunctionResolver0(CompleteDataType eventList, CompleteDataType events) {
		return events;
	}

	@CustomFunctionResolver("ContainSameTrigEventsCustomFunctionResolver0")
	public static boolean ContainSameTrigEvents(List<Tuple> eventList, List<Tuple> events) {
		try {
			if(eventList == null || eventList.isEmpty()) {
				return false;
			}else {
				return events.stream().allMatch(event-> {
					try {
						String eventName = event.getString("eventName");
						Double value = event.getDouble("value");
						Double matchValue = eventList.stream().filter(e->{
								try {
									return eventName.equals(e.getString("eventName"));
								} catch (Exception e1) {
									e1.printStackTrace();
									return false;
								}
							}).map(e->{
								try {
									return e.getDouble("value");
								} catch (Exception e1) {
									e1.printStackTrace();
									return null;
								}
							})
							.findFirst().orElse(null);
						
						return (matchValue==null)? false :  Double.compare(value,matchValue)==0;
					} catch (TupleException e1) {
						e1.printStackTrace();
						return false;
					}
				});
			}
		}catch(Exception e) {
			e.printStackTrace();
			return false;
		}
	}
	
	public static CompleteDataType ContainSameTrigEventsCustomFunctionResolver0(CompleteDataType eventList, CompleteDataType events) {
		return CompleteDataType.forBoolean();
	}
	
	@CustomFunctionResolver("GetEventFromTrigListCustomFunctionResolver0")
	public static Tuple GetEventFromTrigList(List<Tuple> eventList, String eventName) {
		try {
			if(eventList == null || eventList.isEmpty()) {
				return null;
			}else {
				return eventList.stream().filter(f -> {
					try {
						return eventName.equals(f.getString("eventName"));
					} catch (Exception e) {
						return false;
					}
				}).findFirst().orElse(null);
			}
		}catch(Exception e) {
			return null;
		}
	}

	public static CompleteDataType GetEventFromTrigListCustomFunctionResolver0(CompleteDataType eventList, CompleteDataType eventName) {
		return eventList.getElementType();
	}

	@CustomFunctionResolver("GetEventValueFromTrigListCustomFunctionResolver0")
	public static Double GetEventValueFromTrigList(List<Tuple> eventList, String eventName) {
		try {
			if(eventList == null || eventList.isEmpty()) {
				return null;
			}else {
				return eventList.stream().filter(f -> {
					try {
						return eventName.equals(f.getString("eventName"));
					} catch (Exception e) {
						return false;
					}
				}).map(f->{
					try {
						return f.getDouble("value");
					} catch (Exception e) {
						return null;
					}
				}).findFirst().orElse(null);
			}
		}catch(Exception e) {
			return null;
		}
	}

	public static CompleteDataType GetEventValueFromTrigListCustomFunctionResolver0(CompleteDataType eventList, CompleteDataType eventName) {
		return CompleteDataType.forDouble();
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
	}

}
