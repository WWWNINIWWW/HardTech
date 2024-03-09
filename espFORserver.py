import asyncio
import serial
import serial.tools.list_ports
import requests
import getpass
import psutil

async def send_data(data, username_pc):
    try:
        url = 'https://hardtech-ibos.onrender.com/'+'PC/user/'
        headers = {'Content-Type': 'application/json'}
        itens = data.split(';')
        payload = {
            'user': username_pc,
            "dados": [
                {
                    'temperatura': float(itens[0]),
                    'uso_CPU': float(psutil.cpu_percent(interval=1)),
                    'uso_RAM': float(psutil.virtual_memory().percent)
                }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        #print(response.text)
    except Exception as e:
        print(e)
        pass

async def read_and_send(ser):
    while True:
        try:
            data = ser.readline().decode().strip()
            if data:
                print(f"< {data}")
                await send_data(data, username_pc=getpass.getuser())
        except serial.SerialException:
            print("> Porta serial desconectada. Tentando reconectar...")
            ser.close()
            ser = await connect_to_esp32()

async def connect_to_esp32():
    while True:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, 115200, timeout=1)
                print(f"> Conectado à porta serial {port.device}")
                return ser
            except serial.SerialException:
                pass
        print("> Nenhuma porta serial encontrada. Tentando novamente em 1 segundo...")
        await asyncio.sleep(1)

async def main():
    ser = await connect_to_esp32()
    asyncio.create_task(read_and_send(ser))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
