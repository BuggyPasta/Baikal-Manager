<template>
  <BaseModal :title="modalTitle" @close="$emit('close')">
    <form @submit.prevent="handleSubmit">
      <div class="space-y-4">
        <!-- Name Fields -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FormField label="First Name" required>
            <input
              type="text"
              v-model="formData.firstName"
              required
              :class="inputClasses"
            />
          </FormField>

          <FormField label="Last Name" required>
            <input
              type="text"
              v-model="formData.lastName"
              required
              :class="inputClasses"
            />
          </FormField>
        </div>

        <FormField label="Display Name">
          <input
            type="text"
            v-model="formData.displayName"
            :class="inputClasses"
          />
        </FormField>

        <FormField label="Organization">
          <input
            type="text"
            v-model="formData.organization"
            :class="inputClasses"
          />
        </FormField>

        <FormField label="Email">
          <input
            type="email"
            v-model="formData.email"
            :class="inputClasses"
          />
        </FormField>

        <FormField label="Phone">
          <input
            type="tel"
            v-model="formData.phone"
            :class="inputClasses"
          />
        </FormField>

        <FormField label="Address">
          <textarea
            v-model="formData.address"
            rows="3"
            :class="inputClasses"
          ></textarea>
        </FormField>

        <FormField label="Address Book" required>
          <select
            v-model="formData.addressBookId"
            required
            :class="inputClasses"
          >
            <option
              v-for="book in addressBooks"
              :key="book.id"
              :value="book.id"
            >
              {{ book.name }}
            </option>
          </select>
        </FormField>

        <FormField label="Notes">
          <textarea
            v-model="formData.notes"
            rows="3"
            :class="inputClasses"
          ></textarea>
        </FormField>
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <button
          v-if="contact"
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
          {{ contact ? 'Save Changes' : 'Create Contact' }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseModal from './BaseModal.vue'
import FormField from './FormField.vue'

const props = defineProps({
  contact: Object,
  addressBooks: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['close', 'save', 'delete'])

// Form data with default values
const defaultFormData = {
  firstName: '',
  lastName: '',
  displayName: '',
  organization: '',
  email: '',
  phone: '',
  address: '',
  addressBookId: '',
  notes: ''
}

const formData = ref({ ...defaultFormData })

// Computed properties
const modalTitle = computed(() => props.contact ? 'Edit Contact' : 'New Contact')

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
  formData.value = props.contact
    ? { ...defaultFormData, ...props.contact }
    : { ...defaultFormData, addressBookId: props.addressBooks[0]?.id || '' }
}

function handleSubmit() {
  emit('save', props.contact 
    ? { ...formData.value, id: props.contact.id }
    : { ...formData.value }
  )
}

function handleDelete() {
  if (confirm('Are you sure you want to delete this contact?')) {
    emit('delete', props.contact)
  }
}

// Initialize form data
initializeFormData()
</script> 