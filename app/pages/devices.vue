<template>
  <div class="devices-page">
    <header class="main-header">
      <h1 class="page-title">Device Inventory</h1>
      <h3 class="subtitle">Management and connection status of smart mattresses</h3>
    </header>

    <section class="summary-grid">
      <div class="summary-card shadow-sm">
        <span class="icon">🛏️</span>
        <div class="info">
          <label>Total Devices</label>
          <div class="value">{{ beds.length }}</div>
        </div>
      </div>
      <div class="summary-card shadow-sm">
        <span class="icon text-success">●</span>
        <div class="info">
          <label>Connected</label>
          <div class="value">{{ beds.filter(b => b.isOnline).length }}</div>
        </div>
      </div>
      <div class="summary-card shadow-sm">
        <span class="icon text-danger">●</span>
        <div class="info">
          <label>Disconnected</label>
          <div class="value">{{ beds.filter(b => !b.isOnline).length }}</div>
        </div>
      </div>
    </section>

    <div class="filters-bar shadow-sm">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input v-model="filters.search" type="text" placeholder="Search by name or MAC..." />
      </div>
      <div class="select-group">
        <select v-model="filters.status">
          <option value="all">All Status</option>
          <option value="online">Connected</option>
          <option value="offline">Disconnected</option>
        </select>
        <select v-model="filters.type">
          <option value="all">All Types</option>
          <option value="Critical Care">Critical Care</option>
          <option value="Standard">Standard</option>
        </select>
        <select v-model="filters.presence">
          <option value="all">All Presence</option>
          <option value="Occupied">Occupied</option>
          <option value="Empty">Empty</option>
        </select>
        <button class="btn-reset" @click="resetFilters" title="Reset Filters">🔄</button>
      </div>
    </div>

    <div class="styled-container mb-5 shadow-sm">
      <div class="container-header">
        <h3 class="container-title">Inventory List ({{ filteredBeds.length }})</h3>
      </div>
      <div class="table-wrapper">
        <table class="devices-table">
          <thead>
            <tr>
              <th>MAC / UUID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Connection</th>
              <th>Presence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bed in filteredBeds" :key="bed.mac">
              <td class="mac-cell"><code class="mac-code-text">{{ bed.mac }}</code></td>
              <td class="device-name"><strong>{{ bed.name }}</strong></td>
              <td><span class="type-tag">{{ bed.type }}</span></td>
              <td>
                <span :class="['status-pill', bed.isOnline ? 'connected' : 'disconnected']">
                  {{ bed.isOnline ? 'Connected' : 'Disconnected' }}
                </span>
              </td>
              <td class="presence-cell">
                <span :class="['presence-tag', bed.presence === 'Occupied' ? 'occupied' : 'empty']">
                  {{ bed.presence }}
                </span>
              </td>
              <td><button class="btn-icon" @click="editDevice(bed)">⚙️</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <h3 class="section-title mb-3">Connection status per device</h3>
    <div class="device-status-grid">
      <div v-for="bed in beds" :key="'card-' + bed.mac" class="styled-container p-4 shadow-sm">
        <div class="card-status-header">
          <div class="dot-title">
            <span :class="['dot', bed.isOnline ? 'bg-success' : 'bg-danger']"></span>
            <span class="mac-title">{{ bed.mac }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="data-row">
            <span class="label">Connection Status</span>
            <span :class="['value-text', bed.isOnline ? 'text-success' : 'text-danger', 'status-pill-card']">
              {{ bed.isOnline ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
          <div class="data-row">
            <span class="label">Last connection event</span>
            <span class="value-text muted">{{ bed.isOnline ? 'connected' : 'disconnected' }} • {{ bed.lastEventDate }}</span>
          </div>
          <div class="data-row">
            <span class="label">Last heartbeat received</span>
            <span class="value-text muted">{{ bed.isOnline ? 'online' : 'offline' }} • {{ bed.lastEventDate }}</span>
          </div>
          <div class="data-row">
            <span class="label">Total events (Session)</span>
            <span class="value-text">{{ bed.eventCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isEditing" class="modal-overlay" @click.self="isEditing = false">
      <div class="edit-modal shadow-sm">
        <h3 class="modal-title">Edit Device</h3>
        <p class="modal-subtitle">Update information for {{ editingBed.mac }}</p>
        
        <div class="form-group">
          <label>Device Name</label>
          <input v-model="editForm.name" type="text" />
        </div>

        <div class="form-group">
          <label>Device Type</label>
          <select v-model="editForm.type">
            <option value="Critical Care">Critical Care</option>
            <option value="Standard">Standard</option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="btn-cancel" @click="isEditing = false">Cancel</button>
          <button class="btn-save" @click="saveChanges">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { io } from "socket.io-client";

const beds = ref([])
const filters = ref({ search: '', status: 'all', type: 'all', presence: 'all' })

// Lógica de edición
const isEditing = ref(false)
const editingBed = ref(null)
const editForm = ref({ name: '', type: '' })

// --- CARGAR DATOS DE LA BASE DE DATOS ---
const fetchInventory = async () => {
  try {
    const data = await $fetch('http://localhost:5000/devices')
    const dbDevices = data || []

    dbDevices.forEach(dbDev => {
      // Ignoramos mayúsculas para evitar fallos de cruce
      const dbMac = (dbDev.mac || dbDev.id || '').toLowerCase()
      const existing = beds.value.find(b => b.mac.toLowerCase() === dbMac)

      if (existing) {
        // Actualizamos nombre y tipo por si se editaron, mantenemos el resto de datos del socket intactos
        existing.name = dbDev.name || existing.name
        existing.type = dbDev.type || existing.type
      } else {
        // Cama registrada en DB pero que no ha enviado datos por Socket todavía (Offline)
        beds.value.push({
          mac: dbDev.mac || dbDev.id,
          name: dbDev.name || `Bed-${(dbDev.mac || dbDev.id).slice(-5)}`,
          type: dbDev.type || 'Standard',
          isOnline: false,
          presence: 'Empty',
          lastEventDate: 'Never',
          eventCount: '0/0'
        })
      }
    })
  } catch (err) {
    console.error("Error fetching inventory from DB:", err)
  }
}

// --- CONEXIÓN SOCKET.IO (TIEMPO REAL) ---
const socket = io("http://localhost:5000");

socket.on("sensor_update", (data) => {
  const incomingMac = (data.mac || '').toLowerCase();
  const existingBed = beds.value.find(b => b.mac.toLowerCase() === incomingMac);

  if (existingBed) {
    // Actualizar estado en tiempo real
    existingBed.isOnline = true;
    existingBed.presence = data.isOccupied ? 'Occupied' : 'Empty';
    existingBed.lastEventDate = new Date().toLocaleString();
    
    // Incrementar contador de eventos con seguridad
    let currentEvents = parseInt((existingBed.eventCount || '0/0').split('/')[0]) || 0;
    existingBed.eventCount = (currentEvents + 1) + "/" + (currentEvents + 1);
  } else {
    // Autodescubrimiento: si es nueva y el fetchInventory no la ha pillado aún
    beds.value.push({
      mac: data.mac,
      name: `Bed-${data.mac.slice(-5)}`,
      type: 'Standard',
      isOnline: true,
      presence: data.isOccupied ? 'Occupied' : 'Empty',
      lastEventDate: new Date().toLocaleString(),
      eventCount: '1/1'
    });
    // Forzamos sincronización con DB para obtener nombre real si existe
    fetchInventory();
  }
});

// --- LÓGICA DE EDICIÓN ---
const editDevice = (bed) => {
  editingBed.value = bed
  editForm.value = { name: bed.name, type: bed.type }
  isEditing.value = true
}

const saveChanges = async () => {
  if (editingBed.value) {
    try {
      // Guardar de forma persistente en la Base de Datos
      await $fetch('http://localhost:5000/devices', {
        method: 'POST',
        body: {
          mac: editingBed.value.mac,
          id: editingBed.value.mac, // Aseguramos enviar el id
          name: editForm.value.name,
          type: editForm.value.type
        }
      });
      
      // Actualizar visualmente
      editingBed.value.name = editForm.value.name
      editingBed.value.type = editForm.value.type
      isEditing.value = false
    } catch (err) {
      console.error("Error saving changes to DB:", err)
    }
  }
}

const filteredBeds = computed(() => {
  return beds.value.filter(bed => {
    const matchesSearch = bed.name.toLowerCase().includes(filters.value.search.toLowerCase()) || 
                          bed.mac.toLowerCase().includes(filters.value.search.toLowerCase());
    const matchesStatus = filters.value.status === 'all' || (filters.value.status === 'online' ? bed.isOnline : !bed.isOnline);
    const matchesType = filters.value.type === 'all' || bed.type === filters.value.type;
    const matchesPresence = filters.value.presence === 'all' || bed.presence === filters.value.presence;
    return matchesSearch && matchesStatus && matchesType && matchesPresence;
  });
})

const resetFilters = () => { filters.value = { search: '', status: 'all', type: 'all', presence: 'all' }; }

onMounted(() => {
  fetchInventory();
  // Refrescar cada 5 segundos para descubrir nuevas camas guardadas en la DB
  setInterval(fetchInventory, 5000);
})
</script>

<style scoped>
/* SE MANTIENEN TODOS TUS ESTILOS SIN CAMBIOS */
.devices-page { padding: 20px; }
.shadow-sm { box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important; }
.summary-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 35px; }
.summary-card { background: var(--bg-card); padding: 22px; border-radius: 12px; border: 1px solid var(--border-color); display: flex; align-items: center; gap: 18px; }
.summary-card .value { font-size: 1.6rem; font-weight: 700; }
.styled-container { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }
.container-header { padding: 16px 20px; border-bottom: 1px solid var(--border-color); background: rgba(255, 255, 255, 0.02); }
.devices-table { width: 100%; border-collapse: collapse; }
.devices-table th { padding: 14px 20px; text-align: left; font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); background: rgba(0, 0, 0, 0.1); }
.devices-table td { padding: 16px 20px; border-bottom: 1px solid var(--border-color); }
.device-status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 24px; }
.filters-bar { display: flex; justify-content: space-between; align-items: center; gap: 15px; background: var(--bg-card); padding: 12px 20px; border-radius: 10px; border: 1px solid var(--border-color); margin-bottom: 25px; }
.search-box { flex: 1; position: relative; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); opacity: 0.5; }
.search-box input { width: 100%; padding: 8px 12px 8px 35px; background: rgba(255, 255, 255, 0.9); border: 1px solid var(--border-color); border-radius: 6px; color: #000000; outline: none; }
.select-group { display: flex; gap: 8px; align-items: center; }
.select-group select { padding: 8px; background: rgba(255, 255, 255, 0.9); border: 1px solid var(--border-color); border-radius: 6px; color: #000000; }
.btn-reset { background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); padding: 5px 8px; border-radius: 6px; cursor: pointer; }
.mac-title { font-weight: bold; font-family: monospace; color: #60a5fa; font-size: 1.1rem; }
.data-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; margin-bottom: 18px; }
.status-pill { padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }
.status-pill.connected { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.status-pill.disconnected { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.presence-tag.occupied { color: #3b82f6; font-weight: 600; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.text-success { color: #10b981 !important; }
.text-danger { color: #ef4444 !important; }
.bg-success { background-color: #10b981; }
.bg-danger { background-color: #ef4444; }
.p-4 { padding: 1.5rem; }
.mb-5 { margin-bottom: 3rem; }
.mb-3 { margin-bottom: 1rem; }
.card-status-header { margin-bottom: 20px; }
.status-pill-card { padding: 4px 10px; border-radius: 6px; font-weight: bold; line-height: 1; }
.card-body .text-success.status-pill-card { background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); }
.card-body .text-danger.status-pill-card { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); }

/* ESTILOS DEL MODAL DE EDICIÓN */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.edit-modal { background: white; padding: 25px; border-radius: 12px; width: 400px; color: #333; }
.dark-mode .edit-modal { background: #1a202c; color: white; }
.modal-title { margin-bottom: 5px; font-size: 1.25rem; }
.modal-subtitle { font-size: 0.85rem; color: #666; margin-bottom: 20px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 0.8rem; font-weight: bold; margin-bottom: 5px; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; background: #fff; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; }
.btn-cancel { background: #eee; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; }
.btn-save { background: #60a5fa; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; }

/* Dark mode fixes */
.dark-mode .value, .dark-mode .device-name strong, .dark-mode .value-text, .dark-mode .container-title, .dark-mode .type-tag { color: #ffffff !important; }
.dark-mode .label, .dark-mode .summary-card label, .dark-mode .value-text.muted { color: #94a3b8 !important; }
.dark-mode .mac-code-text { color: #ffffff !important; }
.dark-mode .presence-tag.empty { color: #ffffff !important; }
</style>