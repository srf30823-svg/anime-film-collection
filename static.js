// === ECHO UX ENHANCEMENTS ===
(function() {
  // 1. Anlık arama (debounce)
  var searchInput = document.querySelector('input[name="q"]');
  var searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function() {
        if (searchInput.value.length >= 2 || searchInput.value.length === 0) {
          searchInput.closest('form').submit();
        }
      }, 600);
    });
  }

  // 2. Lazy loading cover images
  if ('IntersectionObserver' in window) {
    var lazyImages = document.querySelectorAll('img[loading="lazy"]');
    var imgObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imgObserver.unobserve(img);
        }
      });
    });
    lazyImages.forEach(function(img) { imgObserver.observe(img); });
  }

  // 3. Scroll to top butonu
  var scrollBtn = null;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 500) {
      if (!scrollBtn) {
        scrollBtn = document.createElement('button');
        scrollBtn.innerHTML = '↑';
        scrollBtn.setAttribute('aria-label', 'Yukarı çık');
        scrollBtn.style.cssText = 'position:fixed;bottom:70px;right:14px;width:34px;height:34px;border-radius:50%;background:var(--accent);color:#fff;border:none;cursor:pointer;font-size:0.95em;opacity:0.7;z-index:99;transition:opacity 0.2s;';
        scrollBtn.onclick = function() { window.scrollTo({ top: 0, behavior: 'smooth' }); };
        scrollBtn.onmouseenter = function() { scrollBtn.style.opacity = '1'; };
        scrollBtn.onmouseleave = function() { scrollBtn.style.opacity = '0.7'; };
        document.body.appendChild(scrollBtn);
      }
      scrollBtn.style.display = 'block';
    } else if (scrollBtn) {
      scrollBtn.style.display = 'none';
    }
  });
})();

// === LAIN AUDIO — Serial Experiments Lain "Wired" Synth ===
(function() {
  var ctx = null, master = null, convolver = null, delay = null, delayGain = null, feedback = null;
  var isPlaying = false, loopId = null;
  var vol = parseFloat(localStorage.getItem('lain-vol') || '0.25');

  var BPM = 52;
  var T = {
    w: 240 / BPM,
    h: 120 / BPM,
    q:  60 / BPM,
    e:  30 / BPM,
    s:  15 / BPM,
    dh: 180 / BPM,
    dq:  90 / BPM
  };

  // Melodi — Lain "Duvet" tonlaması, E phrygian dominant
  var mel = [
    [329.63, T.dh], [0, T.h],  [311.13, T.q], [0, T.e],
    [293.66, T.dh], [0, T.h],  [329.63, T.q], [0, T.e],
    [349.23, T.dh], [0, T.h],  [392.00, T.h],
    [349.23, T.q],  [329.63, T.dh], [0, T.w],
    [261.63, T.h],  [293.66, T.q], [329.63, T.dh], [0, T.h],
    [293.66, T.q],  [0, T.e],  [261.63, T.dh], [0, T.h],
    [0, T.w * 2],
  ];

  var bass = [
    [82.41, T.w * 4], [0, T.w],
    [73.42, T.w * 4], [0, T.w],
    [82.41, T.w * 3], [65.41, T.w * 3], [0, T.w * 2],
  ];

  var pad = [
    { n: [164.81, 196.00, 246.94, 329.63, 392.00], d: T.w * 16 },
    { n: [146.83, 174.61, 220.00, 293.66, 349.23], d: T.w * 16 },
  ];

  var arp1 = [[659.25,T.e],[523.25,T.e],[493.88,T.e],[329.63,T.e],[261.63,T.e],[164.81,T.h]];
  var arp2 = [[587.33,T.e],[440.00,T.e],[349.23,T.e],[293.66,T.e],[220.00,T.e],[146.83,T.h]];
  var drone = [41.20, 61.74, 82.41];

  function createImpulse(actx, dur, decay) {
    var sr  = actx.sampleRate;
    var len = Math.floor(sr * dur);
    var buf = actx.createBuffer(2, len, sr);
    for (var ch = 0; ch < 2; ch++) {
      var d = buf.getChannelData(ch);
      for (var i = 0; i < len; i++) {
        d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
      }
    }
    return buf;
  }

  function init() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();

    master = ctx.createGain();
    master.gain.setValueAtTime(0.001, ctx.currentTime);
    master.gain.linearRampToValueAtTime(vol, ctx.currentTime + 2);

    convolver = ctx.createConvolver();
    convolver.buffer = createImpulse(ctx, 3, 2);
    var reverbGain = ctx.createGain();
    reverbGain.gain.setValueAtTime(0.28, ctx.currentTime);

    delay = ctx.createDelay(1.0);
    delay.delayTime.setValueAtTime(60 / BPM * 0.75, ctx.currentTime);
    delayGain = ctx.createGain();
    delayGain.gain.setValueAtTime(0.18, ctx.currentTime);
    feedback = ctx.createGain();
    feedback.gain.setValueAtTime(0.28, ctx.currentTime);

    var dryGain = ctx.createGain();
    dryGain.gain.setValueAtTime(0.6, ctx.currentTime);

    master.connect(dryGain);      dryGain.connect(ctx.destination);
    master.connect(convolver);    convolver.connect(reverbGain); reverbGain.connect(ctx.destination);
    master.connect(delay);        delay.connect(delayGain);
    delayGain.connect(ctx.destination);
    delayGain.connect(feedback);  feedback.connect(delay);
  }

  function playOsc(type, freq, start, dur, detune, vm) {
    if (!ctx) return;
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    var f = ctx.createBiquadFilter();

    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    if (detune) o.detune.setValueAtTime(detune, start);

    // Hafif saturation (sıcaklık)
    var w = ctx.createWaveShaper ? ctx.createWaveShaper() : null;
    if (w) {
      var curve = new Float32Array(256);
      for (var i = 0; i < 256; i++) {
        var x = (i * 2) / 256 - 1;
        curve[i] = Math.tanh(x * 1.5);
      }
      w.curve = curve;
      o.connect(w); w.connect(f);
    } else {
      o.connect(f);
    }

    f.type = 'lowpass';
    f.frequency.setValueAtTime(type === 'sine' ? 600 : type === 'sawtooth' ? 1800 : 2200, start);
    f.Q.setValueAtTime(2, start);

    var v = (vm || 0.04) * vol;
    g.gain.setValueAtTime(0, start);
    g.gain.linearRampToValueAtTime(v, start + Math.min(dur * 0.2, 0.3));
    g.gain.exponentialRampToValueAtTime(Math.max(v * 0.9, 0.0001), start + dur * 0.5);
    g.gain.linearRampToValueAtTime(0.0001, start + dur);

    f.connect(g);
    g.connect(master);
    o.start(start);
    o.stop(start + dur + 0.1);
  }

  function loop() {
    if (!isPlaying || !ctx) return;
    var t = ctx.currentTime + 0.1;
    var now = t;

    for (var i = 0; i < mel.length; i++) {
      if (mel[i][0] > 0) playOsc('triangle', mel[i][0], now, mel[i][1] * 0.85, Math.random() * 4 - 2, 0.10);
      now += mel[i][1];
    }

    now = t;
    for (var j = 0; j < bass.length; j++) {
      if (bass[j][0] > 0) playOsc('sawtooth', bass[j][0], now, bass[j][1] * 0.8, 0, 0.18);
      now += bass[j][1];
    }

    var totalMel = mel.reduce(function(s, n) { return s + n[1]; }, 0);
    var pt = 0, pi = 0;
    while (pt < totalMel) {
      var c = pad[pi % pad.length];
      for (var k = 0; k < c.n.length; k++) {
        playOsc('sine', c.n[k], t + pt, c.d * 0.9, Math.random() * 8 - 4, 0.03);
      }
      pt += c.d; pi++;
    }

    var arpLen = arp1.reduce(function(s, n) { return s + n[1]; }, 0);
    var at = 0;
    while (at < totalMel) {
      var an = Math.random() > 0.6 ? arp1 : arp2;
      var a2 = t + at;
      for (var a = 0; a < an.length; a++) {
        playOsc('sine', an[a][0], a2, an[a][1] * 0.6, 0, 0.02);
        a2 += an[a][1];
      }
      at += arpLen + T.w;
    }

    for (var di = 0; di < drone.length; di++) {
      playOsc('sine', drone[di], t, totalMel * 3, Math.random() * 6 - 3, 0.07);
    }

    loopId = setTimeout(loop, totalMel * 1000 + 2000);
  }

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
    if (loopId) clearTimeout(loopId);
    if (master && ctx) {
      master.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.6);
      setTimeout(function() {
        if (ctx) { ctx.close(); ctx = null; master = null; }
      }, 700);
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
  }

  // --- Panel UI ---
  var panel = document.createElement('div');
  panel.id = 'lain-panel';
  panel.style.cssText = 'position:fixed;bottom:58px;left:6px;z-index:98;display:flex;align-items:center;gap:5px;opacity:0;transition:opacity 0.4s;';
  panel.innerHTML =
    '<button id="lain-play" title="Serial Experiments Lain — The Wired" ' +
    'style="width:28px;height:28px;border-radius:50%;background:rgba(10,10,15,0.88);border:1px solid var(--accent);color:var(--accent);font-size:0.65em;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px);flex-shrink:0;">▶</button>' +
    '<div style="display:flex;flex-direction:column;gap:2px;">' +
    '<input id="lain-vl" type="range" min="0" max="1" step="0.01" title="Ses seviyesi" ' +
    'style="width:50px;height:2px;accent-color:var(--accent);cursor:pointer;" value="' + vol.toFixed(2) + '">' +
    '<span id="lain-pct" style="font-size:0.42em;color:var(--muted);text-align:center;">' + Math.round(vol * 100) + '%</span>' +
    '</div>';

  document.body.appendChild(panel);

  setTimeout(function() { panel.style.opacity = '0.55'; }, 1800);
  panel.onmouseenter = function() { panel.style.opacity = '1'; };
  panel.onmouseleave = function() { panel.style.opacity = '0.55'; };

  document.getElementById('lain-play').onclick = function() { isPlaying ? stopM() : startM(); };
  document.getElementById('lain-vl').oninput  = function() { setVol(parseFloat(this.value)); };

  // İlk etkileşimde otomatik başlat
  var started = false;
  function autoStart() {
    if (!started && !isPlaying) { started = true; startM(); }
    ['click', 'touchstart', 'keydown'].forEach(function(e) {
      document.removeEventListener(e, autoStart);
    });
  }
  ['click', 'touchstart', 'keydown'].forEach(function(e) {
    document.addEventListener(e, autoStart);
  });
})();
