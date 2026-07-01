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

<hr>

<div id="türkçe-kılavuz"></div>

<h2>🇹🇷 Türkçe Kılavuz</h2>

<p>
<strong>Vestel & Toshiba TV Entegrasyonu</strong>, SmartCenter altyapısını kullanan Vestel, Toshiba, JVC, Hitachi, Telefunken gibi markaların akıllı televizyonlarını Home Assistant üzerinden yerel ağda kontrol etmenizi sağlar.
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

<h3>❤️ Geliştirici</h3>
<ul>
<li><strong>Geliştirici:</strong> Mutlu Tekir</li>
</ul>
