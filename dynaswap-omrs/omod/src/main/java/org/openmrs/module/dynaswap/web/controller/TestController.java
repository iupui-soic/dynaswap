package org.openmrs.module.dynaswap.web.controller;

import java.io.IOException;
// import java.net.http.HttpHeaders;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;

import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;

import org.codehaus.jackson.JsonGenerationException;
import org.codehaus.jackson.JsonProcessingException;
import org.codehaus.jackson.map.JsonMappingException;
import org.codehaus.jackson.map.ObjectMapper;
import org.openmrs.module.dynaswap.atallah.CryptDAG;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.ModelAndView;

@Controller
@RequestMapping(value = "module/dynaswap")
public class TestController {
	
	@RequestMapping(value = "/testing", method = RequestMethod.GET)
	@ResponseBody
	public String getTesting() {
		return "TESTING";
	}
	
	@RequestMapping(value = "/dag.json", method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON_VALUE)
	@ResponseBody
	public ResponseEntity<String> getDag() throws IOException, JsonGenerationException, JsonMappingException {
		CryptDAG dag = new CryptDAG();
		try {
			HashMap<String, HashMap<String, ArrayList<String>>> roleDataMapping = dag.getRoleDataMapFromTxtFile();
			dag.setupRolePrivMapFromRoleDataMap(roleDataMapping);
			dag.createGraph();
		}
		catch (Exception e) {
			System.out.println(e.getStackTrace());
		}
		final HttpHeaders httpHeaders = new HttpHeaders();
		httpHeaders.setContentType(MediaType.APPLICATION_JSON);
		return new ResponseEntity<String>(dag.getFormattedGraph(), httpHeaders, HttpStatus.OK);
	}
	
	@RequestMapping(value = "/test", method = RequestMethod.GET)
	public ModelAndView getTest() {
		ModelAndView modelAndView = new ModelAndView("module/dynaswap/test");
		return modelAndView;
	}
	
}
