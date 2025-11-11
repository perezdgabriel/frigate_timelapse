class FrigateTimelapseCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("Please define an entity");
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      this.content = document.createElement("ha-card");
      this.content.innerHTML = `
        <style>
          .card-content {
            padding: 16px;
          }
          .status-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
          }
          .status-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 14px;
          }
          .status-idle { background-color: #4caf50; color: white; }
          .status-capturing { background-color: #2196f3; color: white; }
          .status-generating { background-color: #ff9800; color: white; }
          .status-error { background-color: #f44336; color: white; }
          .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
          }
          .stat-box {
            background: var(--primary-background-color);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
          }
          .stat-label {
            font-size: 12px;
            color: var(--secondary-text-color);
            margin-bottom: 4px;
          }
          .stat-value {
            font-size: 24px;
            font-weight: 500;
            color: var(--primary-text-color);
          }
          .button-group {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
          }
          .control-button {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
          }
          .btn-start {
            background-color: #4caf50;
            color: white;
          }
          .btn-stop {
            background-color: #f44336;
            color: white;
          }
          .btn-generate {
            background-color: #2196f3;
            color: white;
          }
          .btn-capture {
            background-color: #ff9800;
            color: white;
          }
          .control-button:hover {
            opacity: 0.9;
          }
          .control-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }
          .video-section {
            margin-top: 16px;
          }
          .video-container {
            position: relative;
            width: 100%;
            background: black;
            border-radius: 8px;
            overflow: hidden;
          }
          video {
            width: 100%;
            display: block;
          }
          .no-video {
            padding: 40px;
            text-align: center;
            color: var(--secondary-text-color);
          }
          ha-icon {
            --mdi-icon-size: 20px;
          }
        </style>
        <div class="card-content">
          <div class="status-section">
            <h2 style="margin: 0;">Frigate Timelapse</h2>
            <span class="status-badge" id="status-badge"></span>
          </div>
          
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-label">Imágenes Capturadas</div>
              <div class="stat-value" id="images-count">0</div>
            </div>
            <div class="stat-box">
              <div class="stat-label">Última Captura</div>
              <div class="stat-value" id="last-capture" style="font-size: 14px;">-</div>
            </div>
          </div>

          <div class="button-group">
            <button class="control-button btn-start" id="btn-start">
              <ha-icon icon="mdi:play"></ha-icon>
              Iniciar
            </button>
            <button class="control-button btn-stop" id="btn-stop">
              <ha-icon icon="mdi:stop"></ha-icon>
              Detener
            </button>
          </div>

          <div class="button-group">
            <button class="control-button btn-capture" id="btn-capture">
              <ha-icon icon="mdi:camera"></ha-icon>
              Capturar Ahora
            </button>
            <button class="control-button btn-generate" id="btn-generate">
              <ha-icon icon="mdi:movie-open"></ha-icon>
              Generar Timelapse
            </button>
          </div>

          <div class="video-section" id="video-section">
            <h3>Último Timelapse</h3>
            <div class="video-container" id="video-container">
              <div class="no-video">
                <ha-icon icon="mdi:video-off" style="--mdi-icon-size: 48px;"></ha-icon>
                <p>No hay videos disponibles</p>
              </div>
            </div>
          </div>
        </div>
      `;
      this.shadowRoot.appendChild(this.content);
      this._attachEventListeners();
    }

    this._updateCard();
  }

  _attachEventListeners() {
    const btnStart = this.shadowRoot.getElementById("btn-start");
    const btnStop = this.shadowRoot.getElementById("btn-stop");
    const btnCapture = this.shadowRoot.getElementById("btn-capture");
    const btnGenerate = this.shadowRoot.getElementById("btn-generate");

    btnStart.addEventListener("click", () =>
      this._callService("start_capture")
    );
    btnStop.addEventListener("click", () => this._callService("stop_capture"));
    btnCapture.addEventListener("click", () =>
      this._callService("capture_image")
    );
    btnGenerate.addEventListener("click", () =>
      this._callService("generate_timelapse")
    );
  }

  _updateCard() {
    const statusEntity = this._hass.states[this.config.entity];
    const imagesEntity =
      this._hass.states[this.config.entity.replace("_status", "_images_count")];
    const lastCaptureEntity =
      this._hass.states[this.config.entity.replace("_status", "_last_capture")];

    if (!statusEntity) return;

    // Update status badge
    const statusBadge = this.shadowRoot.getElementById("status-badge");
    const status = statusEntity.state;
    statusBadge.textContent = this._getStatusText(status);
    statusBadge.className = `status-badge status-${status}`;

    // Update images count
    if (imagesEntity) {
      const imagesCount = this.shadowRoot.getElementById("images-count");
      imagesCount.textContent = imagesEntity.state;
    }

    // Update last capture
    if (lastCaptureEntity && lastCaptureEntity.state !== "unknown") {
      const lastCapture = this.shadowRoot.getElementById("last-capture");
      const date = new Date(lastCaptureEntity.state);
      lastCapture.textContent = date.toLocaleTimeString();
    }

    // Update button states
    const btnStart = this.shadowRoot.getElementById("btn-start");
    const btnStop = this.shadowRoot.getElementById("btn-stop");
    const btnGenerate = this.shadowRoot.getElementById("btn-generate");

    btnStart.disabled = status === "capturing";
    btnStop.disabled = status !== "capturing";
    btnGenerate.disabled = status === "generating";

    // Update video if configured
    this._updateVideo();
  }

  _updateVideo() {
    if (!this.config.video_path) return;

    const videoContainer = this.shadowRoot.getElementById("video-container");
    const existingVideo = videoContainer.querySelector("video");

    if (existingVideo) return; // Already showing video

    // Check if video exists (this would need to be implemented based on your setup)
    // For now, we'll create a placeholder for the video element
    videoContainer.innerHTML = `
      <video controls>
        <source src="${this.config.video_path}" type="video/mp4">
        Tu navegador no soporta el elemento video.
      </video>
    `;
  }

  _getStatusText(status) {
    const statusMap = {
      idle: "Inactivo",
      capturing: "Capturando",
      generating: "Generando",
      error: "Error",
    };
    return statusMap[status] || status;
  }

  _callService(service) {
    this._hass.callService("frigate_timelapse", service, {
      entity_id: this.config.entity,
    });
  }

  getCardSize() {
    return 6;
  }
}

customElements.define("frigate-timelapse-card", FrigateTimelapseCard);

// Register the card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: "frigate-timelapse-card",
  name: "Frigate Timelapse Card",
  description: "Control panel for Frigate Timelapse",
  preview: true,
});
