import sqlite3

# from path_plan.msg import PathResponse


class DB():
    def __init__(self):
        self.__conn = sqlite3.connect(
            "/home/acca/catkin_ws/src/ACCA2022-new/path_plan/path.db")
        self.__cur = self.__conn.cursor()
        self.flag = self.checkDB()

        if self.flag == 0:
            # create table
            self.maketable()

    def maketable(self):
        self.__cur.execute(
            "CREATE TABLE PathPoint(Start_point CHAR, End_point CHAR, path_id CHAR key unique);")
        self.__cur.execute(
            "CREATE TABLE PathInfo(path_id CHAR,idx INT, x FLOAT, y FlOAT, yaw FLOAT);")

    def makepoint(self, start, end, path_id):
        query = "INSERT INTO PathPoint VALUES(?, ?, ?);"
        self.__cur.execute(query, (start, end, path_id))
        self.__conn.commit()

    def savePath(self, path):
        # path = PathResponse()
        self.makepoint(path.start, path.end, path.path_id)
        for i in range(len(path.cx)):
            query = "INSERT INTO PathInfo VALUES(?, ?, ?, ?, ?);"
            self.__cur.execute(
                query, (path.path_id, i, path.cx[i], path.cy[i], path.cyaw[i]))

        self.__conn.commit()

    def checkDB(self):
        query = "SELECT COUNT(*) FROM sqlite_master WHERE Name = '%s' OR Name = '%s';"
        flag = self.__cur.execute(
            query % ('PathPoint', 'PathInfo')).fetchall()[0][0]
        self.__conn.commit()
        return flag

    def check_path_id(self, path_id):
        query = "SELECT COUNT(*) From PathPoint Where path_id = '%s';"
        flag = self.__cur.execute(query % path_id).fetchall()[0][0]
        self.__conn.commit()
        return flag

    def deletePath(self, path_id):
        query_Point = "DELETE FROM PathPoint WHERE path_id = '%s';"
        query_info = "DELETE FROM PathInfo WHERE path_id = '%s';"
        self.__cur.execute(query_Point % path_id)
        self.__cur.execute(query_info % path_id)
        self.__conn.commit()

    def bring_path_id(self, s_point, e_point):
        query = "SELECT path_id From PathPoint Where Start_point = '%s' AND End_point = '%s';"
        path_id = self.__cur.execute(
            query % (s_point, e_point)).fetchall()[0][0]
        self.__conn.commit()
        path_id = str(path_id)
        return path_id

    def bring_pathinfo(self, path_id):
        query = "SELECT x, y, yaw From PathInfo  Where path_id = '%s';"
        pathinfo = self.__cur.execute(query % (path_id)).fetchall()
        return pathinfo