#!/bin/bash
# Script de instalación manual para Frigate Timelapse

set -e

echo "🎬 Instalador de Frigate Timelapse para Home Assistant"
echo "======================================================"
echo ""

# Detectar directorio de configuración de Home Assistant
if [ -d "/config" ]; then
    CONFIG_DIR="/config"
elif [ -d "$HOME/.homeassistant" ]; then
    CONFIG_DIR="$HOME/.homeassistant"
else
    echo "❌ No se pudo detectar el directorio de configuración de Home Assistant"
    read -p "Por favor, introduce la ruta completa: " CONFIG_DIR
    if [ ! -d "$CONFIG_DIR" ]; then
        echo "❌ El directorio no existe"
        exit 1
    fi
fi

echo "📁 Directorio de configuración: $CONFIG_DIR"
echo ""

# Crear directorio de componentes personalizados si no existe
CUSTOM_COMPONENTS_DIR="$CONFIG_DIR/custom_components"
INTEGRATION_DIR="$CUSTOM_COMPONENTS_DIR/frigate_timelapse"

echo "📦 Creando directorios..."
mkdir -p "$INTEGRATION_DIR/translations"
mkdir -p "$INTEGRATION_DIR/www"

# Copiar archivos
echo "📋 Copiando archivos de integración..."
cp custom_components/frigate_timelapse/*.py "$INTEGRATION_DIR/"
cp custom_components/frigate_timelapse/*.json "$INTEGRATION_DIR/"
cp custom_components/frigate_timelapse/*.yaml "$INTEGRATION_DIR/"

echo "🌍 Copiando traducciones..."
cp custom_components/frigate_timelapse/translations/*.json "$INTEGRATION_DIR/translations/"

echo "🎨 Copiando recursos frontend..."
cp custom_components/frigate_timelapse/www/*.js "$INTEGRATION_DIR/www/"

# Crear directorio de medios
MEDIA_DIR="/media/timelapse"
echo "📂 Creando directorio de medios: $MEDIA_DIR"
mkdir -p "$MEDIA_DIR/captures"

# Verificar permisos
echo "🔐 Verificando permisos..."
chmod -R 755 "$INTEGRATION_DIR"
chmod -R 755 "$MEDIA_DIR"

# Verificar ffmpeg
echo "🎥 Verificando ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg encontrado: $(ffmpeg -version | head -n1)"
else
    echo "⚠️  ffmpeg no encontrado. El componente lo necesita para generar videos."
    echo "   Instálalo con: apt-get install ffmpeg"
fi

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Reinicia Home Assistant"
echo "   2. Ve a Configuración → Dispositivos y Servicios"
echo "   3. Haz clic en '+ Añadir integración'"
echo "   4. Busca 'Frigate Timelapse'"
echo "   5. Sigue el asistente de configuración"
echo ""
echo "📚 Documentación: README.md"
echo "💡 Ejemplos: examples/lovelace_examples.yaml"
echo ""
