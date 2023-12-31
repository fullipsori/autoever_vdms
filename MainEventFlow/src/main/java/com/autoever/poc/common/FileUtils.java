package com.autoever.poc.common;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import com.streambase.sb.CompleteDataType;
import com.streambase.sb.client.CustomFunctionResolver;

/**
* Generated by JDT StreamBase Client Templates (Version: 11.0.0).
*
* All custom java simple functions must live in a public Java class as a public static method.
* Custom Java simple functions can be accessed by the simple form of calljava in any expression
* except in aggregate functions.
* They may also be aliased for use as if that function were embedded
* in your StreamBase Application.
* <p>
* For in-depth information on implementing a StreamBase simple function, please see some
* related topics from "Developing StreamBase Custom Functions" in the StreamBase 
* documentation.
* <p>
*/
public class FileUtils {

	/**
	* A StreamBase Simple Function. Use this function
	* in StreamBase expressions using the <em>calljava</em> function, or 
	* by an assigned alias. It can then be called directly 
	* using the alias name instead of using calljava().
	*/
	@CustomFunctionResolver("GetFilesInPathCustomFunctionResolver0")
	public static List<?> GetFilesInPath(String dirPath, String ext){
		try {
			List<String> files = Files.list(Paths.get(dirPath)).sorted()
					.filter(file -> file.toString().endsWith(ext))
					.map(file-> file.toAbsolutePath().toString()).collect(Collectors.toList());
			return files;
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

	public static CompleteDataType GetFilesInPathCustomFunctionResolver0(CompleteDataType dirPath, CompleteDataType ext) {
		return CompleteDataType.forList(CompleteDataType.forString());
	}
	
	@CustomFunctionResolver("GetFilenameListInPathCustomFunctionResolver0")
	public static List<String> GetFilenameListInPath(String dirPath, String ext) {
		try {
			return Files.list(Paths.get(dirPath)).sorted()
					.filter(file -> file.toString().endsWith(ext))
					.map(file -> file.getFileName().toString())
					.map(filename -> filename.substring(0, filename.lastIndexOf('.')))
					.collect(Collectors.toList());
		} catch (IOException e) {
			return null;
		}
	}

	public static CompleteDataType GetFilenameListInPathCustomFunctionResolver0(CompleteDataType dirPath, CompleteDataType ext) {
		return CompleteDataType.forList(CompleteDataType.forString());
	}
	

	public static void main(String[] args) {
	}
}
