import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('drop table card')
conn.commit()
# cur.execute('create table card(id int,number varchar(16), pin varchar(16), balance int default 0)')
# cur.execute('insert into card (id, number, pin) values (1, "1111111111111111", "0000")')

# a = cur.execute('select number from card where number = "4000008785980082"')
# for i in a:
#     print(i)




