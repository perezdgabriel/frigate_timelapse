# Preguntas Frecuentes (FAQ)

## General

### ¿Qué es Frigate Timelapse?

Frigate Timelapse es una integración personalizada para Home Assistant que permite crear videos timelapse automáticamente desde las cámaras configuradas en Frigate NVR. Todo se gestiona desde la interfaz de Home Assistant sin necesidad de scripts externos o configuración en terminal.

### ¿Necesito conocimientos de programación?

No, la integración se instala con HACS y se configura completamente desde la interfaz gráfica de Home Assistant.

### ¿Es compatible con otras NVR además de Frigate?

Actualmente solo es compatible con Frigate. Frigate debe estar instalado y funcionando en tu red local.

## Instalación

### ¿Por qué no aparece la integración después de instalarla?

1. Asegúrate de haber reiniciado Home Assistant después de la instalación
2. Limpia la caché del navegador (Ctrl + Shift + R)
3. Verifica que HACS haya completado la descarga correctamente
4. Revisa los logs de Home Assistant para errores

### ¿Dónde se instalan los archivos?

Los archivos se instalan en:
- Integración: `/config/custom_components/frigate_timelapse/`
- Recursos frontend: `/config/custom_components/frigate_timelapse/www/`
- Capturas: `/media/timelapse/captures/`
- Videos: `/media/timelapse/`

### ¿Puedo cambiar la ubicación de los archivos?

Sí, puedes configurar la ruta de salida durante la configuración inicial o desde las opciones de la integración.

## Configuración

### ¿Qué URL debo usar para Frigate?

Depende de tu configuración:
- Si Frigate está en Docker en el mismo host: `http://frigate:5000`
- Si está en otro dispositivo: `http://IP_DEL_DISPOSITIVO:5000`
- Si usas un puerto diferente: `http://IP:PUERTO`

Ejemplo: `http://192.168.1.100:5000`

### ¿Puedo configurar múltiples cámaras?

Sí, puedes añadir la integración varias veces, una por cada cámara. Cada instancia será independiente.

### ¿Qué intervalo de captura debo usar?

Depende de lo que quieras capturar:
- **10-30 segundos**: Cambios rápidos (construcción, cocina)
- **60 segundos (1 min)**: Uso general, día típico
- **300 segundos (5 min)**: Timelapses largos (días completos)
- **600-3600 segundos (10-60 min)**: Cambios muy lentos (plantas creciendo)

Considera el espacio de almacenamiento: 1 imagen cada 60s = 1440 imágenes/día ≈ 200-500 MB

### ¿Qué resolución debo elegir?

- **1920x1080 (1080p)**: Recomendado, buen balance calidad/tamaño
- **1280x720 (720p)**: Para ahorrar espacio o cámaras de menor resolución
- **3840x2160 (4K)**: Alta calidad, requiere mucho espacio
- **2560x1440 (1440p)**: Compromiso entre 1080p y 4K

La resolución final se ajusta automáticamente a la de las imágenes originales.

### ¿Qué FPS es mejor?

- **24-30 FPS**: Estándar para video fluido
- **15-20 FPS**: Efecto más notorio de timelapse
- **60 FPS**: Para slow motion posterior o máxima suavidad

Recomendación: 30 FPS para uso general.

## Uso

### ¿Cómo inicio la captura?

Tres formas:
1. Desde la tarjeta Lovelace: botón "Iniciar"
2. Desde Developer Tools → Services: `frigate_timelapse.start_capture`
3. Con una automación (ver ejemplos en `examples/lovelapse_examples.yaml`)

### ¿Cuándo debo generar el timelapse?

Puedes generarlo en cualquier momento:
- Manualmente desde el botón "Generar Timelapse"
- Automáticamente con una automación (ej: cada noche)
- Después de detener la captura

**Nota**: Necesitas al menos 2 imágenes capturadas.

### ¿Puedo generar un timelapse de un rango específico?

Sí, usa el servicio con parámetros:

```yaml
service: frigate_timelapse.generate_timelapse
data:
  start_time: "2025-11-11 08:00:00"
  end_time: "2025-11-11 18:00:00"
  output_file: "timelapse_dia.mp4"
```

### ¿Dónde encuentro los videos generados?

Los videos se guardan en `/media/timelapse/` por defecto. Puedes acceder a ellos:
- Desde el Media Browser de Home Assistant
- Por Samba/NFS si tienes compartido `/media`
- Directamente en el sistema de archivos

### ¿Se pueden ver los videos en Home Assistant?

Sí, de varias formas:
1. Con la tarjeta personalizada (si configuras `video_path`)
2. Con una tarjeta de medios estándar:
```yaml
type: media-control
entity: media_player.tu_dispositivo
```
3. Añadiendo el directorio a `configuration.yaml`:
```yaml
media_dirs:
  timelapse: /media/timelapse
```

## Almacenamiento

### ¿Cuánto espacio necesito?

Estimación aproximada:
- **1 imagen JPG**: ~150 KB (depende de la resolución y compresión)
- **24 horas a 60s/captura**: ~200 MB
- **Video 1080p@30fps de 1 día**: ~50-200 MB (depende de la duración)

Ejemplo completo:
- Capturas durante 1 día: 200 MB
- Video final: 100 MB
- **Total por día**: ~300 MB

### ¿Se borran las imágenes después de generar el video?

No automáticamente. Las imágenes se mantienen para poder regenerar el video con diferentes configuraciones.

### ¿Cómo limpio archivos antiguos?

La integración tiene un método de limpieza que puedes llamar manualmente o programar:

```yaml
automation:
  - alias: "Limpiar timelapses antiguos"
    trigger:
      - platform: time
        at: "03:00:00"
    condition:
      - condition: time
        weekday: sun
    action:
      - service: shell_command.cleanup_timelapses

shell_command:
  cleanup_timelapses: >
    find /media/timelapse/captures -type d -mtime +7 -exec rm -rf {} +
```

Esto elimina sesiones de captura con más de 7 días.

## Problemas Comunes

### "Cannot connect to Frigate"

**Causas posibles:**
1. URL incorrecta
2. Frigate no está ejecutándose
3. Problema de red entre Home Assistant y Frigate
4. Firewall bloqueando la conexión

**Soluciones:**
1. Verifica que Frigate esté activo: `http://FRIGATE_IP:5000` en un navegador
2. Prueba la conectividad desde terminal de Home Assistant:
   ```bash
   curl http://frigate:5000/api/config
   ```
3. Revisa la configuración de red de Docker (si aplica)
4. Verifica que el puerto 5000 esté abierto

### "No cameras found in Frigate"

**Causas:**
- Frigate no tiene cámaras configuradas
- Error en la configuración de Frigate
- API de Frigate no responde correctamente

**Solución:**
1. Verifica las cámaras en la UI de Frigate
2. Revisa el `config.yml` de Frigate
3. Consulta los logs de Frigate

### "Failed to generate timelapse"

**Causas posibles:**
1. ffmpeg no está instalado
2. No hay suficientes imágenes (mínimo 2)
3. Permisos de escritura en el directorio de salida
4. Error de codificación de video

**Soluciones:**
1. Verifica ffmpeg:
   ```bash
   ffmpeg -version
   ```
   Si no está instalado: `apt-get install ffmpeg`

2. Verifica que hay imágenes capturadas:
   ```bash
   ls -la /media/timelapse/captures/SESION/
   ```

3. Verifica permisos:
   ```bash
   chmod -R 755 /media/timelapse
   ```

4. Revisa los logs de Home Assistant para el error específico de ffmpeg

### La tarjeta Lovelace no aparece

**Causas:**
1. Recurso no añadido
2. Caché del navegador
3. Error de sintaxis en la configuración

**Soluciones:**
1. Añade el recurso en Configuración → Dashboards → Recursos:
   - URL: `/local/community/frigate_timelapse/frigate-timelapse-card.js`
   - Tipo: JavaScript Module

2. Limpia caché: Ctrl + Shift + R

3. Abre la consola del navegador (F12) para ver errores

4. Verifica que el archivo existe:
   ```bash
   ls -la /config/custom_components/frigate_timelapse/www/
   ```

### Las imágenes no se capturan

**Diagnóstico:**
1. Verifica el estado del sensor: `sensor.frigate_timelapse_CAMERA_status`
2. Si no está en "capturing", inicia la captura
3. Revisa que el intervalo no sea demasiado largo
4. Verifica conectividad con Frigate

**Logs útiles:**
```yaml
logger:
  logs:
    custom_components.frigate_timelapse: debug
```

Revisa logs:
```bash
tail -f /config/home-assistant.log | grep frigate_timelapse
```

### El video generado está corrupto o no se reproduce

**Causas:**
1. Proceso de ffmpeg interrumpido
2. Espacio insuficiente en disco
3. Formato no compatible

**Soluciones:**
1. Regenera el video
2. Verifica espacio: `df -h`
3. Prueba reproducir con VLC u otro reproductor
4. Regenera con configuración diferente (resolución menor, FPS diferente)

### Error "Permission denied" al guardar

**Causa:** Permisos incorrectos en el directorio

**Solución:**
```bash
# Desde terminal de Home Assistant o SSH
sudo chown -R homeassistant:homeassistant /media/timelapse
sudo chmod -R 755 /media/timelapse
```

## Rendimiento

### ¿Afecta al rendimiento de Home Assistant?

Impacto mínimo:
- La captura de imágenes es asíncrona y no bloquea
- La generación de video usa un proceso separado
- El consumo de CPU es bajo durante la captura

La generación de video puede usar más CPU temporalmente, pero:
- Se ejecuta en proceso independiente
- No afecta otras operaciones de Home Assistant
- Típicamente dura solo unos segundos

### ¿Afecta a Frigate?

Impacto muy bajo:
- Solo se descarga una imagen cada N segundos
- Frigate ya genera los snapshots automáticamente
- No interfiere con la grabación o detección de eventos

### ¿Puedo capturar de múltiples cámaras simultáneamente?

Sí, cada cámara tiene su propia instancia de la integración y funcionan independientemente.

## Avanzado

### ¿Puedo personalizar los parámetros de ffmpeg?

Actualmente los parámetros están predefinidos. Para personalizarlos necesitarías modificar `timelapse_manager.py`:

```python
cmd = [
    "ffmpeg",
    "-y",
    "-framerate", str(self.fps),
    "-pattern_type", "glob",
    "-i", str(input_path / "frame_*.jpg"),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-preset", "medium",  # fast, medium, slow
    "-crf", "23",          # 18-28, menor = mejor calidad
    str(output_path),
]
```

### ¿Puedo añadir overlays de fecha/hora?

Puedes modificar el comando ffmpeg para añadir texto:

```python
"-vf", f"drawtext=fontfile=/path/to/font.ttf:text='%{{pts\\:localtime\\:{start_time}\\:%Y-%m-%d %H\\\\:%M}}':x=10:y=10:fontsize=24:fontcolor=white",
```

Esto requiere modificar el código fuente.

### ¿Puedo exportar a otros formatos además de MP4?

Sí, modificando la extensión y codec en `timelapse_manager.py`. Ejemplo para WebM:

```python
output_file = f"timelapse_{self.camera}_{timestamp}.webm"
# ...
"-c:v", "libvpx-vp9",
```

### ¿Cómo integro con Node-RED?

Ejemplo de flujo Node-RED:

```json
[{
    "type": "inject",
    "name": "Iniciar captura al amanecer",
    "topic": "",
    "payload": "",
    "payloadType": "date",
    "repeat": "",
    "crontab": "",
    "once": false
}, {
    "type": "api-call-service",
    "name": "Start Capture",
    "server": "home-assistant",
    "service_domain": "frigate_timelapse",
    "service": "start_capture",
    "data": ""
}]
```

## Contribuir

### ¿Cómo puedo contribuir al proyecto?

Ver `CONTRIBUTING.md` para:
- Configuración de entorno de desarrollo
- Guías de estilo
- Proceso de pull requests
- Roadmap de características

### ¿Dónde reporto bugs?

En GitHub Issues: https://github.com/yourusername/frigate-timelapse/issues

Incluye:
- Versión de Home Assistant
- Versión de la integración
- Logs relevantes
- Pasos para reproducir

## Más Información

- **Documentación completa**: README.md
- **Ejemplos**: examples/lovelace_examples.yaml
- **Desarrollo**: CONTRIBUTING.md
- **Changelog**: CHANGELOG.md
- **Frigate Docs**: https://docs.frigate.video/
- **Home Assistant Docs**: https://www.home-assistant.io/docs/
