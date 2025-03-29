<template>
  <div v-if="message" :class="baseClasses">
    <div class="flex">
      <div class="flex-shrink-0">
        <component :is="icon" :class="iconClasses" />
      </div>
      <div class="ml-3">
        <h3 :class="titleClasses">{{ title || defaultTitle }}</h3>
        <div :class="messageClasses"><p>{{ message }}</p></div>
        <div v-if="retry" class="mt-4">
          <button @click="$emit('retry')" :class="buttonClasses">Try again</button>
        </div>
      </div>
      <div class="ml-auto pl-3">
        <button @click="$emit('close')" :class="closeButtonClasses">
          <span class="sr-only">Dismiss</span>
          <CloseIcon />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Icons as components for better reusability
const ErrorIcon = {
  template: `
    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  `
}

const WarningIcon = {
  template: `
    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  `
}

const CloseIcon = {
  template: `
    <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" clip-rule="evenodd"
        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" />
    </svg>
  `
}

const props = defineProps({
  type: {
    type: String,
    default: 'error',
    validator: (value) => ['error', 'warning'].includes(value)
  },
  title: String,
  message: {
    type: String,
    required: true
  },
  retry: Boolean
})

const isError = computed(() => props.type === 'error')

const baseClasses = computed(() => [
  'rounded-md p-4',
  isError.value ? 'bg-red-50 dark:bg-red-900' : 'bg-yellow-50 dark:bg-yellow-900'
])

const iconClasses = computed(() => [
  isError.value ? 'text-red-400 dark:text-red-300' : 'text-yellow-400 dark:text-yellow-300'
])

const titleClasses = computed(() => [
  'text-sm font-medium',
  isError.value ? 'text-red-800 dark:text-red-200' : 'text-yellow-800 dark:text-yellow-200'
])

const messageClasses = computed(() => [
  'mt-2 text-sm',
  isError.value ? 'text-red-700 dark:text-red-300' : 'text-yellow-700 dark:text-yellow-300'
])

const buttonClasses = computed(() => [
  'inline-flex items-center px-3 py-2 border rounded-md text-sm leading-4 font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
  isError.value
    ? 'border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-900 hover:bg-red-100 dark:hover:bg-red-800 focus:ring-red-500'
    : 'border-yellow-300 dark:border-yellow-700 text-yellow-700 dark:text-yellow-300 bg-yellow-50 dark:bg-yellow-900 hover:bg-yellow-100 dark:hover:bg-yellow-800 focus:ring-yellow-500'
])

const closeButtonClasses = computed(() => [
  'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2',
  isError.value
    ? 'text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-800 focus:ring-red-500'
    : 'text-yellow-500 dark:text-yellow-400 hover:bg-yellow-100 dark:hover:bg-yellow-800 focus:ring-yellow-500'
])

const icon = computed(() => isError.value ? ErrorIcon : WarningIcon)
const defaultTitle = computed(() => isError.value ? 'Error' : 'Warning')

defineEmits(['retry', 'close'])
</script> 