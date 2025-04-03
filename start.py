import asyncio
from bleak import BleakScanner

async def run():
    print("Iniciando a varredura por dispositivos Bluetooth...")
    devices = await BleakScanner.discover()
    
    for d in devices:
        print(f"Dispositivo: {d.name}, Endereço: {d.address}, RSSI: {d.rssi}")
        
        # Verifica se há dados do fabricante (possivelmente contendo informações do iBeacon)
        if d.metadata.get("manufacturer_data"):
            for manuf_id, manuf_data in d.metadata["manufacturer_data"].items():
                print(f"  ID do fabricante: {manuf_id}, Dados: {manuf_data.hex()}")
                
                # Verifica se é um iBeacon (ID do fabricante 76, que é 0x004C)
                if manuf_id == 76 and len(manuf_data) >= 22:
                    # Estrutura típica do pacote iBeacon:
                    # Bytes 0-1: Prefixo (ex: 0x02, 0x15)
                    # Bytes 2-17: UUID
                    # Bytes 18-19: Major
                    # Bytes 20-21: Minor
                    # Byte 22: TX Power
                    uuid = manuf_data[2:18]
                    major = int.from_bytes(manuf_data[18:20], byteorder='big')
                    minor = int.from_bytes(manuf_data[20:22], byteorder='big')
                    tx_power = int.from_bytes(manuf_data[22:23], byteorder='big', signed=True)
                    
                    print("  >> iBeacon detectado:")
                    print(f"     UUID: {uuid.hex()}")
                    print(f"     Major: {major}")
                    print(f"     Minor: {minor}")
                    print(f"     TX Power: {tx_power}")
                    
                    # Estimar a distância usando a fórmula de perda de caminho
                    # Supondo n = 2 (valor comum para ambiente livre)
                    n = 2  
                    distance = 10 ** ((tx_power - d.rssi) / (10 * n))
                    print(f"     Distância aproximada: {distance:.2f} metros")
        print("-" * 40)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
