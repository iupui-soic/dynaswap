/**
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0 + Health disclaimer. If a copy of the MPL was not distributed with
 * this file, You can obtain one at http://license.openmrs.org
 */
package org.openmrs.module.dynaswap.filter;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.openmrs.Patient;
import org.openmrs.PatientIdentifier;
import org.openmrs.api.context.Context;

/**
 * @author sunbiz
 */
public class BioCapsuleAuthFilter implements Filter {
	
	@Override
	public void init(FilterConfig fc) throws ServletException {
		
	}
	
	@Override
	public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
		HttpServletRequest request = (HttpServletRequest) req;
		String requestURI = request.getRequestURI();
		Boolean showBioCapsule = Boolean.valueOf(Context.getAdministrationService().getGlobalProperty(
		    "dynaswap.showBioCapsule"));
		if (showBioCapsule) {
			PrintWriter out = res.getWriter();
			CharResponseWrapper responseWrapper = new CharResponseWrapper((HttpServletResponse) res);
			chain.doFilter(request, responseWrapper);
			StringBuilder servletResponse = new StringBuilder(responseWrapper.toString());
			int indexOf = servletResponse.indexOf("<fieldset>");
			servletResponse.delete(indexOf, servletResponse.indexOf("</fieldset>") + 11);
			String bioCapsuleIFrame = "<iframe id=\"bioCapsuleIFrame\" width=\"100%\" height=\"600px\" src=\"/\"></iframe>";
			String responseText = servletResponse.insert(indexOf, bioCapsuleIFrame).toString();
			out.write(responseText);
		} else {
			chain.doFilter(req, res);
		}
	}
	
	@Override
	public void destroy() {
	}
	
}
