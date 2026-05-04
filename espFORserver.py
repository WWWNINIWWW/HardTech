
import asyncio
import serial
import serial.tools.list_ports
import requests
import getpass
import psutil
import platform
import os

async def send_data(data, username_pc, ser):
    try:
        # Mantendo a rota de envio original
        # url = 'https://hardtech-ibos.onrender.com/'+'PC/user/'
        url = 'http://192.168.3.125:8080/PC/user/'
        
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
        
        # Só verifica se a requisição de envio funcionou (200 OK ou 201 Created)
        if response.status_code in [200, 201]:
            try: 
                res_data = response.json()
                update_flag = res_data.get('update', False)
                mode_fan = res_data.get('mode_fan', 0)
            except Exception as e: 
                print(f'[!] Erro ao ler JSON da resposta: {e}')
                update_flag = False

            # Se update for True, envia o modo para a serial e reseta a flag
            if update_flag:
                print(f'> Update detectado! Modo da Fan recebido: {mode_fan}')
                
                # Monta o comando (ex: "FAN_MODE:1\n") e envia para o ESP32
                comando = f"FAN_MODE:{mode_fan}\n"
                ser.write(comando.encode('utf-8'))
                print(f"> Comando enviado para o ESP32: {comando.strip()}")
                
                # Rota de PUT para resetar a flag update para False
                # (Se o seu Django usar o prefixo /PC/, mude para /PC/fans/...)
                url_update = f'http://192.168.3.125:8080/PC/fans/{username_pc}/update/'
                
                r_put = requests.put(url_update, json={"update": False})
                
                if r_put.status_code == 200:
                    print("> Flag 'update' resetada para False no servidor.")
                else:
                    print(f"> Falha ao resetar 'update'. Status: {r_put.status_code}")
            else:
                pass # Nenhuma atualização pendente
            
    except Exception as e:
        print(f"Erro no send_data: {e}")
        pass

async def read_and_send(ser):
    while True:
        try:
            data = ser.readline().decode().strip()
            if data:
                print(f"< Recebido do ESP: {data}")
                await send_data(data, username_pc=getpass.getuser(), ser=ser)
        except serial.SerialException:
            print("> Porta serial desconectada. Tentando reconectar...")
            ser.close()
            ser = await connect_to_esp32()
            await asyncio.sleep(2) 

async def connect_to_esp32():
    while True:
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                if port.device != 'COM1':
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