<template>
  <BaseModal :title="modalTitle" @close="$emit('close')">
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4">
        <FormField label="Title" required>
          <input
            type="text"
            v-model="formData.title"
            required
            :class="inputClasses"
          />
        </FormField>

        <FormField label="Description">
          <textarea
            v-model="formData.description"
            rows="3"
            :class="inputClasses"
          ></textarea>
        </FormField>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="Start Date" required>
            <DateTimeInput
              v-model:date="formData.startDate"
              v-model:time="formData.startTime"
              :disabled="formData.allDay"
              required
            />
          </FormField>

          <FormField label="End Date" required>
            <DateTimeInput
              v-model:date="formData.endDate"
              v-model:time="formData.endTime"
              :disabled="formData.allDay"
              required
            />
          </FormField>
        </div>

        <FormField label="Calendar" required>
          <select
            v-model="formData.calendarId"
            required
            :class="inputClasses"
          >
            <option v-for="cal in calendars" :key="cal.id" :value="cal.id">
              {{ cal.name }}
            </option>
          </select>
        </FormField>

        <FormField label="Color">
          <select
            v-model="formData.color"
            :class="inputClasses"
          >
            <option v-for="color in availableColors" :key="color.value" :value="color.value">
              {{ color.label }}
            </option>
          </select>
        </FormField>

        <div class="flex items-center">
          <input
            type="checkbox"
            v-model="formData.allDay"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
            All day event
          </label>
        </div>
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <button
          v-if="event"
          type="button"
          @click="handleDelete"
          :class="deleteButtonClasses"
        >
          Delete
        </button>
        <button
          type="button"
          @click="$emit('close')"
          :class="cancelButtonClasses"
        >
          Cancel
        </button>
        <button
          type="submit"
          :class="submitButtonClasses"
        >
          {{ event ? 'Save Changes' : 'Create Event' }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { format } from 'date-fns'
import BaseModal from './BaseModal.vue'
import FormField from './FormField.vue'
import DateTimeInput from './DateTimeInput.vue'

const props = defineProps({
  event: Object,
  date: {
    type: Date,
    required: true
  }
})

const emit = defineEmits(['close', 'save', 'delete'])

const formData = ref({
  title: '',
  description: '',
  startDate: '',
  startTime: '',
  endDate: '',
  endTime: '',
  calendarId: 'default',
  color: 'blue',
  allDay: false
})

const calendars = ref([
  { id: 'default', name: 'Default Calendar' }
])

const availableColors = [
  { value: 'blue', label: 'Blue' },
  { value: 'green', label: 'Green' },
  { value: 'red', label: 'Red' },
  { value: 'yellow', label: 'Yellow' },
  { value: 'purple', label: 'Purple' },
  { value: 'pink', label: 'Pink' }
]

// Computed properties
const modalTitle = computed(() => props.event ? 'Edit Event' : 'New Event')

const inputClasses = computed(() => [
  'mt-1 block w-full rounded-md border-gray-300 shadow-sm',
  'focus:border-blue-500 focus:ring-blue-500',
  'dark:bg-gray-700 dark:border-gray-600 dark:text-white',
  'sm:text-sm'
])

const buttonBaseClasses = [
  'inline-flex justify-center rounded-md border shadow-sm px-4 py-2',
  'text-base font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
  'sm:text-sm'
]

const submitButtonClasses = computed(() => [
  ...buttonBaseClasses,
  'border-transparent bg-blue-600 text-white',
  'hover:bg-blue-700 focus:ring-blue-500'
])

const cancelButtonClasses = computed(() => [
  ...buttonBaseClasses,
  'border-gray-300 bg-white dark:bg-gray-800',
  'text-gray-700 dark:text-gray-300',
  'hover:bg-gray-50 dark:hover:bg-gray-700',
  'focus:ring-blue-500'
])

const deleteButtonClasses = computed(() => [
  ...buttonBaseClasses,
  'border-red-300 bg-white dark:bg-gray-800',
  'text-red-700 dark:text-red-300',
  'hover:bg-red-50 dark:hover:bg-red-900',
  'focus:ring-red-500'
])

// Methods
function initializeFormData() {
  if (props.event) {
    const start = new Date(props.event.start)
    const end = new Date(props.event.end)
    
    formData.value = {
      ...props.event,
      startDate: format(start, 'yyyy-MM-dd'),
      startTime: format(start, 'HH:mm'),
      endDate: format(end, 'yyyy-MM-dd'),
      endTime: format(end, 'HH:mm')
    }
  } else {
    const defaultEnd = new Date(props.date.getTime() + 60 * 60 * 1000)
    formData.value = {
      title: '',
      description: '',
      startDate: format(props.date, 'yyyy-MM-dd'),
      startTime: format(props.date, 'HH:mm'),
      endDate: format(props.date, 'yyyy-MM-dd'),
      endTime: format(defaultEnd, 'HH:mm'),
      calendarId: 'default',
      color: 'blue',
      allDay: false
    }
  }
}

function handleSubmit() {
  const eventData = {
    ...formData.value,
    start: new Date(`${formData.value.startDate}T${formData.value.startTime}`),
    end: new Date(`${formData.value.endDate}T${formData.value.endTime}`)
  }
  emit('save', eventData)
}

function handleDelete() {
  if (confirm('Are you sure you want to delete this event?')) {
    emit('delete', props.event)
  }
}

// Initialize form data
initializeFormData()

// Watch for all-day changes
watch(() => formData.value.allDay, (isAllDay) => {
  if (isAllDay) {
    formData.value.startTime = '00:00'
    formData.value.endTime = '23:59'
  }
})
</script> 