import serial

import sqlite3

DB_FILE = r"C:\Users\user01\Desktop\UIDアンマッチ\documents.db"

def get_document(docnum): 
    return cur.execute("select * from documents where docnum = '%s';" % (docnum,)).fetchall()

def open_comport():
  ser = serial.Serial('COM1', baudrate=38400, parity=serial.PARITY_NONE)
  ser.timeout = 0.3
  return ser


# rawdata = ser.read(323)

rawdata = b'\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00\x00\x00\x00\x00\x03\xdf\r\x02\x00L\x18\xc8\xffG\x87P\x01\x04\xe0\x1a \xf2a\x06\xb1\xba\xae\x00\x00\x00\x00'

r_data = rawdata.split(b"\r")[1]

cmd_rdloop_button = "02 00 4E 04 00 58 00 BC 03 6B 0D"
cmd_command_button = "02 00 4E 04 00 00 00 BC 03 13 0D"
cmd_rdloop_custom = "02 00 78 06 F2 A0 00 00 10 00 03 25 0D"
cmd_rdloop_custom_recv = "02 00 30 01 F2 03 28 0D"
recv_button = "02 00 30 00 03 35 0D"
cmd_get_current_mode = "02 00 4F 01 00 03 55 0D"

cmd_get_rom_version = "02 00 4F 01 90 03 E5 0D"
cmd_get_rom_version_recv = "02 00 30 0A 90 31 33 30 30 36 30 38 32 38 03 9B 0D"
rom_version = "ROMバージョン : 1.30 060828"
#>>>" 31 33 30 30 36 30 38 32 38".replace(" 3","")
#'130060828'
cmd_rdloop_custom2 = "02 00 4E 04 00 58 00 8C 03 3B 0D"
cmd_rdloop_custom2_recv = "02 00 30 00 03 35 0D"


def write_cmd(ser, command):
    w_data = bytes.fromhex(command.replace(" ",""))
    return ser.write(w_data)

def get_siryounum(r_data):
    #return str(int(r_data[16:20].hex(), 16))
    return str(int.from_bytes(r_data[16:20], "big"))

def get_uidnum(r_data):
    return r_data[11:3:-1].hex().upper()

def get_romversion(r_data):
    verstring = bytes.decode(r_data[5:-3], "ascii")
    return "ROM version: %1s.%2s %s" % (verstring[0], verstring[1:3], verstring[3:])

formathex = lambda data: " ".join([data[n:n+2] for n in range(0,len(data),2)]).upper()

"""
>>> get_siryounum(r_data)
'112310958'

>>> get_uidnum(r_data)
'E00401508747FFC8'
"""

"""
>>> for i,n in enumerate(r_data):
	print("%i,%02x" % (i,n))

	
0,02
1,00
2,4c
3,18
4,c8
5,ff
6,47
7,87
8,50
9,01
10,04
11,e0
12,1a
13,20
14,f2
15,61
16,06
17,b1
18,ba
19,ae
20,00
21,00
22,00
23,00
24,00
25,00
26,00
27,00
28,03
29,df
"""


if __name__  == '__main__':
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    ser = open_comport()
    write_cmd(ser, cmd_get_rom_version)
    r_data = ser.read_until(b"\r")
    if len(r_data) != 0 and r_data[0:2].hex() == '0200' and r_data[-3:].hex() == '039b0d':
        romversion = get_romversion(r_data)
        print(romversion)
    else:
        print("cannot get rom version.")
    
    write_cmd(ser, cmd_get_current_mode)
    ret = ser.read_until(b"\r")
    print(formathex(ret.hex()))

    write_cmd(ser, cmd_rdloop_custom)
    ret = ser.read_until(b"\r")
    print(formathex(ret.hex()))

    while(True):
        r_data = ser.read_until(b"\r")
        if len(r_data) != 0:
            formathex(r_data.hex())
            
        if len(r_data) != 0 and r_data[0:2].hex() == '0200' and r_data[-3:].hex() == '03df0d':
            print(u"UID-num: " + get_uidnum(r_data))
            docnum = get_siryounum(r_data)
            print(u"siryo-num: " + docnum)
            docinfo = get_document(docnum)
            if len(docinfo) == 0:
                print(u"該当する資料番号なし")
            else:
                print(docinfo)
    
    
    
    
