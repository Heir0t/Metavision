import asyncio
from bleak import BleakScanner

scan_active = True #Variável para controlar a varredura contínua
distancia_obstaculo = 10  # metros --> Distância do beacon para o obstáculo (exemplo: 10 metros)
raio_alerta = 5  # metros --> Raio de ação para alerta
beacon_em_alerta = {}  # Dicionário para armazenar o estado de alerta por beacon

async def scan_loop(): # Função assíncrona para varredura contínua por dispositivos Bluetooth
    global scan_active, beacon_em_alerta # Variáveis globais para controle da varredura e alerta ativo

    print('Iniciando varredura contínua por dispositivos Bluetooth... (Digite "sair" para parar)\n')

    while scan_active: # Enquanto a varredura estiver ativa
        devices = await BleakScanner.discover(timeout=0.3)  # timeout mínimo para varredura rápida 

        detected_uuids = set()  # Para rastrear quais UUIDs estão dentro do raio no momento

        for d in devices: # Percorre os dispositivos encontrados
            manufacturer_data = d.metadata.get('manufacturer_data') # Obtém os dados do fabricante do dispositivo
            if manufacturer_data: # Se houver dados do fabricante
                for data in manufacturer_data.values(): # Percorre os dados do fabricante
                    if len(data) >= 23: # Verifica se os dados têm o tamanho mínimo esperado
                        uuid = data[2:18] # Extrai o UUID dos dados do fabricante
                        uuid_hex = uuid.hex()
                        if uuid_hex == 'fda50693a4e24fb1afcfc6eb07647825': # Verifica se o UUID corresponde ao esperado
                            rssi = d.rssi # Obtém o RSSI (Received Signal Strength Indicator) do dispositivo
                            tx_power = int.from_bytes(data[22:23], byteorder='big', signed=True) #Obtém o TX Power dos dados do fabricante
                            n = 2 # Fator de propagação (exemplo: 2 para ambientes internos)
                            distancia_beacon = 10 ** ((tx_power - rssi) / (10 * n)) # Calcula a distância do beacon usando a fórmula de propagação do sinal

                            if distancia_beacon <= raio_alerta: # Verifica se a distância está dentro do raio de alerta
                                detected_uuids.add(uuid_hex) # Marca como dentro do raio

                                # Se nunca foi registrado como "dentro do raio" ou acabou de entrar
                                if not beacon_em_alerta.get(uuid_hex, False):
                                    beacon_em_alerta[uuid_hex] = True # Marca como dentro do raio (alertado)

                                    print('\n>> iBeacon detectado:')
                                    print(f'   UUID: {uuid_hex}')
                                    print(f'   RSSI: {rssi}')
                                    print(f'   TX Power: {tx_power}')
                                    print(f'   Distância até o beacon: {distancia_beacon:.2f} metros')

                                    distancia_usuario_obstaculo = distancia_obstaculo - distancia_beacon # Calcula a distância do usuário até o obstáculo
                                    print(f'>>> Travessia à frente detectada a aproximadamente {distancia_usuario_obstaculo:.2f} metros <<<')
                                    print('!!! ALERTA: Obstáculo próximo! Fique atento. !!!')

        # Libera o alerta novamente apenas se o beacon saiu do raio (não foi detectado na varredura atual)
        for uuid in list(beacon_em_alerta.keys()):
            if uuid not in detected_uuids:
                beacon_em_alerta[uuid] = False

        await asyncio.sleep(0.1) # Espera curta entre varreduras para maior responsividade

async def wait_for_exit(): # Função assíncrona para permitir que o usuário encerre a varredura digitando "sair"
    global scan_active
    loop = asyncio.get_event_loop()
    while scan_active:
        user_input = await loop.run_in_executor(None, input, '') # Aguarda entrada do usuário
        if user_input.strip().lower() == 'sair': # Se o usuário digitar "sair"
            scan_active = False # Encerra a varredura
            print('Encerrando varredura...')

async def main():# Função principal para iniciar a varredura contínua
    await asyncio.gather(scan_loop(), wait_for_exit()) # Executa simultaneamente a varredura e o monitoramento de saída

if __name__ == '__main__': # Executa a função principal se o script for executado diretamente
    asyncio.run(main()) # Inicia o loop de eventos assíncronos
