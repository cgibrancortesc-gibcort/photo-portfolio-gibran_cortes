#!/usr/bin/env python3
"""Redimensiona fotos, las pasa a sRGB y elimina sus metadatos (incluido GPS).

Uso: python scripts/preparar_fotos.py originales/danza danza --autor "Tu Nombre"
"""
import argparse
import io
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

SECCIONES = ("danza", "retrato", "comercial-alimentos")
LADO_MAXIMO = 2400
PESO_MAXIMO = 1_500_000  # bytes, igual que en check_fotos.py
EXTENSIONES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
DESTINO = Path(__file__).resolve().parent.parent / "src" / "assets" / "fotos"


def slug(texto: str) -> str:
    plano = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plano.lower()).strip("-") or "foto"


def a_srgb(img: Image.Image) -> Image.Image:
    """Convierte usando el perfil incrustado (p. ej. Adobe RGB) para no alterar color."""
    perfil = img.info.get("icc_profile")
    if perfil:
        return ImageCms.profileToProfile(
            img,
            ImageCms.ImageCmsProfile(io.BytesIO(perfil)),
            ImageCms.createProfile("sRGB"),
            outputMode="RGB",
        )
    return img.convert("RGB")


def procesar(origen: Path, salida: Path, autor: str) -> None:
    with Image.open(origen) as original:
        img = ImageOps.exif_transpose(original)  # respeta la orientación
        img = a_srgb(img)
    img.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.Resampling.LANCZOS)

    limpia = Image.new("RGB", img.size)  # imagen nueva: sin metadatos heredados
    limpia.paste(img)
    exif = Image.Exif()
    if autor:
        ascii_autor = unicodedata.normalize("NFKD", autor).encode("ascii", "ignore").decode()
        exif[0x013B] = ascii_autor  # Artist
        exif[0x8298] = f"(c) {ascii_autor}"  # Copyright
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    # Baja la calidad por pasos hasta respetar el límite de peso
    for calidad in (85, 80, 75, 70, 65, 60):
        limpia.save(salida, "JPEG", quality=calidad, optimize=True, progressive=True,
                    exif=exif, icc_profile=srgb)
        if salida.stat().st_size <= PESO_MAXIMO:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origen", type=Path, help="carpeta con las originales")
    parser.add_argument("seccion", choices=SECCIONES)
    parser.add_argument("--autor", default="", help="crédito que se guarda en la foto")
    args = parser.parse_args()

    if not args.origen.is_dir():
        print(f"No existe la carpeta: {args.origen}", file=sys.stderr)
        return 1
    fotos = sorted(p for p in args.origen.iterdir() if p.suffix.lower() in EXTENSIONES)
    if not fotos:
        print("No encontré fotos JPG, PNG o TIFF.", file=sys.stderr)
        return 1

    carpeta = DESTINO / args.seccion
    carpeta.mkdir(parents=True, exist_ok=True)
    errores = 0
    for foto in fotos:
        salida = carpeta / f"{slug(foto.stem)}.jpg"
        if salida.exists():
            print(f"OMITIDA {foto.name}: ya existe {salida.name}")
            continue
        try:
            procesar(foto, salida, args.autor)
            print(f"OK {foto.name} -> {salida.name} ({salida.stat().st_size // 1024} KB)")
        except (OSError, ImageCms.PyCMSError) as error:
            print(f"ERROR {foto.name}: {error}", file=sys.stderr)
            errores += 1
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
