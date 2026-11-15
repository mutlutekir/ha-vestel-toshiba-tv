<h1 align="center">Vestel & Toshiba TV - Home Assistant Integration</h1>

<div align="center">

<a href="https://github.com/hacs/integration">
<img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge" alt="HACS">
</a>
<a href="https://github.com/mutlutekir/ha-vestel-toshiba-tv/releases">
<img src="https://img.shields.io/github/v/release/mutlutekir/ha-vestel-toshiba-tv?style=for-the-badge&color=blue" alt="Release">
</a>
<a href="https://github.com/mutlutekir">
<img src="https://img.shields.io/badge/maintainer-Mutlu%20Tekir-green?style=for-the-badge" alt="Maintainer">
</a>

<h3>
<a href="#english">🇬🇧 English</a> | <a href="#türkçe-kılavuz">🇹🇷 Türkçe</a>
</h3>
<img width="329" height="724" alt="Ekran görüntüsü 2026-07-05 171314" src="https://github.com/user-attachments/assets/d14bb3ca-4dbf-43a1-94b2-06f22068e601" />

</div>

<hr>

<div id="english"></div>

<h2>🇬🇧 English</h2>

<p>
<strong>Vestel & Toshiba TV Integration</strong> allows you to control smart televisions of brands such as Vestel and Toshiba (which use the SmartCenter infrastructure) over your local network via the DIAL protocol in Home Assistant. It features a custom, realistic-looking remote control dashboard card.
</p>

<h3>🚀 Installation</h3>

<h4>Method 1: HACS (Recommended)</h4>

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=ha-vestel-toshiba-tv&category=integration" target="_blank">
<img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.">
</a>

<ol>
<li>Open <strong>HACS</strong> in Home Assistant.</li>
<li>Go to <strong>Integrations</strong> > click the 3 dots in the top right corner > <strong>Custom repositories</strong>.</li>
<li>Paste the URL of this repository: <code>https://github.com/mutlutekir/ha-vestel-toshiba-tv</code></li>
<li>Select <strong>Integration</strong> as the category and click <strong>Add</strong>.</li>
<li>Search for <strong>"Vestel & Toshiba TV"</strong> and install it.</li>
<li><strong>Restart</strong> Home Assistant.</li>
</ol>

<h4>Method 2: Manual</h4>
<ol>
<li>Copy the <code>custom_components/vestel_toshiba_tv</code> folder to your Home Assistant's <code>custom_components</code> directory.</li>
<li><strong>Restart</strong> Home Assistant.</li>
</ol>

<h3>📱 Dashboard Card Setup</h3>
<pre><code class="language-yaml">type: custom:vestel-toshiba-tv-card
entity: media_player.vestel_toshiba_tv
title: SmartCenter TV Kumandası
</code></pre>

<h3>🛠️ Automations</h3>
<p>You can use the <code>vestel_toshiba_tv.send_key</code> service in your automations with these commands:</p>
<pre><code class="language-text">power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9
</code></pre>

<h3>🍏 Apple Home (HomeKit)</h3>
<p>The TV can be controlled from the Apple Home app and the Control Center remote on iPhone/iPad. No automation is needed; the integration handles the remote keys itself.</p>

<h4>Setup</h4>
<ol>
<li>Go to <strong>Settings</strong> > <strong>Devices & Services</strong> > <strong>Add Integration</strong> > <strong>HomeKit Bridge</strong>.</li>
<li>Select the <code>media_player</code> domain, set the mode to <strong>accessory</strong> and choose the TV entity.</li>
<li>Scan the QR code from the Home Assistant notification in the Apple Home app.</li>
<li>Open Control Center on your iPhone, tap the <strong>Remote</strong> icon and select the TV.</li>
</ol>

<h4>Remote keys</h4>
<table>
<tr><th>Apple remote</th><th>TV key</th></tr>
<tr><td>Arrows</td><td>Up / Down / Left / Right</td></tr>
<tr><td>Center button</td><td>OK</td></tr>
<tr><td>Back</td><td>Back</td></tr>
<tr><td>Play/Pause</td><td>Play</td></tr>
<tr><td>Info (i)</td><td>Home</td></tr>
<tr><td>iPhone volume buttons</td><td>Volume up / down</td></tr>
</table>
<p>To change the mapping, edit <code>HOMEKIT_KEY_MAP</code> in <code>const.py</code>.</p>

<h4>Notes</h4>
<ul>
<li>The TV must be added with Home Assistant's own <strong>HomeKit Bridge</strong> in <strong>accessory</strong> mode. The remote keys do not work through Homebridge.</li>
<li>The Apple remote has no channel keys, and Siri cannot change the TV volume. Use scripts calling <code>vestel_toshiba_tv.send_key</code> for these.</li>
<li>If the TV was added to Apple Home before v1.1.0, remove it from the Home app and add it again.</li>
</ul>

<hr>

<div id="türkçe-kılavuz"></div>

<h2>🇹🇷 Türkçe Kılavuz</h2>

<p>
<strong>Vestel & Toshiba TV Entegrasyonu</strong>, SmartCenter altyapısını kullanan Vestel ve Toshiba gibi markaların akıllı televizyonlarını Home Assistant üzerinden yerel ağda kontrol etmenizi sağlar.
</p>

<h3>🚀 Kurulum</h3>

<h4>Yöntem 1: HACS (Önerilen)</h4>

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=mutlutekir&repository=ha-vestel-toshiba-tv&category=integration" target="_blank">
<img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Home Assistant örneğinizi açın ve Home Assistant Topluluk Mağazası içinde bir depo açın.">
</a>

<ol>
<li>Home Assistant'ta <strong>HACS</strong> menüsünü açın.</li>
<li><strong>Integrations</strong> kısmına gidin > sağ üstteki üç noktaya tıklayın > <strong>Custom repositories</strong>.</li>
<li>Bu reponun adresini yapıştırın: <code>https://github.com/mutlutekir/ha-vestel-toshiba-tv</code></li>
<li>Kategori olarak <strong>Integration</strong> seçin ve <strong>Ekle</strong> deyin.</li>
<li>Listeden <strong>"Vestel & Toshiba TV"</strong> entegrasyonunu bulup indirin.</li>
<li>Home Assistant'ı <strong>Yeniden Başlatın</strong>.</li>
</ol>

<h4>Yöntem 2: Manuel</h4>
<ol>
<li><code>custom_components/vestel_toshiba_tv</code> klasörünü Home Assistant dizininizdeki <code>custom_components</code> klasörünün içine kopyalayın.</li>
<li>Home Assistant'ı <strong>Yeniden Başlatın</strong>.</li>
</ol>

<h3>📱 Dashboard (Kumanda) Kurulumu</h3>
<pre><code class="language-yaml">type: custom:vestel-toshiba-tv-card
entity: media_player.vestel_toshiba_tv
title: SmartCenter TV Kumandası
</code></pre>

<h3>🛠️ Otomasyonlar</h3>
<p><code>vestel_toshiba_tv.send_key</code> servisini otomasyonlarınızda kullanabilirsiniz:</p>
<pre><code class="language-text">power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9
</code></pre>

<h3>🍏 Apple Home (HomeKit)</h3>
<p>TV, Apple Home uygulamasından ve iPhone/iPad'deki Denetim Merkezi kumandasından kontrol edilebilir. Otomasyon gerekmez; entegrasyon kumanda tuşlarını kendisi işler.</p>

<h4>Kurulum</h4>
<ol>
<li><strong>Ayarlar</strong> > <strong>Cihazlar ve Hizmetler</strong> > <strong>Entegrasyon Ekle</strong> > <strong>HomeKit Bridge</strong> yolunu izleyin.</li>
<li><code>media_player</code> alanını seçin, modu <strong>accessory</strong> yapın ve TV varlığını seçin.</li>
<li>Home Assistant bildirimindeki QR kodu Apple Home uygulamasında okutun.</li>
<li>iPhone'da Denetim Merkezi'ni açın, <strong>Kumanda</strong> simgesine dokunun ve TV'yi seçin.</li>
</ol>

<h4>Kumanda tuşları</h4>
<table>
<tr><th>Apple kumandası</th><th>TV tuşu</th></tr>
<tr><td>Yön tuşları</td><td>Yukarı / Aşağı / Sol / Sağ</td></tr>
<tr><td>Ortadaki tuş</td><td>OK</td></tr>
<tr><td>Geri</td><td>Geri</td></tr>
<tr><td>Oynat/Duraklat</td><td>Oynat</td></tr>
<tr><td>Bilgi (i)</td><td>Ana ekran</td></tr>
<tr><td>iPhone ses tuşları</td><td>Ses aç / kıs</td></tr>
</table>
<p>Eşlemeyi değiştirmek için <code>const.py</code> içindeki <code>HOMEKIT_KEY_MAP</code> sözlüğünü düzenleyin.</p>

<h4>Notlar</h4>
<ul>
<li>TV, Home Assistant'ın kendi <strong>HomeKit Bridge</strong> entegrasyonuyla ve <strong>accessory</strong> modunda eklenmelidir. Kumanda tuşları Homebridge üzerinden çalışmaz.</li>
<li>Apple kumandasında kanal tuşu yoktur ve Siri TV sesini değiştiremez. Bunlar için <code>vestel_toshiba_tv.send_key</code> çağıran script'ler kullanın.</li>
<li>TV, v1.1.0 öncesinde Apple Home'a eklendiyse Home uygulamasından kaldırıp yeniden ekleyin.</li>
</ul>

<h3>❤️ Geliştirici</h3>
<ul>
<li><strong>Geliştirici:</strong> Mutlu Tekir</li>
</ul>
