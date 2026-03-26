<template>
  <div class="accept-page">
    <div v-if="loading" class="loader">Verificando invitacion...</div>

    <div v-else-if="invitation" class="invite-card panel shadow-sm">
      <div class="icon">Invitation</div>
      <h2>Hola, {{ invitation.name || 'familiar' }}</h2>
      <p>Has sido invitado para supervisar a:</p>

      <div class="resident-box">
        <strong>{{ invitation.patientName }}</strong>
      </div>

      <p class="meta">Completa tu registro para activar el acceso como familiar.</p>

      <form v-if="invitation.state !== 'ACCEPTED'" class="register-form" @submit.prevent="completeRegistration">
        <label class="field">
          <span>Nombre</span>
          <input v-model="form.name" type="text" required />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="form.email" type="email" disabled />
        </label>
        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" minlength="6" required />
        </label>

        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

        <div class="actions">
          <button class="btn btn-primary" type="submit" :disabled="submitting">
            {{ submitting ? 'Registrando...' : 'Aceptar y registrarme' }}
          </button>
        </div>
      </form>

      <p v-else class="accepted-message">Esta invitacion ya fue aceptada.</p>
    </div>

    <div v-else class="error-card panel">
      <p>Esta invitacion no es valida o ya ha expirado.</p>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const token = route.query.token
const invitation = ref(null)
const loading = ref(true)
const submitting = ref(false)
const errorMessage = ref('')
const form = ref({ name: '', email: '', password: '' })

onMounted(async () => {
  try {
    invitation.value = await $fetch(`http://localhost:5000/invites/verify?token=${token}`)
    form.value.name = invitation.value?.name || ''
    form.value.email = invitation.value?.email || ''
  } catch (error) {
    console.error('Invalid invite token', error)
  } finally {
    loading.value = false
  }
})

const completeRegistration = async () => {
  errorMessage.value = ''
  submitting.value = true
  try {
    invitation.value = await $fetch('http://localhost:5000/invites/register', {
      method: 'POST',
      body: {
        token,
        name: form.value.name,
        password: form.value.password
      }
    })
    alert('Registro completado correctamente.')
    router.push('/login')
  } catch (error) {
    errorMessage.value = 'No se pudo completar el registro o la invitacion ya fue usada.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.accept-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: var(--bg-main); }
.invite-card, .error-card { text-align: center; max-width: 420px; padding: 40px; }
.resident-box { margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd; }
.icon { font-size: 1rem; margin-bottom: 1rem; font-weight: 700; color: #3b82f6; text-transform: uppercase; }
.accepted-message { color: #10b981; font-weight: 600; }
.register-form { display: grid; gap: 14px; text-align: left; margin-top: 20px; }
.field { display: grid; gap: 6px; }
.field input { width: 100%; box-sizing: border-box; padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-main); color: var(--text-main); }
.field input:disabled { opacity: 0.7; }
.error-message { color: #ef4444; font-size: 0.9rem; text-align: center; }
</style>
