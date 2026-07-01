\# Vestel \& Toshiba TV Integration for Home Assistant



This custom component allows you to control smart televisions of brands such as Vestel, Toshiba, JVC, Hitachi, and Telefunken (which use the SmartCenter infrastructure) over your local network via the DIAL protocol in Home Assistant.



\## 👨‍💻 Developer



\*\*Mutlu Tekir\*\* | \[YouTube: @mutlutekir](https://www.youtube.com/@mutlutekir) | \[GitHub: @mutlutekir](https://www.google.com/search?q=https://github.com/mutlutekir)



\## 🚀 Installation



\### Method 1: Via HACS (Recommended)



\### Method 2: Manual Installation



1\. Download this repository.

2\. Copy the custom\_components/vestel\_toshiba\_tv folder into your custom\_components directory in your Home Assistant configuration folder.

3\. Restart Home Assistant.



\## 📱 Dashboard (Remote Card) Setup



To add the remote to your UI:



1\. Go to your Dashboard and click Edit Dashboard.

2\. Click Add Card > Manual.

3\. Paste the following YAML code:



type: custom:vestel-toshiba-tv-card

entity: media\_player.vestel\_toshiba\_tv

title: SmartCenter TV Kumandası



4\. Click Save.



\## 🛠️ Supported Commands



You can use vestel\_toshiba\_tv.send\_key in your automations with these commands:

power, mute, volume\_up, volume\_down, channel\_up, channel\_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9



\---



\---



\# Home Assistant için Vestel \& Toshiba TV Entegrasyonu



Bu özel bileşen, SmartCenter altyapısını kullanan Vestel, Toshiba, JVC, Hitachi, Telefunken gibi markaların akıllı televizyonlarını Home Assistant üzerinden yerel ağda kontrol etmenizi sağlar.



\## 👨‍💻 Geliştirici



\*\*Mutlu Tekir\*\* | \[YouTube: @mutlutekir](https://www.youtube.com/@mutlutekir) | \[GitHub: @mutlutekir](https://www.google.com/search?q=https://github.com/mutlutekir)



\## 🚀 Kurulum



\### Yöntem 1: HACS Üzerinden (Önerilen)



\### Yöntem 2: Manuel Kurulum



1\. Bu repoyu indirin.

2\. İçindeki custom\_components/vestel\_toshiba\_tv klasörünü custom\_components dizinine kopyalayın.

3\. Home Assistant'ı yeniden başlatın.



\## 📱 Dashboard (Kumanda) Kurulumu



Kumandayı arayüze eklemek için:



1\. Gösterge Paneline gidin ve Paneli Düzenle deyin.

2\. Kart Ekle > Manuel seçin.

3\. Aşağıdaki YAML kodunu yapıştırın:



type: custom:vestel-toshiba-tv-card

entity: media\_player.vestel\_toshiba\_tv

title: SmartCenter TV Kumandası



4\. Kaydet butonuna basın.



\## 🛠️ Desteklenen Komutlar \& Otomasyonlar



vestel\_toshiba\_tv.send\_key servisini otomasyonlarınızda kullanabilirsiniz.



Desteklenen komutlar:

power, mute, volume\_up, volume\_down, channel\_up, channel\_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9

