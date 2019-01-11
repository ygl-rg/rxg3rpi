#encoding: utf-8

#initialize the system

import sqlite3
import rg_lib
import node_models


def SetPassword(connid):
    new_pwd = "root"
    connid.execute("insert into rxg_sys_cfg(key,val) values(?,?)", ("pwd", new_pwd))
    return new_pwd


def SetPagekitePath(connid):
    pk_path = "/home/pi/pagekite.py"
    connid.execute("insert into rxg_sys_cfg(key,val) values(?,?)", ("pagekite_path", pk_path))


def main(db_path):
    with rg_lib.DbConnWrap(sqlite3.connect(db_path, check_same_thread=False)) as conn:
        conn.conn_obj.execute("PRAGMA journal_mode=WAL")
        conn.conn_obj.execute("PRAGMA synchronous=1")
    with rg_lib.DbConnWrap(sqlite3.connect(db_path, check_same_thread=False)) as conn:
        conn.conn_obj.execute("drop table if exists rxg_sys_cfg")
        conn.conn_obj.execute(rg_lib.Sqlite.CreateTable(node_models.SysCfg.TBL, node_models.SysCfg.TBL_FIELDS))
        SetPagekitePath(conn.conn_obj)
        new_pwd = SetPassword(conn.conn_obj)
        print('password is {0}'.format(new_pwd))


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("need db")
    else:
        db_path = sys.argv[1]
        main(db_path)


