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
  // 3. Tema değiştirici (localStorage)
  var theme = localStorage.getItem('echo-theme') || 'dark';
  if (theme === 'light') { document.documentElement.classList.add('light-theme'); }
  // 4.Scroll to top
  var scrollBtn = null;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 500) {
      if (!scrollBtn) {
        scrollBtn = document.createElement('button');
        scrollBtn.innerHTML = '↑';
        scrollBtn.style.cssText = 'position:fixed;bottom:70px;right:16px;width:36px;height:36px;border-radius:50%;background:var(--accent);color:#fff;border:none;cursor:pointer;font-size:1em;opacity:0.7;z-index:99;';
        scrollBtn.onclick = function() { window.scrollTo({top:0,behavior:'smooth'}); };
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

// === LAIN AUDIO v4 — Kaliteli synth + Reverb + Delay ===
(function() {
  var ctx, master, convolver, delay, delayGain, feedback;
  var isPlaying = false, loopId = null;
  var vol = parseFloat(localStorage.getItem('lain-vol') || '0.3');

  var BPM = 52;
  var T = { w: 240/BPM, h: 120/BPM, q: 60/BPM, e: 30/BPM, s: 15/BPM,
            dh: 180/BPM, dq: 90/BPM };

  // Melodi — Lain "Duvet" tonlaması, E phrygian dominant
  var mel = [
    [329.63, T.dh], [0, T.h], [311.13, T.q], [0, T.e],
    [293.66, T.dh], [0, T.h], [329.63, T.q], [0, T.e],
    [349.23, T.dh], [0, T.h], [392.00, T.h],
    [349.23, T.q], [329.63, T.dh], [0, T.w],
    [261.63, T.h], [293.66, T.q], [329.63, T.dh], [0, T.h],
    [293.66, T.q], [0, T.e], [261.63, T.dh], [0, T.h],
    [0, T.w*2],
  ];

  var bass = [
    [82.41, T.w*4], [0, T.w], [73.42, T.w*4], [0, T.w],
    [82.41, T.w*3], [65.41, T.w*3], [0, T.w*2],
  ];

  var pad = [
    { n: [164.81, 196.00, 246.94, 329.63, 392.00], d: T.w*16 },
    { n: [146.83, 174.61, 220.00, 293.66, 349.23], d: T.w*16 },
  ];

  var arp1 = [[659.25,T.e],[523.25,T.e],[493.88,T.e],[329.63,T.e],[261.63,T.e],[164.81,T.h]];
  var arp2 = [[587.33,T.e],[440.00,T.e],[349.23,T.e],[293.66,T.e],[220.00,T.e],[146.83,T.h]];
  var drone = [41.20, 61.74, 82.41];

  // Reverb için impulse response oluştur
  function createImpulse(ctx, dur, decay) {
    var sr = ctx.sampleRate;
    var len = sr * dur;
    var buf = ctx.createBuffer(2, len, sr);
    for (var ch = 0; ch < 2; ch++) {
      var data = buf.getChannelData(ch);
      for (var i = 0; i < len; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
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

    // Reverb
    convolver = ctx.createConvolver();
    convolver.buffer = createImpulse(ctx, 3, 2);
    var reverbGain = ctx.createGain();
    reverbGain.gain.setValueAtTime(0.3, ctx.currentTime);

    // Delay
    delay = ctx.createDelay(1);
    delay.delayTime.setValueAtTime(60 / BPM * 0.75, ctx.currentTime); // dotted eighth
    delayGain = ctx.createGain();
    delayGain.gain.setValueAtTime(0.2, ctx.currentTime);
    feedback = ctx.createGain();
    feedback.gain.setValueAtTime(0.3, ctx.currentTime);

    // Routing: master → dry + reverb + delay
    var dryGain = ctx.createGain();
    dryGain.gain.setValueAtTime(0.6, ctx.currentTime);

    master.connect(dryGain);
    dryGain.connect(ctx.destination);

    master.connect(convolver);
    convolver.connect(reverbGain);
    reverbGain.connect(ctx.destination);

    master.connect(delay);
    delay.connect(delayGain);
    delayGain.connect(ctx.destination);
    delayGain.connect(feedback);
    feedback.connect(delay);
  }

  function playOsc(type, freq, start, dur, detune, vm) {
    var o = ctx.createOscillator();
    var g = ctx.createGain();
    var f = ctx.createBiquadFilter();
    var w = ctx.createWaveShaperNode ? ctx.createWaveShaperNode() : null;

    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    if (detune) o.detune.setValueAtTime(detune, start);

    // Warmth için slight saturation
    if (w) {
      var curve = new Float32Array(256);
      for (var i = 0; i < 256; i++) {
        var x = (i * 2) / 256 - 1;
        curve[i] = Math.tanh(x * 1.5);
      }
      w.curve = curve;
      o.connect(w);
      w.connect(f);
    } else {
      o.connect(f);
    }

    f.type = 'lowpass';
    f.frequency.setValueAtTime(type === 'sine' ? 600 : type === 'sawtooth' ? 1800 : 2200, start);
    f.Q.setValueAtTime(2, start);

    var v = (vm || 0.04) * vol;
    g.gain.setValueAtTime(0, start);
    g.gain.linearRampToValueAtTime(v, start + Math.min(dur * 0.2, 0.3));
    g.gain.exponentialRampToValueAtTime(v * 0.9, start + dur * 0.5);
    g.gain.linearRampToValueAtTime(0, start + dur);

    f.connect(g);
    g.connect(master);
    o.start(start);
    o.stop(start + dur + 0.1);
  }

  function loop() {
    if (!isPlaying) return;
    var t = ctx.currentTime + 0.1;
    var now = t;

    for (var i = 0; i < mel.length; i++) {
      if (mel[i][0] > 0) playOsc('triangle', mel[i][0], now, mel[i][1]*0.85, Math.random()*4-2, 0.1);
      now += mel[i][1];
    }

    now = t;
    for (var j = 0; j < bass.length; j++) {
      if (bass[j][0] > 0) playOsc('sawtooth', bass[j][0], now, bass[j][1]*0.8, 0, 0.18);
      now += bass[j][1];
    }

    var totalMel = mel.reduce(function(s,n){return s+n[1];}, 0);
    var pt = 0, pi = 0;
    while (pt < totalMel) {
      var c = pad[pi % pad.length];
      for (var k = 0; k < c.n.length; k++) {
        playOsc('sine', c.n[k], t + pt, c.d * 0.9, Math.random()*8-4, 0.03);
      }
      pt += c.d; pi++;
    }

    var arpLen = arp1.reduce(function(s,n){return s+n[1];}, 0);
    var at = 0;
    while (at < totalMel) {
      var an = Math.random() > 0.6 ? arp1 : arp2;
      var a2 = t + at;
      for (var a = 0; a < an.length; a++) {
        playOsc('sine', an[a][0], a2, an[a][1]*0.6, 0, 0.02);
        a2 += an[a][1];
      }
      at += arpLen + T.w;
    }

    for (var d = 0; d < drone.length; d++) {
      playOsc('sine', drone[d], t, totalMel * 3, Math.random()*6-3, 0.07);
    }

    loopId = setTimeout(loop, totalMel * 1000 + 2000);
  }

  function startM() {
    init(); isPlaying = true; loop();
    updateUI();
  }

  function stopM() {
    if (!isPlaying) return;
    isPlaying = false;
    if (loopId) clearTimeout(loopId);
    if (master && ctx) {
      master.gain.linearRampToValueAtTime(0.001, ctx.currentTime + 0.5);
      setTimeout(function() { if (ctx) { ctx.close(); ctx = null; } }, 600);
    }
    updateUI();
  }

  function setVol(v) {
    vol = Math.max(0, Math.min(1, v));
    localStorage.setItem('lain-vol', vol.toFixed(2));
    if (master && ctx) master.gain.setValueAtTime(vol, ctx.currentTime);
    var p = document.getElementById('lain-pct');
    if (p) p.textContent = Math.round(vol*100) + '%';
  }

  function updateUI() {
    var b = document.getElementById('lain-play');
    if (b) {
      b.textContent = isPlaying ? '⏸' : '▶';
      b.style.borderColor = isPlaying ? '#2dd4bf' : 'var(--accent)';
      b.style.color = isPlaying ? '#2dd4bf' : 'var(--accent)';
    }
  }

  var panel = document.createElement('div');
  panel.style.cssText = 'position:fixed;bottom:56px;left:4px;z-index:98;display:flex;align-items:center;gap:4px;opacity:0;transition:opacity 0.5s';
  panel.innerHTML =
    '<button id="lain-play" title="Lain — Wired" style="width:26px;height:26px;border-radius:50%;background:rgba(10,10,15,0.85);border:1px solid var(--accent);color:var(--accent);font-size:0.65em;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px)">▶</button>' +
    '<input id="lain-vl" type="range" min="0" max="1" step="0.01" title="Ses" style="width:48px;height:2px;accent-color:var(--accent)">' +
    '<span id="lain-pct" style="font-size:0.4em;color:var(--muted);width:20px;text-align:center">30%</span>';
  document.body.appendChild(panel);

  setTimeout(function(){panel.style.opacity='0.5';}, 1500);
  panel.onmouseenter=function(){panel.style.opacity='1';};
  panel.onmouseleave=function(){panel.style.opacity='0.5';};

  document.getElementById('lain-play').onclick = function() { isPlaying ? stopM() : startM(); };
  document.getElementById('lain-vl').oninput = function() { setVol(parseFloat(this.value)); };

  var auto = false;
  function aStart() {
    if (!auto && !isPlaying) { auto = true; startM(); }
    ['click','touchstart','keydown'].forEach(function(e){document.removeEventListener(e,aStart);});
  }
  ['click','touchstart','keydown'].forEach(function(e){document.addEventListener(e,aStart);});
})();

  // Lain temposu: 50-65 BPM arası, yavaş, atmospheric
  var BPM = 55;
  var T = { whole: 60/BPM*4, half: 60/BPM*2, quarter: 60/BPM, eighth: 60/BPM/2,
            dotted_half: 60/BPM*3, dotted_q: 60/BPM*1.5 };

  // === MELODİ: Ana tema — Lain'in "Wired" temasına sadık, E minor ===
  // Her eleman: [nota_hz, süre, oscillator_type, volume_multiplier]
  var melody = [
    [329.63, T.dotted_half],                    // E4
    [0, T.half],
    [311.13, T.quarter],                        // Eb4
    [0, T.eighth],
    [293.66, T.dotted_half],                    // D4
    [0, T.half],
    [329.63, T.quarter],                        // E4
    [0, T.eighth],
    [349.23, T.dotted_half],                    // F4
    [0, T.half],
    [392.00, T.half],                           // G4
    [349.23, T.quarter],                        // F4
    [329.63, T.dotted_half],                    // E4
    [0, T.whole],
    [261.63, T.half],                           // C4
    [293.66, T.quarter],                        // D4
    [329.63, T.dotted_half],                    // E4
    [0, T.half],
    [293.66, T.quarter],                        // D4
    [0, T.eighth],
    [261.63, T.dotted_half],                    // C4
    [0, T.half],
    [0, T.whole * 2],                           // Uzun sessizlik
  ];

  // === BASS: Derin, yavaş, karanlık ===
  var bassLine = [
    [82.41,  T.whole * 4],                      // E2
    [0, T.whole],
    [73.42,  T.whole * 4],                      // D2
    [0, T.whole],
    [82.41,  T.whole * 3],                      // E2
    [65.41,  T.whole * 3],                      // C2
    [0, T.whole * 2],
  ];

  // === PAD: Sürekli dron ===
  var padChord = [
    { notes: [164.81, 196.00, 246.94, 329.63], dur: T.whole * 16 },  // E minor maj7
    { notes: [146.83, 174.61, 220.00, 293.66], dur: T.whole * 16 },  // D maj7
  ];

  // === ARPEJ: Parmak izi gibi yankılanan notalar ===
  var arpeggio = [
    [659.25, T.eighth],                         // E5
    [523.25, T.eighth],                         // C5
    [493.88, T.eighth],                         // B4
    [329.63, T.eighth],                         // E4
    [261.63, T.eighth],                         // C4
    [164.81, T.half],                           // E3
  ];

  var arpeggio2 = [
    [587.33, T.eighth],                         // D5
    [440.00, T.eighth],                         // A4
    [349.23, T.eighth],                         // F4
    [293.66, T.eighth],                         // D4
    [220.00, T.eighth],                         // A3
    [146.83, T.half],                           // D3
  ];

  // === DRONE: Ultra derin sese mantık ===
  var droneNotes = [41.20, 61.74];              // E1, B0

  function mkOsc(c, type, freq, start, dur, detuneVal, volMul) {
    var o = c.createOscillator();
    var g = c.createGain();
    var f = c.createBiquadFilter();
    o.type = type;
    o.frequency.setValueAtTime(freq, start);
    if (detuneVal) o.detune.setValueAtTime(detuneVal, start);
    f.type = 'lowpass';
    f.frequency.setValueAtTime(type === 'sine' ? 800 : 2500, start);
    f.Q.setValueAtTime(3, start);
    var v = (volMul || 0.05) * vol;
    g.gain.setValueAtTime(0, start);
    g.gain.linearRampToValueAtTime(v, start + Math.min(dur * 0.3, 0.5));
    g.gain.setValueAtTime(v, start + dur * 0.7);
    g.gain.linearRampToValueAtTime(0, start + dur);
    o.connect(f); f.connect(g); g.connect(master);
    o.start(start); o.stop(start + dur + 0.1);
  }

  function playLoop() {
    if (!isPlaying) return;
    var t = ctx.currentTime + 0.15;
    var now = t;

    // MELODİ katmanı — triangle + slight detune
    for (var i = 0; i < melody.length; i++) {
      var n = melody[i];
      if (n[0] > 0) mkOsc(ctx, 'triangle', n[0], now, n[1] * 0.9, Math.random()*6-3, 0.12);
      now += n[1];
    }

    // BASS katmanı — sawtooth + heavy filter
    now = t;
    for (var j = 0; j < bassLine.length; j++) {
      var b = bassLine[j];
      if (b[0] > 0) mkOsc(ctx, 'sawtooth', b[0], now, b[1] * 0.8, 0, 0.15);
      now += b[1];
    }

    // PAD katmanı — sine wave dron
    var padIdx = 0;
    var padTime = 0;
    var totalMelody = melody.reduce(function(s,n){return s+n[1];}, 0);
    while (padTime < totalMelody) {
      var chord = padChord[padIdx % padChord.length];
      for (var k = 0; k < chord.notes.length; k++) {
        mkOsc(ctx, 'sine', chord.notes[k], t + padTime, chord.dur * 0.95, Math.random()*10-5, 0.04);
      }
      padTime += chord.dur;
      padIdx++;
    }

    // ARPEJ katmanı — echo gibi, düşük ses
    var arpLen = arpeggio.reduce(function(s,n){return s+n[1];}, 0);
    var arpTime = 0;
    while (arpTime < totalMelody) {
      var arpNotes = Math.random() > 0.5 ? arpeggio : arpeggio2;
      var at2 = t + arpTime;
      for (var a = 0; a < arpNotes.length; a++) {
        var an = arpNotes[a];
        mkOsc(ctx, 'sine', an[0], at2, an[1] * 0.7, 0, 0.025);
        at2 += an[1];
      }
      arpTime += arpLen + T.whole;
    }

    // DRONE katmanı
    for (var d = 0; d < droneNotes.length; d++) {
      mkOsc(ctx, 'sine', droneNotes[d], t, totalMelody * 4, Math.random()*8-4, 0.06);
    }

    var totalMs = totalMelody * 1000 + 1000;
    loopId = setTimeout(playLoop, totalMs);
  }

  function startM() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain();
      master.gain.setValueAtTime(vol, ctx.currentTime);
      master.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') ctx.resume();
    isPlaying = true;
    playLoop();
    updateUI();
  }

  function stopM() {
    isPlaying = false;
    if (loopId) clearTimeout(loopId);
    if (ctx) { ctx.close(); ctx = null; master = null; }
    updateUI();
  }

  function setVol(v) {
    vol = Math.max(0, Math.min(1, v));
    localStorage.setItem('lain-vol', vol.toFixed(2));
    if (master && ctx) master.gain.setValueAtTime(vol, ctx.currentTime);
    updateUI();
  }

  function updateUI() {
    var btn = document.getElementById('lain-play');
    if (btn) {
      btn.textContent = isPlaying ? '⏸' : '▶';
      btn.style.borderColor = isPlaying ? '#2dd4bf' : 'var(--accent)';
      btn.style.color = isPlaying ? '#2dd4bf' : 'var(--accent)';
    }
    var vl = document.getElementById('lain-vl');
    if (vl) vl.value = vol;
    var pct = document.getElementById('lain-pct');
    if (pct) pct.textContent = Math.round(vol * 100) + '%';
  }

  // UI — minimalist, Lain temalı
  var panel = document.createElement('div');
  panel.style.cssText = 'position:fixed;bottom:56px;left:4px;z-index:98;display:flex;align-items:center;gap:5px;opacity:0;transition:opacity 0.5s';
  panel.innerHTML =
    '<button id="lain-play" title="Serial Experiments Lain — Wired" style="width:28px;height:28px;border-radius:50%;background:rgba(10,10,15,0.8);border:1px solid var(--accent);color:var(--accent);font-size:0.7em;cursor:pointer;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)">▶</button>' +
    '<div style="display:flex;flex-direction:column;gap:1px">' +
    '<input id="lain-vl" type="range" min="0" max="1" step="0.01" title="Ses" style="width:52px;height:2px;accent-color:var(--accent);cursor:pointer">' +
    '<span id="lain-pct" style="font-size:0.45em;color:var(--muted);text-align:center">25%</span>' +
    '</div>';
  document.body.appendChild(panel);

  // 2sn sonra göster
  setTimeout(function() { panel.style.opacity = '0.6'; }, 2000);
  panel.onmouseenter = function() { panel.style.opacity = '1'; };
  panel.onmouseleave = function() { panel.style.opacity = '0.6'; };

  document.getElementById('lain-play').onclick = function() { isPlaying ? stopM() : startM(); };
  document.getElementById('lain-vl').oninput = function() { setVol(parseFloat(this.value)); };

  // İlk etkileşimde otomatik başlat
  var started = false;
  function autoStart() {
    if (!started && !isPlaying) { started = true; startM(); }
    ['click','touchstart','keydown'].forEach(function(e) { document.removeEventListener(e, autoStart); });
  }
  ['click','touchstart','keydown'].forEach(function(e) { document.addEventListener(e, autoStart); });
})();