<template>
  <div v-if="error" class="error-boundary card p-6 mx-auto max-w-lg mt-8">
    <h2 class="text-xl font-semibold text-red-600 dark:text-red-400 mb-4">Something went wrong</h2>
    <div class="bg-red-50 dark:bg-red-900/30 rounded-lg p-4 mb-4">
      <p class="text-sm text-red-700 dark:text-red-300 font-mono">{{ error.message || error }}</p>
      <pre v-if="error.stack && isDevelopment" class="mt-2 text-xs text-red-600 dark:text-red-400 overflow-auto max-h-40">{{ error.stack }}</pre>
    </div>
    <div class="flex justify-between">
      <button 
        @click="reset" 
        class="btn-primary"
      >
        Try again
      </button>
      <button 
        @click="reportError" 
        class="btn-secondary"
      >
        Report issue
      </button>
    </div>
  </div>
  <slot v-else></slot>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import { useLogger } from '@/composables/useLogger'

const props = defineProps({
  component: {
    type: String,
    default: 'Unknown component'
  }
})

const error = ref(null)
const logger = useLogger()
const isDevelopment = process.env.NODE_ENV === 'development'

const reset = () => {
  error.value = null
}

const reportError = async () => {
  try {
    await logger.error({
      component: props.component,
      error: error.value instanceof Error ? error.value : new Error(error.value),
      timestamp: new Date().toISOString()
    })
    alert('Error reported successfully')
  } catch (e) {
    console.error('Failed to report error:', e)
    alert('Failed to report error. Please try again later.')
  }
}

onErrorCaptured((e) => {
  error.value = e
  return false // Prevent error from propagating
})
</script> 