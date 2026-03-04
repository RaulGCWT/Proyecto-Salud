<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">
          <h2>WELLTECH</h2>
          <span>IoT Health</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <a href="#" class="nav-item active">📊 Dashboard</a>
        <a href="#" class="nav-item">🛏️ Colchones</a>
        <a href="#" class="nav-item">⚠️ Alertas</a>
        <a href="#" class="nav-item">🕒 Historial</a>
      </nav>

      <div class="sidebar-footer">
        <p><strong>Admin_Health</strong></p>
        <button class="btn-logout">Cerrar Sesión</button>
      </div>
    </aside>

    <main class="content-area">
      <header class="main-header">
        <h1>Monitorización de Sensores</h1>
        <p>Estado actual de los colchones inteligentes</p>
      </header>

      <section class="sensor-grid">
        <div class="card card-heart">
          <span class="card-label">Ritmo Cardíaco</span>
          <div class="card-value">72 <small>BPM</small></div>
          <div class="card-indicator status-ok">Normal</div>
        </div>
        
        <div class="card card-resp">
          <span class="card-label">Resp. Rate</span>
          <div class="card-value">16 <small>RPM</small></div>
          <div class="card-indicator status-ok">Normal</div>
        </div>

        <div class="card card-presence">
          <span class="card-label">Estado</span>
          <div class="card-value">En Uso</div>
          <div class="card-indicator status-ok">Usuario en cama</div>
        </div>
      </section>

      <section class="table-container">
        <h3>Registro de Alertas (Últimas 24h)</h3>
        <table class="custom-table">
          <thead>
            <tr>
              <th>Hora</th>
              <th>Sensor</th>
              <th>Mensaje</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>12:30:15</td>
              <td>Frecuencia Cardíaca</td>
              <td>Pico detectado: 105 BPM</td>
              <td><span class="badge badge-error">Crítico</span></td>
            </tr>
            <tr>
              <td>09:12:04</td>
              <td>Movimiento</td>
              <td>Ausencia prolongada (1h)</td>
              <td><span class="badge badge-warn">Aviso</span></td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<style>
/* 1. RESET Y BASE */
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', 'Segoe UI', sans-serif;
  background-color: #f8fafc;
  color: #1e293b;
}

.dashboard-wrapper {
  display: flex;
}

/* 2. SIDEBAR (FIJO) */
.sidebar {
  width: 260px;
  background-color: #0f172a;
  color: white;
  height: 100vh;
  position: fixed; /* Mantiene el menú siempre visible */
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: #020617;
}

.logo-icon {
  background: #3b82f6;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-weight: bold;
}

.logo-text h2 { margin: 0; font-size: 1.1rem; }
.logo-text span { font-size: 0.7rem; color: #64748b; text-transform: uppercase; }

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: block;
  padding: 12px 24px;
  color: #94a3b8;
  text-decoration: none;
  transition: 0.2s;
}

.nav-item:hover, .nav-item.active {
  color: white;
  background-color: #1e293b;
}

.nav-item.active {
  border-left: 4px solid #3b82f6;
  background-color: #1e293b;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #1e293b;
  font-size: 0.85rem;
}

.btn-logout {
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  background: transparent;
  border: 1px solid #ef4444;
  color: #ef4444;
  border-radius: 6px;
  cursor: pointer;
}

/* 3. CONTENIDO PRINCIPAL (CON MARGEN) */
.content-area {
  flex: 1;
  margin-left:
}
</style>


