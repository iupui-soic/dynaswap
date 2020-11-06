/**
 * This Source Code Form is subject to the terms of the Mozilla Public License,
 * v. 2.0. If a copy of the MPL was not distributed with this file, You can
 * obtain one at http://mozilla.org/MPL/2.0/. OpenMRS is also distributed under
 * the terms of the Healthcare Disclaimer located at http://openmrs.org/license.
 *
 * Copyright (C) OpenMRS Inc. OpenMRS is a registered trademark and the OpenMRS
 * graphic logo is a trademark of OpenMRS Inc.
 */
package org.openmrs.module.dynaswap.api.dao;

import org.hibernate.criterion.Restrictions;
import org.openmrs.api.db.hibernate.DbSession;
import org.openmrs.api.db.hibernate.DbSessionFactory;
import org.openmrs.module.dynaswap.Item;
import org.openmrs.module.dynaswap.atallah.CryptNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

@Repository("dynaswap.DynaSWAPBaseModuleDao")
public class DynaSWAPBaseModuleDao {
	
	@Autowired
	DbSessionFactory sessionFactory;
	
	private DbSession getSession() {
		return sessionFactory.getCurrentSession();
	}
	
	public Item getItemByUuid(String uuid) {
		return (Item) getSession().createCriteria(Item.class).add(Restrictions.eq("uuid", uuid)).uniqueResult();
	}
	
	public Item saveItem(Item item) {
		getSession().saveOrUpdate(item);
		return item;
	}
	
	public CryptNode saveCryptNode(CryptNode node) {
		getSession().saveOrUpdate(node);
		return node;
	}
	
	public int deleteAllCryptNodeEdgeData() {
		// Total number of rows deleted across the three tables.
		int result = 0;
		String query1 = "delete from cryptnode_cryptedge;";
		String query2 = "delete from cryptnode;";
		String query3 = "delete from cryptedge;";
		result += getSession().createSQLQuery(query1).executeUpdate();
		result += getSession().createSQLQuery(query2).executeUpdate();
		result += getSession().createSQLQuery(query3).executeUpdate();
		return result;
	}
}
