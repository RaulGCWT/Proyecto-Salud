<template>
  <div>
    <ToastNotification v-model="activeToast" />

    <NuxtLayout v-if="!disableLayout" :name="layoutName">
      <NuxtPage />
    </NuxtLayout>

    <NuxtPage v-else />
  </div>
</template>

<script setup>
import { useHealthStore } from '~/stores/health'
import { useHealthSocket } from '~/composables/useHealthSocket'
const health = useHealthStore()
const { connect: connectHealthSocket } = useHealthSocket()
const activeToast = ref(null)
const telemetryRefreshInterval = ref(null)
const route = useRoute()
const disableLayout = computed(() => route.meta.layout === false)
const layoutName = computed(() => disableLayout.value ? undefined : route.meta.layout)

onMounted(async () => {
  await health.fetchDeviceInventory()
  await health.fetchLatestTelemetry()
  await health.fetchTelemetryHistoryForInventory(200)
  connectHealthSocket()
  telemetryRefreshInterval.value = window.setInterval(() => {
    health.fetchDeviceInventory()
    health.fetchLatestTelemetry()
  }, 5000)
})

onBeforeUnmount(() => {
  if (telemetryRefreshInterval.value) {
    window.clearInterval(telemetryRefreshInterval.value)
  }
})

// Vigilamos si llega una nueva alerta al Store
watch(() => health.lastToast, (newVal) => {
  if (newVal) {
    activeToast.value = newVal
    setTimeout(() => {
      if (activeToast.value?.id === newVal.id) activeToast.value = null
    }, 4000)
  }
})
</script>
