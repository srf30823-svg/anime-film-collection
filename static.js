// === ECHO UX ENHANCEMENTS ===
(function() {
  // Anlık arama (debounce 500ms)
  var searchInput = document.querySelector('input[name="q"]');
  if (searchInput) {
    var st = null;
    searchInput.addEventListener('input', function() {
      clearTimeout(st);
      st = setTimeout(function() {
        if (searchInput.value.length >= 2 || searchInput.value.length === 0)
          searchInput.closest('form').submit();
      }, 500);
    });
  }

  // Lazy loading cover images
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          var img = e.target;
          if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
          obs.unobserve(img);
        }
      });
    });
    document.querySelectorAll('img[loading="lazy"]').forEach(function(img) { obs.observe(img); });
  }

  // Scroll-to-top butonu
  var scBtn = null;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 500) {
      if (!scBtn) {
        scBtn = document.createElement('button');
        scBtn.innerHTML = '↑';
        scBtn.setAttribute('aria-label', 'Yukarı çık');
        scBtn.style.cssText = 'position:fixed;bottom:72px;right:14px;width:34px;height:34px;border-radius:50%;background:var(--accent);color:#fff;border:none;cursor:pointer;font-size:1em;opacity:0.7;z-index:99;transition:opacity 0.2s;box-shadow:0 0 8px rgba(107,91,149,0.4)';
        scBtn.onclick = function() { window.scrollTo({ top: 0, behavior: 'smooth' }); };
        scBtn.onmouseenter = function() { scBtn.style.opacity = '1'; };
        scBtn.onmouseleave = function() { scBtn.style.opacity = '0.7'; };
        document.body.appendChild(scBtn);
      }
      scBtn.style.display = 'block';
    } else if (scBtn) { scBtn.style.display = 'none'; }
  });
})();

// === LAIN AUDIO v5 — Wired Atmospheric Synth ===
// Serial Experiments Lain "Duvet" temali, katmanli ambient synth
// Katmanlar: melodi (chorus), bas, sub-bas, pad (LFO tremolo),
//            arpej, drone, atmosferik statik, rastgele glitch
(function() {
  var ctx = null, master = null, reverb = null, dly = null;
  var lfoNode = null, lfoGain = null;
  var isPlaying = false, loopId = null, glitchId = null;
  var vol = parseFloat(localStorage.getItem('lain-vol') || '0.28');

  var BPM = 50;
  var q  = 60 / BPM;
  var T  = { w: q*4, h: q*2, q: q, e: q/2, s: q/4, dh: q*3, dq: q*1.5 };

  // ─── Nota dizisi: E phrygian dominant (Lain atmosferi) ─────────────────
  var MEL = [
    [329.63, T.dh], [0, T.h],   [311.13, T.q],  [0, T.e],
    [293.66, T.dh], [0, T.h],   [329.63, T.q],  [0, T.e],
    [349.23, T.dh], [0, T.h],   [392.00, T.h],
    [349.23, T.q],  [329.63, T.dh], [0, T.w],
    [261.63, T.h],  [293.66, T.q],  [329.63, T.dh], [0, T.h],
    [293.66, T.q],  [0, T.e],   [261.63, T.dh], [0, T.h],
    [0, T.w * 2.5],
  ];

  // Bas hattı (derin, yavaş)
  var BASS = [
    [82.41, T.w*4], [0, T.w],
    [73.42, T.w*4], [0, T.w],
    [82.41, T.w*3], [65.41, T.w*3], [0, T.w*2],
  ];

  // Pad akorları
  var PADS = [
    { n: [164.81, 196.00, 246.94, 329.63, 392.00], d: T.w*16 },
    { n: [146.83, 174.61, 220.00, 293.66, 349.23], d: T.w*16 },
  ];

  // Arpej dizisi
  var ARP1 = [[659.25,T.e],[523.25,T.e],[493.88,T.e],[329.63,T.e],[261.63,T.e],[164.81,T.h]];
  var ARP2 = [[587.33,T.e],[440.00,T.e],[349.23,T.e],[293.66,T.e],[220.00,T.e],[146.83,T.h]];

  // Drone (ultra derin)
  var DRONE = [41.20, 61.74, 82.41];

  // ─── Reverb impulse response (5 saniye, daha zengin) ──────────────────
  function mkImpulse(dur, decay, wet) {
    var sr = ctx.sampleRate, len = Math.floor(sr * dur);
    var buf = ctx.createBuffer(2, len, sr);
    for (var ch = 0; ch < 2; ch++) {
      var d = buf.getChannelData(ch);
      for (var i = 0; i < len; i++) {
        // Birden fazla bileşen: gürültü + hafif periyodik dalgalanma
        var noise = (Math.random() * 2 - 1);
        var tail  = Math.pow(1 - i / len, decay);
        var mod   = 1 + 0.08 * Math.sin(i / sr * 6.28 * 0.5);
        d[i] = noise * tail * mod * (wet || 1);
      }
    }
    return buf;
  }

  // ─── Sinyal zinciri kurulumu ───────────────────────────────────────────
  function init() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();

    // Master gain
    master = ctx.createGain();
    master.gain.setValueAtTime(0.001, ctx.currentTime);
    master.gain.linearRampToValueAtTime(vol, ctx.currentTime + 2.5);

    // Reverb
    reverb = ctx.createConvolver();
    reverb.buffer = mkImpulse(5, 1.8);
    var revGain = ctx.createGain();
    revGain.gain.setValueAtTime(0.32, ctx.currentTime);

    // Delay (noktalı sekizlik)
    dly = ctx.createDelay(2.0);
    dly.delayTime.setValueAtTime(T.q * 1.5, ctx.currentTime);
    var dlyGain = ctx.createGain();
    dlyGain.gain.setValueAtTime(0.22, ctx.currentTime);
    var fb = ctx.createGain();
    fb.gain.setValueAtTime(0.32, ctx.currentTime);

    // High-pass temizleyici (bulanıklık giderir)
    var hp = ctx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.setValueAtTime(40, ctx.currentTime);

    // Kuru/ıslak mix
    var dry = ctx.createGain();
    dry.gain.setValueAtTime(0.55, ctx.currentTime);

    master.connect(hp);
    hp.connect(dry);          dry.connect(ctx.destination);
    hp.connect(reverb);       reverb.connect(revGain);  revGain.connect(ctx.destination);
    hp.connect(dly);          dly.connect(dlyGain);
    dlyGain.connect(ctx.destination);
    dlyGain.connect(fb);      fb.connect(dly);

    // LFO tremolo — padlere sinyal yolu üzerinden (0.22 Hz)
    lfoNode = ctx.createOscillator();
    lfoGain = ctx.createGain();
    lfoNode.type = 'sine';
    lfoNode.frequency.value = 0.22;
    lfoGain.gain.value = 0.06;
    lfoNode.connect(lfoGain);
    lfoGain.connect(master.gain);
    lfoNode.start();
  }

  // ─── Saturation eğrisi ────────────────────────────────────────────────
  function mkCurve(amount) {
    var n = 256, curve = new Float32Array(n);
    for (var i = 0; i < n; i++) {
      var x = (i * 2) / n - 1;
      curve[i] = Math.tanh(x * amount);
    }
    return curve;
  }

  // ─── Temel osilatör çalma ──────────────────────────────────────────────
  function osc(type, freq, start, dur, detune, vm, filterHz) {
    if (!ctx || !master) return;
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    var f = ctx.createBiquadFilter();

    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    if (detune) o.detune.setValueAtTime(detune, start);

    // Hafif vibrato (pitch LFO)
    if (type === 'triangle') {
      var vLFO = ctx.createOscillator();
      var vGain = ctx.createGain();
      vLFO.frequency.value = 5.5;
      vGain.gain.value = 3; // 3 cent derinlik
      vLFO.connect(vGain);
      vGain.connect(o.detune);
      vLFO.start(start);
      vLFO.stop(start + dur + 0.2);
    }

    // Saturation
    var w = ctx.createWaveShaper();
    w.curve = mkCurve(type === 'sawtooth' ? 2.0 : 1.2);
    o.connect(w);

    f.type = 'lowpass';
    f.frequency.setValueAtTime(filterHz || (type === 'sine' ? 800 : 2000), start);
    f.Q.setValueAtTime(type === 'sine' ? 1 : 3, start);
    w.connect(f);

    var v = (vm || 0.05) * vol;
    var att = Math.min(dur * 0.15, 0.4);
    var rel = Math.min(dur * 0.3, 0.8);
    g.gain.setValueAtTime(0.0001, start);
    g.gain.linearRampToValueAtTime(v, start + att);
    g.gain.setValueAtTime(v * 0.85, start + dur - rel);
    g.gain.linearRampToValueAtTime(0.0001, start + dur);

    f.connect(g);
    g.connect(master);
    o.start(start);
    o.stop(start + dur + 0.15);
  }

  // ─── Chorus: 3 detuned osilatör (daha zengin ses) ─────────────────────
  function chorus(freq, start, dur, vm) {
    osc('triangle', freq, start, dur,  0,   vm * 0.55, 1400);
    osc('triangle', freq, start, dur,  9,   vm * 0.28, 1200);
    osc('triangle', freq, start, dur, -9,   vm * 0.28, 1200);
    // Hafif sine katmanı (üst parlak ton)
    osc('sine',     freq * 2, start, dur * 0.6, 0, vm * 0.04, 2800);
  }

  // ─── Beyaz gürültü / atmosferik statik ───────────────────────────────
  function staticNoise(start, dur, vm) {
    if (!ctx) return;
    var sr = ctx.sampleRate;
    var bufLen = Math.floor(sr * Math.min(dur, 8));
    var buf = ctx.createBuffer(2, bufLen, sr);
    for (var ch = 0; ch < 2; ch++) {
      var d = buf.getChannelData(ch);
      for (var i = 0; i < bufLen; i++) d[i] = Math.random() * 2 - 1;
    }
    var src = ctx.createBufferSource();
    src.buffer = buf;
    src.loop = dur > 8;

    var bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.setValueAtTime(600, start);
    bp.Q.setValueAtTime(0.4, start);

    var ng = ctx.createGain();
    var nv = (vm || 0.006) * vol;
    ng.gain.setValueAtTime(0.0001, start);
    ng.gain.linearRampToValueAtTime(nv, start + 2);
    ng.gain.linearRampToValueAtTime(nv * 0.8, start + dur - 1);
    ng.gain.linearRampToValueAtTime(0.0001, start + dur);

    src.connect(bp); bp.connect(ng); ng.connect(master);
    src.start(start);
    src.stop(start + dur + 0.1);
  }

  // ─── Glitch efekti (dijital bozulma patlaması) ────────────────────────
  function glitch(start) {
    if (!ctx) return;
    // Kısa gürültü patlaması
    var sr = ctx.sampleRate;
    var gBuf = ctx.createBuffer(1, Math.floor(sr * 0.08), sr);
    var gd = gBuf.getChannelData(0);
    for (var i = 0; i < gd.length; i++) gd[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / gd.length, 0.5);
    var gSrc = ctx.createBufferSource();
    gSrc.buffer = gBuf;
    var gGain = ctx.createGain();
    gGain.gain.setValueAtTime(0.15 * vol, start);
    gGain.gain.linearRampToValueAtTime(0.0001, start + 0.08);
    gSrc.connect(gGain); gGain.connect(master);
    gSrc.start(start); gSrc.stop(start + 0.1);

    // Pitch bend (kısa, tiz nota)
    var glitchNote = [523.25, 659.25, 783.99, 987.77][Math.floor(Math.random() * 4)];
    osc('square', glitchNote, start, 0.05, 0, 0.08, 4000);
    osc('square', glitchNote * 1.5, start + 0.04, 0.04, 0, 0.05, 3000);
  }

  // ─── Zamanlanmış glitch olayları ──────────────────────────────────────
  function scheduleGlitches(startTime, totalDur) {
    // Döngü başına 2-4 glitch, rastgele konumda
    var count = 2 + Math.floor(Math.random() * 3);
    for (var i = 0; i < count; i++) {
      var offset = T.w * 4 + Math.random() * (totalDur - T.w * 6);
      glitch(startTime + offset);
    }
  }

  // ─── Ana oynatma döngüsü ───────────────────────────────────────────────
  function loop() {
    if (!isPlaying || !ctx) return;
    var t = ctx.currentTime + 0.12;
    var now = t;

    // 1. Melodi katmanı (chorus)
    for (var i = 0; i < MEL.length; i++) {
      if (MEL[i][0] > 0) chorus(MEL[i][0], now, MEL[i][1] * 0.88, 0.11);
      now += MEL[i][1];
    }
    var totalMel = now - t;

    // 2. Bas katmanı (sawtooth, derin)
    now = t;
    for (var j = 0; j < BASS.length; j++) {
      if (BASS[j][0] > 0) osc('sawtooth', BASS[j][0], now, BASS[j][1] * 0.82, 0, 0.20, 400);
      now += BASS[j][1];
    }

    // 3. Sub-bas (bir oktav aşağı, sine)
    now = t;
    for (var js = 0; js < BASS.length; js++) {
      if (BASS[js][0] > 0) osc('sine', BASS[js][0] * 0.5, now, BASS[js][1] * 0.9, 0, 0.14, 200);
      now += BASS[js][1];
    }

    // 4. Pad katmanı (sine dronlar, LFO tremololu)
    var pt = 0, pi = 0;
    while (pt < totalMel) {
      var pc = PADS[pi % PADS.length];
      for (var k = 0; k < pc.n.length; k++) {
        var detune = (k % 2 === 0 ? 1 : -1) * Math.random() * 6;
        osc('sine', pc.n[k], t + pt, pc.d * 0.93, detune, 0.032, 1800);
      }
      pt += pc.d; pi++;
    }

    // 5. Arpej katmanı (yankılanan, düşük ses)
    var arpLen = ARP1.reduce(function(s, n) { return s + n[1]; }, 0);
    var at = 0;
    while (at < totalMel - arpLen) {
      var an = Math.random() > 0.55 ? ARP1 : ARP2;
      var a2 = t + at + T.w;
      for (var a = 0; a < an.length; a++) {
        osc('sine', an[a][0], a2, an[a][1] * 0.65, 0, 0.022, 2400);
        a2 += an[a][1];
      }
      at += arpLen + T.w * (1 + Math.floor(Math.random() * 2));
    }

    // 6. Drone katmanı (en derin, tüm döngü boyunca)
    for (var di = 0; di < DRONE.length; di++) {
      osc('sine', DRONE[di], t, totalMel * 3.2, Math.random() * 8 - 4, 0.065, 120);
    }

    // 7. Atmosferik statik gürültü
    staticNoise(t, totalMel, 0.0045);

    // 8. Glitch efektleri
    scheduleGlitches(t, totalMel);

    // Bir sonraki döngüyü zamanla
    loopId = setTimeout(loop, (totalMel + 1.5) * 1000);
  }

  // ─── Oynatma kontrol fonksiyonları ────────────────────────────────────
  function startM() {
    init();
    if (ctx.state === 'suspended') ctx.resume();
    isPlaying = true;
    loop();
    updateUI();
  }

  function stopM() {
    if (!isPlaying) return;
    isPlaying = false;
    clearTimeout(loopId);
    clearTimeout(glitchId);
    if (lfoNode) { try { lfoNode.stop(); } catch(e) {} lfoNode = null; }
    if (master && ctx) {
      master.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.8);
      setTimeout(function() {
        if (ctx) { ctx.close(); ctx = null; master = null; reverb = null; }
      }, 900);
    }
    updateUI();
  }

  function setVol(v) {
    vol = Math.max(0, Math.min(1, v));
    localStorage.setItem('lain-vol', vol.toFixed(2));
    if (master && ctx) master.gain.setValueAtTime(vol, ctx.currentTime);
    var p = document.getElementById('lain-pct');
    if (p) p.textContent = Math.round(vol * 100) + '%';
  }

  function updateUI() {
    var b = document.getElementById('lain-play');
    if (!b) return;
    b.textContent = isPlaying ? '⏸' : '▶';
    b.style.borderColor = isPlaying ? '#2dd4bf' : 'var(--accent)';
    b.style.color       = isPlaying ? '#2dd4bf' : 'var(--accent)';
    b.style.boxShadow   = isPlaying ? '0 0 6px rgba(45,212,191,0.4)' : 'none';
  }

  // ─── Panel UI (minimal Lain temalı) ───────────────────────────────────
  var panel = document.createElement('div');
  panel.id = 'lain-panel';
  panel.style.cssText = [
    'position:fixed;bottom:60px;left:6px;z-index:98',
    'display:flex;align-items:center;gap:6px',
    'opacity:0;transition:opacity 0.5s',
  ].join(';');

  panel.innerHTML =
    '<button id="lain-play" title="The Wired is everywhere..." ' +
      'style="width:30px;height:30px;border-radius:50%;' +
      'background:rgba(8,8,14,0.92);border:1px solid var(--accent);' +
      'color:var(--accent);font-size:0.68em;cursor:pointer;' +
      'display:flex;align-items:center;justify-content:center;' +
      'backdrop-filter:blur(8px);flex-shrink:0;transition:all 0.2s">▶</button>' +
    '<div style="display:flex;flex-direction:column;gap:3px;min-width:52px">' +
      '<input id="lain-vl" type="range" min="0" max="1" step="0.01" ' +
        'title="Ses" style="width:52px;height:2px;accent-color:var(--accent);cursor:pointer" ' +
        'value="' + vol.toFixed(2) + '">' +
      '<span id="lain-pct" style="font-size:0.4em;color:var(--muted);text-align:center;' +
        'letter-spacing:0.06em">' + Math.round(vol * 100) + '%</span>' +
    '</div>';

  document.body.appendChild(panel);

  // 2 saniye sonra belir
  setTimeout(function() { panel.style.opacity = '0.55'; }, 2000);
  panel.onmouseenter = function() { panel.style.opacity = '1'; };
  panel.onmouseleave = function() { panel.style.opacity = '0.55'; };

  document.getElementById('lain-play').onclick = function() { isPlaying ? stopM() : startM(); };
  document.getElementById('lain-vl').oninput   = function() { setVol(parseFloat(this.value)); };

  // İlk kullanıcı etkileşiminde otomatik başlat
  var started = false;
  function autoStart() {
    if (!started) { started = true; startM(); }
    ['click', 'touchstart', 'keydown'].forEach(function(ev) {
      document.removeEventListener(ev, autoStart);
    });
  }
  ['click', 'touchstart', 'keydown'].forEach(function(ev) {
    document.addEventListener(ev, autoStart);
  });
})();
