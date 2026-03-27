<template>
  <div class="invite-wrapper">
    <div class="invite-card">
      <div class="invite-header">
        <div class="logo-img">
          <img src="../images/logo.png" alt="Welltech Logo">
          <span class="brand-subtitle">IoT Health</span>
        </div>
        <p>Family invitation access</p>
      </div>

      <div v-if="loading" class="status-box">Verifying invitation...</div>

      <template v-else-if="invitation">
        <div class="resident-box">
          <span class="resident-label">Resident</span>
          <strong>{{ invitation.patientName }}</strong>
        </div>

        <p class="invite-copy">Complete your registration to activate family access.</p>

        <form v-if="invitation.state !== 'ACCEPTED'" class="register-form" @submit.prevent="completeRegistration">
          <div class="form-group">
            <label>Name</label>
            <input v-model="form.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" disabled />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input v-model="form.password" type="password" minlength="6" required />
          </div>

          <div v-if="errorMessage" class="error-alert">
            {{ errorMessage }}
          </div>

          <button class="btn-submit" type="submit" :disabled="submitting">
            {{ submitting ? 'Creating account...' : 'Accept Invitation' }}
          </button>
        </form>

        <div v-else class="success-box">
          This invitation has already been used.
        </div>
      </template>

      <div v-else class="error-alert">
        This invitation is not valid or has expired.
      </div>

      <div class="invite-footer">
        <p>Access available only for invited family members</p>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false
})

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
.invite-wrapper { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 1.5rem; background: #020617; font-family: 'Inter', sans-serif; }
.invite-card { background: #0f172a; padding: 40px; border-radius: 20px; width: 100%; max-width: 420px; border: 1px solid #1e293b; text-align: center; box-shadow: 0 18px 40px rgba(2, 6, 23, 0.45); }
.invite-header p { color: #94a3b8; font-size: 14px; margin-top: 5px; margin-bottom: 24px; }
.logo-img { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.logo-img img { max-width: 180px; height: auto; max-height: 60px; object-fit: contain; filter: brightness(1.18) contrast(1.05); }
.brand-subtitle { font-size: 0.75rem; color: #3b82f6; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.status-box, .resident-box, .success-box { border-radius: 12px; padding: 14px 16px; margin-bottom: 18px; }
.status-box { background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2); color: #bfdbfe; }
.resident-box { background: #020617; border: 1px solid #334155; text-align: left; }
.resident-label { display: block; color: #94a3b8; font-size: 12px; text-transform: uppercase; font-weight: 700; margin-bottom: 6px; }
.resident-box strong { color: #f8fafc; font-size: 1rem; }
.invite-copy { color: #cbd5e1; font-size: 14px; margin: 0 0 20px; }
.register-form { text-align: left; }
.form-group { text-align: left; margin-bottom: 20px; }
.form-group label { display: block; color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }
.form-group input { width: 100%; padding: 12px 16px; border-radius: 10px; border: 1px solid #334155; background: #020617; color: #f8fafc; outline: none; box-sizing: border-box; }
.form-group input:focus { border-color: #3b82f6; }
.form-group input:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-submit { width: 100%; padding: 14px; background: #3b82f6; color: white; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; transition: all 0.2s; }
.btn-submit:hover:not(:disabled) { background: #2563eb; transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.error-alert { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 20px; border: 1px solid rgba(239, 68, 68, 0.2); }
.success-box { background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.2); }
.invite-footer p { color: #64748b; font-size: 11px; margin-top: 30px; }
</style>
