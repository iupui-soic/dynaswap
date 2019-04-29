import os
import numpy as np
import pickle
import MySQLdb


def get_db_connection_configs(file_name):
    ''' Retrieve the database connection configurations from the given file '''
    try:
        lines = [line.rstrip('\n') for line in open(file_name)]
        conn_str = [line[15:].split('?')[0] for line in lines if line.startswith('connection.url=')][0]
        parts = conn_str.split('\:')
        host = parts[2][2:]
        port = parts[3][:4]
        user = [line[20:] for line in lines if line.startswith('connection.username=')][0]
        passwd = [line[20:] for line in lines if line.startswith('connection.password=')][0]
        schema = conn_str[conn_str.rfind('/') + 1:]
    except:
        print('ERROR : Unable to retrieve database connection parameters')
        host = port = user = passwd = schema = ''

    return {'host': host, 'port': port, 'user': user, 'passwd': passwd, 'schema': schema}


def rs_startup():
    ''' Inserting image paths and facial features into OpenMRS roles table '''
    query1 = "UPDATE openmrs.role " \
             "SET feature = %s " \
             "WHERE role = %s"
    query2 = "UPDATE openmrs.role " \
             "SET url = %s " \
             "WHERE role = %s"

    rs = np.load('rs_feat.npz')['arr_0']

    configs = get_db_connection_configs('/var/lib/OpenMRS/openmrs-runtime.properties')
    conn = MySQLdb.connect(configs['host'], configs['user'], configs['passwd'], configs['schema'])
    cur = conn.cursor()
    cur.execute("SELECT role FROM openmrs.role")
    result_set = cur.fetchall()

    for role in result_set:
        print(role)
        role_n = role[0]
        role_n = role_n.replace(' ', '')
        role_n = role_n.replace(':', '')
        rs_ids = rs[:, -1]
        idx = np.where(rs_ids == role_n)
        rs_feat = rs[idx, :]
        rs_feat_binary = pickle.dumps(rs_feat, protocol=pickle.HIGHEST_PROTOCOL)
        args = (rs_feat_binary, role[0])
        cur.execute(query1, args)
        conn.commit()
        args = ('/images/' + role_n + '.jpg', role[0])
        cur.execute(query2, args)
        conn.commit()

    cur.close()
    conn.close()
