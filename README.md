# Vestel & Toshiba TV Integration for Home Assistant

This custom component allows you to control smart televisions of brands such as Vestel, Toshiba, JVC, Hitachi, and Telefunken (which use the SmartCenter infrastructure) over your local network via the DIAL protocol in Home Assistant.

## 👨‍💻 Developer

**Mutlu Tekir** | [YouTube: @mutlutekir](https://www.youtube.com/@mutlutekir) | [GitHub: @mutlutekir](https://www.google.com/search?q=https://github.com/mutlutekir)

## 🚀 Installation

### Method 1: Via HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=ha-vestel-toshiba-tv&category=integration)

### Method 2: Manual Installation

1. Download this repository.
2. Copy the custom_components/vestel_toshiba_tv folder into your custom_components directory in your Home Assistant configuration folder.
3. Restart Home Assistant.

## 📱 Dashboard (Remote Card) Setup

To add the remote to your UI:

1. Go to your Dashboard and click Edit Dashboard.
2. Click Add Card > Manual.
3. Paste the following YAML code:

type: custom:vestel-toshiba-tv-card
entity: media_player.vestel_toshiba_tv
title: SmartCenter TV Kumandası

4. Click Save.

## 🛠️ Supported Commands

You can use vestel_toshiba_tv.send_key in your automations with these commands:
power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9

---

---

# Home Assistant için Vestel & Toshiba TV Entegrasyonu

Bu özel bileşen, SmartCenter altyapısını kullanan Vestel, Toshiba, JVC, Hitachi, Telefunken gibi markaların akıllı televizyonlarını Home Assistant üzerinden yerel ağda kontrol etmenizi sağlar.

## 👨‍💻 Geliştirici

**Mutlu Tekir** | [YouTube: @mutlutekir](https://www.youtube.com/@mutlutekir) | [GitHub: @mutlutekir](https://www.google.com/search?q=https://github.com/mutlutekir)

## 🚀 Kurulum

### Yöntem 1: HACS Üzerinden (Önerilen)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=ha-vestel-toshiba-tv&category=integration)

### Yöntem 2: Manuel Kurulum

1. Bu repoyu indirin.
2. İçindeki custom_components/vestel_toshiba_tv klasörünü custom_components dizinine kopyalayın.
3. Home Assistant'ı yeniden başlatın.

## 📱 Dashboard (Kumanda) Kurulumu

Kumandayı arayüze eklemek için:

1. Gösterge Paneline gidin ve Paneli Düzenle deyin.
2. Kart Ekle > Manuel seçin.
3. Aşağıdaki YAML kodunu yapıştırın:

type: custom:vestel-toshiba-tv-card
entity: media_player.vestel_toshiba_tv
title: SmartCenter TV Kumandası

4. Kaydet butonuna basın.

## 🛠️ Desteklenen Komutlar & Otomasyonlar

vestel_toshiba_tv.send_key servisini otomasyonlarınızda kullanabilirsiniz.

Desteklenen komutlar:
power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9
