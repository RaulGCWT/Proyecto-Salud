import multiprocessing
import time
import os
import sys
from cama import run_simulation

def start_simulation(mac):
    try:
        run_simulation(mac)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Limpiar pantalla para que se vea bien la pregunta
    os.system('cls' if os.name == 'nt' else 'clear')
    print("========================================")
    print("   BIENVENIDO AL GENERADOR WELLTECH")
    print("========================================")
    
    num_camas = 0
    while num_camas <= 0:
        try:
            # El strip() y el flush ayudan a que Docker maneje mejor la entrada
            sys.stdout.write("¿Cuántas camas quieres simular? (ej. 5): ")
            sys.stdout.flush()
            val = sys.stdin.readline().strip()
            if val:
                num_camas = int(val)
            else:
                time.sleep(1) # Espera si la entrada está vacía por delay de Docker
        except EOFError:
            time.sleep(2)
        except ValueError:
            print("❌ Por favor, introduce un número entero.")

    print(f"\n🚀 Levantando {num_camas} dispositivos...")
    procesos = []

    for i in range(num_camas):
        p = multiprocessing.Process(target=start_simulation, args=(None,))
        p.start()
        procesos.append(p)
        time.sleep(0.3)
        print(f"  [+] Dispositivo {i+1} activo (PID: {p.pid})")

    print("\n✅ Todos los dispositivos están emitiendo datos.")
    print("Presiona Ctrl+C para detener la simulación.")

    try:
        for p in procesos:
            p.join()
    except KeyboardInterrupt:
        print("\nCerrando dispositivos...")
        for p in procesos:
            p.terminate()