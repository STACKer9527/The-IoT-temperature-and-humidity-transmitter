from  machine import *
import utime
#DEV_STOR_ADDR = 200
TEM_STOR_ADDR = 1
HUM_STOR_ADDR = 2

       
class SHT3x_Sensor:
    def __init__(self,ch,sclpin,sdapin,freq):
        self.i2c = I2C(ch, scl=Pin(sclpin),sda=Pin(sdapin),freq=freq)
        addrs = self.i2c.scan()
        if not addrs:
            #raise Exception('没找到总线SDA引脚%dSCL引脚%d' % (sdapin, sclpin))
            self.addr = 0#addrs.pop()
            #return None
        else:
            self.addr = addrs.pop()
        self.tm_shift = 0
        self.hm_shift = 0
        self.t1_range = 0
        self.t2_range = 100
        self.h1_range = 0
        self.h2_range = 100        
    def read_temp_humd(self):
        try:
            if self.addr==0:
                return [255,255]
            else:
                status = self.i2c.writeto(self.addr,b'\x24\x00')
        except (OSError):
             return [255,255]
        utime.sleep_ms(50)
        #print(status)
        try:
            databytes = self.i2c.readfrom(self.addr, 6)
        except (OSError):
             return [255,255]        
        #dataset = [databytes[0],databytes[1]]
        #dataset = [databytes[3],databytes[4]]
        temperature_raw = databytes[0] << 8 | databytes[1]
        temperature = (175.0 * float(temperature_raw) / 65535.0) - 45
        humidity_raw = databytes[3] << 8  | databytes[4]
        humidity = (100.0 * float(humidity_raw) / 65535.0)
        sensor_data = [temperature, humidity]
        return sensor_data

sht = SHT3x_Sensor(1,13,12,500_000)