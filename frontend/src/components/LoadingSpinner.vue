<template>
  <div :class="containerClasses">
    <div :class="spinnerClasses"></div>
    <span v-if="text" class="ml-3 text-gray-700 dark:text-gray-300">{{ text }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  text: String,
  fullScreen: Boolean
})

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12'
}

const containerClasses = computed(() => [
  'flex items-center justify-center',
  props.fullScreen && 'fixed inset-0 bg-white/75 dark:bg-gray-900/75 z-50'
])

const spinnerClasses = computed(() => [
  'animate-spin rounded-full border-t-2 border-blue-500',
  sizeClasses[props.size] || sizeClasses.md
])
</script> 