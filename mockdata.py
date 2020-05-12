import random
from datetime import datetime
import time
from decimal import Decimal
import threading
host = "192.168.1.77"
port = 3306
user = "root"
password = "jsjs=123"
database = "xin_rc"
# host = "127.0.0.1"
# port = 3306
# user = "root"
# password = "123456"
# database = "test"
mesh_width = 0.5
roller_width = 2.3
one_seconds_length = 1.4
# 经度:0.2m = 0.0000023/2=0.00000115   维度: 0.2m 0.0000018/2 = 0.0000009
# deter_length = 2.3/0.2*0.0000023

base_height = 3780
deter_length = int(roller_width/0.2*0.00000115*1e8)  # deter_lon 因为循环遍历的时候步长不能为小数
# deter_length = int(2.17/0.2*0.0000023*1e7)
deter_width = int(one_seconds_length/0.2*0.0000009*1e7)    # deter_lat
# deter_width = int(2.432/0.0000135*1e7)
#  下边这些生成的数据有8890条
#            左上                     右上                   右下            左下
# [[116.402472,39.925186],[117.400000,39.925186],[117.400000,39.923211],[116.402472,39.923211]]

def get_cursor_conn(host=host,port=port,user=user,password=password,database=database):
    """
    连接数据库返回cursor和conn
    :return:
    """
    import pymysql
    pymysql.install_as_MySQLdb()
    conn=pymysql.connect(host=host, port=port, user=user, password=password,database=database,charset="utf8")
    cursor=conn.cursor()
    print('连接成功')
    return cursor,conn
def close_curse_conn(cursor,conn):
    """
    关闭之前打开的cursor，conn
    :param cursor:
    :param conn:
    :return:
    """
    cursor.close()
    conn.close()
    print('成功关闭连接')
    
def get_lon_lat():

    cursor,conn = get_cursor_conn(host,port,user,password,database)
    sql = 'select control_points from xin_daba_unit where uid = "uid001" and rid = "rid001"'
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
# 军机处,景运门,中左门,中右门    190*150
# 116.402481,39.925165   116.404296,39.925255    116.404395,39.923498    116.402589,39.923471

# 经度:0.2m = 0.0000023  维度: 0.2m 0.0000018
# print(calcDistance(116.402481,39.925165,116.402481,39.923471)*1000)
# 0.001694
# 188.0900103304462/0.2 = 940.450051652231
# 0.001694/940.450051652231 = 1.801265252762647e-6 = 1.8+e-6 = 0.0000018
def each_data():
    """
    long current_time = new Date().getTime();
    long gps_time = (long) floor(current_time / 1000) * 1000;
    BigDecimal lon = randomLonLat(102.262271, 102.262960, 22.080568, 22.081568, "Lon");
    BigDecimal lat = randomLonLat(102.262271, 102.262960, 22.080568, 22.081568, "Lat");
    double height = 500 + ((Math.random() *    ) * 100) / 10;
    int quality_index = (int) (1 + Math.random() * (10 - 1 + 1));
    double cmv = ((Math.random() * 9 + 1) * 100) / 10;
    int frequency = (int) ((Math.random() * 9 + 1) * 100);
    int amplitude = (int) ((Math.random() * 9 + 1) * 100);
    float velocity = 0;
    int satellite_number = 2;
    """
    sn = "1000" if random.randint(0,1) else "cs3" # 这个暂时别删了如果删了改动比较多不值
    gpsTime = int(time.time())*1000
    height = base_height + (random.randint(0,20)+80.0)/100
    velocity = 0
    qualityIndex = 4 if random.randint(3,6)>=4 else 3
    satelliteNumber = 0
    cmv = 130+random.randint(-5,5)
    frequency = random.randint(1,40)
    amplitude = random.randint(1,5) if frequency else 0
    frequency = frequency if amplitude else 0
    frequency = frequency+20 if 0 < frequency < 20 else frequency

    return sn,gpsTime,Decimal(height),Decimal(velocity),qualityIndex,\
           satelliteNumber,Decimal(cmv),Decimal(frequency),Decimal(amplitude)
class MyThread(threading.Thread):

    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None
def insert_data(sn1,end_lon,start_lat,start_lon,end_lat):
    cursor,conn = get_cursor_conn()
    # start_lon = int(103.025039 * 1e8)
    # if sn1 == "cs3":
    #     start_lon = int(103.025039*1e8)+deter_length
    for lon in range(start_lon,end_lon,int(2*deter_length)):
        for lat in range(start_lat, end_lat, -deter_width):
            per_data = each_data()
            sql = "insert into xin_daba_gpsdatum(sn,gps_time,longitude,latitude,height,velocity,quality_index,satellite_number,cmv,frequency,amplitude)" \
                  " values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(sn1,str(per_data[1]),str(round(Decimal(lon / (1e8)), 8)),
                                                               str(round(Decimal(lat / (1e7)), 8)),str(round(Decimal(per_data[2]), 3)),
                                                               str(round(Decimal(per_data[3]), 3)),str(per_data[4]),str(per_data[5]),
                                                               str(round(Decimal(per_data[6]), 3)),str(round(Decimal(per_data[7]), 3)),
                                                               str(round(Decimal(per_data[8]), 3)))
            print(sql)
            time.sleep(1)
            try:
                cursor.execute(sql)
                # print('执行一次插入操作')
                conn.commit()
            except Exception as e:
                # print(e)
                # print('插入出现问题')
                pass
        print("循环一轮了")
    close_curse_conn(cursor,conn)


if __name__ == '__main__':
    # end_lon = int(str(int(float(lon[-1]) * 1e6))+'00')
    # start_lon = int(str(int(float(lon[0]) * 1e6))+'00')
    # start_lat = int(str(int(float(lat[-1]) * 1e6))+'0')
    # end_lat = int(str(int(float(lat[0]) * 1e6))+'0')

    # 103.02629773377608:32.548317101263706,103.02569397423683:32.54805324214986
    # end_lon = int(103.024977 * 1e8)
    # start_lon = int(103.024451 * 1e8)
    # # print(end_lon)
    # start_lat = int(32.547471 * 1e7)
    # end_lat = int(32.547106 * 1e7)

    # uid004的
    # 103.02437338601855:32.548009252031044,
    # 103.02508067126857:32.54801157662211,
    # 103.02506545562521:32.54773177900123,
    # 103.02437339705602:32.54774229649762
    # end_lon = int(103.025064 * 1e8)
    # start_lon = int(103.024374 * 1e8)
    # # print(end_lon)
    # start_lat = int(32.548008 * 1e7)
    # end_lat = int(32.547743 * 1e7)



    # uid005的
    # 103.02569397423683: 32.548317101263706,
    # 103.02629773377607: 32.54831091424887,
    # 103.02629240141122: 32.54805324214986,
    # 103.0257100134279: 32.54806841179083
    # end_lon = int(103.026296 * 1e8)
    # start_lon = int(103.025694 * 1e8)
    # start_lat = int(32.548316 * 1e7)
    # end_lat = int(32.548054 * 1e7)
    # print(end_lat, end_lon, start_lon, start_lat)
    # for i in range(5):
        # print('第%s遍'%i)
        # thread1 = MyThread(insert_data,args=("1000",))
    
    # sn003
    # 103.02658917385443:32.54721185264436,
    # 103.02725466034346:32.54720591516331,
    # 103.02717692887651:32.54692669183979,
    # 103.02664747917812:32.54691580065166
    # end_lon = int(103.027175 * 1e8)
    # start_lon = int(103.026648 * 1e8)
    # start_lat = int(32.547204 * 1e7)
    # end_lat = int(32.546927 * 1e7)

    # 103.02621759758271: 32.54808509397123, 
    # 103.02681602253193: 32.5480608449201, 
    # 103.0267572582839: 32.54782140189332, 
    # 103.02619088936129: 32.54791789681688

    # 103.021975292352: 32.55163605720181,
    # 103.02246146114018: 32.551702489169095,
    # 103.02256832856254: 32.551317933155886,
    # 103.02208750120394: 32.55125148477919
    end_lon = int(103.022461 * 1e8)
    start_lon = int(103.022087 * 1e8)
    start_lat = int(32.551636 * 1e7)
    end_lat = int(32.551317 * 1e7)
    thread2 = MyThread(insert_data,args=("sn004",end_lon,start_lat,start_lon,end_lat))
    # thread1.start()
    thread2.start()



