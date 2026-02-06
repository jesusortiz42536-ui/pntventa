/**
 * Cargo-GO PWA - App JavaScript v3.0
 * Paqueteria Express + Marketplace
 * Sistema 100% completo y profesional
 */

const API = '';  // Same origin

const App = {
  usuario: null,
  cotizacionData: null,
  negocios: [],
  historialData: [],
  screenStack: [],
  currentScreen: 'dashboard',
  currentTrackEnvio: null,
  mapAnimInterval: null,

  // ═══════════ INIT ═══════════

  init() {
    // Splash screen
    setTimeout(() => {
      document.getElementById('splash').classList.add('hide');
      setTimeout(() => {
        document.getElementById('splash').style.display = 'none';
        this.checkSession();
      }, 600);
    }, 2200);

    // Event listeners
    document.getElementById('form-login').addEventListener('submit', (e) => {
      e.preventDefault();
      this.login();
    });

    document.getElementById('form-registro-negocio').addEventListener('submit', (e) => {
      e.preventDefault();
      this.registrarNegocio();
    });

    // CP auto-detect
    document.getElementById('envio-cp').addEventListener('input', (e) => {
      if (e.target.value.length === 5) {
        this.detectarZona(e.target.value);
      } else {
        document.getElementById('zona-detectada').style.display = 'none';
      }
      this.updateLiveCost();
      this.validateFormFields();
    });

    // Peso change -> live cost
    document.getElementById('envio-peso').addEventListener('input', () => {
      this.updateLiveCost();
      this.validateFormFields();
    });

    // Tipo paquete change -> live cost
    document.getElementById('envio-tipo').addEventListener('change', () => {
      this.updateLiveCost();
    });

    // Real-time form validation on all envio fields
    const envioFields = [
      'envio-origen-nombre', 'envio-origen-tel',
      'envio-destino-nombre', 'envio-destino-tel',
      'envio-cp', 'envio-direccion', 'envio-contenido', 'envio-peso'
    ];
    envioFields.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('input', () => this.validateFormFields());
        el.addEventListener('blur', () => this.validateSingleField(id));
      }
    });

    // Home search
    document.getElementById('home-search-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = e.target.value.trim().toUpperCase();
        if (val.startsWith('CGO-')) {
          this.navigate('rastrear');
          document.getElementById('rastreo-folio').value = val;
          this.rastrear();
        } else if (val.length > 0) {
          this.navigate('marketplace');
        }
        e.target.value = '';
      }
    });

    // Rastreo folio enter key
    document.getElementById('rastreo-folio').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.rastrear();
    });

    // Back button
    document.getElementById('btn-back').addEventListener('click', () => this.goBack());

    // Set current date
    const hoy = new Date();
    const opciones = { weekday: 'long', day: 'numeric', month: 'long' };
    document.getElementById('current-date').textContent =
      hoy.toLocaleDateString('es-MX', opciones);

    // Register SW
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('service-worker.js').catch(() => {});
    }
  },

  // ═══════════ SESSION ═══════════

  checkSession() {
    const saved = localStorage.getItem('cargo_go_user');
    if (saved) {
      this.usuario = JSON.parse(saved);
      this.showApp();
    } else {
      document.getElementById('screen-login').style.display = 'flex';
    }
  },

  // ═══════════ AUTH ═══════════

  async login() {
    const usuario = document.getElementById('login-usuario').value.trim();
    const password = document.getElementById('login-password').value.trim();

    if (!usuario || !password) {
      this.toast('Ingresa usuario y contrasena', 'error');
      return;
    }

    const btn = document.getElementById('btn-login');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-inline"></span> Verificando...';
    btn.classList.add('btn-loading');

    try {
      const res = await fetch(`${API}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usuario, password })
      });

      const data = await res.json();

      if (data.success) {
        this.usuario = data.usuario;
        localStorage.setItem('cargo_go_user', JSON.stringify(data.usuario));
        this.toast('Bienvenido a Cargo-GO', 'success');
        this.showApp();
      } else {
        this.toast(data.error || 'Credenciales incorrectas', 'error');
      }
    } catch (err) {
      this.toast('Error de conexion', 'error');
    }

    btn.innerHTML = originalHtml;
    btn.classList.remove('btn-loading');
  },

  logout() {
    localStorage.removeItem('cargo_go_user');
    this.usuario = null;
    document.getElementById('app-container').style.display = 'none';
    document.getElementById('screen-login').style.display = 'flex';
    document.getElementById('login-usuario').value = '';
    document.getElementById('login-password').value = '';
  },

  showApp() {
    document.getElementById('screen-login').style.display = 'none';
    document.getElementById('app-container').style.display = 'block';

    // Set user info
    document.getElementById('welcome-name').textContent = this.usuario.nombre || 'Usuario';
    document.getElementById('perfil-nombre').textContent = this.usuario.nombre || 'Usuario';
    document.getElementById('perfil-rol').textContent = this.usuario.nivel || 'Operador';

    this.loadStats();
    this.loadHomeData();
    this.navigate('dashboard');
  },

  // ═══════════ NAVIGATION ═══════════

  navigate(screen) {
    const mainScreens = ['dashboard', 'nuevo-envio', 'rastrear', 'marketplace', 'historial', 'perfil'];
    const isMain = mainScreens.includes(screen);

    // Hide all screens
    document.querySelectorAll('#app-container .screen').forEach(s => {
      s.classList.remove('active');
    });

    // Show target
    const target = document.getElementById(`screen-${screen}`);
    if (target) {
      target.classList.add('active');
    }

    // Update nav
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.screen === screen);
    });

    // Header: hide on dashboard (home has its own), show on others
    const appHeader = document.querySelector('.app-header');
    if (appHeader) {
      appHeader.style.display = (screen === 'dashboard') ? 'none' : 'flex';
    }

    // Back button
    const btnBack = document.getElementById('btn-back');
    const headerLogo = document.getElementById('header-logo');

    if (!isMain) {
      btnBack.style.display = 'flex';
      if (headerLogo) headerLogo.style.display = 'none';
      this.screenStack.push(this.currentScreen);
    } else {
      btnBack.style.display = 'none';
      if (headerLogo) headerLogo.style.display = 'block';
      this.screenStack = [];
    }

    this.currentScreen = screen;

    // Load screen data
    if (screen === 'marketplace') this.loadNegocios();
    if (screen === 'historial') this.loadHistorial();
    if (screen === 'dashboard') { this.loadStats(); this.loadHomeData(); }
    if (screen === 'perfil') this.loadPerfil();
    if (screen === 'nuevo-envio') this.initFormProgress();

    // Stop map animation when leaving rastrear
    if (screen !== 'rastrear' && this.mapAnimInterval) {
      clearInterval(this.mapAnimInterval);
      this.mapAnimInterval = null;
    }
  },

  goBack() {
    const prev = this.screenStack.pop() || 'dashboard';
    this.navigate(prev);
  },

  // ═══════════ STATS WITH ANIMATION ═══════════

  async loadStats() {
    try {
      const res = await fetch(`${API}/api/stats`);
      const data = await res.json();

      this.animateValue('stat-envios', data.envios_hoy || 0);
      this.animateValue('stat-ruta', data.en_ruta || 0);
      this.animateValue('stat-entregados', data.entregados || 0);
      this.animateStatText('stat-ingresos',
        '$' + (data.ingresos_hoy || 0).toLocaleString('es-MX', { minimumFractionDigits: 0 }));
      document.getElementById('stat-negocios').textContent = data.negocios_activos || 0;
    } catch (err) {
      console.log('Stats error:', err);
    }
  },

  animateValue(id, endVal) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('stat-animate');
    const startVal = parseInt(el.textContent) || 0;
    if (startVal === endVal) { el.textContent = endVal; return; }
    const duration = 600;
    const startTime = Date.now();
    const tick = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(startVal + (endVal - startVal) * eased);
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    setTimeout(() => el.classList.remove('stat-animate'), 600);
  },

  animateStatText(id, text) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add('stat-animate');
    el.textContent = text;
    setTimeout(() => el.classList.remove('stat-animate'), 600);
  },

  async loadPerfil() {
    try {
      const res = await fetch(`${API}/api/stats`);
      const data = await res.json();

      this.animateValue('perfil-total-envios', data.total_envios || 0);
      this.animateValue('perfil-negocios', data.negocios_activos || 0);
      this.animateValue('perfil-repartidores', data.repartidores_activos || 0);
    } catch (err) {}
  },

  // ═══════════ HOME DATA ═══════════

  async loadHomeData() {
    // Load recent historial for home
    try {
      const res = await fetch(`${API}/api/historial`);
      const envios = await res.json();
      const el = document.getElementById('home-historial');

      const iconMap = {
        'RECIBIDO': 'fas fa-inbox',
        'ASIGNADO': 'fas fa-user-check',
        'EN_RUTA': 'fas fa-truck',
        'ENTREGADO': 'fas fa-check-circle',
        'CANCELADO': 'fas fa-times-circle'
      };

      if (envios.length === 0) {
        el.innerHTML = `
          <div class="empty-state">
            <i class="fas fa-shipping-fast"></i>
            <p>Aun no tienes envios</p>
            <button class="empty-action" onclick="App.navigate('nuevo-envio')">
              <i class="fas fa-plus"></i> Crear primer envio
            </button>
          </div>`;
      } else {
        el.innerHTML = envios.slice(0, 3).map((e, i) => `
          <div class="home-hist-card" onclick="App.rastrearDesdeHistorial('${e.folio}')" style="animation-delay:${i * 0.1}s">
            <div class="home-hist-icon ${e.estado}">
              <i class="${iconMap[e.estado] || 'fas fa-box'}"></i>
            </div>
            <div class="home-hist-info">
              <h4>${e.folio}</h4>
              <p>${e.destino_nombre || ''} - ${e.destino_cp || ''}</p>
            </div>
            <div class="home-hist-right">
              <span class="amount">$${(e.total || 0).toFixed(2)}</span>
              <span class="htime">${e.hora_registro || ''}</span>
            </div>
          </div>
        `).join('');
      }
    } catch (err) {}

    // Load negocios for home scroll
    try {
      const res = await fetch(`${API}/api/negocios`);
      const negocios = await res.json();
      const el = document.getElementById('home-negocios');

      const iconMap = {
        'FARMACIA': '💊', 'RESTAURANTE': '🍽️', 'ABARROTES': '🛒',
        'PANADERIA': '🍞', 'FLORERIA': '🌹', 'PAPELERIA': '📎',
        'VETERINARIA': '🐾', 'TIENDA': '🏪'
      };

      if (negocios.length === 0) {
        el.innerHTML = '<div class="home-hist-empty">Sin negocios disponibles</div>';
      } else {
        el.innerHTML = negocios.slice(0, 8).map((n, i) => `
          <div class="home-neg-card" onclick="App.verCatalogo(${n.id})" style="animation-delay:${i * 0.05}s">
            <span class="home-neg-icon">${iconMap[n.tipo] || '🏪'}</span>
            <span class="home-neg-name">${n.nombre}</span>
            <span class="home-neg-type">${n.tipo}</span>
            <span class="home-neg-rating"><i class="fas fa-star"></i> ${(n.calificacion_promedio || 5).toFixed(1)}</span>
          </div>
        `).join('');
      }
    } catch (err) {}
  },

  // ═══════════ ZONA DETECTION ═══════════

  async detectarZona(cp) {
    try {
      const res = await fetch(`${API}/api/detectar-zona/${cp}`);
      if (res.ok) {
        const zona = await res.json();
        document.getElementById('zona-detectada').style.display = 'flex';
        document.getElementById('zona-nombre-text').textContent =
          `Zona: ${zona.nombre} - ${zona.delegacion || ''}`;
        // Mark CP as valid
        const ig = document.getElementById('ig-cp');
        if (ig) { ig.classList.add('valid'); ig.classList.remove('invalid'); }
      } else {
        document.getElementById('zona-detectada').style.display = 'none';
        const ig = document.getElementById('ig-cp');
        if (ig) { ig.classList.add('invalid'); ig.classList.remove('valid'); }
        this.toast('Codigo postal fuera de cobertura', 'error');
      }
    } catch (err) {}
  },

  // ═══════════ FORM VALIDATION ═══════════

  initFormProgress() {
    const fp = document.querySelector('.form-progress');
    if (fp) fp.setAttribute('data-step', '1');
    this.validateFormFields();
  },

  validateSingleField(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const ig = el.closest('.input-group');
    if (!ig) return;
    const val = el.value.trim();

    if (id === 'envio-origen-tel' || id === 'envio-destino-tel') {
      if (val.length >= 10) {
        ig.classList.add('valid'); ig.classList.remove('invalid');
      } else if (val.length > 0) {
        ig.classList.add('invalid'); ig.classList.remove('valid');
      }
    } else if (id === 'envio-cp') {
      if (val.length === 5) {
        // handled by detectarZona
      } else if (val.length > 0) {
        ig.classList.add('invalid'); ig.classList.remove('valid');
      }
    } else {
      if (val.length >= 2) {
        ig.classList.add('valid'); ig.classList.remove('invalid');
      } else if (val.length > 0 && val.length < 2) {
        ig.classList.add('invalid'); ig.classList.remove('valid');
      }
    }
  },

  validateFormFields() {
    const fields = {
      step1: ['envio-origen-nombre', 'envio-origen-tel'],
      step2: ['envio-destino-nombre', 'envio-destino-tel', 'envio-cp', 'envio-direccion'],
      step3: ['envio-contenido', 'envio-peso']
    };

    let step1Done = true, step2Done = true;

    for (const id of fields.step1) {
      const el = document.getElementById(id);
      const val = el ? el.value.trim() : '';
      const ig = el ? el.closest('.input-group') : null;
      if (val.length >= 2) {
        if (ig && !ig.classList.contains('invalid')) ig.classList.add('valid');
      } else {
        step1Done = false;
        if (ig) ig.classList.remove('valid');
      }
    }

    for (const id of fields.step2) {
      const el = document.getElementById(id);
      const val = el ? el.value.trim() : '';
      if (val.length < 2) step2Done = false;
    }

    // Update progress
    const fp = document.querySelector('.form-progress');
    const step1El = document.getElementById('fp-step-1');
    const step2El = document.getElementById('fp-step-2');
    const step3El = document.getElementById('fp-step-3');

    if (fp) {
      if (step1Done && step2Done) {
        fp.setAttribute('data-step', '3');
        step1El.classList.add('completed'); step1El.classList.remove('active');
        step2El.classList.add('completed'); step2El.classList.remove('active');
        step3El.classList.add('active');
      } else if (step1Done) {
        fp.setAttribute('data-step', '2');
        step1El.classList.add('completed'); step1El.classList.remove('active');
        step2El.classList.add('active'); step2El.classList.remove('completed');
        step3El.classList.remove('active', 'completed');
      } else {
        fp.setAttribute('data-step', '1');
        step1El.classList.add('active'); step1El.classList.remove('completed');
        step2El.classList.remove('active', 'completed');
        step3El.classList.remove('active', 'completed');
      }
    }
  },

  // ═══════════ LIVE COST PREVIEW ═══════════

  updateLiveCost() {
    const cp = document.getElementById('envio-cp').value;
    const peso = parseFloat(document.getElementById('envio-peso').value) || 1;
    const preview = document.getElementById('live-cost-preview');
    const valueEl = document.getElementById('live-cost-value');

    if (cp && cp.length === 5 && peso > 0) {
      // Estimate based on base rate + weight
      const baseRate = 120;
      const weightRate = peso > 1 ? (peso - 1) * 25 : 0;
      const subtotal = baseRate + weightRate;
      const iva = subtotal * 0.16;
      const total = subtotal + iva;

      preview.style.display = 'flex';
      valueEl.textContent = '~$' + total.toFixed(0);
      valueEl.style.animation = 'none';
      // Force reflow
      void valueEl.offsetWidth;
      valueEl.style.animation = 'costPop 0.3s ease';
    } else {
      preview.style.display = 'none';
    }
  },

  // ═══════════ COTIZAR ═══════════

  async cotizar() {
    const cp = document.getElementById('envio-cp').value;
    const peso = document.getElementById('envio-peso').value;

    if (!cp || cp.length < 4) {
      this.toast('Ingresa un codigo postal valido', 'error');
      return;
    }

    const btn = document.getElementById('btn-cotizar');
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-inline"></span> Calculando...';
    btn.classList.add('btn-loading');

    try {
      const res = await fetch(`${API}/api/cotizar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cp: parseInt(cp), peso: parseFloat(peso) || 1 })
      });

      if (!res.ok) {
        const err = await res.json();
        this.toast(err.error || 'Error al cotizar', 'error');
        btn.innerHTML = origHtml;
        btn.classList.remove('btn-loading');
        return;
      }

      const data = await res.json();
      this.cotizacionData = data;

      document.getElementById('cot-zona').textContent = data.zona_nombre;
      document.getElementById('cot-repartidor').textContent = data.repartidor_nombre;
      document.getElementById('cot-tarifa').textContent = '$' + data.tarifa_base.toFixed(2);
      document.getElementById('cot-peso').textContent = '$' + data.cargo_peso.toFixed(2);
      document.getElementById('cot-subtotal').textContent = '$' + data.subtotal.toFixed(2);
      document.getElementById('cot-iva').textContent = '$' + data.iva.toFixed(2);
      document.getElementById('cot-total').textContent = '$' + data.total.toFixed(2);

      document.getElementById('cotizacion-result').style.display = 'block';
      document.getElementById('cotizacion-result').scrollIntoView({ behavior: 'smooth' });

      // Hide live preview since we have exact quote
      document.getElementById('live-cost-preview').style.display = 'none';

      this.toast('Cotizacion lista', 'success');
    } catch (err) {
      this.toast('Error de conexion', 'error');
    }

    btn.innerHTML = origHtml;
    btn.classList.remove('btn-loading');
  },

  // ═══════════ CREAR ENVIO ═══════════

  async crearEnvio() {
    if (!this.cotizacionData) {
      this.toast('Primero cotiza el envio', 'error');
      return;
    }

    const fields = {
      origen_nombre: document.getElementById('envio-origen-nombre').value.trim(),
      origen_telefono: document.getElementById('envio-origen-tel').value.trim(),
      destino_nombre: document.getElementById('envio-destino-nombre').value.trim(),
      destino_telefono: document.getElementById('envio-destino-tel').value.trim(),
      destino_cp: parseInt(document.getElementById('envio-cp').value),
      destino_direccion: document.getElementById('envio-direccion').value.trim(),
      destino_referencias: document.getElementById('envio-referencias').value.trim(),
      contenido: document.getElementById('envio-contenido').value.trim(),
      peso: parseFloat(document.getElementById('envio-peso').value),
      tipo_paquete: document.getElementById('envio-tipo').value
    };

    // Validate
    for (const [key, val] of Object.entries(fields)) {
      if (key !== 'destino_referencias' && !val) {
        this.toast('Completa todos los campos', 'error');
        return;
      }
    }

    const payload = {
      ...fields,
      zona_id: this.cotizacionData.zona_id,
      repartidor_id: this.cotizacionData.repartidor_id,
      tarifa_base: this.cotizacionData.tarifa_base,
      cargo_peso: this.cotizacionData.cargo_peso,
      subtotal: this.cotizacionData.subtotal,
      iva: this.cotizacionData.iva,
      total: this.cotizacionData.total,
      usuario: this.usuario?.usuario || 'app'
    };

    const btn = document.getElementById('btn-crear-envio');
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-inline"></span> Creando envio...';
    btn.classList.add('btn-loading');

    try {
      const res = await fetch(`${API}/api/envios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (data.success) {
        // Launch confetti
        this.launchConfetti();

        this.showModal('Envio Creado', `
          <div style="text-align:center;padding:20px">
            <div style="font-size:56px;margin-bottom:16px">
              <span style="display:inline-block;animation:costPop 0.5s ease">🎉</span>
            </div>
            <h3 style="color:#001A4D;margin-bottom:4px;font-size:18px">Envio registrado exitosamente</h3>
            <p style="font-size:28px;font-weight:900;color:#001A4D;margin:12px 0;letter-spacing:1px">${data.folio}</p>
            <p style="color:#64748B;font-size:13px;line-height:1.5">
              Guarda tu folio para rastrear tu envio.<br>
              Se ha asignado un repartidor automaticamente.
            </p>
            <div style="display:flex;gap:8px;margin-top:20px">
              <button class="btn-secondary" onclick="App.closeModal();App.rastrearDesdeHistorial('${data.folio}')" style="flex:1;margin-top:0">
                <i class="fas fa-search-location"></i> Rastrear
              </button>
              <button class="btn-primary" onclick="App.closeModal();App.resetFormEnvio()" style="flex:1;margin-top:0">
                <i class="fas fa-check"></i> Aceptar
              </button>
            </div>
          </div>
        `);

        this.cotizacionData = null;
        this.loadStats();
      } else {
        this.toast('Error al crear envio', 'error');
      }
    } catch (err) {
      this.toast('Error de conexion', 'error');
    }

    btn.innerHTML = origHtml;
    btn.classList.remove('btn-loading');
  },

  resetFormEnvio() {
    document.getElementById('form-envio').reset();
    document.getElementById('cotizacion-result').style.display = 'none';
    document.getElementById('zona-detectada').style.display = 'none';
    document.getElementById('live-cost-preview').style.display = 'none';
    document.getElementById('envio-peso').value = '1';
    // Clear validation states
    document.querySelectorAll('#form-envio .input-group').forEach(ig => {
      ig.classList.remove('valid', 'invalid');
    });
    this.navigate('dashboard');
  },

  // ═══════════ RASTREAR (ENHANCED) ═══════════

  async rastrear() {
    const folio = document.getElementById('rastreo-folio').value.trim().toUpperCase();
    if (!folio) {
      this.toast('Ingresa un folio', 'error');
      return;
    }

    // Show loading
    const btn = document.querySelector('#screen-rastrear .btn-primary');
    if (btn) {
      btn.innerHTML = '<span class="spinner-inline"></span> Buscando...';
      btn.classList.add('btn-loading');
    }

    try {
      const res = await fetch(`${API}/api/rastrear/${folio}`);
      if (!res.ok) {
        this.toast('Envio no encontrado', 'error');
        document.getElementById('rastreo-result').style.display = 'none';
        if (btn) {
          btn.innerHTML = '<i class="fas fa-search"></i> Buscar';
          btn.classList.remove('btn-loading');
        }
        return;
      }

      const data = await res.json();
      const envio = data.envio;
      const historial = data.historial;
      this.currentTrackEnvio = envio;

      document.getElementById('track-folio').textContent = envio.folio;
      const statusEl = document.getElementById('track-status');
      statusEl.textContent = this.formatEstado(envio.estado);
      statusEl.className = `tracking-status status-${envio.estado}`;

      document.getElementById('track-origen').textContent = envio.origen_nombre || '-';
      document.getElementById('track-destino').textContent =
        `${envio.destino_nombre} - ${envio.destino_direccion || ''}`;
      document.getElementById('track-repartidor').textContent =
        envio.rep_nombre ? `${envio.rep_nombre} ${envio.rep_apellidos}` : 'Por asignar';
      document.getElementById('track-total').textContent =
        '$' + (envio.total || 0).toFixed(2);

      // Enhanced map with checkpoints
      this.updateMapInteractive(envio.estado);

      // ETA calculation
      const etaMap = { 'RECIBIDO': '~ 2 hrs', 'ASIGNADO': '~ 1.5 hrs', 'EN_RUTA': '~ 45 min', 'EN_CDMX': '~ 15 min', 'ENTREGADO': 'Entregado' };
      document.getElementById('map-eta').textContent = etaMap[envio.estado] || '~ 1 hr';

      // Timeline with all possible states
      const timelineEl = document.getElementById('tracking-timeline');
      timelineEl.innerHTML = '';

      const allStates = ['RECIBIDO', 'ASIGNADO', 'EN_RUTA', 'ENTREGADO'];
      const iconMap = {
        'RECIBIDO': 'fas fa-inbox',
        'ASIGNADO': 'fas fa-user-check',
        'EN_RUTA': 'fas fa-motorcycle',
        'EN_CDMX': 'fas fa-city',
        'ENTREGADO': 'fas fa-check-double',
        'CANCELADO': 'fas fa-times'
      };

      // Show actual historial entries
      historial.forEach((h, i) => {
        timelineEl.innerHTML += `
          <div class="timeline-item" style="animation:fadeSlideUp 0.3s ease-out ${i * 0.1}s both">
            <div class="timeline-dot">
              <i class="${iconMap[h.estado_nuevo] || 'fas fa-circle'}"></i>
            </div>
            <div class="timeline-content">
              <strong>${this.formatEstado(h.estado_nuevo)}</strong>
              <p>${h.notas || 'Estado actualizado'}</p>
              <small><i class="fas fa-clock"></i> ${h.fecha} ${h.hora}</small>
            </div>
          </div>
        `;
      });

      // Show pending states grayed out
      const currentIdx = allStates.indexOf(envio.estado);
      if (currentIdx >= 0 && currentIdx < allStates.length - 1) {
        for (let i = currentIdx + 1; i < allStates.length; i++) {
          timelineEl.innerHTML += `
            <div class="timeline-item" style="opacity:0.35">
              <div class="timeline-dot" style="background:var(--gray-300)">
                <i class="${iconMap[allStates[i]] || 'fas fa-circle'}" style="color:var(--gray-400)"></i>
              </div>
              <div class="timeline-content">
                <strong style="color:var(--gray-400)">${this.formatEstado(allStates[i])}</strong>
                <p style="color:var(--gray-300)">Pendiente</p>
              </div>
            </div>
          `;
        }
      }

      document.getElementById('rastreo-result').style.display = 'block';
      this.toast('Envio encontrado', 'success');

    } catch (err) {
      this.toast('Error de conexion', 'error');
    }

    if (btn) {
      btn.innerHTML = '<i class="fas fa-search"></i> Buscar';
      btn.classList.remove('btn-loading');
    }
  },

  updateMapInteractive(estado) {
    const progressMap = {
      'RECIBIDO': 5,
      'ASIGNADO': 25,
      'EN_RUTA': 55,
      'EN_CDMX': 80,
      'ENTREGADO': 100
    };
    const progress = progressMap[estado] || 10;

    // Road progress bar
    const roadProgress = document.getElementById('map-road-progress');
    if (roadProgress) {
      const maxWidth = 100 - 15; // account for padding
      roadProgress.style.width = (progress * maxWidth / 100) + '%';
    }

    // Checkpoints
    const checkpoints = ['chk-recibido', 'chk-ruta', 'chk-cdmx', 'chk-entregado'];
    const stateOrder = ['RECIBIDO', 'EN_RUTA', 'EN_CDMX', 'ENTREGADO'];
    const currentIdx = stateOrder.indexOf(estado);

    checkpoints.forEach((id, i) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.classList.remove('active', 'completed');
      if (i < currentIdx) el.classList.add('completed');
      else if (i === currentIdx) el.classList.add('active');
    });

    // Animated truck on route line
    const mapLine = document.querySelector('.map-line');
    const mapTruck = document.getElementById('map-truck');
    if (mapLine) mapLine.style.setProperty('--progress', progress + '%');
    if (mapTruck) mapTruck.style.left = progress + '%';

    // Animate truck bouncing
    if (this.mapAnimInterval) clearInterval(this.mapAnimInterval);
    if (estado !== 'ENTREGADO') {
      let bounce = 0;
      this.mapAnimInterval = setInterval(() => {
        bounce = bounce === 0 ? -3 : 0;
        if (mapTruck) mapTruck.style.transform = `translate(-50%,-50%) translateY(${bounce}px)`;
      }, 500);
    }
  },

  // ═══════════ TRACK ACTIONS ═══════════

  trackAction(action) {
    const envio = this.currentTrackEnvio;
    if (!envio) return;

    if (action === 'call') {
      const tel = envio.rep_telefono || envio.destino_telefono || '';
      if (tel) {
        window.open(`tel:${tel}`, '_self');
      } else {
        this.toast('No hay telefono disponible', 'info');
      }
    } else if (action === 'chat') {
      const tel = envio.rep_telefono || envio.destino_telefono || '';
      if (tel) {
        const msg = encodeURIComponent(`Hola, consulto sobre el envio ${envio.folio} de Cargo-GO`);
        window.open(`https://wa.me/52${tel.replace(/\D/g,'')}?text=${msg}`, '_blank');
      } else {
        this.toast('No hay telefono para WhatsApp', 'info');
      }
    } else if (action === 'share') {
      const shareText = `Mi envio Cargo-GO: ${envio.folio}\nEstado: ${this.formatEstado(envio.estado)}\nDestino: ${envio.destino_nombre}`;
      if (navigator.share) {
        navigator.share({ title: 'Rastreo Cargo-GO', text: shareText }).catch(() => {});
      } else {
        navigator.clipboard.writeText(shareText).then(() => {
          this.toast('Copiado al portapapeles', 'success');
        }).catch(() => {
          this.toast('No se pudo compartir', 'error');
        });
      }
    }
  },

  // ═══════════ MARKETPLACE ═══════════

  async loadNegocios() {
    const grid = document.getElementById('negocios-grid');
    grid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

    try {
      const res = await fetch(`${API}/api/negocios`);
      this.negocios = await res.json();
      this.renderNegocios(this.negocios);
    } catch (err) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1">
          <i class="fas fa-wifi"></i>
          <p>Error al cargar negocios</p>
          <button class="empty-action" onclick="App.loadNegocios()">
            <i class="fas fa-redo"></i> Reintentar
          </button>
        </div>`;
    }
  },

  renderNegocios(negocios) {
    const grid = document.getElementById('negocios-grid');

    if (negocios.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column:1/-1">
          <i class="fas fa-store-slash"></i>
          <p>No hay negocios en esta categoria</p>
        </div>`;
      return;
    }

    const iconMap = {
      'FARMACIA': 'fas fa-pills',
      'RESTAURANTE': 'fas fa-utensils',
      'ABARROTES': 'fas fa-shopping-basket',
      'PANADERIA': 'fas fa-bread-slice',
      'FLORERIA': 'fas fa-seedling',
      'PAPELERIA': 'fas fa-pencil-ruler',
      'VETERINARIA': 'fas fa-paw',
      'TIENDA': 'fas fa-store'
    };

    grid.innerHTML = negocios.map((n, i) => `
      <div class="negocio-card" onclick="App.verCatalogo(${n.id})" style="animation-delay:${i * 0.05}s">
        <div class="negocio-card-banner">
          <span class="negocio-card-icon"><i class="${iconMap[n.tipo] || 'fas fa-store'}"></i></span>
          ${n.destacado ? '<span class="negocio-card-badge">DESTACADO</span>' : ''}
        </div>
        <div class="negocio-card-body">
          <h4>${n.nombre}</h4>
          <p>${n.descripcion || n.tipo}</p>
          <div class="negocio-card-meta">
            <span class="rating"><i class="fas fa-star"></i> ${(n.calificacion_promedio || 5).toFixed(1)}</span>
            <span class="delivery"><i class="fas fa-truck"></i> $${n.costo_envio || 0}</span>
          </div>
        </div>
      </div>
    `).join('');
  },

  filtrarNegocios(tipo, btn) {
    document.querySelectorAll('#market-filters .chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');

    if (tipo === 'TODOS') {
      this.renderNegocios(this.negocios);
    } else {
      this.renderNegocios(this.negocios.filter(n => n.tipo === tipo));
    }
  },

  // ═══════════ CATALOGO ═══════════

  async verCatalogo(negocioId) {
    this.navigate('catalogo');

    const iconMap = {
      'FARMACIA': '<i class="fas fa-pills"></i>',
      'RESTAURANTE': '<i class="fas fa-utensils"></i>',
      'ABARROTES': '<i class="fas fa-shopping-basket"></i>',
      'PANADERIA': '<i class="fas fa-bread-slice"></i>',
      'FLORERIA': '<i class="fas fa-seedling"></i>',
      'PAPELERIA': '<i class="fas fa-pencil-ruler"></i>',
      'VETERINARIA': '<i class="fas fa-paw"></i>',
      'TIENDA': '<i class="fas fa-store"></i>'
    };

    const prodIconMap = {
      'Medicamentos': '💊', 'Vitaminas': '💉', 'Higiene': '🧴',
      'Tacos': '🌮', 'Antojitos': '🫔', 'Bebidas': '🥤',
      'Lacteos': '🥛', 'Panaderia': '🍞', 'Pan dulce': '🧁',
      'Pan salado': '🥖', 'Ramos': '🌹', 'Arreglos': '💐',
      'Copias': '📄', 'Impresiones': '🖨️', 'Papeleria': '📓'
    };

    // Show loading
    document.getElementById('productos-list').innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

    try {
      const [negRes, prodRes] = await Promise.all([
        fetch(`${API}/api/negocios/${negocioId}`),
        fetch(`${API}/api/negocios/${negocioId}/productos`)
      ]);

      const negocio = await negRes.json();
      const productos = await prodRes.json();

      document.getElementById('catalogo-icon').innerHTML =
        iconMap[negocio.tipo] || '<i class="fas fa-store"></i>';
      document.getElementById('catalogo-nombre').textContent = negocio.nombre;
      document.getElementById('catalogo-desc').textContent = negocio.descripcion || '';
      document.getElementById('catalogo-horario').textContent =
        `${negocio.horario_apertura} - ${negocio.horario_cierre}`;
      document.getElementById('catalogo-rating').textContent =
        (negocio.calificacion_promedio || 5).toFixed(1);
      document.getElementById('catalogo-envio').textContent = negocio.costo_envio || 0;

      const listEl = document.getElementById('productos-list');

      if (productos.length === 0) {
        listEl.innerHTML = `
          <div class="empty-state">
            <i class="fas fa-box-open"></i>
            <p>Este negocio aun no tiene productos</p>
          </div>`;
        return;
      }

      listEl.innerHTML = productos.map((p, i) => `
        <div class="producto-card" style="animation-delay:${i * 0.05}s">
          <div class="producto-img">
            ${prodIconMap[p.categoria] || '📦'}
          </div>
          <div class="producto-info">
            <h4>${p.nombre}</h4>
            <p>${p.descripcion || p.categoria || ''}</p>
          </div>
          <div class="producto-price">
            ${p.precio_oferta ? `
              <span class="price-old">$${p.precio.toFixed(2)}</span>
              <span class="price price-offer">$${p.precio_oferta.toFixed(2)}</span>
            ` : `
              <span class="price">$${p.precio.toFixed(2)}</span>
            `}
          </div>
        </div>
      `).join('');
    } catch (err) {
      this.toast('Error al cargar catalogo', 'error');
      document.getElementById('productos-list').innerHTML = `
        <div class="empty-state">
          <i class="fas fa-exclamation-triangle"></i>
          <p>Error al cargar productos</p>
          <button class="empty-action" onclick="App.verCatalogo(${negocioId})">
            <i class="fas fa-redo"></i> Reintentar
          </button>
        </div>`;
    }
  },

  // ═══════════ REGISTRO NEGOCIO ═══════════

  async registrarNegocio() {
    const payload = {
      nombre: document.getElementById('reg-nombre').value.trim(),
      descripcion: document.getElementById('reg-descripcion').value.trim(),
      tipo: document.getElementById('reg-tipo').value,
      propietario_nombre: document.getElementById('reg-propietario').value.trim(),
      propietario_telefono: document.getElementById('reg-telefono').value.trim(),
      propietario_email: document.getElementById('reg-email').value.trim(),
      direccion: document.getElementById('reg-direccion').value.trim(),
      cp: document.getElementById('reg-cp').value.trim(),
      ciudad: document.getElementById('reg-ciudad').value.trim(),
      horario_apertura: document.getElementById('reg-apertura').value,
      horario_cierre: document.getElementById('reg-cierre').value
    };

    if (!payload.nombre || !payload.tipo || !payload.propietario_nombre || !payload.propietario_telefono || !payload.direccion) {
      this.toast('Completa los campos obligatorios', 'error');
      return;
    }

    const btn = document.querySelector('#form-registro-negocio .btn-primary');
    const origHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-inline"></span> Registrando...';
    btn.classList.add('btn-loading');

    try {
      const res = await fetch(`${API}/api/negocios/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (data.success) {
        this.launchConfetti();

        this.showModal('Registro Exitoso', `
          <div style="text-align:center;padding:20px">
            <div style="font-size:56px;margin-bottom:16px">🏪</div>
            <h3 style="color:#001A4D;margin-bottom:4px;font-size:18px">Negocio registrado</h3>
            <p style="font-size:24px;font-weight:900;color:#001A4D;margin:12px 0;letter-spacing:1px">${data.codigo}</p>
            <p style="color:#64748B;font-size:13px;line-height:1.5">${data.mensaje}</p>
            <button class="btn-primary" onclick="App.closeModal();App.navigate('marketplace')" style="margin-top:20px">
              <i class="fas fa-check"></i> Ver Marketplace
            </button>
          </div>
        `);

        document.getElementById('form-registro-negocio').reset();
      } else {
        this.toast('Error al registrar', 'error');
      }
    } catch (err) {
      this.toast('Error de conexion', 'error');
    }

    btn.innerHTML = origHtml;
    btn.classList.remove('btn-loading');
  },

  // ═══════════ HISTORIAL ═══════════

  async loadHistorial() {
    const list = document.getElementById('historial-list');
    list.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

    try {
      const res = await fetch(`${API}/api/historial`);
      this.historialData = await res.json();
      this.renderHistorial(this.historialData);
    } catch (err) {
      list.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-wifi"></i>
          <p>Error al cargar historial</p>
          <button class="empty-action" onclick="App.loadHistorial()">
            <i class="fas fa-redo"></i> Reintentar
          </button>
        </div>`;
    }
  },

  renderHistorial(envios) {
    const list = document.getElementById('historial-list');

    if (envios.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No hay envios en esta categoria</p>
          <button class="empty-action" onclick="App.navigate('nuevo-envio')">
            <i class="fas fa-plus"></i> Crear envio
          </button>
        </div>`;
      return;
    }

    const iconMap = {
      'RECIBIDO': 'fas fa-inbox',
      'ASIGNADO': 'fas fa-user-check',
      'EN_RUTA': 'fas fa-truck',
      'ENTREGADO': 'fas fa-check-circle',
      'CANCELADO': 'fas fa-times-circle'
    };

    list.innerHTML = envios.map((e, i) => `
      <div class="historial-item" onclick="App.rastrearDesdeHistorial('${e.folio}')" style="animation-delay:${i * 0.03}s">
        <div class="historial-icon ${e.estado}">
          <i class="${iconMap[e.estado] || 'fas fa-box'}"></i>
        </div>
        <div class="historial-info">
          <h4>${e.folio}</h4>
          <p>${e.destino_nombre || ''} - ${e.zona_nombre || e.destino_cp || ''}</p>
        </div>
        <div class="historial-right">
          <span class="amount">$${(e.total || 0).toFixed(2)}</span>
          <span class="date">${e.fecha_registro || ''}</span>
        </div>
      </div>
    `).join('');
  },

  filtrarHistorial(estado, btn) {
    document.querySelectorAll('#screen-historial .chip').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');

    if (estado === 'TODOS') {
      this.renderHistorial(this.historialData);
    } else {
      this.renderHistorial(this.historialData.filter(e => e.estado === estado));
    }
  },

  rastrearDesdeHistorial(folio) {
    this.navigate('rastrear');
    document.getElementById('rastreo-folio').value = folio;
    this.rastrear();
  },

  // ═══════════ CONFETTI ═══════════

  launchConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    canvas.style.display = 'block';
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const colors = ['#FFD700', '#00D4FF', '#FF8C00', '#10B981', '#D32F2F', '#001A4D', '#FFA500'];

    for (let i = 0; i < 120; i++) {
      particles.push({
        x: canvas.width / 2 + (Math.random() - 0.5) * 200,
        y: canvas.height / 2,
        vx: (Math.random() - 0.5) * 16,
        vy: Math.random() * -18 - 4,
        size: Math.random() * 8 + 3,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 12,
        gravity: 0.35,
        life: 1,
        decay: 0.008 + Math.random() * 0.008
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      let alive = false;

      particles.forEach(p => {
        if (p.life <= 0) return;
        alive = true;
        p.x += p.vx;
        p.vy += p.gravity;
        p.y += p.vy;
        p.rotation += p.rotSpeed;
        p.life -= p.decay;
        p.vx *= 0.99;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rotation * Math.PI / 180);
        ctx.globalAlpha = Math.max(p.life, 0);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        ctx.restore();
      });

      if (alive) {
        requestAnimationFrame(animate);
      } else {
        canvas.style.display = 'none';
      }
    };

    requestAnimationFrame(animate);
  },

  // ═══════════ UTILS ═══════════

  formatEstado(estado) {
    const map = {
      'RECIBIDO': 'Recibido',
      'ASIGNADO': 'Asignado',
      'EN_RUTA': 'En Ruta',
      'EN_CDMX': 'En CDMX',
      'ENTREGADO': 'Entregado',
      'CANCELADO': 'Cancelado'
    };
    return map[estado] || estado;
  },

  toast(msg, type = 'info') {
    const el = document.getElementById('toast');
    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    el.innerHTML = `<span style="margin-right:6px">${icons[type] || ''}</span> ${msg}`;
    el.className = `toast toast-${type} show`;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => el.classList.remove('show'), 3000);
  },

  showModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal').style.display = 'flex';
  },

  closeModal() {
    document.getElementById('modal').style.display = 'none';
  }
};

// ═══════════ BLUE DASHBOARD ═══════════

// Cargar envío activo en card azul
App.cargarEnvioActivoBlue = async function() {
    try {
        const response = await fetch(`${API}/api/historial`);
        const envios = await response.json();

        const activo = envios.find(e => e.estado === 'EN_RUTA' || e.estado === 'ASIGNADO');

        const container = document.getElementById('active-shipment-blue');
        if (!container) return;

        if (activo) {
            const progreso = Math.floor(Math.random() * 30) + 60;
            container.innerHTML = `
                <div class="active-shipment-box">
                    <div class="shipment-progress">
                        <span class="progress-icon">🚚</span>
                        <div class="progress-bar-wrapper">
                            <div class="progress-bar-fill" style="width: ${progreso}%">${progreso}%</div>
                        </div>
                    </div>
                    <div class="shipment-info">
                        <div class="shipment-folio">${activo.folio} → Pachuca</div>
                    </div>
                    <div class="shipment-route">
                        <span class="route-icon">👤</span>
                        <span>En ruta ahora</span>
                        <div style="flex: 1;"></div>
                        <span class="shipment-eta">15:30</span>
                        <a href="#" onclick="App.navigate('rastrear'); return false;" style="color: white; font-weight: 600; margin-left: 12px;">Ver todo →</a>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="active-shipment-box">
                    <p style="color: white; text-align: center; margin: 0;">No hay envíos activos</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
    }
};

// Inicializar dashboard azul
App.initBlueHome = function() {
    App.cargarEnvioActivoBlue();
};

// Hook navegación para dashboard azul
const _originalNavigate = App.navigate.bind(App);
App.navigate = function(screenName) {
    // Hide/show blue bottom nav vs regular bottom nav
    const blueNav = document.querySelector('.blue-bottom-nav');
    const regularNav = document.querySelector('.bottom-nav');

    _originalNavigate(screenName);

    if (blueNav) blueNav.style.display = (screenName === 'dashboard') ? 'flex' : 'none';
    if (regularNav) regularNav.style.display = (screenName === 'dashboard') ? 'none' : 'flex';

    if (screenName === 'dashboard') {
        setTimeout(() => App.initBlueHome(), 100);
    }
};

// Funciones quick actions
App.repetirUltimo = function() {
    alert('Repitiendo último envío...');
    App.navigate('nuevo-envio');
};

App.abrirSoporte = function() {
    alert('Abriendo chat de soporte 24/7...');
};

App.mostrarCupones = function() {
    alert('Cupones disponibles:\n• PROMO20: 20% OFF\n• FIRST50: $50 OFF');
};

App.compartirReferido = function() {
    const link = 'https://cargo-go.com/ref/CHULE123';
    if (navigator.share) {
        navigator.share({
            title: 'Cargo-GO',
            text: '¡Únete a Cargo-GO y gana $50!',
            url: link
        });
    } else {
        alert('Link de referido: ' + link);
    }
};

// ═══════════ START ═══════════
document.addEventListener('DOMContentLoaded', () => App.init());
