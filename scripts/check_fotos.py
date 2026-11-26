#!/usr/bin/env python3
"""Puerta de calidad: falla si alguna foto del repo incumple las reglas."""
import re
import sys
from pathlib import Path

from PIL import Image

CARPETA = Path(__file__).resolve().parent.parent / "src" / "assets" / "fotos"
LADO_MAXIMO = 2400
PESO_MAXIMO = 1_500_000  # bytes
NOMBRE_VALIDO = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.jpg$")
GPS_IFD = 0x8825


def revisar(foto: Path) -> list[str]:
    if not NOMBRE_VALIDO.match(foto.name):
        return ["nombre inválido (usa minúsculas, números, guiones y .jpg)"]
    fallas = []
    if foto.stat().st_size > PESO_MAXIMO:
        fallas.append(f"pesa más de {PESO_MAXIMO // 1000} KB")
    try:
        with Image.open(foto) as img:
            if img.format != "JPEG":
                fallas.append("no es un JPEG")
            if max(img.size) > LADO_MAXIMO:
                fallas.append(f"lado mayor de {LADO_MAXIMO} px")
            xmp = img.info.get("xmp", b"")
            if GPS_IFD in img.getexif() or b"GPS" in xmp:
                fallas.append("contiene datos GPS")
    except OSError as error:
        fallas.append(f"no se puede leer: {error}")
    return fallas


def main() -> int:
    fotos = [p for p in CARPETA.rglob("*") if p.is_file() and p.name != ".gitkeep"]
    malas = 0
    for foto in sorted(fotos):
        fallas = revisar(foto)
        if fallas:
            malas += 1
            print(f"FALLA {foto.relative_to(CARPETA)}: {'; '.join(fallas)}")
    print(f"{len(fotos)} archivos revisados, {malas} con fallas")
    return 1 if malas else 0


if __name__ == "__main__":
    sys.exit(main())
