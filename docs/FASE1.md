# Fase 1: puesta en marcha

Requisitos: Node 24, Python 3.10 o superior, cuenta de GitHub y cuenta de Cloudflare.
No necesitas dominio propio: el sitio usa una dirección `workers.dev`.

## 1. Copiar los archivos
Descomprime el ZIP en la raíz de tu repo, en tu rama de trabajo.
Si ya tienes `.gitignore`, combina ambos en lugar de reemplazarlo.

## 2. Probar en tu equipo
    npm install
    npm run dev          # http://localhost:4321
    npm run build

`npm install` crea `package-lock.json`. **Súbelo al repo**: el pipeline usa `npm ci`.

## 3. Agregar fotos
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    python scripts/preparar_fotos.py originales/danza danza --autor "Tu Nombre"
    python scripts/check_fotos.py

Repite con `retrato` y `comercial-alimentos`. Nombra las originales de forma
descriptiva: el nombre se usa como texto alternativo.
Si el repo es público, las fotos también se pueden descargar desde GitHub.
Publica solo fotos para las que tengas autorización.
El script baja la calidad por pasos para no pasar de 1.5 MB; revisa el resultado.

## 4. Primer despliegue (manual, una sola vez)
Las vistas previas requieren que el Worker ya exista. Revisa antes el nombre en
`wrangler.jsonc` y tu nombre en `src/data/sitio.ts`.

    npx wrangler login
    npm run build
    npx wrangler deploy

Wrangler te mostrará la URL pública.

## 5. Configurar GitHub
En Cloudflare, crea un token de API con la plantilla **Edit Cloudflare Workers**,
limitado a tu cuenta. En GitHub: Settings > Secrets and variables > Actions.

| Tipo     | Nombre                  | Valor                     |
|----------|-------------------------|---------------------------|
| Secret   | `CLOUDFLARE_API_TOKEN`  | el token                  |
| Secret   | `CLOUDFLARE_ACCOUNT_ID` | ID de tu cuenta           |
| Variable | `SITE_URL`              | URL pública del paso 4    |

Nunca guardes el token en el repo.

## 6. Primer pull request
Abre un PR de tu rama hacia `main` (si tu rama principal tiene otro nombre,
cámbialo en el workflow). La URL de vista previa aparece en el log del paso
"Publicar vista previa". Al hacer merge se despliega a producción.

## 7. Simulacro de rollback
Hazlo antes de confiar en él. En una rama, agrega a `RUTAS` en
`scripts/smoke_test.py` una ruta inexistente con código 200, por ejemplo
`"/simulacro/": 200`, y haz merge. Resultado esperado: despliega, falla el
smoke test y restaura la versión previa. Comprueba el ID con
`npx wrangler deployments status`. Después revierte el cambio y documenta lo
ocurrido: es tu primer postmortem.

Nota: tras un rollback, `main` sigue conteniendo el cambio defectuoso.
Corrígelo o reviértelo con un nuevo PR.
