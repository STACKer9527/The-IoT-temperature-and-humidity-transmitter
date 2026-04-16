from  machine import *

import time
import network
from umqttrobust import MQTTClient #导入同目录下的umqttrobust.py文件
import json

from modbus import *#MODBUS
from Key import *
from LCD12232 import *
from sht3x import *
freq(240_000_000) # set the CPU frequency to 240 MHz
wifi_name = 'zhou403'  # wifi名称
password = 'zhou15099246901' # wifi密码
# MQTT配置信息
mqtt_client_id = '1_ESP32_TemHum_Transmitter_0_0_2024011915'

mqtt_server_ip = 'ade816010a.st1.iotda-device.cn-north-4.myhuaweicloud.com'
mqtt_server_port = '1883'
mqtt_server_user ='1_ESP32_TemHum_Transmitter'
mqtt_server_password='aae09c44cb14f6dddeecaabe51d18e5f800c7a3236913caf8bb9bd53dfae9c98'
mqtt_publish_topic = '$oc/devices/1_ESP32_TemHum_Transmitter_0_0_2024012013/sys/properties/report'#发布信息主题（上传数据）
mqtt_subscribe_topic =''#订阅主题（接收上位机的命令）

pub_temphum = ''
RE_DE = Pin(45, Pin.OUT)
RE_DE.on()
def main():
    #date_time = rtc.datetime() # get date and time
    global MQTT_hum_Data
    global MQTT_tem_Data
    while True:
        measure_data = sht.read_temp_humd()
        measure_data[0] = sht.tm_shift+measure_data[0]
        measure_data[1] = sht.hm_shift+measure_data[1]
        if measure_data[0] ==255 or measure_data[1]==255:
            SHT3x_Sensor(1,13,12,500_000)
        if measure_data[0] >99.9:
            measure_data[0]=99.9        
        if measure_data[1] >99.9:
            measure_data[1]=99.9
        MQTT_hum_Data = fdat_trunc(measure_data[1],1,0)
        MQTT_tem_Data = fdat_trunc(measure_data[0],1,0)
        m_bus.RegAssign(0,int(measure_data[0]*10))
        m_bus.RegAssign(1,int(measure_data[1]*10))
        ks.KeyProcess()
        lcd.display_process(fdat_trunc(measure_data[0],1,"str"),fdat_trunc(measure_data[1],1,"str"))
        tem_dat = Calc(sht.t1_range,sht.t2_range,measure_data[0]) #0-100 a1--a2
        dac.send_data(TEM,tem_dat)
        hum_dat = Calc(sht.h1_range,sht.h2_range,measure_data[1])
        dac.send_data(HUM,hum_dat)
        led_blink()

def wifi_connect():
    wifi_times = 0
    wlan = network.WLAN(network.STA_IF)  # 创建STA模式
    wlan.active(True)  # 激活wifi

    if not wlan.isconnected():  # 首次判断状态，尝试连接
        print('connect...')
        wlan.connect(wifi_name, password)  # 连接wifi

        while not wlan.isconnected():  # 用循环等待wifi连接（wifi连接需要点时间），每1s重新判断一次，若连接成功则不进入循环了
            wifi_times += 1  # 计数器+1
            time.sleep(1)  # 每次等待1S
            print(wifi_times)
            if wifi_times == 30:  # 如果过了30S都没连上，判定连接失败
                wlan.active(False)
                return False  # 返回False
    ip=wlan.ifconfig()
    print("wifi connected！")  # 若连接成功则不进入循环，从这里向下继续
    print("IPaddress："+ip[0])
    print('network ：', wlan.status())  # 返回网络工作状态,信号强度
    return True	# 返回True

#保留n位小数（不四舍五入）
def fdat_trunc(f_dat,n_pt,xtype):
    str_fdat = str(f_dat).split('.')[0] + '.' + str(f_dat).split('.')[1][:n_pt]
    if xtype!="str":
        str_fdat = float(str_fdat)
    return str_fdat

#直线方程： k = 16/(a2-a1)  b = (4*a2-20*a1)/(a2-a1)
#输出电流方程： Iot = k*tm + b   Ioh = k*hm + b
# 0-0xFFFF   scal = 65536/(a2-a1)
def Calc(a1,a2,sample_dat):
    if a1==a2:
        return 0
    scal = 0xFFFF/(a2-a1)
    equat_k = 16/(a2-a1)
    equat_b = (4*a2-20*a1)/(a2-a1)
    Iout_dat = (equat_k*sample_dat + equat_b) *scal
    return Iout_dat

DA_DATA = [0,1]
DA_SCLOCK = [0,1]
DA_LATCH = [0,1]
TEM = 0
HUM = 1
DA_DATA[TEM] = Pin(7, Pin.OUT)
DA_SCLOCK[TEM] = Pin(6, Pin.OUT)
DA_LATCH[TEM] = Pin(5, Pin.OUT)

DA_DATA[HUM] = Pin(10, Pin.OUT)
DA_SCLOCK[HUM] = Pin(9, Pin.OUT)
DA_LATCH[HUM] = Pin(8, Pin.OUT)

class AD421:
    def __init__(self):
        self.temp = 0x8000
    #input_dat :0-0xFFFF 对应4-19.999756mA
    def send_data(self,n_ch,input_dat):
        
        DA_SCLOCK[n_ch].on()
        DA_DATA[n_ch].off()
        DA_LATCH[n_ch].off()
        for i in range(0,16):
            if  self.temp & int(input_dat):
                DA_DATA[n_ch].on()
            else:
                DA_DATA[n_ch].off()
            DA_SCLOCK[n_ch].off()
            utime.sleep_us(90)
            DA_SCLOCK[n_ch].on()
            utime.sleep_us(90)
            self.temp = self.temp>>1
        self.temp =0x8000
        DA_LATCH[n_ch].on()
dac = AD421()

lcd = LCD_12232()
state = disable_irq()
measure_data = [0,0,0]
#modbus  80毫秒定时中断查询接收命令
# Timer.ONE_SHOT - 计时器运行一次，直到配置完毕通道的期限到期。
# Timer.PERIODIC - 定时器以通道的配置频率定期运行。
tim0 = Timer(0)
tim0.init(period = 31,# period - 定时器执行的周期，单位是ms,  period取值范围： 0 < period <= 3435973836
          mode = Timer.PERIODIC,
          callback=lambda t:m_bus.modbusHandle())# callback - 定时器的回调函数
#设置位闪烁
tim1 = Timer(1)
tim1.init(period = 300, mode = Timer.PERIODIC,callback=lambda t:lcd.blink_flag())# callback - 定时器的回调函数
#刷新显示
tim2 = Timer(2)
tim2.init(period = 170,mode = Timer.PERIODIC,callback=lambda t:lcd.display_170ms())# callback - 定时器的回调函数
LED = Pin(38, Pin.OUT)
LED.off()
def led_blink():
    if lcd.blk_flag:
        LED.on()
    else:
        LED.off()

#def apptimerevent(mytimer):
#    mymessage = {"data":{"hum":MQTT_hum_Data,"temp":MQTT_tem_Data}}
#    client.publish(topic=publish_TOPIC,msg = json.dumps(mymessage), retain=False, qos=0)
 
# MQTT回调函数，收到服务器消息后会调用这个函数
def mqtt_sub(topic, msg): 
    print('收到服务器信息')
    print(topic, msg)
    
#订阅主题回调函数 收到消息时在此处理
def subCallBack(subTopic, msg):
    
    pub_temphum = {"services":[{"service_id":"TemHum","properties":{"temperature":MQTT_tem_Data,"humidity":MQTT_hum_Data}}]}
    #pub_temphum = "{\"services\":[{\"service_id\":\"TemHum\",\"properties\":{\"temperature\":26.6,\"humidity\":33.3}}]}"
    #print('当前温度：' + current_temp)
    #mqtt.check_msg()
    pub_temphum = json.dumps(pub_temphum)
    mqtt.publish(mqtt_publish_topic, pub_temphum)

def tm3_CallBack(self):
    pub_temphum = {"services":[{"service_id":"TemHum","properties":{"temperature":MQTT_tem_Data,"humidity":MQTT_hum_Data}}]}
    pub_temphum = json.dumps(pub_temphum)
    #print(pub_temphum)
    mqtt.publish(mqtt_publish_topic, pub_temphum)


enable_irq(state)
#wifi_connect()
'''
mqtt = MQTTClient(mqtt_client_id, mqtt_server_ip, mqtt_server_port,mqtt_server_user,mqtt_server_password,60)
mqtt.set_callback(subCallBack)
mqtt.connect()
mqtt.subscribe(mqtt_subscribe_topic)
print("订阅成功")
'''
#tim3 = Timer(3)
#tim3.init(period = 30000,mode = Timer.PERIODIC,callback=tm3_CallBack)# callback - 定时器的回调函数


#mqtt_client = mqtt_init()

if __name__=='__main__':
    main()


