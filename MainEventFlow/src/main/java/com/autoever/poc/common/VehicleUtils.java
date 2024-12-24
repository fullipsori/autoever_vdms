package com.autoever.poc.common;

import java.util.ArrayList;
import java.util.List;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Tuple;
import com.streambase.sb.client.CustomFunctionResolver;

public class VehicleUtils {

	@CustomFunctionResolver("UpdateVehicleSignalStatusCustomFunctionResolver0")
	public static List<Tuple> UpdateVehicleSignalStatus(List<Tuple> vehicleStatusList, Tuple newStatus) {
		try {
			long vehicleKeyID = newStatus.getLong("vehicleKeyID");
			if(vehicleStatusList == null) {
				List<Tuple> vList = new ArrayList<Tuple>();
				vList.add(newStatus);
				return vList;
			}else {
				vehicleStatusList.stream().filter(t-> {
					try {
						return t.getLong("vehicleKeyID")==vehicleKeyID;
					}catch(Exception e) {
						return false;
					}
				}).limit(1).map(vehicleStatusList::indexOf).findFirst()
				.ifPresentOrElse(index-> vehicleStatusList.set(index, newStatus),()->vehicleStatusList.add(newStatus));

				return vehicleStatusList;
			}
			
		} catch (Exception e) {
			e.printStackTrace();
			return vehicleStatusList;
		}

	}
	
	public static CompleteDataType UpdateVehicleSignalStatusCustomFunctionResolver0(CompleteDataType vehicleStatusList, CompleteDataType newStatus) {
		return vehicleStatusList;
	}

	@CustomFunctionResolver("GetVehicleSignalStatusCustomFunctionResolver0")
	public static Tuple GetVehicleSignalStatus(List<Tuple> vehicleStatusList, long vehicleKeyID) {
		try {
			if(vehicleStatusList == null) {
				return null;
			}else {
				return vehicleStatusList.stream().filter(t-> {
					try {
						return t.getLong("vehicleKeyID")==vehicleKeyID;
					}catch(Exception e) {
						return false;
					}
				}).findFirst().orElse(null);
			}
			
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	
	public static CompleteDataType GetVehicleSignalStatusCustomFunctionResolver0(CompleteDataType vehicleStatusList, CompleteDataType vehicleKeyID) {
		return vehicleStatusList.getElementType();
	}

	
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

}
