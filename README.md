# Portafolio fotográfico

Sitio de fotografía de danza, retrato y comercial de alimentos, construido con
Astro y preparado para operarse con prácticas de SRE.

## Arquitectura
- **Astro:** sitio estático
- **Cloudflare Workers (assets estáticos):** hospedaje
- **GitHub Actions:** integración y despliegue continuos
- **Python y Pillow:** preparación y validación de fotografías

## Cómo se opera este sitio
1. Cada pull request hacia `main` valida las fotos y construye el sitio.
2. Si pasa y la rama pertenece a este repo, se publica una vista previa.
3. Al integrar en `main` se despliega a producción.
4. Un smoke test comprueba las rutas y que responda el commit recién desplegado.
5. Si el smoke test falla, se intenta restaurar la versión que estaba activa.

## Decisiones de diseño
- **Construir una vez:** se despliega lo construido en esa misma ejecución.
- **Concurrencia controlada:** no hay dos ejecuciones simultáneas sobre `main`.
- **Rollback a una versión concreta:** se anota su ID antes de desplegar, porque
  la versión inmediata anterior podría ser una vista previa.
- **Privacidad de las fotos:** el procesamiento elimina el GPS y el resto de los
  metadatos originales; el pipeline rechaza fotos con datos GPS.
- **Presupuesto de imagen:** máximo 2400 px por lado y 1.5 MB por foto.

## Uso local
    nvm use
    npm install
    npm run dev

La puesta en marcha completa y el simulacro de rollback están en
[docs/FASE1.md](docs/FASE1.md).

## Estado y siguientes pasos
- [ ] Compilación verificada
- [ ] Primer despliegue
- [ ] Simulacro de rollback
- [ ] Monitoreo y SLOs
- [ ] Infraestructura como código con Terraform
