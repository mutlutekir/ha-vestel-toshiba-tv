class VestelToshibaTVCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Entity zorunludur.");
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  _send(key) {
    if (!this._hass || !this._config.entity) return;

    const haptic = new CustomEvent("haptic", { detail: "light" });
    window.dispatchEvent(haptic);

    this._hass.callService("vestel_toshiba_tv", "send_key", {
      entity_id: this._config.entity,
      key: key
    });
  }

  _render() {
    const title = this._config.title || "SmartCenter TV Kumandası";

    // Orijinal sol görselinizdeki birebir sıralama ve isimlendirme (Vol+, Vol-, P+, P- vb. alt alta)
    const buttons = [
      { key: "power", icon: "mdi:power" },
      { key: "menu", icon: "mdi:cog-box", name: "Settings" },
      { key: "mute", icon: "mdi:volume-mute" },

      { key: "volume_up", icon: "mdi:volume-plus" },
      { key: "home", icon: "mdi:home" },
      { key: "channel_up", icon: "mdi:arrow-up-bold-box-outline", name: "P+" },

      { key: "volume_down", icon: "mdi:volume-minus" },
      { key: "up", icon: "mdi:menu-up" },
      { key: "channel_down", icon: "mdi:arrow-down-bold-box-outline", name: "P-" },

      { key: "left", icon: "mdi:menu-left" },
      { key: "ok", icon: "mdi:selection-ellipse", name: "OK" },
      { key: "right", icon: "mdi:menu-right" },

      { key: "back", icon: "mdi:backup-restore", name: "Back" },
      { key: "down", icon: "mdi:menu-down" },
      { key: "internet", icon: "mdi:web" },

      { key: "favorites", icon: "mdi:star" },
      { key: "stop", icon: "mdi:pause", name: "Stop" },
      { key: "play", icon: "mdi:play", name: "Play" },

      { key: "channel_list", icon: "mdi:list-box", name: "Channel List" },
      { key: "source", icon: "mdi:import", name: "Source" },
      { key: "exit", icon: "mdi:close-box", name: "Exit" },

      { key: "1", icon: "mdi:numeric-1" },
      { key: "2", icon: "mdi:numeric-2" },
      { key: "3", icon: "mdi:numeric-3" },

      { key: "4", icon: "mdi:numeric-4" },
      { key: "5", icon: "mdi:numeric-5" },
      { key: "6", icon: "mdi:numeric-6" },

      { key: "7", icon: "mdi:numeric-7" },
      { key: "8", icon: "mdi:numeric-8" },
      { key: "9", icon: "mdi:numeric-9" },

      { key: "0", icon: "mdi:numeric-0" },
      { empty: true },
      { empty: true }
    ];

    let gridHtml = "";
    buttons.forEach(btn => {
      if (btn.empty) {
        gridHtml += `<div></div>`;
      } else {
        gridHtml += `
          <button class="btn" data-key="${btn.key}">
            <ha-icon icon="${btn.icon}"></ha-icon>
            ${btn.name ? `<div class="btn-name">${btn.name}</div>` : ""}
          </button>
        `;
      }
    });

    this.shadowRoot.innerHTML = `
    <style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      :host { display: block; font-family: var(--paper-font-body1_-_font-family, sans-serif); }

      .container { padding: 0px; }

      .header {
        font-size: var(--ha-card-header-font-size, 24px);
        color: var(--ha-card-header-color, var(--primary-text-color));
        margin-bottom: 16px;
        font-weight: 400;
        line-height: 32px;
      }

      .grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
      }

      .btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: var(--ha-card-background, var(--card-background-color, #1c1c1e));
        border-radius: var(--ha-card-border-radius, 12px);
        box-shadow: var(--ha-card-box-shadow, 0px 2px 1px -1px rgba(0, 0, 0, 0.2), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12));
        border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, transparent);
        color: var(--primary-text-color, #fff);
        cursor: pointer;
        padding: 12px;
        min-height: 90px;
        transition: background .15s ease-out;
        -webkit-tap-highlight-color: transparent;
        outline: none;
      }

      .btn:hover { background: var(--secondary-background-color, #2c2c2e); }
      .btn:active { transform: scale(0.96); background: var(--divider-color, #3c3c3e); }

      ha-icon {
        --mdc-icon-size: 38px;
        color: var(--state-icon-active-color, #44739e);
        pointer-events: none;
      }

      .btn-name {
        font-size: 13px;
        font-weight: 500;
        text-align: center;
        pointer-events: none;
        margin-top: 8px;
        width: 100%;
        color: var(--primary-text-color, #e1e1e1);
      }
    </style>

    <div class="container">
      <div class="header">${title}</div>
      <div class="grid">
        ${gridHtml}
      </div>
    </div>
    `;

    this.shadowRoot.querySelectorAll("[data-key]").forEach(el => {
      el.addEventListener("click", () => this._send(el.dataset.key));
    });
  }

  static getStubConfig() {
    return { entity: "media_player.vestel_toshiba_tv" };
  }

  getCardSize() { return 10; }
}

customElements.define("vestel-toshiba-tv-card", VestelToshibaTVCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "vestel-toshiba-tv-card",
  name: "Vestel & Toshiba TV Kumanda",
  description: "Standart Grid Tasarımlı TV Kumandası",
  preview: true,
});
