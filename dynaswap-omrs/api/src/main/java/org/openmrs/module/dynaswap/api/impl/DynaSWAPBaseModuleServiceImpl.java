/**
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at http://mozilla.org/MPL/2.0/. OpenMRS is also distributed under
 * the terms of the Healthcare Disclaimer located at http://openmrs.org/license.
 *
 * Copyright (C) OpenMRS Inc. OpenMRS is a registered trademark and the OpenMRS
 * graphic logo is a trademark of OpenMRS Inc.
 */
package org.openmrs.module.dynaswap.api.impl;

import org.openmrs.api.APIException;
import org.openmrs.api.UserService;
import org.openmrs.api.impl.BaseOpenmrsService;
import org.openmrs.module.dynaswap.Item;
import org.openmrs.module.dynaswap.api.DynaSWAPBaseModuleService;
import org.openmrs.module.dynaswap.api.dao.DynaSWAPBaseModuleDao;
import org.openmrs.module.dynaswap.atallah.CryptNode;

public class DynaSWAPBaseModuleServiceImpl extends BaseOpenmrsService implements DynaSWAPBaseModuleService {
	
	DynaSWAPBaseModuleDao dao;
	
	UserService userService;
	
	/**
	 * Injected in moduleApplicationContext.xml
	 */
	public void setDao(DynaSWAPBaseModuleDao dao) {
		this.dao = dao;
	}
	
	/**
	 * Injected in moduleApplicationContext.xml
	 */
	public void setUserService(UserService userService) {
		this.userService = userService;
	}
	
	@Override
	public Item getItemByUuid(String uuid) throws APIException {
		return dao.getItemByUuid(uuid);
	}
	
	@Override
	public Item saveItem(Item item) throws APIException {
		if (item.getOwner() == null) {
			item.setOwner(userService.getUser(1));
		}
		
		return dao.saveItem(item);
	}
	
	@Override
	public CryptNode saveCryptNode(CryptNode node) throws APIException {
		return dao.saveCryptNode(node);
	}
	
	@Override
	public int deleteAllCryptNodeEdgeData() throws APIException {
		return dao.deleteAllCryptNodeEdgeData();
	}
	
}
