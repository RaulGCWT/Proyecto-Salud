<template>
  <div class="login-page" :class="{ 'dark-mode': isDarkMode }">
    <main class="login-stage">
      <section class="login-shell">
        <aside class="login-hero">
          <div class="brand-showcase">
            <img class="brand-showcase__logo" src="../images/logo.png" alt="Welltech Logo">
            <span class="brand-showcase__subtitle">IoT Health</span>
          </div>
        </aside>

        <section class="login-panel">
          <div class="panel-head">
            <div>
              <p class="panel-eyebrow">LOGIN</p>
              <h2>Welcome back</h2>
              <p class="panel-subtitle">Please authenticate to access the clinical workspace.</p>
            </div>
          </div>

          <div v-if="errorMessage" class="error-banner" role="alert">
            <span class="material-symbols-outlined" aria-hidden="true">error</span>
            <span>{{ errorMessage }}</span>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <label class="field">
              <span>Email</span>
              <div class="field-shell">
                <span class="material-symbols-outlined field-icon" aria-hidden="true">mail</span>
                <input
                  v-model.trim="email"
                  :disabled="isLoading"
                  type="email"
                  name="email"
                  autocomplete="email"
                  placeholder="example@gmail.com"
                  required
                >
              </div>
            </label>

            <label class="field">
              <div class="field-row">
                <span>Password</span>
                <a href="#" class="field-link" @click.prevent>Forgot?</a>
              </div>
              <div class="field-shell">
                <span class="material-symbols-outlined field-icon" aria-hidden="true">lock</span>
                <input
                  v-model="password"
                  :disabled="isLoading"
                  :type="showPassword ? 'text' : 'password'"
                  name="password"
                  autocomplete="current-password"
                  placeholder="••••••••"
                  required
                >
                <button
                  class="field-action"
                  type="button"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  @click="showPassword = !showPassword"
                >
                  <span class="material-symbols-outlined" aria-hidden="true">
                    {{ showPassword ? 'visibility_off' : 'visibility' }}
                  </span>
                </button>
              </div>
            </label>

            <label class="remember-row">
              <input v-model="keepLoggedIn" type="checkbox">
              <span>Keep me logged in for 12 hours</span>
            </label>

            <button class="submit-button" type="submit" :disabled="isLoading">
              <span v-if="isLoading" class="button-spinner" aria-hidden="true"></span>
              <span>{{ isLoading ? 'Signing in...' : 'Access Welltech' }}</span>
              <span class="material-symbols-outlined submit-icon" aria-hidden="true">arrow_forward</span>
            </button>
          </form>

          <footer class="panel-footer">
            <p>
              Don't have an account?
              <a href="#" @click.prevent>Register here</a>
            </p>
          </footer>
        </section>
      </section>
    </main>

  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({
  layout: false
})

useHead({
  title: 'Login | Clinical Sentinel'
})

const auth = useAuthStore()
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const keepLoggedIn = ref(true)
const showPassword = ref(false)
const isDarkMode = ref(false)

const loginErrorMessage = computed(() => {
  return 'Invalid credentials. Please try again.'
})

const handleLogin = async () => {
  if (isLoading.value) return

  isLoading.value = true
  errorMessage.value = ''

  try {
    await auth.login(email.value, password.value)
    await navigateTo('/')
  } catch (error) {
    console.error('Login error:', error)
    errorMessage.value = loginErrorMessage.value
  } finally {
    isLoading.value = false
  }
}

const syncThemeFromStorage = () => {
  if (typeof window === 'undefined') return

  isDarkMode.value = localStorage.getItem('theme') === 'dark'
}

onMounted(() => {
  syncThemeFromStorage()
  window.addEventListener('storage', syncThemeFromStorage)
})

onBeforeUnmount(() => {
  if (typeof window === 'undefined') return

  window.removeEventListener('storage', syncThemeFromStorage)
})

watch(keepLoggedIn, (value) => {
  if (typeof window === 'undefined') return

  localStorage.setItem('login.remember', value ? 'true' : 'false')
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at top left, rgba(37, 89, 189, 0.08), transparent 28%),
    radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.08), transparent 22%),
    var(--surface-page, #f7f9fb);
  color: var(--text-main, #1e293b);
}

.login-page.dark-mode {
  --surface-page: #0b1220;
}

.login-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px 24px 24px;
}

.login-shell {
  width: min(1100px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(360px, 0.95fr);
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid var(--surface-border, rgba(148, 163, 184, 0.16));
  background: var(--surface-card, #ffffff);
  box-shadow: 0 28px 60px var(--surface-shadow, rgba(15, 23, 42, 0.08));
}

.login-hero {
  position: relative;
  min-height: 620px;
  padding: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top left, rgba(37, 89, 189, 0.16), transparent 34%),
    radial-gradient(circle at bottom right, rgba(16, 185, 129, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(241, 245, 249, 0.98), rgba(226, 232, 240, 0.96));
  overflow: hidden;
}

.login-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0));
  pointer-events: none;
}

.brand-showcase {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.brand-showcase__logo {
  width: min(360px, 82%);
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 20px 28px rgba(15, 23, 42, 0.18));
}

.brand-showcase__subtitle {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #3b82f6;
}

.login-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  background: var(--surface-card, #ffffff);
}

.panel-head h2 {
  margin: 0 0 6px;
  font-size: 1.9rem;
  line-height: 1.05;
  font-weight: 900;
  letter-spacing: -0.05em;
}

.panel-eyebrow {
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.68rem;
  font-weight: 900;
  color: #2559bd;
}

.panel-subtitle {
  margin: 0;
  color: var(--text-muted, #64748b);
  line-height: 1.6;
}

.error-banner {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-top: 22px;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid rgba(239, 68, 68, 0.18);
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  font-size: 0.86rem;
  font-weight: 700;
}

.login-form {
  display: grid;
  gap: 18px;
  margin-top: 22px;
}

.field {
  display: grid;
  gap: 8px;
}

.field > span,
.field-row > span {
  font-size: 0.68rem;
  font-weight: 900;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.field-link {
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #2559bd;
  text-decoration: none;
}

.field-shell {
  position: relative;
  display: flex;
  align-items: center;
}

.field-icon {
  position: absolute;
  left: 16px;
  color: var(--text-muted, #64748b);
  font-size: 1.05rem;
  pointer-events: none;
}

.field-shell input {
  width: 100%;
  padding: 14px 46px 14px 44px;
  border-radius: 18px;
  border: 1px solid var(--surface-border, rgba(148, 163, 184, 0.16));
  background: var(--surface-panel-strong, #f8fafc);
  color: var(--text-main, #1e293b);
  font-weight: 700;
  outline: none;
  box-sizing: border-box;
}

.field-shell input::placeholder {
  color: var(--text-muted, #64748b);
}

.field-shell input:focus {
  border-color: rgba(37, 89, 189, 0.34);
  box-shadow: 0 0 0 4px rgba(37, 89, 189, 0.08);
}

.field-action {
  position: absolute;
  right: 10px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted, #64748b);
  cursor: pointer;
}

.remember-row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-muted, #64748b);
  font-size: 0.88rem;
}

.remember-row input {
  width: 16px;
  height: 16px;
  accent-color: #2559bd;
}

.submit-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  margin-top: 6px;
  padding: 14px 18px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, #00327d 0%, #0047ab 100%);
  color: #ffffff;
  font-size: 0.96rem;
  font-weight: 900;
  box-shadow: 0 16px 34px rgba(37, 89, 189, 0.2);
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.submit-button:disabled {
  opacity: 0.72;
  cursor: progress;
}

.submit-icon {
  font-size: 1rem;
}

.button-spinner {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.42);
  border-top-color: #ffffff;
  display: inline-block;
  animation: spin 0.8s linear infinite;
}

.panel-footer {
  margin-top: 18px;
}

.panel-footer p {
  margin: 0;
  color: var(--text-muted, #64748b);
  font-size: 0.88rem;
  line-height: 1.6;
}

.panel-footer a {
  color: #2559bd;
  font-weight: 800;
  text-decoration: none;
}

.login-page.dark-mode .login-shell {
  background: var(--surface-card);
  border-color: var(--surface-border);
}

.login-page.dark-mode .login-hero {
  background: var(--surface-hero);
}

.login-page.dark-mode .login-panel {
  background: var(--surface-card);
}

.login-page.dark-mode .panel-subtitle,
.login-page.dark-mode .panel-footer p,
.login-page.dark-mode .login-footer,
.login-page.dark-mode .footer-links a {
  color: var(--text-muted);
}

.login-page.dark-mode .topbar-button,
.login-page.dark-mode .field-shell input,
.login-page.dark-mode .submit-button,
.login-page.dark-mode .field-action {
  background: var(--surface-panel-strong);
  border-color: var(--surface-border);
  color: var(--text-main);
}

.login-page.dark-mode .panel-eyebrow,
.login-page.dark-mode .brand-subtitle,
.login-page.dark-mode .field-link,
.login-page.dark-mode .panel-footer a {
  color: #93c5fd;
}

.login-page.dark-mode .panel-head h2,
.login-page.dark-mode .brand-name {
  color: var(--text-main);
}

.login-page.dark-mode .topbar-button:hover {
  background: rgba(37, 99, 235, 0.16);
}

.login-page.dark-mode .field-shell input:focus {
  background: var(--surface-card);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-hero {
    min-height: auto;
    padding: 32px 24px;
  }

  .login-panel {
    padding: 32px 24px;
  }
}

@media (max-width: 640px) {
  .login-topbar {
    padding: 14px 18px;
  }

  .login-stage {
    padding: 18px;
  }

  .login-hero {
    padding: 28px 18px;
  }

  .login-panel {
    padding: 28px 18px;
  }
}
</style>
