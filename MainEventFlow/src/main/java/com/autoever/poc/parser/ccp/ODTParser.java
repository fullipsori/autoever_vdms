package com.autoever.poc.parser.ccp;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiConsumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.xml.parsers.DocumentBuilder;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import com.autoever.poc.parser.DataSavable;
import com.autoever.poc.parser.Parseable;
import com.streambase.sb.CompleteDataType;
import com.streambase.sb.Schema;
import com.streambase.sb.Tuple;
import com.streambase.sb.util.Pair;


public class ODTParser implements Parseable, DataSavable {
	
	private String filename;
	private Path filePath;
	private Element rootNode;
	
	private int rootCount = 0;
	public List<Pair<Double, Tuple>> prevTuples= new ArrayList<>();
	
	private List<Pair<String,String>> measurement_list;
	public List<Object[]> odt_map = new ArrayList<>();
	public int ccpRawEndCmd = 0x36;  // genODT 에서 다시 계산된다.
	
	public ODTParser(Path filePath, DocumentBuilder documentBuilder) {
		this.filePath = filePath;
		this.filename = this.filePath.getFileName().toString().substring(0, this.filePath.getFileName().toString().lastIndexOf('.'));
		try {
			Document document = documentBuilder.parse(filePath.toFile());
			rootNode = document.getDocumentElement();
		} catch (Exception e) {
			rootNode = null;
		}
		parse();
	}
	
	public String GetFilename() {
		return filename;
	}
	
	public boolean InitParams(int rootCount) {

		if(this.rootCount != rootCount) { 
			initData(rootCount);
			return true;
		}
		return true;
	}
	
	public Tuple getMatchedTupleByInterval(Tuple dataTuple, double realTime, double minInterval, double maxInterval) {
		//1. removed over maxInterval
		double removeTime = realTime - maxInterval;
		double searchTime = realTime - minInterval;
		prevTuples.removeIf(p -> p.first <= removeTime);
		//2. search matched tuple
		Tuple matched = prevTuples.stream().filter(p -> p.first <= searchTime).findFirst().map(Pair::getSecond).orElse(null);
		//3. add current tuple at first index.
		if(prevTuples.isEmpty() || prevTuples.get(0).first != realTime) {
			prevTuples.add(0, new Pair<Double, Tuple>(realTime, dataTuple));
		}
		return matched;
	}
	
	public List<Long> getCellDiff(List<Tuple> curCells, List<Tuple> prevCells) {
		if(prevCells == null) return null;
		return IntStream.range(0, curCells.size()).mapToObj(d -> {
			try {
				long prev = prevCells.get(d).getLong(1);
				long cur = curCells.get(d).getLong(1);
				return prev-cur;
			} catch (Exception e) {
				return (long)0;
			}
		}).collect(Collectors.toList());
	}


	@Override
	public void parse() {
		if(rootNode == null) return;
		try {
			measurement_list = GetElement.apply(rootNode.getChildNodes(), "ChannelSetting")
					.flatMap(el -> GetElement.apply(el.getChildNodes(), "Channel"))
					.flatMap(el -> GetElement.apply(el.getChildNodes(), "Protocols"))
					.flatMap(el -> GetElement.apply(el.getChildNodes(), "CCP"))
					.map(el -> GetElements.apply(el.getChildNodes(), "Measurement"))
					.orElse(Collections.emptyList()).stream()
					.map(el -> new Pair<String,String>(
						GetElement.apply(el.getChildNodes(), "identName").get().getTextContent(),
						GetElement.apply(el.getChildNodes(), "Datatype").get().getTextContent()
						)
					).collect(Collectors.toList());
			genODT(measurement_list);
		} catch(Exception e) { }
	}
	
	
	final Set<String> longStrSet = Set.of("SLONG", "ULONG");
	final Set<String> wordStrSet = Set.of("SWORD", "UWORD");
	final String byteStr = "UBYTE";
	final String byteInit = "BBBBBBBB";

	@SuppressWarnings("unchecked")
	final BiConsumer<Pair<?,?>, String> alignODT = (el, type) ->  {
		int needCount = ("L".equals(type))? 4 : ("H".equals(type))? 2 : 1;
		odt_map.stream().filter(d -> ((Integer)d[1]) >= needCount).findFirst().ifPresent(a -> {
			((ArrayList<String>)a[0]).add((String)el.getFirst());
			a[1] = (Integer)a[1] - needCount;
			a[2] = ((String)a[2]).concat(type);
		});
	};
	
	public void genODT(List<Pair<String,String>> dataList) {
		odt_map.clear();
		
		int max_odt = 50;
		IntStream.range(0, max_odt)
			.forEach(i -> odt_map.add(new Object[]{new ArrayList<String>(), 7, new String("")}));
		
		Map<String, List<Pair<?,?>>> groups = dataList.stream()
			.collect(Collectors.groupingBy(pair -> {
				if(longStrSet.contains(pair.getSecond())) return "L";
				else if(wordStrSet.contains(pair.getSecond())) return "H";
				else return "B";
			}));
				
		Optional.ofNullable(groups.get("L")).ifPresent(g -> {
			g.stream().forEach(el -> alignODT.accept(el, "L"));
		});
		Optional.ofNullable(groups.get("H")).ifPresent(g -> {
			g.stream().forEach(el -> alignODT.accept(el, "H"));
		});
		Optional.ofNullable(groups.get("B")).ifPresent(g -> {
			g.stream().forEach(el -> alignODT.accept(el, "B"));
		});

		// finalize
		odt_map.stream()
			.filter(el -> ((Integer)el[1]) >= 1)
			.forEach(el -> {
				el[2] = ((String)el[2]).concat(byteInit.substring(0, ((Integer)el[1])));
			});

		// last Element Index (start: 0x0a + (first_7 -1) -1)
		ccpRawEndCmd = CCPPreProcessor.ccpStartCmd - 1 +  IntStream.range(0, odt_map.size()).filter(d -> ((Integer)((Object[])odt_map.get(d))[1]) == 7).findFirst().orElse(odt_map.size());
		if(ccpRawEndCmd > CCPPreProcessor.ccpEndCmd) ccpRawEndCmd = CCPPreProcessor.ccpEndCmd;
	}
	
	private static Schema prevTupleSchema = new Schema("", List.of(
			new Schema.Field("realTime", CompleteDataType.forDouble()),
			new Schema.Field("rawParsed", CompleteDataType.forTuple(CCPPreProcessor.RawParsed))));

	public static Schema saveSchema = new Schema("", List.of(
			new Schema.Field("params", CompleteDataType.forString()),
			new Schema.Field("prevTuples", CompleteDataType.forList(CompleteDataType.forTuple(prevTupleSchema)))
	));

	@Override
	public void initData(int param) {
		this.rootCount = param;
		prevTuples.clear();
	}

	@Override
	public Object toSave() {
		try {
			String params = String.format("%d", rootCount);
			List<Tuple> prevs = prevTuples.stream().map(pair -> {
					try {
						Tuple dTuple = prevTupleSchema.createTuple();
						dTuple.setDouble(0, pair.first);
						dTuple.setTuple(1, pair.second);
						return dTuple;
					}catch(Exception e) {
						return null;
					}
				}).filter(t -> t != null).collect(Collectors.toList());
			
			Tuple saveTuple = saveSchema.createTuple();
			saveTuple.setString(0, params);
			saveTuple.setList(1, prevs);

			return saveTuple;
		}catch(Exception e) {
			e.printStackTrace();
			return null;
		}
	}

	@SuppressWarnings("unchecked")
	@Override
	public void fromSave(Object saved) {
		try {
			if(saved == null) return;
			String params = ((Tuple)saved).getString(0);
			List<Tuple> prevs = (List<Tuple>)((Tuple)saved).getList(1);
			this.rootCount = Integer.parseInt(params);
			this.prevTuples = prevs.stream().map(prev -> {
					try {
						return new Pair<Double, Tuple>(prev.getDouble(0), prev.getTuple(1));
					}catch(Exception e) {
						return null;
					}
				}).filter(pair -> pair != null).collect(Collectors.toList());

		}catch(Exception e) {
			e.printStackTrace();
		}
	}

	@Override
	public Schema getSaveSchema() {
		return saveSchema;
	}
}
