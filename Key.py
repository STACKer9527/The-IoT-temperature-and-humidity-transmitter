from  machine import *
from modbus import *#MODBUS
from sht3x import *
MENU = 0
ENTER = 1
DOWN = 2
RIGHT = 3
STAT_QUERY  = 0
STAT_PRESS  = 1
STAT_RELEASE  = 2
#设为输入、上拉模式
RightKey= Pin(3,Pin.IN,Pin.PULL_UP)
DownKey = Pin(2,Pin.IN,Pin.PULL_UP)
MenuKey = Pin(1,Pin.IN,Pin.PULL_UP)
EnterKey= Pin(4,Pin.IN,Pin.PULL_UP)
# 菜单/返回，↑，→，确认


class KeyScan:
    
    def __init__(self):
        self.key_stat = [0,0,0,0]
        self.mainID = 0
        self.subID = 0
        self.baseID = 0
        self.maxItem = 0
        self.sonID = 0
        self.isFinal = False
        self.isSet = 0
        self.Update_LCD_Flg=True
        self.return_flg = 0
        self.brt_idx = 0
        self.adr_idx =0
        self.adr_b  = 0
        self.adr_s  = 0
        self.adr_g  = 1
        self.adr_s_max = 9
        self.adr_g_max = 9
        self.t_adj_idx =0
        self.t_adj_sign = "+"
        self.t_adj_s = 0
        self.t_adj_g = 0
        self.h_adj_idx =0
        self.h_adj_sign = "+"
        self.h_adj_s = 0
        self.h_adj_g = 0
        
        self.t_range_idx = 0
        self.t1_range_sign = "+"
        self.t2_range_sign = "+"
        self.t1_range_b = 0
        self.t1_range_s = 0
        self.t1_range_g = 0
        self.t2_range_b = 1
        self.t2_range_s = 0
        self.t2_range_g = 0
        
        self.h_range_idx = 0
        self.h1_range_b = 0
        self.h1_range_s = 0
        self.h1_range_g = 0
        self.h2_range_b = 1
        self.h2_range_s = 0
        self.h2_range_g = 0
        
    def KeyProcess(self):
        if self.key_stat[DOWN] == STAT_QUERY:
            if DownKey.value()==0:               
                self.key_stat[DOWN] = STAT_PRESS
        elif self.key_stat[DOWN] == STAT_PRESS:
            if DownKey.value()==0:
                self.key_stat[DOWN] = STAT_RELEASE
                #print("up_press")
            else:
                self.key_stat[DOWN] = STAT_QUERY
        elif self.key_stat[DOWN] == STAT_RELEASE:
            if DownKey.value()!=0:
                self.key_stat[DOWN] = STAT_QUERY
                print("↓")
                self.DownKeyProcess()
        else:  #default
            self.key_stat[DOWN] = STAT_QUERY


        if self.key_stat[RIGHT] == STAT_QUERY:
            if RightKey.value()==0:               
                self.key_stat[RIGHT] = STAT_PRESS
        elif self.key_stat[RIGHT] == STAT_PRESS:
            if RightKey.value()==0:
                self.key_stat[RIGHT] = STAT_RELEASE
                #print("down_press")
            else:
                self.key_stat[RIGHT] = STAT_QUERY
        elif self.key_stat[RIGHT] == STAT_RELEASE:
            if RightKey.value()!=0:
                self.key_stat[RIGHT] = STAT_QUERY
                print("→")
                self.RightKeyProcess()
        else:  #default
            self.key_stat[RIGHT] = STAT_QUERY
            
        if self.key_stat[MENU] == STAT_QUERY:
            if MenuKey.value()==0:               
                self.key_stat[MENU] = STAT_PRESS
        elif self.key_stat[MENU] == STAT_PRESS:
            if MenuKey.value()==0:
                self.key_stat[MENU] = STAT_RELEASE
                #print("menu_press")
            else:
                self.key_stat[MENU] = STAT_QUERY
        elif self.key_stat[MENU] == STAT_RELEASE:
            if MenuKey.value()!=0:
                self.key_stat[MENU] = STAT_QUERY
                print("菜单/返回")
                
                self.MenuKeyProcess()
                
        else:  #default
            self.key_stat[MENU] = STAT_QUERY
            

        if self.key_stat[ENTER] == STAT_QUERY:
            if EnterKey.value()==0:               
                self.key_stat[ENTER] = STAT_PRESS
        elif self.key_stat[ENTER] == STAT_PRESS:
            if EnterKey.value()==0:
                self.key_stat[ENTER] = STAT_RELEASE
                #print("enter_press")
            else:
                self.key_stat[ENTER] = STAT_QUERY
        elif self.key_stat[ENTER] == STAT_RELEASE:
            if EnterKey.value()!=0:
                self.key_stat[ENTER] = STAT_QUERY
                print("确认/OK")
                self.EnterKeyProcess()
        else:  #default
            self.key_stat[ENTER] = STAT_QUERY

    def MenuKeyProcess(self):
        self.Update_LCD_Flg=True
        if int(self.mainID /100)==1:
            #self.subID = 0
            self.mainID = 0#int(self.mainID /100)*100-100+self.subID
            self.sonID = 0
            self.baseID = 0
        elif int(self.mainID /100)==2:
            self.mainID = int(self.mainID /100)*100-100+self.subID
            self.sonID = 0
            self.isFinal = False
            self.isSet = 0
            self.brt_idx = 0
            self.adr_idx =0
            self.t_adj_idx =0
            self.h_adj_idx =0
            
        else:
            self.mainID = 100
            self.subID = 0
            self.sonID = 0
            self.baseID = 0
            self.maxItem = 0

    def EnterKeyProcess(self):
        if self.isFinal is False:
            if int(self.mainID /100)==1:
                self.Update_LCD_Flg=True
                self.mainID = (self.baseID +self.subID)*2
                #print(self.mainID)
            elif int(self.mainID /100)==2:
                self.Update_LCD_Flg=True
                self.mainID = self.baseID +self.sonID+100

                #print(self.mainID)
        else:#终极目录，设置参数 切换上下设置参数
            #self.isSet = 1#~self.isSet
            #print(self.isSet)
            
            if  self.mainID != 206:
                self.sonID = self.sonID +1
                if self.sonID>self.maxItem-1:
                    self.sonID = 0
                    self.return_flg = 1
            self.mainID = self.baseID+self.sonID
            
            #self.mainID = self.baseID+self.sonID
            print(self.mainID)
            #return
            if self.mainID > 206:
                self.mainID = 206
            if self.mainID == 200:
                print("200--200")
                
                self.adr_idx =0
                self.mainID = int(self.mainID /100)*100-100+self.subID
                self.isFinal = False
                self.isSet = 0                
                self.Update_LCD_Flg=True

            elif self.mainID == 201:
                print("201--201")
                m_bus.localAddr = self.adr_b*100 + self.adr_s*10 + self.adr_g

            elif self.mainID == 202:
                #sht.tm_shift = self.t_adj_s + self.t_adj_g
                print("202--202")
                if self.h_adj_sign == "+":
                    sht.hm_shift = (self.h_adj_s*10+self.h_adj_g)/10
                else:
                    sht.hm_shift = -(self.h_adj_s*10+self.h_adj_g)/10
                self.mainID = int(self.mainID /100)*100-100+self.subID
                self.isFinal = False
                self.isSet = 0                
                self.Update_LCD_Flg=True
            elif self.mainID == 203:
                print("203--203")
                if self.t_adj_sign == "+":
                    sht.tm_shift = (self.t_adj_s*10+self.t_adj_g)/10
                    #print(sht.tm_shift)
                else:
                    sht.tm_shift = -(self.t_adj_s*10+self.t_adj_g)/10                

            elif self.mainID == 204:
                print("204--204")
                sht.h1_range = self.h1_range_b*100+self.h1_range_s*10+self.h1_range_g
                sht.h2_range = self.h2_range_b*100+self.h2_range_s*10+self.h2_range_g
                self.mainID = int(self.mainID /100)*100-100+self.subID
                self.isFinal = False
                self.isSet = 0                
                self.Update_LCD_Flg=True                    
            elif self.mainID == 205:                
                print("205--205")
                if self.t1_range_sign == "+":
                    sht.t1_range = self.t1_range_b*100+self.t1_range_s*10+self.t1_range_g
                else:
                    sht.t1_range = -(self.t1_range_b*100+self.t1_range_s*10+self.t1_range_g)
                if self.t2_range_sign == "+":
                    sht.t2_range = self.t2_range_b*100+self.t2_range_s*10+self.t2_range_g
                else:
                    sht.t2_range = -(self.t2_range_b*100+self.t2_range_s*10+self.t2_range_g)
            elif self.mainID == 206:
                self.adr_b  = 0
                self.adr_s  = 0
                self.adr_g  = 1
                self.t_adj_sign = "+"
                self.t_adj_s = 0
                self.t_adj_g = 0
                self.h_adj_sign = "+"
                self.h_adj_s = 0
                self.h_adj_g = 0
                sht.tm_shift = 0
                sht.hm_shift = 0
                m_bus.localAddr = 1
                m_bus.BaudRate = 9600
                #写dat文件保存到Falsh
                print("恢复出厂设置！")
                self.mainID = int(self.mainID /100)*100-100+self.subID
                self.Update_LCD_Flg=True


    def DownKeyProcess(self):
        
        if self.isSet !=0:
            print(self.mainID)
            if self.mainID == 200:
                if self.adr_idx ==0:
                    #print(11)
                    if self.adr_b ==1 and  self.adr_s ==2:
                        self.adr_g_max=8
                    else:
                        self.adr_g_max = 9
                    if self.adr_g <self.adr_g_max:
                        self.adr_g  = self.adr_g+1
                    else:
                        self.adr_g = 0
                elif self.adr_idx ==1:
                    #print(11)
                    if self.adr_b <1:
                        self.adr_b  = self.adr_b+1
                    else:
                        self.adr_b = 0
                elif self.adr_idx ==2:
                    #print(22)
                    
                    if self.adr_b ==1:
                        self.adr_s_max = 2
                    else:
                        self.adr_s_max = 9
                    if self.adr_s <self.adr_s_max:
                        self.adr_s  = self.adr_s+1
                    else:
                        self.adr_s =0
                #print(self.adr_b,self.adr_s,self.adr_g)
                
                
            elif self.mainID ==201:
                self.brt_idx = self.brt_idx+1
                if self.brt_idx ==0:
                    m_bus.BaudRate = 9600
                elif self.brt_idx==1:
                    m_bus.BaudRate = 19200
                elif self.brt_idx ==2:
                    m_bus.BaudRate = 38400
                elif self.brt_idx==3:
                    m_bus.BaudRate = 57600
                elif self.brt_idx ==4:
                    m_bus.BaudRate = 115200
                else:
                    self.brt_idx = 0
                    m_bus.BaudRate = 9600
            elif self.mainID ==202:
                if self.t_adj_idx ==0:
                    if self.t_adj_sign =="+":
                        self.t_adj_sign ="-"
                    else:
                        self.t_adj_sign = "+"
                    print(self.t_adj_sign)
                elif self.t_adj_idx ==1:
                    if self.t_adj_s <9:
                        self.t_adj_s  = self.t_adj_s+1
                    else:
                        self.t_adj_s = 0
                elif self.t_adj_idx ==2:
                    if self.t_adj_g <9:
                        self.t_adj_g  = self.t_adj_g+1
                    else:
                        self.t_adj_g = 0
            elif self.mainID ==203:
                if self.h_adj_idx ==0:
                    if self.h_adj_sign =="+":
                        self.h_adj_sign ="-"
                    else:
                        self.h_adj_sign = "+"
                    #print(self.t_adj_sign)
                elif self.h_adj_idx ==1:
                    if self.h_adj_s <9:
                        self.h_adj_s  = self.h_adj_s+1
                    else:
                        self.h_adj_s = 0
                elif self.h_adj_idx ==2:
                    if self.h_adj_g <9:
                        self.h_adj_g  = self.h_adj_g+1
                    else:
                        self.h_adj_g = 0
            elif self.mainID ==204:
                if self.t_range_idx ==0:
                    if self.t1_range_sign =="+":
                        self.t1_range_sign ="-"
                    else:
                        self.t_range_sign = "+"
                elif self.t_range_idx ==1:
                    if self.t1_range_b ==0:
                        self.t1_range_b =1
                    else:
                        self.t1_range_b = 0
                elif self.t_range_idx ==2:
                    if self.t1_range_s <9:
                        self.t1_range_s =self.t1_range_s+1
                    else:
                        self.t1_range_s = 0
                elif self.t_range_idx ==3:
                    if self.t1_range_g <9:
                        self.t1_range_g =self.t1_range_g+1
                    else:
                        self.t1_range_g = 0
                elif self.t_range_idx ==4:
                    if self.t2_range_sign =="+":
                        self.t2_range_sign ="-"
                    else:
                        self.t2_range_sign = "+"
                elif self.t_range_idx ==5:
                    if self.t2_range_b ==0:
                        self.t2_range_b =1
                    else:
                        self.t2_range_b = 0
                elif self.t_range_idx ==6:
                    if self.t2_range_s <9:
                        self.t2_range_s =self.t2_range_s+1
                    else:
                        self.t2_range_s = 0
                elif self.t_range_idx ==7:
                    if self.t2_range_g <9:
                        self.t2_range_g =self.t2_range_g+1
                    else:
                        self.t2_range_g = 0
            elif self.mainID ==205:
                if self.h_range_idx ==0:
                    if self.h1_range_b ==0:
                        self.h1_range_b =1
                    else:
                        self.h1_range_b = 0
                elif self.h_range_idx ==1:
                    if self.h1_range_s <9:
                        self.h1_range_s =self.h1_range_s+1
                    else:
                        self.t1_range_s = 0
                elif self.h_range_idx ==2:
                    if self.h1_range_g <9:
                        self.h1_range_g =self.h1_range_g+1
                    else:
                        self.h1_range_g = 0
                elif self.h_range_idx ==3:
                    if self.h2_range_b ==0:
                        self.h2_range_b =1
                    else:
                        self.h2_range_b = 0
                elif self.h_range_idx ==4:
                    if self.h2_range_s <9:
                        self.h2_range_s =self.h2_range_s+1
                    else:
                        self.h2_range_s = 0
                elif self.h_range_idx ==5:
                    if self.h2_range_g <9:
                        self.h2_range_g =self.h2_range_g+1
                    else:
                        self.h2_range_g = 0
                
        else:
            if int(self.mainID /100)==1:
                self.subID = self.subID+1
                if self.subID>self.maxItem-1:
                    self.subID = 0
                self.mainID = self.baseID+self.subID #
                #print(self.mainID)
                self.Update_LCD_Flg=True
            elif int(self.mainID /100)==2:
                self.sonID = self.sonID+1
                if self.sonID>self.maxItem-1:
                    self.sonID = 0            
                self.mainID = self.baseID+self.sonID
                #print(self.mainID)
                self.Update_LCD_Flg=True

    def RightKeyProcess(self):
        if self.mainID == 200:
            if self.adr_idx <2:
                self.adr_idx = self.adr_idx+1
            else:
                self.adr_idx = 0
        elif self.mainID == 202:
            if self.t_adj_idx <2:
                self.t_adj_idx = self.t_adj_idx+1
            else:
                self.t_adj_idx = 0
        elif self.mainID == 203:
            if self.h_adj_idx <2:
                self.h_adj_idx = self.h_adj_idx+1
            else:
                self.h_adj_idx = 0
        elif self.mainID == 204:
            if self.t_range_idx <7:
                self.t_range_idx = self.t_range_idx+1
            else:
                self.t_range_idx = 0
            
        elif self.mainID == 205:
            if self.h_range_idx <5:
                self.h_range_idx = self.h_range_idx+1
            else:
                self.h_range_idx = 0
            
    def Key17ms(self):
        self.key_17ms_flg = True
ks = KeyScan() 
