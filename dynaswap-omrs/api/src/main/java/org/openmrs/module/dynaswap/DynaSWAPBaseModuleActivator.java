/**
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at http://mozilla.org/MPL/2.0/. OpenMRS is also distributed under
 * the terms of the Healthcare Disclaimer located at http://openmrs.org/license.
 *
 * Copyright (C) OpenMRS Inc. OpenMRS is a registered trademark and the OpenMRS
 * graphic logo is a trademark of OpenMRS Inc.
 */
package org.openmrs.module.dynaswap;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.openmrs.module.BaseModuleActivator;
import java.io.IOException;

/**
 * This class contains the logic that is run every time this module is either started or shutdown
 */
public class DynaSWAPBaseModuleActivator extends BaseModuleActivator {
	
	private Log log = LogFactory.getLog(this.getClass());
	
	/**
	 * @see #started()
	 */
	public void started() {
		log.info("Started DynaSWAP.BaseModule");
		Runtime rt = Runtime.getRuntime();
		try {
			rt.exec("python3 dynaswap_activator.py");
			rt.exec("python3 /var/lib/tomcat7/webapps/openmrs/WEB-INF/view/module/dynaswap/manage.py runserver 0.0.0.0:8000");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * @see #shutdown()
	 */
	public void shutdown() {
		log.info("Shutdown DynaSWAP.BaseModule");
	}
	
}
