"""
run_local.py — Punto de entrada para correr el tablero localmente.

Uso:
    python run_local.py              # Genera datos frescos y abre el servidor
    python run_local.py --port 9000  # Puerto personalizado
    python run_local.py --no-fetch   # Solo levanta servidor, sin regenerar datos
"""

import argparse
import os
import subprocess
import sys
import threading
import time
import http.server
import socketserver
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_data():
    """Genera/actualiza data.json. Usa IA si hay GROQ_API_KEY, si no Polymarket."""
    script = os.path.join(BASE_DIR, "update_board.py")
    print("\n── Generando datos ─────────────────────────────────────────")
    result = subprocess.run([sys.executable, script], cwd=BASE_DIR)
    if result.returncode != 0:
        print("⚠  update_board.py falló. Intenta correr fetch_data.py manualmente.")
    print("────────────────────────────────────────────────────────────\n")


def serve(port: int):
    """Levanta un servidor HTTP local sirviendo los archivos del proyecto."""
    os.chdir(BASE_DIR)

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Silencia los logs de cada petición para no saturar la terminal
            pass

    with socketserver.TCPServer(("", port), QuietHandler) as httpd:
        print(f"Servidor corriendo en: http://localhost:{port}")
        print("Presiona Ctrl+C para detener.\n")
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Tablero de Probabilidades — Servidor Local")
    parser.add_argument("--port", type=int, default=8000, help="Puerto HTTP (default: 8000)")
    parser.add_argument("--no-fetch", action="store_true", help="No regenerar datos, solo servir")
    args = parser.parse_args()

    print("=" * 60)
    print("  TABLERO DE PROBABILIDADES GEOPOLÍTICO")
    print("=" * 60)

    if not args.no_fetch:
        fetch_data()

    # Abrir navegador medio segundo después de levantar el servidor
    url = f"http://localhost:{args.port}"
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        serve(args.port)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: el puerto {args.port} ya está en uso.")
            print(f"Prueba con otro puerto: python run_local.py --port {args.port + 1}")
        else:
            raise


if __name__ == "__main__":
    main()
