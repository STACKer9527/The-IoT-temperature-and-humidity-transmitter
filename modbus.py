from  machine import *
class My_UART(object):
    def __init__(self, UART_id: int = 1, baudrate: int = 9600, timeout: int = 1000):
        self.baud = baudrate
        #self.uartx = UART(UART_id, self.baud, bits=8,parity=None,stop=1,tx=Pin(41), rx=Pin(42))
        self.uartx = UART(UART_id, self.baud, bits=8,parity=None,stop=1,tx=41, rx=42)
    def my_any(self):
        return self.uartx.any()

    def readchar(self):
        return self.uartx.read(1)
        
    def writechar(self,w_char):
        self.uartx.write(w_char.to_bytes(1, "big"))
        
    def write(self,w_str:str):
        self.uartx.write(w_str)
        
    def sendbreak(self):
        self.uartx.sendbreak()

StorConfig = []
class MODBUS(object):
    localAddr = 1
    receBuf_Length = 200  
    sendBuf_Length = 100 
    ModbusCoilAdd = 100   
    ModbusRegAdd = 200   
    CoilLen = 100         
    RegLen = 100          
    sendBuf = [0 for x in range(0,sendBuf_Length)]
    receBuf = [0 for x in range(0,receBuf_Length)]
    checkoutError = 0
    receTimeOut = 1000
    receCount = 0   
    CoilData = [0 for x in range(0, CoilLen)]  
    RegData = [0 for x in range(0, RegLen)]  
    def __init__(self,
                 localAddr = 1,
                 ModbusCoilAdd=100,
                 ModbusRegAdd = 200+CoilLen,
                 CoilLen = 100,
                 RegLen = 100,
                 receTimeOut = 1000):
        self.ModbusRegAdd = ModbusRegAdd
        self.ModbusCoilAdd = ModbusCoilAdd
        self.CoilLen = CoilLen
        self.RegLen = RegLen
        self.receTimeOut = receTimeOut
        self.uart = My_UART()
        self.BaudRate = 9600
        self.localAddr = 1

    def printf(self, com: str = ''):
        self.uart.write(str(com))
        
    def sprintf(self, mode: str = "%s", val: str = ''):

        i = mode.index('%')  # 找到%号的位置
        temp = mode[i:i + 2]  # 提取打印模式  如：%s
        temp_front = str(mode[0:i])
        temp_behind = str(mode[i + 2:len(mode)])
        if temp == "%s":
            self.uart.write(temp_front + str(val) + temp_behind)
        elif temp == "%d":
            self.uart.write(temp_front + str(int(val)) + temp_behind)
        elif temp == "%f":
            self.uart.write(temp_front + str(float(val)) + temp_behind)
        elif temp == "%x":
            self.uart.write(temp_front + str(hex(val)) + temp_behind)
        elif temp == "%c":
            self.uart.write(temp_front + str(chr(val)) + temp_behind)
        elif temp == "%o":
            self.uart.write(temp_front + str(oct(val)) + temp_behind)

    #ByteToHex的转换，返回数据16进制字符串
    def ByteToHex( self,bins ):
        return '0x'+''.join( [ "%02X" % x for x in bins ] ).strip()
    
    def UsartxDataRec(self):
        if self.uart.my_any() > 0:
            temp =self.uart.readchar()
            hex_cmd = int(self.ByteToHex(temp))
            if(self.receCount < self.receBuf_Length):
                self.receBuf[self.receCount] = hex_cmd
                self.receCount += 1
                
    def crc16(self,puchMsg = [0], usDataLen = 6):          
        uchCRCLo = 0xff
        uchCRCHi = 0xff
        
        for i in range(0,usDataLen,1):
            uIndex = uchCRCHi ^ puchMsg[i]
            uchCRCHi = uchCRCLo ^ auchCRCHi[uIndex]
            uchCRCLo = auchCRCLo[uIndex]
        return (uchCRCHi << 8 | uchCRCLo)

    def clearReceBuf(self):
        for i in range(0,1,self.receBuf_Length):
            self.receBuf[i] = 0
            self.sendBuf[i] = 0
        self.receCount = 0
        self.checkoutError = 0

    def byteConvert16(self,a,b):
        return a << 8 | b

    def byteConvert32(self, a, b):
        return a << 16 | b

    def OperateAdd(self,a,b):
        return  (a + (b*2))
    def getCoilVal(self,dataAddr):
        tempAddr = dataAddr & 0x0fff
        tempData = self.CoilData[tempAddr]
        return tempData

    def beginSend(self,sendCount):
        for i in range(0,sendCount,1):
            #print(hex(self.sendBuf[i]))
            self.uart.writechar(self.sendBuf[i])
        self.receCount = 0
        self.checkoutError = 0

    def readCoil(self):
        exit = 0
        addr = self.byteConvert16(self.receBuf[2],self.receBuf[3])
        tempAddr = addr
        CoilNum = self.receBuf[4] << 8 | self.receBuf[5]
        byteCount = (CoilNum + 7) // 8
        for k in range(0, byteCount, 1):
            self.sendBuf[k + 3] = 0
            for i in range(0, 8, 1):
                tempData = self.getCoilVal(tempAddr)
                self.sendBuf[k + 3] |= (tempData << i)
                tempAddr += 1
                if (tempAddr >= (addr + CoilNum)):  
                    exit = 1
                    break
            if exit == 1:
                break
        self.sendBuf[0] = self.localAddr  
        self.sendBuf[1] = self.receBuf[1] 
        self.sendBuf[2] = byteCount  
        byteCount += 3  
        crcData = self.crc16(self.sendBuf, byteCount)  
        self.sendBuf[byteCount] = crcData >> 8  
        byteCount += 1
        self.sendBuf[byteCount] = crcData & 0xff  
        byteCount += 1
        self.beginSend(byteCount)

    def setCoilVal(self,addr,tempData):
        result = 0
        tempAddr = addr & 0x0fff
        self.CoilData[tempAddr] = tempData
        if tempAddr < self.CoilLen:
            result = self.eeprom.writeByteToMem(self.ModbusCoilAdd + tempAddr,tempData)
        return  result

    def setRegisterVal(self,addr,tempData):
        result = 0
        tempAddr = addr & 0x0fff
        self.RegData[tempAddr] = tempData
        if tempAddr < self.RegLen:
            result =1
        return result

    def forceSingleCoil(self):
        addr = self.receBuf[2] << 8 | self.receBuf[3]
        tempAddr = addr
        onOff = self.receBuf[4] << 8 | self.receBuf[5]
        if onOff == 0xff00:
            tempData = 1    
        elif onOff == 0x0000:
            tempData = 0    
        self.setCoilVal(tempAddr,tempData)
        for i in range(0,self.receCount,1):
            self.sendBuf[i] = self.receBuf[i]
        self.beginSend(self.receCount)
    def ForceMultipleCoils(self):
        finish = 0
        addr = self.byteConvert16(self.receBuf[2], self.receBuf[3])
        CoilNum = self.receBuf[4] << 8 | self.receBuf[5]
        byteCount = self.receBuf[6]
        tempAddr = addr
        for k in range(0,byteCount,1):
            for i in range(0,8,1):
                tempData = (self.receBuf[k+7]) >> i & 0x01 
                self.setCoilVal(tempAddr,tempData)
                tempAddr += 1
                if (tempAddr >= (CoilNum + addr)):
                    finish = 1
                    break
            if 1 == finish:
                break

        self.sendBuf[0] = self.localAddr  # 从地址
        self.sendBuf[1] = self.receBuf[1]  # 功能号
        self.sendBuf[2] = addr >> 8 #地址高位
        self.sendBuf[3] = addr & 0x0ff #
        self.sendBuf[4] = CoilNum >> 8 #
        self.sendBuf[5] = CoilNum & 0x0ff #
        crcData = self.crc16(self.sendBuf, 6)  # 产生校验数据
        self.sendBuf[6] = crcData >> 8  # 校验数据高位
        self.sendBuf[7] = crcData & 0xff  # 校验数据低位
        self.beginSend(8)

    def getRegisterVal(self,dataAddr):
        if dataAddr>self.RegLen:
            dataAddr = self.RegLen
        tempAddr = dataAddr & 0x0fff
        tempData = self.RegData[tempAddr]
        return tempData

    def readRegisters(self):
        addr = self.byteConvert16(self.receBuf[2], self.receBuf[3])
        tempAddr = addr
        readCount= self.receBuf[4] << 8 | self.receBuf[5]
        byteCount = readCount * 2
        for i in range(0, byteCount, 2):
            tempData = self.getRegisterVal(tempAddr)
            self.sendBuf[i+3] = tempData >> 8
            self.sendBuf[i+4] = tempData & 0xff
            tempAddr += 1
        self.sendBuf[0] = self.localAddr 
        self.sendBuf[1] = self.receBuf[1]  
        self.sendBuf[2] = byteCount  
        byteCount += 3  
        crcData = self.crc16(self.sendBuf, byteCount)  
        self.sendBuf[byteCount] = crcData >> 8  
        byteCount += 1
        self.sendBuf[byteCount] = crcData & 0xff  
        byteCount += 1
        self.beginSend(byteCount)

    def writetSingleRegister(self):
        addr = self.receBuf[2] << 8 | self.receBuf[3]
        tempAddr = addr
        ReVal = self.receBuf[4] << 8 | self.receBuf[5]
        tempData = ReVal
        self.setRegisterVal(tempAddr,tempData)
        for i in range(0, self.receCount, 1):
            self.sendBuf[i] = self.receBuf[i]
        self.beginSend(self.receCount)

    def SetMultipleRegisters(self):
        addr = self.receBuf[2] << 8 | self.receBuf[3]     
        setCount = self.receBuf[4] << 8 | self.receBuf[5] 
        byteCount = self.receBuf[6] 
        tempAddr = addr
        for i in range(0,setCount,1):
            tempData = (self.receBuf[i*2+7] << 8) | self.receBuf[i*2+8]
            self.setRegisterVal(tempAddr,tempData)
            tempAddr += 1

        self.sendBuf[0] = self.localAddr  
        self.sendBuf[1] = self.receBuf[1]  
        self.sendBuf[2] = addr >> 8  
        self.sendBuf[3] = addr & 0x0ff 
        self.sendBuf[4] = setCount >> 8  
        self.sendBuf[5] = setCount & 0x0ff 
        crcData = self.crc16(self.sendBuf, 6)  
        self.sendBuf[6] = crcData >> 8  
        self.sendBuf[7] = crcData & 0xff  
        self.beginSend(8)

    def InitCoilAndReg(self):
        self.CoilData[0] = 1
        self.CoilData[1] = 3
        self.RegData[0] = 0
        self.RegData[1] = 0

    def RegAssign(self,Reg_Addr,Reg_Dat):
        self.RegData[Reg_Addr] = Reg_Dat

    def modbusHandle(self):
        self.UsartxDataRec()
        if(self.receCount >= 4):
            if((self.receBuf[1] == 0x01) 
            or (self.receBuf[1] == 0x02)
            or (self.receBuf[1] == 0x03)
            or (self.receBuf[1] == 0x04)
            or (self.receBuf[1] == 0x05)
            or (self.receBuf[1] == 0x06)):
                
                if(self.receCount >= 8): 
                    if((self.receBuf[0] == self.localAddr) and (self.checkoutError == 0)):
                        crcData = self.crc16(self.receBuf,6)
                        TcrcD = self.receBuf[6] << 8 | self.receBuf[7]
                        if(crcData == TcrcD):  
                            if((self.receBuf[1] == 1) or       
                               (self.receBuf[1] == 2)):        
                                self.readCoil()
                            elif ((self.receBuf[1] == 3) or
                                 (self.receBuf[1] == 4)): 
                                self.readRegisters()
                            elif self.receBuf[1] == 5:
                                self.forceSingleCoil()
                            elif self.receBuf[1] == 6:
                                self.writetSingleRegister()
                    self.receCount = 0
                    self.checkoutError = 0
            elif self.receBuf[1] == 15:   
                tempData = self.receBuf[6]
                tempData += 9
                if(self.receCount >= tempData):
                    if ((self.receBuf[0] == self.localAddr) and (self.checkoutError == 0)):
                        crcData = self.crc16(self.receBuf,tempData - 2)
                        TcrcD = (self.receBuf[tempData - 2] << 8) + self.receBuf[tempData - 1]
                        if(crcData == TcrcD):
                            self.ForceMultipleCoils()
                    self.receCount = 0
                    self.checkoutError = 0
            elif self.receBuf[1] == 16:  
                tempData = self.receBuf[4] << 8 | self.receBuf[5]
                tempData = tempData * 2
                tempData += 9
                if (self.receCount >= tempData):
                     if ((self.receBuf[0] == self.localAddr) and (self.checkoutError == 0)):
                        crcData = self.crc16(self.receBuf, tempData - 2)
                        TcrcD = (self.receBuf[tempData - 2] << 8) + self.receBuf[tempData - 1]
                        if (crcData == TcrcD):
                            self.SetMultipleRegisters()
                     self.receCount = 0
                     self.checkoutError = 0
            else:
                if self.receCount >= 8:
                    self.clearReceBuf()

m_bus = MODBUS() 