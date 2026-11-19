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
<img width="431" height="915" alt="Ekran görüntüsü 2026-11-20 000345" src="https://github.com/user-attachments/assets/ab03b3dc-52c8-4840-9c52-7e20c4de9cb5" />


</div>

<hr>

<div id="english"></div>

<h2>🇬🇧 English</h2>

<p>
<strong>Vestel & Toshiba TV Integration</strong> allows you to control smart televisions of brands such as Vestel and Toshiba (which use the SmartCenter infrastructure) over your local network via the DIAL protocol in Home Assistant. It features a custom, realistic-looking remote control dashboard card.
</p>

<h3>✨ Features</h3>
<ul>
<li><strong>Switch between TV broadcast, YouTube and Netflix</strong> from Home Assistant, the Apple Home app or Siri. YouTube and Netflix are started directly on the TV; choosing <strong>TV</strong> closes the app and returns to the broadcast.</li>
<li><strong>See what the TV is doing:</strong> the input shows whether the TV is on its broadcast or in YouTube or Netflix, and the TV is shown as <strong>off</strong> both in standby and when it is switched off completely.</li>
<li><strong>Real volume and mute state</strong>, read from the TV, and an exact volume can be set (for example 15).</li>
<li><strong>Sensors:</strong> <strong>Status</strong> (Off, TV broadcast, YouTube, Netflix) and <strong>Volume</strong> (0–100), ready for automations, history and dashboards.</li>
<li><strong>Remote control:</strong> a dashboard card (with Netflix, YouTube and Internet keys), the <code>vestel_toshiba_tv.send_key</code> action and the Apple Home remote in Control Center.</li>
<li><strong>Apple Home and Siri:</strong> Volume up/down and Next/Previous channel buttons, plus optional shortcut inputs so Siri can change volume and channel.</li>
</ul>

<h3>📺 Supported TVs</h3>
<p>Smart TVs made by Vestel that run Vestel's own Smart TV system — the TVs that work with the <strong>Vestel Smart Center</strong>, <strong>Toshiba TV Smart Center</strong> or <strong>Regal Smart Center</strong> apps.</p>
<ul>
<li><strong>Tested:</strong> Vestel 65Q9900 (65" QLED 4K, MB180 chassis).</li>
<li><strong>Vestel's own and main licensed brands:</strong> Vestel, Regal, Finlux, SEG, Luxor, Techwood, Digihome, Toshiba (Europe), Hitachi (Europe), JVC (Europe), Telefunken.</li>
<li><strong>Some models only</strong> (depends on country and year): Medion, Tevion, Polaroid, Celcus, Innohit, Kendo, Gorenje, Panasonic (some entry-level models), Alba and Bush (older models; newer ones are made by another manufacturer), Horizon (older models; current ones are Google TV).</li>
</ul>
<p>Which manufacturer makes a brand's TVs depends on the country and the year, and Android TV / Google TV models from these brands do not use Vestel's system. If the brand's Smart Center app can control your TV, this integration should work too. Reports for other models are welcome in the issues.</p>

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
<p>The card is served by the integration and added to the dashboard resources automatically (<code>/vestel_toshiba_tv/vestel_toshiba_tv-card.js</code>, JavaScript module). If your resources are managed in YAML, add that URL yourself. Versions up to 1.1.x copied the card to <code>config/www</code>; that copy is no longer used and can be deleted.</p>

<h3>🛠️ Automations</h3>
<p>You can use the <code>vestel_toshiba_tv.send_key</code> action in your automations; target the TV entity and pick one of these keys:</p>
<pre><code class="language-text">power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9
</code></pre>
<p>The TV's state is available as two sensors on the TV device, and on the media player:</p>
<ul>
<li><strong>Status</strong> sensor: <code>off</code>, <code>tv</code> (TV broadcast), <code>youtube</code> or <code>netflix</code> (shown translated). Off also in standby.</li>
<li><strong>Volume</strong> sensor: the TV's volume, 0–100; unknown while the TV is off.</li>
<li>Media player: state <code>on</code>/<code>off</code>, attributes <code>source</code> (<code>TV</code>, <code>YouTube</code>, <code>Netflix</code>), <code>volume_level</code> (0–1) and <code>is_volume_muted</code>.</li>
</ul>

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

<h4>Buttons, Netflix/YouTube and Siri (v1.2.0)</h4>
<p>The integration adds four buttons to the TV device: <strong>Volume up</strong>, <strong>Volume down</strong>, <strong>Next channel</strong> and <strong>Previous channel</strong>. The volume buttons change the volume by 3 steps per press; change this under <strong>Settings</strong> > <strong>Devices & Services</strong> > the TV > <strong>Configure</strong>.</p>
<p><strong>Inputs:</strong> <strong>Netflix</strong> and <strong>YouTube</strong> start the app directly via DIAL; <strong>TV</strong> closes them and returns to the broadcast. The selected input also follows the TV: when Netflix or YouTube is opened with the TV remote, the input changes to it, and back to <strong>TV</strong> when the app is closed. HDMI and AV inputs cannot be selected over the network; the <code>source</code> key (via <code>send_key</code>) opens the TV's input menu.</p>
<p>To use them with Siri:</p>
<ol>
<li>Add the four button entities to a <strong>HomeKit Bridge</strong> in <strong>bridge</strong> mode (the TV itself stays in its own accessory-mode bridge). They appear in Apple Home as switches.</li>
<li>In the Apple Home app, create a scene for each one (for example "TV louder") that turns the switch on.</li>
<li>Say "Hey Siri, TV louder". Siri runs scenes by name.</li>
</ol>
<p>Avoid scene names such as "volume up": Siri may treat them as its own volume command.</p>
<p><strong>Without scenes (for Siri):</strong> HomeKit gives Siri no volume or channel control for TVs, only switching inputs. Turn on <strong>Add volume and channel shortcuts to the TV inputs</strong> under <strong>Configure</strong>: Volume up, Volume down, Next channel and Previous channel then appear in the TV's input list in Apple Home, and choosing one (or "Hey Siri, switch Living Room TV to Next channel") runs the action. Afterwards the real input is shown again, so the same shortcut can be chosen repeatedly. The channel shortcuts first close Netflix/YouTube if one is open, so the TV is back on its broadcast. The option is off by default.</p>
<p><strong>Real volume and power state:</strong> the volume and mute state are read from the TV's built-in DLNA renderer (port 2870), so Home Assistant shows them and can set an exact volume (it presses the volume keys until the level is reached; the TV ignores direct volume commands). Normal standby is reported by the TV's event websocket (port 7681); a TV switched off completely drops off the network. Both are shown as <strong>off</strong>. While Netflix or YouTube is open, the input shows that app.</p>

<h4>Notes</h4>
<ul>
<li>The TV must be added with Home Assistant's own <strong>HomeKit Bridge</strong> in <strong>accessory</strong> mode. The remote keys do not work through Homebridge.</li>
<li>The Apple remote has no channel keys, and Siri cannot change the volume of a HomeKit TV. Use the buttons below for these.</li>
<li>If the TV was added to Apple Home before v1.1.0, remove it from the Home app and add it again.</li>
</ul>

<hr>

<div id="türkçe-kılavuz"></div>

<h2>🇹🇷 Türkçe Kılavuz</h2>

<p>
<strong>Vestel & Toshiba TV Entegrasyonu</strong>, SmartCenter altyapısını kullanan Vestel ve Toshiba gibi markaların akıllı televizyonlarını Home Assistant üzerinden yerel ağda kontrol etmenizi sağlar.
</p>

<h3>✨ Özellikler</h3>
<ul>
<li><strong>TV yayını, YouTube ve Netflix arasında geçiş:</strong> Home Assistant'tan, Apple Home uygulamasından ya da Siri'den. YouTube ve Netflix TV'de doğrudan açılır; <strong>TV</strong> seçilince uygulama kapanır ve yayına dönülür.</li>
<li><strong>TV'nin ne yaptığını görme:</strong> Giriş, TV'nin yayında mı yoksa YouTube'da ya da Netflix'te mi olduğunu gösterir; TV hem bekleme modunda hem de tamamen kapatıldığında <strong>kapalı</strong> görünür.</li>
<li><strong>Gerçek ses seviyesi ve sessiz durumu</strong> TV'den okunur; ses tam bir seviyeye (ör. 15) ayarlanabilir.</li>
<li><strong>Sensörler:</strong> <strong>Durum</strong> (Kapalı, TV yayını, YouTube, Netflix) ve <strong>Ses seviyesi</strong> (0–100); otomasyonlarda, geçmişte ve dashboard'larda kullanılabilir.</li>
<li><strong>Kumanda:</strong> Dashboard kartı (Netflix, YouTube ve İnternet tuşlarıyla), <code>vestel_toshiba_tv.send_key</code> eylemi ve Denetim Merkezi'ndeki Apple Home kumandası.</li>
<li><strong>Apple Home ve Siri:</strong> Ses artır/azalt ve Sonraki/Önceki kanal düğmeleri; ayrıca Siri'nin ses ve kanal değiştirebilmesi için isteğe bağlı kısayol girişleri.</li>
</ul>

<h3>📺 Desteklenen TV'ler</h3>
<p>Vestel'in ürettiği ve Vestel'in kendi Smart TV sistemini kullanan akıllı TV'ler; yani <strong>Vestel Smart Center</strong>, <strong>Toshiba TV Smart Center</strong> veya <strong>Regal Smart Center</strong> uygulamalarıyla çalışan TV'ler.</p>
<ul>
<li><strong>Test edilen:</strong> Vestel 65Q9900 (65" QLED 4K, MB180 kasa).</li>
<li><strong>Vestel'in kendi ve başlıca lisanslı markaları:</strong> Vestel, Regal, Finlux, SEG, Luxor, Techwood, Digihome, Toshiba (Avrupa), Hitachi (Avrupa), JVC (Avrupa), Telefunken.</li>
<li><strong>Yalnızca bazı modeller</strong> (ülkeye ve yıla göre): Medion, Tevion, Polaroid, Celcus, Innohit, Kendo, Gorenje, Panasonic (bazı giriş seviyesi modeller), Alba ve Bush (eski modeller; yenilerini başka bir üretici yapıyor), Horizon (eski modeller; güncel modeller Google TV).</li>
</ul>
<p>Bir markanın TV'lerini hangi üreticinin yaptığı ülkeye ve yıla göre değişir; bu markaların Android TV / Google TV modelleri Vestel'in sistemini kullanmaz. Markanın Smart Center uygulaması TV'nizi kontrol edebiliyorsa bu entegrasyon da çalışmalıdır. Başka modellerle ilgili deneyimlerinizi issue olarak paylaşabilirsiniz.</p>

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
<p>Kart entegrasyon tarafından sunulur ve dashboard kaynaklarına kendiliğinden eklenir (<code>/vestel_toshiba_tv/vestel_toshiba_tv-card.js</code>, JavaScript modülü). Kaynaklarınızı YAML ile yönetiyorsanız bu adresi kendiniz ekleyin. 1.1.x sürümlerinin <code>config/www</code> klasörüne kopyaladığı kart artık kullanılmaz, silebilirsiniz.</p>

<h3>🛠️ Otomasyonlar</h3>
<p><code>vestel_toshiba_tv.send_key</code> eylemini otomasyonlarınızda kullanabilirsiniz; hedef olarak TV'yi seçip şu tuşlardan birini verin:</p>
<pre><code class="language-text">power, mute, volume_up, volume_down, channel_up, channel_down, up, down, left, right, ok, back, home, menu, exit, source, internet, favorites, play, stop, 0-9
</code></pre>
<p>TV'nin durumu, TV cihazındaki iki sensörden ve medya oynatıcıdan okunabilir:</p>
<ul>
<li><strong>Durum</strong> sensörü: <code>off</code>, <code>tv</code> (TV yayını), <code>youtube</code> veya <code>netflix</code> (arayüzde Türkçe görünür). Bekleme modunda da kapalıdır.</li>
<li><strong>Ses seviyesi</strong> sensörü: TV'nin ses seviyesi, 0–100; TV kapalıyken bilinmiyor görünür.</li>
<li>Medya oynatıcı: durum <code>on</code>/<code>off</code>; <code>source</code> (<code>TV</code>, <code>YouTube</code>, <code>Netflix</code>), <code>volume_level</code> (0–1) ve <code>is_volume_muted</code> özellikleri.</li>
</ul>

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

<h4>Düğmeler, Netflix/YouTube ve Siri (v1.2.0)</h4>
<p>Entegrasyon TV cihazına dört düğme ekler: <strong>Ses artır</strong>, <strong>Ses azalt</strong>, <strong>Sonraki kanal</strong> ve <strong>Önceki kanal</strong>. Ses düğmeleri her basışta sesi 3 kademe değiştirir; bunu <strong>Ayarlar</strong> > <strong>Cihazlar ve Hizmetler</strong> > TV > <strong>Yapılandır</strong> bölümünden değiştirebilirsiniz.</p>
<p><strong>Girişler:</strong> <strong>Netflix</strong> ve <strong>YouTube</strong> uygulamayı DIAL ile doğrudan açar; <strong>TV</strong> onları kapatıp yayına döner. Seçili giriş TV'yi de takip eder: Netflix veya YouTube TV'nin kendi kumandasıyla açılınca giriş o uygulama olur, uygulama kapanınca yeniden <strong>TV</strong> olur. HDMI ve AV girişleri ağ üzerinden seçilemez; <code>send_key</code> ile <code>source</code> tuşu TV'nin giriş menüsünü açar.</p>
<p>Siri ile kullanmak için:</p>
<ol>
<li>Dört düğmeyi <strong>bridge</strong> modundaki bir <strong>HomeKit Bridge</strong>'e ekleyin (TV kendi accessory modundaki köprüsünde kalır). Apple Home'da anahtar olarak görünürler.</li>
<li>Apple Home uygulamasında her biri için ilgili anahtarı açan bir sahne oluşturun (örneğin "Televizyonu yükselt").</li>
<li>"Hey Siri, televizyonu yükselt" deyin. Siri sahneleri adıyla çalıştırır.</li>
</ol>
<p>Sahnelere "sesi aç" gibi adlar vermeyin; Siri bunu kendi ses komutu sanabilir.</p>
<p><strong>Sahnesiz yöntem (Siri için):</strong> HomeKit, Siri'ye TV'lerde ses ve kanal kontrolü vermez, yalnızca giriş değiştirmeye izin verir. <strong>Yapılandır</strong> ekranında <strong>TV girişlerine ses ve kanal kısayollarını ekle</strong> seçeneğini açın: Ses artır, Ses azalt, Sonraki kanal ve Önceki kanal Apple Home'da TV'nin giriş listesine eklenir; birini seçmek (ya da "Hey Siri, Salon TV'yi Sonraki kanal'a geçir") o işlemi yapar. Ardından gerçek giriş yeniden gösterilir, böylece aynı kısayol tekrar seçilebilir. Kanal kısayolları, Netflix/YouTube açıksa önce onu kapatıp yayına döner. Seçenek varsayılan olarak kapalıdır.</p>
<p><strong>Gerçek ses ve açık/kapalı durumu:</strong> Ses seviyesi ve sessiz durumu TV'nin dahili DLNA oynatıcısından (port 2870) okunur; Home Assistant bunları gösterir ve sesi tam bir seviyeye getirebilir (TV doğrudan ses komutunu uygulamadığı için seviyeye ulaşana kadar ses tuşlarına basar). Normal bekleme modunu TV kendi olay websocket'inden (port 7681) bildirir; tamamen kapatılan TV ise ağdan düşer. İkisi de <strong>kapalı</strong> görünür. Netflix veya YouTube açıkken giriş olarak o uygulama görünür.</p>

<h4>Notlar</h4>
<ul>
<li>TV, Home Assistant'ın kendi <strong>HomeKit Bridge</strong> entegrasyonuyla ve <strong>accessory</strong> modunda eklenmelidir. Kumanda tuşları Homebridge üzerinden çalışmaz.</li>
<li>Apple kumandasında kanal tuşu yoktur ve Siri HomeKit TV'lerin sesini değiştiremez. Bunlar için aşağıdaki düğmeleri kullanın.</li>
<li>TV, v1.1.0 öncesinde Apple Home'a eklendiyse Home uygulamasından kaldırıp yeniden ekleyin.</li>
</ul>

<h3>❤️ Geliştirici</h3>
<ul>
<li><strong>Geliştirici:</strong> Mutlu Tekir</li>
</ul>
