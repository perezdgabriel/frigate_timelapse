# Frigate Timelapse for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/perezdgabriel/frigate-timelapse.svg)](https://github.com/perezdgabriel/frigate-timelapse/releases)

Componente personalizado para Home Assistant que crea timelapses automáticos desde cámaras de Frigate.

## Características

- 🎥 **Detección automática** de cámaras en Frigate
- 📸 **Captura periódica** de imágenes configurable
- 🎬 **Generación automática** de videos timelapse con ffmpeg
- 🎛️ **Configuración completa** desde la interfaz de Home Assistant
- 📊 **Sensores de estado** para monitorización
- 🎨 **Tarjeta Lovelace** personalizada para control visual
- 🔧 **Instalación fácil** con HACS

## Requisitos

- Home Assistant 2023.1.0 o superior
- Frigate instalado y funcionando
- ffmpeg instalado en el sistema (generalmente ya incluido en Home Assistant)

## Instalación

### Vía HACS (Recomendado)

1. Abre HACS en Home Assistant
2. Ve a "Integraciones"
3. Haz clic en el menú (⋮) en la esquina superior derecha
4. Selecciona "Repositorios personalizados"
5. Añade la URL: `https://github.com/perezdgabriel/frigate-timelapse`
6. Categoría: "Integration"
7. Haz clic en "Añadir"
8. Busca "Frigate Timelapse" e instálalo
9. Reinicia Home Assistant

### Manual

1. Descarga la carpeta `custom_components/frigate_timelapse`
2. Cópiala en tu directorio `config/custom_components/`
3. Reinicia Home Assistant

## Configuración

### 1. Añadir la integración

1. Ve a **Configuración** → **Dispositivos y servicios**
2. Haz clic en **+ Añadir integración**
3. Busca "Frigate Timelapse"
4. Sigue el asistente de configuración:
   - **URL de Frigate**: Introduce la URL de tu servidor Frigate (ej: `http://frigate:5000`)
   - **Seleccionar cámara**: Elige la cámara que quieres usar
   - **Opciones**:
     - **Intervalo de captura**: Segundos entre capturas (10-3600)
     - **Ruta de salida**: Donde guardar los videos (por defecto: `/media/timelapse`)
     - **FPS**: Frames por segundo del video (1-60)
     - **Resolución**: Resolución del video final

### 2. Configurar la tarjeta Lovelace

#### Método 1: Añadir recurso (Requerido)

1. Ve a **Configuración** → **Dashboards**
2. Haz clic en el menú (⋮) → **Recursos**
3. Añade un nuevo recurso:
   - **URL**: `/local/community/frigate_timelapse/frigate-timelapse-card.js`
   - **Tipo**: JavaScript Module

#### Método 2: Añadir la tarjeta

Añade esta tarjeta a tu dashboard:

```yaml
type: custom:frigate-timelapse-card
entity: sensor.frigate_timelapse_CAMERA_status
```

Reemplaza `CAMERA` con el nombre de tu cámara.

## Uso

### Panel de Control

La tarjeta personalizada muestra:

- **Estado actual**: Inactivo, Capturando, Generando, Error
- **Estadísticas**:
  - Número de imágenes capturadas
  - Hora de la última captura
- **Controles**:
  - 🟢 **Iniciar**: Comienza la captura periódica
  - 🔴 **Detener**: Detiene la captura periódica
  - 📸 **Capturar Ahora**: Captura una imagen inmediatamente
  - 🎬 **Generar Timelapse**: Crea el video con las imágenes capturadas

### Servicios disponibles

#### `frigate_timelapse.start_capture`

Inicia la captura periódica de imágenes.

```yaml
service: frigate_timelapse.start_capture
```

#### `frigate_timelapse.stop_capture`

Detiene la captura periódica.

```yaml
service: frigate_timelapse.stop_capture
```

#### `frigate_timelapse.capture_image`

Captura una única imagen.

```yaml
service: frigate_timelapse.capture_image
```

#### `frigate_timelapse.generate_timelapse`

Genera un video timelapse.

```yaml
service: frigate_timelapse.generate_timelapse
data:
  start_time: "2025-11-11 00:00:00"  # Opcional
  end_time: "2025-11-11 23:59:59"    # Opcional
  output_file: "mi_timelapse.mp4"    # Opcional
```

### Automaciones

#### Ejemplo 1: Timelapse diario automático

```yaml
automation:
  - alias: "Generar timelapse diario"
    trigger:
      - platform: time
        at: "23:55:00"
    action:
      - service: frigate_timelapse.generate_timelapse
      - service: frigate_timelapse.stop_capture
      - delay: "00:05:00"
      - service: frigate_timelapse.start_capture
```

#### Ejemplo 2: Captura durante el día

```yaml
automation:
  - alias: "Iniciar captura por la mañana"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: frigate_timelapse.start_capture
  
  - alias: "Detener captura por la noche"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: frigate_timelapse.stop_capture
      - service: frigate_timelapse.generate_timelapse
```

## Estructura de archivos

Los archivos se organizan de la siguiente manera:

```
/media/timelapse/
├── captures/
│   └── 20251111_080000/     # Sesión de captura
│       ├── frame_20251111_080000_123456.jpg
│       ├── frame_20251111_080100_234567.jpg
│       └── ...
└── timelapse_camera_20251111_235959.mp4  # Videos generados
```

## Sensores

El componente crea tres sensores por cada cámara configurada:

- `sensor.frigate_timelapse_CAMERA_status`: Estado actual (idle, capturing, generating, error)
- `sensor.frigate_timelapse_CAMERA_images_count`: Número de imágenes capturadas
- `sensor.frigate_timelapse_CAMERA_last_capture`: Timestamp de la última captura

## Solución de problemas

### No se conecta a Frigate

- Verifica que la URL de Frigate sea correcta
- Asegúrate de que Frigate sea accesible desde Home Assistant
- Revisa los logs: **Configuración** → **Logs**

### No se generan videos

- Verifica que ffmpeg esté instalado
- Comprueba que haya suficientes imágenes capturadas (mínimo 2)
- Verifica los permisos de escritura en la ruta de salida

### La tarjeta no se muestra

- Asegúrate de haber añadido el recurso JavaScript
- Limpia la caché del navegador (Ctrl + Shift + R)
- Verifica que la entidad exista

## Desarrollo

Para contribuir al proyecto:

```bash
git clone https://github.com/perezdgabriel/frigate-timelapse
cd frigate-timelapse
```

## Licencia

MIT License - Ver archivo LICENSE para más detalles

## Soporte

- 🐛 [Reportar un bug](https://github.com/perezdgabriel/frigate-timelapse/issues)
- 💡 [Solicitar una característica](https://github.com/perezdgabriel/frigate-timelapse/issues)
- 💬 [Discusiones](https://github.com/perezdgabriel/frigate-timelapse/discussions)

## Agradecimientos

- [Frigate](https://frigate.video/) - NVR de código abierto
- [Home Assistant](https://www.home-assistant.io/) - Automatización del hogar

---

**Nota**: Reemplaza `perezdgabriel` con tu nombre de usuario de GitHub en todos los enlaces.
