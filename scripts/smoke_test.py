#!/usr/bin/env python3
"""Comprueba que el sitio publicado responde y sirve el commit esperado.

Uso: python scripts/smoke_test.py https://mi-sitio.workers.dev --sha <commit>
"""
import argparse
import sys
import time
import urllib.error
import urllib.request

RUTAS = {
    "/": 200,
    "/danza/": 200,
    "/retrato/": 200,
    "/comercial-alimentos/": 200,
    "/no-existe-smoke-test/": 404,
}


def pedir(url: str) -> tuple[int, str]:
    solicitud = urllib.request.Request(
        url, headers={"User-Agent": "smoke-test/1.0", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(solicitud, timeout=10) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, ""


def revisar(base: str, sha: str) -> list[str]:
    fallas = []
    for ruta, esperado in RUTAS.items():
        try:
            estado, cuerpo = pedir(base + ruta)
        except OSError as error:
            fallas.append(f"{ruta}: sin respuesta ({error})")
            continue
        if estado != esperado:
            fallas.append(f"{ruta}: HTTP {estado}, esperaba {esperado}")
        elif sha and estado == 200 and f'content="{sha}"' not in cuerpo:
            fallas.append(f"{ruta}: todavía no sirve el commit {sha[:7]}")
    return fallas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--sha", default="")
    parser.add_argument("--intentos", type=int, default=6)
    parser.add_argument("--espera", type=float, default=10)
    args = parser.parse_args()
    if not args.url.startswith(("http://", "https://")):
        print(f"URL inválida: '{args.url}'", file=sys.stderr)
        return 2

    for intento in range(1, args.intentos + 1):
        fallas = revisar(args.url.rstrip("/"), args.sha)
        if not fallas:
            print("Smoke test OK")
            return 0
        print(f"Intento {intento}/{args.intentos}:", *fallas, sep="\n  ")
        if intento < args.intentos:
            time.sleep(args.espera)
    return 1


if __name__ == "__main__":
    sys.exit(main())
