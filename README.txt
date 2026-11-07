TIKTOK DOWNLOADER - PROYECTO PARA DESPLEGAR

IMPORTANTE
- Este proyecto descarga videos públicos que yt-dlp pueda obtener sin iniciar sesión ni eludir controles.
- No elimina marcas de agua ni atribución. Para publicar en TikTok, usa videos propios o con permiso expreso del titular.
- No introduzcas contraseñas, cookies ni credenciales de TikTok.
- TikTok puede cambiar su sistema y hacer que la descarga deje de funcionar; yt-dlp debe mantenerse actualizado.

PUBLICAR EN INTERNET (necesario para instalarlo como PWA en iPhone)
1. Crea una cuenta en GitHub y un repositorio nuevo llamado tiktok-downloader.
2. Descomprime este ZIP en tu PC.
3. Sube TODO el contenido de la carpeta al repositorio (app.py, Dockerfile, requirements.txt, render.yaml y static/).
4. Entra en https://render.com/ y crea una cuenta.
5. En Render: New + -> Web Service -> conecta el repositorio de GitHub.
6. Render detectará el Dockerfile. Pulsa Deploy.
7. Cuando termine, abre la URL https://...onrender.com que te entrega Render.

INSTALAR EN IPHONE
1. Abre la URL de Render en Safari (no dentro de TikTok ni de otra app).
2. Pulsa Compartir.
3. Elige Añadir a pantalla de inicio.
4. Pulsa Añadir.

USO
1. Copia el enlace de un video público de TikTok.
2. Pégalo en la aplicación.
3. Pulsa Descargar.
4. En iPhone, abre el archivo descargado y usa Compartir -> Guardar vídeo si iOS no lo guarda directamente en Fotos.

LIMITACIONES
- El plan gratuito de Render puede suspender el servicio por inactividad y tardar en despertar.
- Algunos videos no se podrán descargar por restricciones de privacidad, región, edad, disponibilidad o cambios técnicos de TikTok.
- La descarga no concede derechos para volver a publicar el contenido.
