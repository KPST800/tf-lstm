# -*- coding: utf-8 -*-
import pymysql as pql


class DB_TEST:
    # DB 접속
    def __init__(self, host, target_db, user='root', passwd='root', charset='utf8', port=3306):
        try:
            self.DB = pql.connect(host=host, port=port, user=user, passwd=passwd, db=target_db, charset=charset)
            self.cursor = self.DB.cursor()
        except Exception as e:
            print(e)

    # DB 접속 종료
    def __del__(self):
        if self.DB:
            self.DB.close()

    # DB 접속 종료
    def close(self):
        if self.DB:
            self.DB.close()
            self.DB = None

    # 쿼리 실행
    def execute(self, query, args=None):
        try:
            return self.cursor.execute(query, args)
        except Exception as e:
            return e

    # 쿼리 실행
    def executemany(self, query, args=None):
        try:
            return self.cursor.executemany(query, args)
        except Exception as e:
            return e

    # 커밋
    def commit(self):
        try:
            self.DB.commit()
        except Exception as e:
            return e

    # 결과 한개 받아오기
    def fetchone(self):
        return self.cursor.fetchone()[0]

    # 결과 전부 받아오기
    def fetchall(self):
        return self.cursor.fetchall()
