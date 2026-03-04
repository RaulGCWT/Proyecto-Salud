<template>
    <div class="card card-presence">
          <span class="card-label">{{ title }}</span>
          <div class="card-value presence-color">
            {{mainText}}
          </div>
          <div class="card-indicator status-ok">
            {{ description}}
          </div>
        </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
// --- REACTIVE STATE (English variables) ---
const isOccupied = ref(true);


const props=defineProps({
  title:String,
  mainText:String,
  description:String,
  type: 'hr' | 'hrv' 
})
</script>