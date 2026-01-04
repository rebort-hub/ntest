# -*- coding: utf-8 -*-

import sys
from contextlib import contextmanager

import pymysql

this = sys.modules[__name__]
if hasattr(this, "env") is False:
    setattr(this, "env", "test")

if env == 'test':
    testDbMysql = {
        "host": "",
        "user": "",
        "password": "",
        "port": "",
        "database": "",
        "charset": "utf8"
    }
elif env == 'dev':
    pass
elif env == 'uat':
    pass


class TestMysql:
    """初始化数据库连接"""

    @contextmanager
    def connect_db(self):
        """ 每次执行前连接 """
        conn = pymysql.connect(**testDbMysql)
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            yield cursor
            conn.commit()
        except:  # 提交异常时需要回滚事件
            conn.rollback()
        finally:  # 关闭连接
            cursor.close()
            conn.close()

    def execute(self, sql):
        """
        @param sql: 执行的sql模板（非查询类sql使用）
        """
        with self.connect_db() as db:
            db.execute(sql)

    def fetchone(self, mysql):
        """ 查询一条数据 """
        data = None
        with self.connect_db() as db:
            db.execute(mysql)
            data = db.fetchone()
        return data

    def fetchall(self, mysql):
        """ 查询所有数据 """
        data = None
        with self.connect_db() as db:
            db.execute(mysql)
            data = db.fetchall()
        return data


database_template = TestMysql()  # 实例化对象，避免操作多个数据库时冲突，实例变量名为脚本名字


def database_template_insert_or_update_user(mobile, password, token, user_id='', company_name='', company_id='',
                                            role=None):
    """ 插入或更新token """
    if database_template_get_info_by_mobile(mobile):  # 如果有就更新
        database_template_update_token(mobile, token, user_id, company_name, company_id)
    else:  # 没有就插入
        database_template_insert_user(mobile, password, token, role, company_id, company_name, user_id)


def database_template_get_info_by_mobile(mobile):
    """ 根据手机号获取用户数据 """
    msql = f"SELECT * FROM auto_test_user WHERE mobile = '{mobile}' and env='{env}';"
    print(msql)
    return database_template.fetchone(msql)


def database_template_update_token(mobile, token, user_id, company_name, company_id):
    """ 更新用户token """
    m_sql = f"UPDATE auto_test_user set u_token='{token}', user_id='{user_id}', company_name='{company_name}', company_id='{company_id}' WHERE mobile='{mobile}' and env='{env}';"
    print(m_sql)
    database_template.execute(m_sql)


def database_template_insert_user(mobile, password, token, role=None, company_id=None, company_name=None, user_id=None):
    """ 插入用户信息 """
    m_sql = f"INSERT INTO `auto_test_user` (`create_time`, `update_time`, `create_user`, `update_user`, `mobile`, `password`, `u_token`, `role`, `company_id`, `company_name`, `user_id`, `comment`, `env`) VALUES (NULL, NULL, NULL, NULL, '{mobile}', '{password}', '{token}', '{role}', '{company_id}', '{company_name}', '{user_id}', NULL, '{env}');"
    print(m_sql)
    database_template.execute(m_sql)


if __name__ == '__main__':
    print(database_template_get_info_by_mobile('15756623400'))
