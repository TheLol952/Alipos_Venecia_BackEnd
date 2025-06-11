import json
from procedimientos.DiccionarioSucursales import ObtenerSucursal 

if __name__ == "__main__":
    json_ejemplo = json.loads(input("Ingrese el JSON a analizar: ")) 

    print("🚀 Iniciando prueba automática...")
    sucursal = ObtenerSucursal(json_ejemplo)
    print(f"RESPUESTA TEST DICCIONARIOSUC: {sucursal}")