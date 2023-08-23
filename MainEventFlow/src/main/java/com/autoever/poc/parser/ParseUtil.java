package com.autoever.poc.parser;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import com.autoever.poc.common.RawDataField;
import com.autoever.poc.parser.can.PolicyParser;
import com.autoever.poc.parser.can.PolicyRepository;
import com.autoever.poc.parser.can.TriggerParser;
import com.autoever.poc.parser.ccp.ODTParser;
import com.autoever.poc.parser.ccp.ODTRepository;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.client.CustomFunctionResolver;
import com.streambase.sb.util.Pair;

import io.fabric8.kubernetes.client.utils.Base64;

public class ParseUtil {

	@CustomFunctionResolver("GetKeyFlagCustomFunctionResolver0")
	public static boolean GetKeyFlag(String policy, Tuple message) {
		PolicyParser policyParser = PolicyRepository.getInstance().mPolicyMap.get(policy);
		if(policyParser != null) return policyParser.GetKeyFlag(message);
		return false;
	}

	public static CompleteDataType GetKeyFlagCustomFunctionResolver0(CompleteDataType policy, CompleteDataType message) {
		return CompleteDataType.forBoolean();
	}
	
	@CustomFunctionResolver("GetTrigDataCustomFunctionResolver0")
	public static List<Tuple> GetTrigData(String policy, Tuple message) {
		PolicyParser policyParser = PolicyRepository.getInstance().mPolicyMap.get(policy);
		if(policyParser != null) return policyParser.GetTrigData(message);
		return null;
	}

	public static CompleteDataType GetTrigDataCustomFunctionResolver0(CompleteDataType policy, CompleteDataType message) {
		return CompleteDataType.forList(CompleteDataType.forTuple(PolicyRepository.trigDataSchema));
	}
	
	public static boolean InitPolicyRepository(String dirPath) {
		return PolicyRepository.getInstance().LoadPolicy(dirPath, "xml");
	}
	
	public static boolean InitODTRepository(String dirPath) {
		return ODTRepository.getInstance().LoadEVT(dirPath, "evt");
	}

	@CustomFunctionResolver("GetPolicyParamsCustomFunctionResolver0")
	public static Tuple GetPolicyParams(String policy) {
		PolicyParser policyParser = PolicyRepository.getInstance().mPolicyMap.get(policy);
		return (Tuple)policyParser.toSave();
	}
	
	public static CompleteDataType GetPolicyParamsCustomFunctionResolver0(CompleteDataType policy) {
		return CompleteDataType.forTuple(PolicyParser.saveSchema);
	}

	@CustomFunctionResolver("AssignPolicyParamsCustomFunctionResolver0")
	public static boolean AssignPolicyParams(String policy, Tuple tuple) {
		PolicyParser policyParser = PolicyRepository.getInstance().mPolicyMap.get(policy);
		policyParser.fromSave(tuple);
		return true;
	}
	
	public static CompleteDataType AssignPolicyParamsCustomFunctionResolver0(CompleteDataType policy, CompleteDataType tuple) {
		return CompleteDataType.forBoolean();
	}

	@CustomFunctionResolver("GetODTParamsCustomFunctionResolver0")
	public static Tuple GetODTParams(long vehicleKeyID) {
		ODTParser odtParser = ODTRepository.getInstance().mODTMap.get(String.valueOf(vehicleKeyID));
		return (Tuple)odtParser.toSave();
	}
	
	public static CompleteDataType GetODTParamsCustomFunctionResolver0(CompleteDataType vehicleKeyID) {
		return CompleteDataType.forTuple(ODTParser.saveSchema);
	}

	@CustomFunctionResolver("AssignODTParamsCustomFunctionResolver0")
	public static boolean AssignODTParams(long vehicleKeyID, Tuple tuple) {
		ODTParser odtParser = ODTRepository.getInstance().mODTMap.get(String.valueOf(vehicleKeyID));
		odtParser.fromSave(tuple);
		return true;
	}
	
	public static CompleteDataType AssignODTParamsCustomFunctionResolver0(CompleteDataType vehicleKeyID, CompleteDataType tuple) {
		return CompleteDataType.forBoolean();
	}
	
	@CustomFunctionResolver("GetMatchedSignalCustomFunctionResolver0")
	public static List<Tuple> GetMatchedSignal(Tuple message, List<Tuple> dbcTuples) {
		try {
			double deltaTime = message.getDouble(RawDataField.DeltaTime.getIndex());
			String dataField = message.getString(RawDataField.DATA.getIndex()); 
			if(dataField == null || dataField.isEmpty()) return null;
			byte[] rawdata = Base64.decode(dataField);
			if(rawdata == null || rawdata.length == 0) return null;
			return dbcTuples.stream()
				.map(dbc -> {
					try {
						return new Pair<String, Double>(dbc.getString("sig_name"),
								TriggerParser.GetRawValue(rawdata, 
									dbc.getString("sig_byte_order").startsWith("little")? "Little" :"Big", 
									(dbc.getString("sig_is_signed").equalsIgnoreCase("True")? "signed": "unsigned"), 
									dbc.getInt("sig_start"), 
									dbc.getInt("sig_length"), 
									dbc.getDouble("sig_scale"), 
									dbc.getDouble("sig_offset")));
					} catch (Exception e) {
						return null;
					}
				})
				.filter(p -> p != null)
				.map(p -> {
					try {
						Tuple tuple = PolicyRepository.trigDataSchema.createTuple();
						tuple.setDouble(0, 0.0);
						tuple.setDouble(1, 0.0);
						tuple.setDouble(2, (double)deltaTime);
						tuple.setString(3, p.first); //event
						tuple.setString(4, ""); //category
						tuple.setString(5, ""); //status
						tuple.setString(6, String.format("%.3f",p.second)); //value
						return tuple;
					}catch(Exception e) {
						return null;
					}
				})
				.collect(Collectors.toList());
		}catch(Exception e) {
			return null;
		}
	}
	
	public static CompleteDataType GetMatchedSignalCustomFunctionResolver0(CompleteDataType message, CompleteDataType dbcTuples) {
		return CompleteDataType.forList(CompleteDataType.forTuple(PolicyRepository.trigDataSchema));
	}
	
	public static Schema fieldStringSchema = new Schema(
			null,
			new Schema.Field("fieldName", CompleteDataType.forString()),
			new Schema.Field("fieldValue", CompleteDataType.forString())
	);

	@CustomFunctionResolver("AddToFieldListCustomFunctionResolver0")
	public static List<Tuple> AddToFieldList(List<Tuple> fieldList, String fieldName, String fieldValue) {
		try {
			Tuple tuple = fieldStringSchema.createTuple();
			tuple.setString(0, fieldName);
			tuple.setString(1, fieldValue);
			if(fieldList == null || fieldList.isEmpty()) {
				ArrayList<Tuple> fList = new ArrayList<>();
				fList.add(tuple);
				return fList;
			}else {
				fieldList.removeIf(f -> {
					try {
						return fieldName.equals(f.getString(0));
					} catch (Exception e) {
						return false;
					}
				});
				fieldList.add(tuple);
				return fieldList;
			}
		}catch(Exception e) {
			return null;
		}
	}
	
	public static CompleteDataType AddToFieldListCustomFunctionResolver0(CompleteDataType fieldList, CompleteDataType fieldName, CompleteDataType fieldValue) {
		return CompleteDataType.forList(CompleteDataType.forTuple(fieldStringSchema));
	}

	@CustomFunctionResolver("GetValueInFieldListCustomFunctionResolver0")
	public static String GetValueInFieldList(List<Tuple> fieldList, String fieldName) {
		try {
			if(fieldList == null || fieldList.isEmpty()) {
				return "";
			}else {
				return fieldList.stream().filter(f -> {
					try {
						return fieldName.equals(f.getString(0));
					} catch (Exception e) {
						return false;
					}
				}).map(f -> {
					try {
						return f.getString(1);
					} catch (Exception e) {
						return "";
					}
				}).findFirst().orElse("");
			}
		}catch(Exception e) {
			return "";
		}
	}

	public static CompleteDataType GetValueInFieldListCustomFunctionResolver0(CompleteDataType fieldList, CompleteDataType fieldName) {
		return CompleteDataType.forString();
	}
}
