# CHANGELOG

## [1.0.0] - 2025-11-11

### Añadido
- Integración inicial con Frigate API
- Detección automática de cámaras disponibles
- Captura periódica de imágenes configurable
- Generación de timelapses con ffmpeg
- Config flow para configuración desde UI
- Tres sensores de estado:
  - Estado de captura (idle, capturing, generating, error)
  - Contador de imágenes capturadas
  - Timestamp de última captura
- Servicios para control:
  - `start_capture`: Iniciar captura periódica
  - `stop_capture`: Detener captura
  - `capture_image`: Capturar imagen única
  - `generate_timelapse`: Generar video
- Tarjeta Lovelace personalizada con controles visuales
- Soporte para múltiples resoluciones (1080p, 720p, 4K, 1440p)
- FPS configurable (1-60)
- Intervalo de captura configurable (10-3600 segundos)
- Limpieza automática de sesiones antiguas
- Traducciones en español e inglés
- Documentación completa
- Ejemplos de automatizaciones
- Compatibilidad con HACS

### Características principales
- ✅ Instalación vía HACS
- ✅ Configuración 100% desde UI (sin YAML requerido)
- ✅ Sin necesidad de cronjobs o scripts externos
- ✅ Panel de control visual en Lovelace
- ✅ Generación automática y manual de timelapses
- ✅ Organización automática de archivos por sesión
- ✅ Soporte para filtrado temporal al generar videos

### Requisitos técnicos
- Home Assistant 2023.1.0 o superior
- Frigate NVR instalado y funcionando
- ffmpeg (generalmente incluido en Home Assistant)
- Python 3.10+

### Notas de instalación
- El componente crea automáticamente los directorios necesarios
- La ruta por defecto es `/media/timelapse/`
- Los videos se guardan en formato MP4 con codec H.264
- Las imágenes capturadas se organizan por sesión con timestamp

## [Próximas versiones]

### Planificado para v1.1.0
- Soporte para captura en horarios específicos
- Integración con Media Browser de Home Assistant
- Previsualización de imágenes capturadas
- Opciones avanzadas de ffmpeg (bitrate, codec)
- Soporte para múltiples cámaras simultáneas
- Estadísticas de almacenamiento
- Exportación a servicios en la nube

### Ideas futuras
- Detección de movimiento para captura inteligente
- Overlays con fecha/hora en el video
- Efectos de transición
- Soporte para cámaras RTSP directas
- Integración con frigate events
- Música de fondo opcional
- Generación de GIFs animados
