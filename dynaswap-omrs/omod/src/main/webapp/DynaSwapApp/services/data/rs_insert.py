import os
import numpy as np
import pickle
import MySQLdb


def get_db_connection_configs(file_name):
    """ retrieve the database connection configurations from the given file """
    try:
        lines = [line.rstrip("\n") for line in open(file_name)]
        conn_str = [line[15:].split(
            "?")[0] for line in lines if line.startswith("connection.url=")][0]
        parts = conn_str.split("\:")
        host = parts[2][2:]
        port = parts[3][:4]
        user = [line[20:]
                for line in lines if line.startswith("connection.username=")][0]
        passwd = [line[20:]
                  for line in lines if line.startswith("connection.password=")][0].replace("\\", "")
        schema = conn_str[conn_str.rfind("/") + 1:]
    except:
        print("ERROR : Unable to retrieve database connection parameters")
        host = port = user = passwd = schema = ""

    return {"host": host, "port": port, "user": user, "passwd": passwd, "schema": schema}


def insert_rs(db_configs, rs_features):
    query1 = "UPDATE openmrs.role " \
             "SET feature = %s " \
             "WHERE role = %s"
    query2 = "UPDATE openmrs.role " \
             "SET url = %s " \
             "WHERE role = %s"

    conn = MySQLdb.connect(host=db_configs["host"], user=db_configs["user"],
                           password=db_configs["passwd"], db=db_configs["schema"], port=int(db_configs["port"]))
    cur = conn.cursor()

    cur.execute("SELECT role FROM openmrs.role")
    result_set = cur.fetchall()

    for i, role in enumerate(result_set):
        print(role)
        role_n = role[0]
        role_n = role_n.replace(":", "").replace(" ", "")

        rs_feat = rs_features[rs_features[:, -1] == role_n][0]
        rs_feat_binary = pickle.dumps(
            rs_feat, protocol=pickle.HIGHEST_PROTOCOL)

        args = (rs_feat_binary, role[0])
        cur.execute(query1, args)
        conn.commit()

        args = ("/images/" + role_n + ".jpg", role[0])
        cur.execute(query2, args)
        conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    db_configs = get_db_connection_configs(os.path.join(
        "/var", "lib", "OpenMRS", "openmrs-runtime.properties"))
    rs_features = np.load(os.path.join(os.path.abspath(""), "rs_features.npz"), allow_pickle=True)["arr_0"]
    insert_rs(db_configs, rs_features)
