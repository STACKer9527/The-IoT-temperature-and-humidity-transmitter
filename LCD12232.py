from  machine import *
import utime
from Key import *
from  dat_tab import *
from modbus import *#MODBUS
#LCD
MOSI = 34
SCK = 35
CS = 33
LCD_BK = 36
SPI_SCK = Pin(35,Pin.OUT)
SPI_MOSI = Pin(34,Pin.OUT)
SPI_CS = Pin(CS,Pin.OUT)
class LCD_12232():
    def __init__(self):
        self.cs = Pin(CS,Pin.OUT)
        self.cs(1)
        self.bk = Pin(LCD_BK,Pin.OUT)
        self.bk(1)
        self.init_display()
        self.disp_flg = True
        self.blk_flag = True
        self.start_pos = 0x83
    def SendByte(self,Sbyte):
        tmp= Sbyte
        Pin(MOSI,Pin.OUT)
        for i in range(8):
            SPI_SCK(0)
            if tmp & 0x80:
                SPI_MOSI(1)
            else:
                SPI_MOSI(0)
            SPI_SCK(1)
            tmp <<= 1
    def ReceiveByte(self):
        Pin(MOSI,Pin.INPUT)
        SPI_SCK(0)
        for i in range(8):
            data <<= 1
            SPI_SCK(1)
            if Pin(MOSI,Pin.INPUT):
                data |= 0x01
            SPI_SCK(0)
        return data        
    def write_cmd(self,Cbyte):
        self.cs(1)
        #self.check_busy()
        utime.sleep_ms(1) #这里用延时代替判忙
        self.SendByte(0xf8)
        self.SendByte(0xf0&Cbyte)
        self.SendByte(0xf0&Cbyte<<4)
        self.cs(0)

    def write_data(self,Dbyte):
        self.cs(1)
        #self.check_busy()
        utime.sleep_ms(1)#这里用延时代替判忙
        self.SendByte(0xfa)
        self.SendByte(0xf0&Dbyte)
        self.SendByte(0xf0&Dbyte<<4)
        self.cs(0)

    def init_display(self):
        self.write_cmd(0x30) #0x30,0x34
        utime.sleep_ms(10)
        self.write_cmd(0x04) #04,05
        utime.sleep_ms(10)
        self.write_cmd(0x0c)
        utime.sleep_ms(10)
        self.write_cmd(0x01)
        utime.sleep_ms(10)
        self.write_cmd(0x02)
        utime.sleep_ms(10)
        self.write_cmd(0x80)
        #self.write_cmd(0x0E)
        
    def test_disp(self,data1,data2):
        self.write_cmd(0x34)

        self.write_data(data1)
        #self.write_data(data1)
        self.write_cmd(0x30)
    #第一行：0x80--0x86(0x87一半)  第二行：0x90-0x96(0x97一半)
    def cn_disp(self,start_pos,hanzi_str):
        self.write_cmd(start_pos)
        for i in hanzi_str:
            self.write_data(cn_fonts16[i][0])
            self.write_data(cn_fonts16[i][1])
    def ascii_disp(self,start_pos,ascii_str):
        self.write_cmd(start_pos)
        for i in ascii_str:
            self.write_data(ord(i))
    def blink_disp(self,start_pos,blink_char):
        self.write_cmd(start_pos)
        self.write_data(blink_char)
    def blink_flag(self):
        if self.blk_flag is False:
            self.blk_flag = True
        else:
            self.blk_flag = False
        
    #主界面，显示温度、湿度            
    def main_interface(self):
        #print(ks.Update_LCD_Flg)
        ks.baseID = 0
        ks.isFinal = True
        if ks.Update_LCD_Flg==True:
            
            self.write_cmd(0x01) 
            self.cn_disp(0x80,"温度：")
            self.cn_disp(0x85,"℃")
            self.cn_disp(0x90,"湿度：")
            self.ascii_disp(0x95,"%RH")
            #self.ascii_disp(0x95,0x08)
        #print("22333")
            ks.Update_LCD_Flg=False

        self.ascii_disp(0x83,self.disp_tem)
        self.ascii_disp(0x93,self.disp_hum)
        #self.write_cmd(0x10)
        
    #一级菜单 界面一通讯参数、校准参数
    def first_set_interface(self):
        ks.maxItem = 4
        ks.baseID = 100
        ks.isFinal = False
        if ks.Update_LCD_Flg==True:
            self.write_cmd(0x01)  
            if ks.mainID == 100 or ks.mainID ==101:
                self.ascii_disp(0x80,"1.")
                self.cn_disp(0x81,"通讯参数")
                self.ascii_disp(0x90,"2.")
                self.cn_disp(0x91,"温湿度修正")
            elif ks.mainID == 102 or ks.mainID ==103:
                self.ascii_disp(0x80,"3.")
                self.cn_disp(0x81,"量程设置")
                self.ascii_disp(0x90,"4.")
                self.cn_disp(0x91,"恢复出厂设置")
            self.write_cmd(0x34)
            if ks.mainID==100 or ks.mainID==102:
                self.write_cmd(0x04)
            elif ks.mainID==101 or ks.mainID==103:
                self.write_cmd(0x05)
            self.write_cmd(0x30)
            ks.Update_LCD_Flg=False
                #utime.sleep_ms(5)
 
    #二级菜单 界面1：地址、波特率           
    def second_set_interface(self):
        #self.write_cmd(0x01)
        ks.maxItem = 2
        
        if ks.Update_LCD_Flg==True:
            self.write_cmd(0x01)
            if ks.mainID == 200 or ks.mainID ==201:
                ks.isFinal = True
                ks.isSet = 1
                ks.baseID = 200
                self.cn_disp(0x80,"地址：")
                self.cn_disp(0x90,"波特率：")

            elif ks.mainID == 202 or ks.mainID ==203:
                ks.isFinal = True
                ks.isSet =1
                ks.baseID = 202
                self.cn_disp(0x80,"温度修正：")
                self.cn_disp(0x90,"湿度修正：")

            elif ks.mainID == 204 or ks.mainID ==205:
                ks.isFinal = True
                ks.isSet =1
                ks.baseID = 204
                self.cn_disp(0x80,"温度：")
                self.cn_disp(0x90,"湿度：")
                
            elif ks.mainID == 206 or ks.mainID ==207:
                ks.baseID = 206
                ks.isFinal = True
                self.cn_disp(0x80,"恢复出厂设置")
                self.ascii_disp(0x86,"?")
                self.cn_disp(0x93,"确认")
                #self.cn_disp(0x95,"取消")
                self.write_cmd(0x34)
                self.write_cmd(0x05)
                self.write_cmd(0x30)
            ks.Update_LCD_Flg=False
        if self.blk_flag is True:
            if ks.mainID == 200:
                if ks.adr_idx==0:
                    self.ascii_disp(0x83,str(ks.adr_b) + str(ks.adr_s) + "_")
                elif ks.adr_idx==1:
                    self.ascii_disp(0x83,"_" + str(ks.adr_s) + str(ks.adr_g))
                elif ks.adr_idx==2:
                    self.ascii_disp(0x83,str(ks.adr_b) + "_" + str(ks.adr_g))

            elif ks.mainID == 201:
                if len(str(m_bus.BaudRate))==6:
                    self.ascii_disp(0x94,"______")
                elif len(str(m_bus.BaudRate))==5:
                    self.ascii_disp(0x94,"_____")
                else:
                    self.ascii_disp(0x94,"____")
            elif ks.mainID == 202:
                if ks.t_adj_idx ==0:
                    self.ascii_disp(0x85,"_"+str(ks.t_adj_s)+"."+str(ks.t_adj_g))
                elif ks.t_adj_idx ==1:
                    self.ascii_disp(0x85,str(ks.t_adj_sign)+"_"+"."+str(ks.t_adj_g))
                elif ks.t_adj_idx ==2:
                    self.ascii_disp(0x85,str(ks.t_adj_sign)+str(ks.t_adj_s)+"."+"_")
            elif ks.mainID == 203:
                if ks.h_adj_idx ==0:
                    self.ascii_disp(0x95,"_"+str(ks.h_adj_s)+"."+str(ks.h_adj_g))
                elif ks.h_adj_idx ==1:
                    self.ascii_disp(0x95,str(ks.h_adj_sign)+"_"+"."+str(ks.h_adj_g))
                elif ks.h_adj_idx ==2:
                    self.ascii_disp(0x95,str(ks.h_adj_sign)+str(ks.h_adj_s)+"."+"_")                    
                #self.ascii_disp(0x95,"+0.5")                
                #self.adj_sign =
            elif ks.mainID == 204:
                if ks.t_range_idx ==0:
                    self.ascii_disp(0x83,"_"+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                elif ks.t_range_idx ==1:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+"_"+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                elif ks.t_range_idx ==2:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+"_"+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                    
                elif ks.t_range_idx ==3:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+"_"
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                elif ks.t_range_idx ==4:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+"_"+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                elif ks.t_range_idx ==5:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+"_"+str(ks.t2_range_s)+str(ks.t2_range_g))
                elif ks.t_range_idx ==6:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+"_"+str(ks.t2_range_g))
                elif ks.t_range_idx ==7:
                    self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                    +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+"_")
            elif ks.mainID == 205:
                if ks.h_range_idx ==0:
                    self.ascii_disp(0x93,"_"+str(ks.h1_range_s)+str(ks.h1_range_g)
                                    +"~"+str(ks.h2_range_b)+str(ks.h2_range_s)+str(ks.h2_range_g))
                elif ks.h_range_idx ==1:
                    self.ascii_disp(0x93,str(ks.h1_range_b)+"_"+str(ks.h1_range_g)
                                    +"~"+str(ks.h2_range_b)+str(ks.h2_range_s)+str(ks.h2_range_g))
                elif ks.h_range_idx ==2:
                    self.ascii_disp(0x93,str(ks.h1_range_b)+str(ks.h1_range_s)+"_"
                                    +"~"+str(ks.h2_range_b)+str(ks.h2_range_s)+str(ks.h2_range_g))
                    
                elif ks.h_range_idx ==3:
                    self.ascii_disp(0x93,str(ks.h1_range_b)+str(ks.h1_range_s)+str(ks.h1_range_g)
                                    +"~"+"_"+str(ks.h2_range_s)+str(ks.h2_range_g))
                elif ks.h_range_idx ==4:
                    self.ascii_disp(0x93,str(ks.h1_range_b)+str(ks.h1_range_s)+str(ks.h1_range_g)
                                    +"~"+str(ks.h2_range_b)+"_"+str(ks.h2_range_g))
                elif ks.h_range_idx ==5:
                    self.ascii_disp(0x93,str(ks.h1_range_b)+str(ks.h1_range_s)+str(ks.h1_range_g)
                                    +"~"+str(ks.h2_range_b)+str(ks.h2_range_s)+"_")
        else:
            if ks.mainID == 200 or ks.mainID == 201:
                self.ascii_disp(0x83,str(ks.adr_b) + str(ks.adr_s) + str(ks.adr_g))
                if len(str(m_bus.BaudRate))<6:
                    self.ascii_disp(0x94,str(m_bus.BaudRate)+"  ")#补齐6位
                else:
                    self.ascii_disp(0x94,str(m_bus.BaudRate))
            elif ks.mainID == 202 or ks.mainID == 203:
                self.ascii_disp(0x85,str(ks.t_adj_sign)+str(ks.t_adj_s)+"."+str(ks.t_adj_g))
                self.ascii_disp(0x95,str(ks.h_adj_sign)+str(ks.h_adj_s)+"."+str(ks.h_adj_g))
            elif ks.mainID == 204 or ks.mainID == 205:
                self.ascii_disp(0x83,str(ks.t1_range_sign)+str(ks.t1_range_b)+str(ks.t1_range_s)+str(ks.t1_range_g)
                                +"~"+str(ks.t2_range_sign)+str(ks.t2_range_b)+str(ks.t2_range_s)+str(ks.t2_range_g))
                self.ascii_disp(0x93,str(ks.h1_range_b)+str(ks.h1_range_s)+str(ks.h1_range_g)
                                +"~"+str(ks.h2_range_b)+str(ks.h2_range_s)+str(ks.h2_range_g))
    #三级菜单界面        
    def third_set_interface(self):
        if ks.mainID == 300 or ks.mainID == 301:
            pass
    
    def display_process(self,tem,hum):
        self.disp_tem = tem
        self.disp_hum = hum
        self.id_index= int(ks.mainID/100)
        #print(self.id_index)
        if self.id_index ==1:
            self.first_set_interface()             
        elif self.id_index==2:
            self.second_set_interface()
        elif self.id_index==3:
            self.third_set_interface()
        else:
            self.main_interface()
            
    def display_170ms(self):
        self.disp_flg = True

#lcd = LCD_12232()

