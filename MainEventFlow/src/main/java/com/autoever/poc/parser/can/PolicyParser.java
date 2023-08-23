package com.autoever.poc.parser.can;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.autoever.poc.common.RawDataField;
import com.autoever.poc.parser.DataSavable;
import com.autoever.poc.parser.Parseable;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;

public class PolicyParser implements Parseable, DataSavable {

	private final String filename;
	private final Path xmlFilePath;
	private Element rootNode;

	public String KeyStatus = "ON";
	public TriggerParser KeyTrig;

	private final static EventCallback eventCallback = (a,b,c) -> null;
	
	/* Atomic 변수가 되어야 하는지 체크 필요함. */
	public int rootCount = 0;

	public PolicyParser(Path filePath, DocumentBuilder documentBuilder) {
		this.xmlFilePath = filePath;
		this.filename = this.xmlFilePath.getFileName().toString().substring(0, this.xmlFilePath.getFileName().toString().lastIndexOf('.'));
		try {
			Document document = documentBuilder.parse(xmlFilePath.toFile());
			rootNode = document.getDocumentElement();
		} catch (Exception e) {
			rootNode = null;
		}
		parse();
	}

	public long minPreTime = 0;
				
	public Map<Integer, Map<Integer, List<Evaluable>>> msgFilter;
	public List<Evaluable> evalList;

	public String GetFileName() {
		return this.filename;
	}

	@SuppressWarnings("unchecked")
	@Override
	public void parse() {
		try {
			if(rootNode == null) return;

			NodeList children = rootNode.getChildNodes();
			GetElement.apply(children, "PreCondition").ifPresent(e -> {
				KeyStatus = e.getAttribute("Key");
				GetElement.apply(e.getChildNodes(), "Trigger").ifPresent(ele -> {
					KeyTrig = new TriggerParser(ele, eventCallback);
				});
			});
			

			msgFilter = GetElements.apply(children, "Event").stream()
					.map(EventParser::new)
					.peek(e -> minPreTime = (minPreTime < e.preTime)? e.preTime : minPreTime)
					.flatMap(e -> e.msgTable.stream())
					.map(ta -> (List<Object>)ta)
					.flatMap(ta -> (ta.size() > 3)?
						Stream.of(
							List.of(ta.get(0), ta.get(1), ta.get(2)),  //(ch,id,parseCAN)
							List.of(ta.get(0), ta.get(3), ta.get(2)))  //(ch,tpdtID, parseDM1)
						:
						Stream.of( List.of(ta.get(0), ta.get(1), ta.get(2)))
					)
					.filter(el -> el.get(1) != null)
					.collect(Collectors.groupingBy(el -> (int)el.get(0), 
								Collectors.groupingBy(el->(int)el.get(1), 
									Collectors.mapping(el -> (Evaluable)el.get(2), Collectors.toList())  )));

			evalList = msgFilter.values().stream()
					.map(e -> (Map<Integer, List<Evaluable>>)e)
					.flatMap(e -> e.values().stream())
					.filter(o -> o != null)
					.map(o -> (List<Evaluable>)o)
					.flatMap(o -> o.stream())
					.filter(ev -> ev != null)
					.collect(Collectors.toList());

		} catch (Exception e) {
			System.out.println("Parse Exception:" + "filename:" + this.filename +  e.getMessage());
		};
	}

	//[DataChannel, DeltaTime, MSGInfo, DataID, DLC, data[10:10 + dlc_Size[DLC]]]
	public boolean GetKeyFlag(Tuple message) {
		try {
			int dataChannel = message.getInt(RawDataField.DataChannel.getIndex());
			int dataID = message.getInt(RawDataField.DataID.getIndex());
			if((dataID & 0x00FFFFFF) == KeyTrig.id && dataChannel == KeyTrig.ch) {
				KeyTrig.callback.Evaluate(message);
			}
			
			if(!"ON".equalsIgnoreCase(KeyStatus) || KeyTrig.status) {
				return true;
			}else {
				return false;
			}
		} catch (Exception e) {
			System.out.println("GetKeyFlag Exception:" + e.getMessage());
			return false;
		}
	}
	
	
	@SuppressWarnings("unchecked")
	public List<Tuple> GetTrigData(Tuple message) {

		try {
			int dataChannel = message.getInt(RawDataField.DataChannel.getIndex());
			double deltaTime = message.getDouble(RawDataField.DeltaTime.getIndex());
			int dataID = message.getInt(RawDataField.DataID.getIndex());

			if(!msgFilter.containsKey(dataChannel)) return null;

			List<Evaluable> callbacks = (List<Evaluable>)((Map<Integer, List<Evaluable>>)msgFilter.get(dataChannel)).get(dataID & 0x00FFFFFF);
			if(callbacks != null) {
				// [name, String.valueOf(preTime), String.valueOf(postTime), category, "OnFalse", value]
				// name, String.valueOf(preTime), String.valueOf(postTime), category, "NOT or RET or status", value
				return callbacks.stream()
					.map(c -> (List<String>)c.Evaluate(message))
					.filter(e -> e != null)
					.collect(Collectors.toMap(e-> e.get(0), e->e, (existVal, newVal) -> newVal))
					.values().stream()
					.filter(e -> e != null)
					.map(e -> {
						try {
							Tuple tuple = PolicyRepository.trigDataSchema.createTuple();
							tuple.setDouble(0, (double)(deltaTime-Double.parseDouble(e.get(1))));
							tuple.setDouble(1, (double)(deltaTime+Double.parseDouble(e.get(2))));
							tuple.setDouble(2, (double)deltaTime);
							tuple.setString(3, e.get(0));
							tuple.setString(4, e.get(3));
							tuple.setString(5, e.get(4));
							tuple.setString(6, e.get(5));
							return tuple;
						}catch (Exception x){
							System.out.println("PolicyParser Tuple Gen Excep:" + x.getMessage());
							return null;
						}
					})
					.filter(t -> t != null)
					.collect(Collectors.toList());
			}

			return null;
		}catch (Exception e) {
			System.out.println("GetTrigData Exception:" + e.getMessage());
			return null;
		}
	}
	
	/**
	 * InitParams 는 CanPreProcessor 에서 호출된다. 
	 * this.rootCount 는 prevData 로 부터 초기화가 먼저 이뤄지고 현재 들어온 kafka 메세지의 rootCount 를 비교해서 초기화가 필요한 경우 진행된다.
	 * @param rootCount
	 * @return
	 */
	public boolean InitParams(int rootCount) { //check kafka.RootCount(trip number)

		if(this.rootCount != rootCount) { 
			initData(rootCount);
			return true;
		}
		return true;
	}
	
	/**
	 * KeyTrig 를 체크 않하거나, 체크하는 경우 id/ch 가 있는 경우에만 메세지를 배출한다.
	 */
	public boolean IsAvailable(int ch, int id) {
		try {
			int dataChannel = ch;
			int dataID = id & 0x00FFFFFF;
			if(!"ON".equals(KeyStatus) || (dataID == KeyTrig.id && dataChannel == KeyTrig.ch)) {
				return true;
			}
			/* KeyTrig.status 가 True 로 평가된 이후에는 dataID Key 가 존재하는 경우에는 모두 유효한 값으로 된다. */
			return Optional.ofNullable((Map<Integer,List<Evaluable>>)msgFilter.get(dataChannel)).map(m -> m.containsKey(dataID)).orElse(false);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		}
	}

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		// new PolicyParser("d:/projects/vdms/resources/policy/BM-15C-0003.xml").parse();
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder documentBuilder;
		try {
			documentBuilder = factory.newDocumentBuilder();
			
			Path policyPath = Paths.get("d:/projects/vdms/resources/policy/BM-16L-0030.xml");
			PolicyParser policyParser =  new PolicyParser(policyPath, documentBuilder);
			System.out.println("result:" + policyParser.msgFilter.size());
			policyParser.InitParams(0);
			
		}catch(Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * rootCount 단위로 파라미터를 저장하여 동작에 연속성을 주기 위한 목적으로, 해당 파라미터들은 QueryTable에 저장한다.
	 */
	public static Schema saveSchema = new Schema("", List.of(new Schema.Field("params", CompleteDataType.forString())));

	@Override
	public void initData(int param) {
		// TODO Auto-generated method stub
		rootCount = param;
		KeyTrig.initData(param);
		evalList.stream().map(e -> (DataSavable)e).forEach(eval -> eval.initData(param));
	}

	@Override
	public Object toSave() {
		// TODO Auto-generated method stub
		try {
			String params = String.format("%d;%s;%s", rootCount, KeyTrig.toSave(), 
					evalList.stream().map(e -> e.trigger).map(DataSavable::toSave).map(o -> (String)o).collect(Collectors.joining(":"))  );
			Tuple saveTuple = saveSchema.createTuple();
			saveTuple.setString(0, params);
			return saveTuple;
		}catch(Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	@Override
	public void fromSave(Object saved) {
		// TODO Auto-generated method stub
		try {
			if(saved == null) return;
			String savedData = ((Tuple)saved).getString(0);
			if(savedData == null || savedData.isEmpty()) return;
			String[] tokens = savedData.split(";", -1);
			rootCount = Integer.parseInt(tokens[0]);
			KeyTrig.fromSave(tokens[1]);
			if(tokens[2] == null) return;
			String[] triggerData = tokens[2].split(":", -1);
			IntStream.range(0, triggerData.length).forEach(d -> evalList.get(d).trigger.fromSave(triggerData[d]));
		}catch(Exception e) {
			e.printStackTrace();
		}
	}

	@Override
	public Schema getSaveSchema() {
		return saveSchema;
	}

}