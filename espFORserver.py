import asyncio
import serial
import serial.tools.list_ports
import requests
import getpass
import psutil

async def send_data(data, username_pc):
    try:
        url = 'https://hardtech-ibos.onrender.com/'+'PC/user/'
        # url = 'http://127.0.0.1:8000/'+'PC/user/'
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
        print(f'> {response.status_code} [POST] {url} - {payload}')
        try: power: bool = response.json()['power']
        except Exception as e: print(f'[!] < {e}')
        if power:
            print('Desligar')
            r_put = requests.put(f'https://hardtech-ibos.onrender.com/PC/power/{username_pc}/', json={"power": False})
            
            if r_put.status_code == 200:
                import platform
                import os
                sistema_operacional = platform.system()

                if sistema_operacional == 'Windows':
                    os.system('shutdown /s /t 1')
                elif sistema_operacional == 'Linux' or sistema_operacional == 'Darwin':
                    os.system('sudo shutdown now' if sistema_operacional == 'Linux' else 'sudo shutdown -h now')
                else:
                    print(f'Sistema operacional {sistema_operacional} não suportado para o desligamento.')

            print('Desligado')
        else:
            print('não Desligar')
        # print(f'< {response.text}')
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
                # if port.device != 'COM1':
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