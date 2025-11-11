# 🚀 Inicio Rápido - Frigate Timelapse

## En 5 minutos tendrás tu primer timelapse funcionando

---

## 📋 Pre-requisitos

Antes de empezar, asegúrate de tener:

- ✅ Home Assistant 2023.1.0 o superior instalado
- ✅ Frigate NVR funcionando en tu red
- ✅ HACS instalado (recomendado) o acceso SSH
- ✅ Al menos una cámara configurada en Frigate

---

## 🎯 Instalación (Opción A: HACS)

### Paso 1: Añadir repositorio a HACS
1. Abre **HACS** en Home Assistant
2. Ve a **Integraciones**
3. Click en el menú **(⋮)** → **Repositorios personalizados**
4. Pega esta URL: `https://github.com/perezdgabriel/frigate-timelapse`
5. Selecciona categoría: **Integration**
6. Click **Añadir**

### Paso 2: Instalar
1. Busca **"Frigate Timelapse"** en HACS
2. Click **Descargar**
3. **Reinicia Home Assistant**

### Paso 3: Configurar
1. Ve a **Configuración** → **Dispositivos y Servicios**
2. Click **+ Añadir integración**
3. Busca **"Frigate Timelapse"**
4. Completa el asistente:
   - **URL Frigate**: `http://frigate:5000` (ajusta según tu instalación)
   - **Cámara**: Selecciona de la lista
   - **Intervalo**: `60` segundos (recomendado para empezar)
   - **Ruta**: `/media/timelapse` (por defecto)
   - **FPS**: `30`
   - **Resolución**: `1920x1080`

¡Listo! La integración está configurada.

---

## 🎯 Instalación (Opción B: Manual)

### Vía SSH/Terminal

```bash
# Conecta por SSH a tu Home Assistant
ssh root@homeassistant.local

# Descarga el proyecto
cd /config/custom_components
git clone https://github.com/perezdgabriel/frigate-timelapse.git frigate_timelapse

# Reinicia Home Assistant
ha core restart
```

Luego sigue el **Paso 3** de la opción A para configurar.

---

## 🎨 Añadir la Tarjeta Lovelace

### Paso 1: Registrar recurso
1. **Configuración** → **Dashboards** → Menú **(⋮)** → **Recursos**
2. Click **+ Añadir recurso**
3. **URL**: `/local/community/frigate_timelapse/frigate-timelapse-card.js`
4. **Tipo**: **JavaScript Module**
5. Click **Crear**

### Paso 2: Añadir tarjeta
1. Edita tu dashboard
2. **+ Añadir tarjeta**
3. Busca **"Frigate Timelapse Card"** o añade manualmente:

```yaml
type: custom:frigate-timelapse-card
entity: sensor.frigate_timelapse_NOMBRE_CAMARA_status
```

> Reemplaza `NOMBRE_CAMARA` con el nombre de tu cámara

**¡Ya tienes tu panel de control!**

---

## 🎬 Crear tu Primer Timelapse

### Opción 1: Desde la Tarjeta (Más fácil)

1. Abre tu dashboard con la tarjeta
2. Click **"Iniciar"** → Comenzará a capturar imágenes
3. Espera al menos 5-10 minutos (para tener suficientes imágenes)
4. Click **"Generar Timelapse"**
5. Espera ~30 segundos
6. ¡Tu video estará en `/media/timelapse/`!

### Opción 2: Desde Servicios

1. **Developer Tools** → **Servicios**
2. Servicio: `frigate_timelapse.start_capture`
3. Click **Llamar servicio**
4. Espera unos minutos...
5. Servicio: `frigate_timelapse.generate_timelapse`
6. Click **Llamar servicio**

---

## 📹 Ver tu Timelapse

### En File Browser

Si tienes instalado **File Browser** o **Samba**:
1. Navega a `/media/timelapse/`
2. Descarga el archivo `.mp4`
3. Ábrelo con cualquier reproductor

### En Home Assistant

Añade una tarjeta de medios:

```yaml
type: video
url: /media/timelapse/timelapse_CAMARA_20251111.mp4
```

---

## ⚙️ Automatización Básica

Copia esto en tu `automations.yaml` para un timelapse automático diario:

```yaml
automation:
  # Iniciar captura por la mañana
  - alias: "Timelapse - Iniciar"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: frigate_timelapse.start_capture

  # Generar video por la noche
  - alias: "Timelapse - Generar"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: frigate_timelapse.stop_capture
      - delay: "00:00:10"
      - service: frigate_timelapse.generate_timelapse
```

Reinicia Home Assistant y tendrás timelapses automáticos cada día.

---

## 🔍 Verificar que Funciona

### 1. Comprobar sensores
Ve a **Developer Tools** → **Estados** y busca:
- `sensor.frigate_timelapse_CAMARA_status` → Debería decir "capturing" o "idle"
- `sensor.frigate_timelapse_CAMARA_images_count` → Debería ir aumentando
- `sensor.frigate_timelapse_CAMARA_last_capture` → Timestamp reciente

### 2. Verificar archivos
Desde SSH o File Browser:
```bash
ls -la /media/timelapse/captures/
```
Deberías ver una carpeta con timestamp y archivos `.jpg` dentro.

### 3. Logs
Si algo falla:
```bash
tail -f /config/home-assistant.log | grep frigate_timelapse
```

---

## ⚠️ Solución de Problemas Rápidos

### "Cannot connect to Frigate"
```bash
# Verifica que Frigate funcione
curl http://frigate:5000/api/config

# Si no responde, usa la IP directa
curl http://192.168.1.X:5000/api/config
```

### "No cameras found"
- Abre Frigate en un navegador: `http://frigate:5000`
- Verifica que veas tus cámaras ahí
- Revisa el `config.yml` de Frigate

### La tarjeta no aparece
1. Limpia caché del navegador: **Ctrl + Shift + R**
2. Verifica que añadiste el recurso JavaScript
3. Revisa la consola del navegador (F12)

### No se generan videos
```bash
# Verifica ffmpeg
ffmpeg -version

# Si no está instalado (raro en HA)
apk add ffmpeg
```

---

## 📱 Ejemplo Completo de Dashboard

```yaml
views:
  - title: Timelapse
    icon: mdi:camera-timer
    cards:
      # Panel de control principal
      - type: custom:frigate-timelapse-card
        entity: sensor.frigate_timelapse_front_door_status
      
      # Estadísticas
      - type: entities
        title: Estado
        entities:
          - sensor.frigate_timelapse_front_door_status
          - sensor.frigate_timelapse_front_door_images_count
          - sensor.frigate_timelapse_front_door_last_capture
      
      # Botón rápido
      - type: button
        name: Generar Video Ahora
        icon: mdi:movie-open
        tap_action:
          action: call-service
          service: frigate_timelapse.generate_timelapse
```

---

## 🎓 Próximos Pasos

Una vez que tengas lo básico funcionando:

1. 📖 Lee el **README.md** completo para opciones avanzadas
2. 🤔 Revisa el **FAQ.md** para casos de uso específicos
3. 🔧 Explora **examples/lovelace_examples.yaml** para automaciones avanzadas
4. 🌟 Personaliza los intervalos y resoluciones según tus necesidades

---

## 💡 Tips Rápidos

- **Intervalo corto (10-30s)**: Para eventos rápidos o pruebas
- **Intervalo medio (60-120s)**: Para timelapses diarios normales
- **Intervalo largo (300-600s)**: Para cambios lentos (plantas, nubes)

- **720p**: Si tienes espacio limitado
- **1080p**: Recomendado, buen balance
- **4K**: Solo si necesitas máxima calidad

- **30 FPS**: Estándar, suave
- **24 FPS**: Estilo cinematográfico
- **15 FPS**: Efecto más notorio de timelapse

---

## 📞 ¿Necesitas Ayuda?

- 🐛 Problemas técnicos: [GitHub Issues](https://github.com/perezdgabriel/frigate-timelapse/issues)
- 💬 Preguntas: [GitHub Discussions](https://github.com/perezdgabriel/frigate-timelapse/discussions)
- 📚 Documentación completa: Ver **README.md** y **FAQ.md**

---

## ✅ Checklist de Inicio Rápido

- [ ] Frigate funcionando
- [ ] Integración instalada vía HACS o manual
- [ ] Home Assistant reiniciado
- [ ] Integración configurada desde UI
- [ ] Recurso JavaScript añadido
- [ ] Tarjeta Lovelace añadida al dashboard
- [ ] Captura iniciada
- [ ] Primer timelapse generado
- [ ] Video visualizado correctamente
- [ ] (Opcional) Automación configurada

---

**¡Disfruta creando increíbles timelapses! 🎬✨**

*Tiempo estimado desde cero hasta primer timelapse: **5-10 minutos***
