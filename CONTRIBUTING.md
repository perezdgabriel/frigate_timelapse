# Guía de Desarrollo - Frigate Timelapse

## Estructura del Proyecto

```
frigate_timelapse/
├── custom_components/
│   └── frigate_timelapse/
│       ├── __init__.py              # Punto de entrada, registro de servicios
│       ├── manifest.json            # Metadata de la integración
│       ├── const.py                 # Constantes y configuración
│       ├── config_flow.py           # Flujo de configuración UI
│       ├── frigate_api.py           # Cliente API de Frigate
│       ├── timelapse_manager.py     # Lógica de captura y generación
│       ├── sensor.py                # Sensores de estado
│       ├── services.yaml            # Definición de servicios
│       ├── translations/            # Traducciones i18n
│       │   ├── en.json
│       │   └── es.json
│       └── www/                     # Recursos frontend
│           └── frigate-timelapse-card.js
├── examples/
│   └── lovelace_examples.yaml       # Ejemplos de configuración
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
└── hacs.json                        # Configuración HACS
```

## Componentes Principales

### 1. frigate_api.py

Cliente asíncrono para la API de Frigate.

**Métodos principales:**
- `get_cameras()`: Lista cámaras disponibles
- `get_latest_image(camera)`: Descarga snapshot más reciente
- `test_connection()`: Verifica conectividad

**Uso:**
```python
api = FrigateAPI("http://frigate:5000")
cameras = await api.get_cameras()
image = await api.get_latest_image("front_door")
```

### 2. timelapse_manager.py

Gestor central de captura y generación de timelapses.

**Métodos principales:**
- `start_capture()`: Inicia captura periódica
- `stop_capture()`: Detiene captura
- `capture_single_image()`: Captura una imagen
- `generate_timelapse()`: Genera video con ffmpeg
- `cleanup_old_sessions()`: Limpia archivos antiguos

**Estados:**
- `idle`: Sin actividad
- `capturing`: Capturando imágenes
- `generating`: Generando video
- `error`: Error en proceso

**Organización de archivos:**
```
/media/timelapse/
├── captures/
│   └── 20251111_080000/          # Sesión por timestamp
│       ├── frame_20251111_080000_123456.jpg
│       └── frame_20251111_080100_234567.jpg
└── timelapse_camera_20251111.mp4
```

### 3. config_flow.py

Flujo de configuración interactivo en 3 pasos:

1. **user**: Introducir URL de Frigate
2. **camera**: Seleccionar cámara (autodetección)
3. **options**: Configurar parámetros

**Validaciones:**
- Conectividad con Frigate
- Existencia de cámaras
- Unicidad de configuración (URL + cámara)

### 4. sensor.py

Tres sensores por integración:

- `sensor.{domain}_{camera}_status`: Estado actual
- `sensor.{domain}_{camera}_images_count`: Contador de imágenes
- `sensor.{domain}_{camera}_last_capture`: Timestamp última captura

## Desarrollo Local

### Requisitos

```bash
# Python 3.10+
python --version

# Dependencias de desarrollo
pip install homeassistant
pip install aiohttp pillow
```

### Configuración del Entorno

1. Clonar el repositorio:
```bash
git clone https://github.com/perezdgabriel/frigate-timelapse
cd frigate-timelapse
```

2. Enlazar con Home Assistant de desarrollo:
```bash
# Crear enlace simbólico
ln -s $(pwd)/custom_components/frigate_timelapse \
      /path/to/homeassistant/config/custom_components/
```

3. Configurar logging en `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.frigate_timelapse: debug
```

### Testing

#### Test manual en Home Assistant

1. Reiniciar Home Assistant
2. Verificar logs:
```bash
tail -f /config/home-assistant.log | grep frigate_timelapse
```

3. Añadir integración desde UI

#### Test de API de Frigate

```python
import asyncio
from custom_components.frigate_timelapse.frigate_api import FrigateAPI

async def test():
    api = FrigateAPI("http://frigate:5000")
    cameras = await api.get_cameras()
    print(f"Cámaras encontradas: {cameras}")
    
    if cameras:
        image = await api.get_latest_image(cameras[0])
        print(f"Imagen descargada: {len(image)} bytes")
    
    await api.close()

asyncio.run(test())
```

#### Test de generación de timelapse

```bash
# Crear directorio de prueba
mkdir -p /tmp/test_timelapse

# Generar imágenes de prueba
for i in {1..10}; do
    convert -size 1920x1080 xc:blue \
            -pointsize 200 -fill white \
            -draw "text 800,540 '$i'" \
            /tmp/test_timelapse/frame_$i.jpg
done

# Probar ffmpeg
ffmpeg -framerate 30 -pattern_type glob \
       -i '/tmp/test_timelapse/frame_*.jpg' \
       -c:v libx264 -pix_fmt yuv420p \
       /tmp/test.mp4
```

## Añadir Nuevas Características

### 1. Añadir un nuevo servicio

En `__init__.py`:
```python
async def handle_new_service(call):
    """Handle new service."""
    # Lógica del servicio
    pass

hass.services.async_register(DOMAIN, "new_service", handle_new_service)
```

En `services.yaml`:
```yaml
new_service:
  name: New Service
  description: Description of the service
  fields:
    parameter:
      name: Parameter Name
      description: Parameter description
      example: "example value"
```

### 2. Añadir un nuevo sensor

En `sensor.py`:
```python
class NewSensor(TimelapseBaseSensor):
    """New sensor description."""

    def __init__(self, manager, camera: str, entry_id: str) -> None:
        super().__init__(manager, camera, entry_id)
        self._attr_name = "Sensor Name"
        self._attr_unique_id = f"{entry_id}_sensor_id"
        self._attr_icon = "mdi:icon-name"

    @property
    def native_value(self):
        """Return sensor value."""
        return self._manager.some_property
```

Registrar en `async_setup_entry`:
```python
sensors = [
    # ... sensores existentes
    NewSensor(timelapse_manager, camera, config_entry.entry_id),
]
```

### 3. Añadir opción de configuración

En `const.py`:
```python
CONF_NEW_OPTION = "new_option"
DEFAULT_NEW_OPTION = "default_value"
```

En `config_flow.py`:
```python
vol.Required(CONF_NEW_OPTION, default=DEFAULT_NEW_OPTION): str,
```

En `timelapse_manager.py`:
```python
def __init__(self, ..., new_option: str):
    # ...
    self.new_option = new_option
```

## Publicación

### Pre-release Checklist

- [ ] Actualizar `manifest.json` con nueva versión
- [ ] Actualizar `CHANGELOG.md`
- [ ] Verificar traducciones completas
- [ ] Probar en Home Assistant limpio
- [ ] Verificar compatibilidad con HACS
- [ ] Actualizar documentación
- [ ] Crear screenshots para README

### Release Process

1. Crear tag:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

2. Crear release en GitHub con:
   - Descripción de cambios (desde CHANGELOG)
   - Archivos binarios si aplica
   - Link a documentación

3. Notificar a HACS (si es primera vez):
   - Crear PR en https://github.com/hacs/default
   - Añadir al archivo `custom_components.json`

## Guías de Estilo

### Python

- Seguir PEP 8
- Type hints en todas las funciones
- Docstrings en formato Google
- Logging apropiado:
  - `DEBUG`: Información detallada de debugging
  - `INFO`: Eventos importantes (inicio, fin de operaciones)
  - `WARNING`: Situaciones recuperables
  - `ERROR`: Errores que impiden funcionalidad

### JavaScript

- Usar ES6+
- Comentarios descriptivos
- Nombres de clase en PascalCase
- Métodos privados con prefijo `_`

## Recursos Útiles

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [Frigate API Documentation](https://docs.frigate.video/integrations/api)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)

## Soporte

Para preguntas de desarrollo:
- GitHub Discussions
- Home Assistant Community Forum
- Discord #development

## Licencia

MIT License - Ver LICENSE para detalles.
