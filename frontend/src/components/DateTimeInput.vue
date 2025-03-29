<template>
  <div class="space-y-2">
    <input
      type="date"
      :value="date"
      @input="$emit('update:date', $event.target.value)"
      :disabled="disabled"
      :required="required"
      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
    />
    <input
      type="time"
      :value="time"
      @input="$emit('update:time', $event.target.value)"
      :disabled="disabled"
      :required="required"
      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white sm:text-sm"
    />
  </div>
</template>

<script setup>
defineProps({
  date: {
    type: String,
    required: true
  },
  time: {
    type: String,
    required: true
  },
  disabled: Boolean,
  required: Boolean
})

defineEmits(['update:date', 'update:time'])
</script> 