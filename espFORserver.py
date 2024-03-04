import asyncio
import serial
import serial.tools.list_ports
import requests
import getpass

async def send_data(data, username_pc):
    try:
        url = 'http://127.0.0.1:8000/data/'
        headers = {'Content-Type': 'application/json'}
        itens = data.split(';')
        payload = {
            'data': float(itens[0]),
            'username_pc': username_pc,
            'type_temperature': str(itens[1])
            }
        response = requests.post(url, headers=headers, json=payload)
        print(response.text)
    except Exception as e:
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
