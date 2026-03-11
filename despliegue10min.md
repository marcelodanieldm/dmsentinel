🚀 Guía de Despliegue Relámpago: DM Global

Sigue estos pasos para pasar de código local a una operación global activa.

1. El Frontend (Landing Page) en Vercel [2 min]

Vercel es el hogar natural para nuestra App de React.

Sube el código a GitHub: Crea un repositorio privado llamado dm-global-web.

Conecta con Vercel: Ve a vercel.com, dale a "Add New Project" e importa tu repo.

Configuración: Vercel detectará automáticamente que es React. Dale a "Deploy".

Resultado: Tendrás una URL tipo dm-global.vercel.app (puedes apuntar tu dominio .com luego).

2. El Backend (Automation Engine) en Render [4 min]

Para que el script de Python reciba Webhooks de Stripe 24/7 sin pagar un VPS caro.

Repositorio: Crea otro repo (o usa una carpeta en el mismo) para sentinel_engine.py.

Despliegue en Render: Ve a render.com y crea un "Web Service".

Variables de Entorno (CRÍTICO): En la pestaña "Environment", añade:

STRIPE_WEBHOOK_SECRET: El secreto de tu dashboard de Stripe.

TELEGRAM_BOT_TOKEN: El token de BotFather.

TELEGRAM_CHAT_ID: Tu ID de usuario.

Archivo de Credenciales: Sube tu credentials.json (de Google Cloud) o pega su contenido en una variable de entorno llamada GOOGLE_CREDS y léela en el código.

3. El Cronjob (Escaneo Programado) vía GitHub Actions [3 min]

Si quieres que el script de scraping de vulnerabilidades CMS corra solo cada 24 horas sin un servidor encendido:

En tu repo de GitHub, crea la carpeta .github/workflows/.

Crea el archivo audit_cron.yml (ver código abajo).

Resultado: GitHub ejecutará el escaneo gratis todos los días a la medianoche.

4. Conexión de Stripe [1 min]

Ve al Dashboard de Stripe > Developers > Webhooks.

Añade la URL que te dio Render: https://tu-app-en-render.com/webhooks/stripe.

Selecciona el evento checkout.session.completed.

¡LISTO! DM Global ya es una entidad viva en la nube.