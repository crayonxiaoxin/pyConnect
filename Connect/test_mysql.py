# -*- coding = utf-8 -*-
# @Time: 2022/3/28 2:12 PM
# @Author: crayonxiaoxin
# @File: test_mysql.py
# @Software: PyCharm
import pymysql

mysql = pymysql.connect(host="localhost", user="root", password="@ne2Nine",
                        database="wordpress", charset="utf8mb4")
mysql.ping()
cursor = mysql.cursor()
# sql = "create table if not exists baidu(`id` int not null auto_increment,`name` varchar(30) not null,primary key(`id`))"
sql = "select * from baidu"
cursor.execute(sql)
result = cursor.fetchall()
cursor.close()
mysql.close()
print(result)
