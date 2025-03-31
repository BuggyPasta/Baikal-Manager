<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4 md:mb-0">Contacts</h1>
      
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Search -->
        <div class="relative">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search contacts..."
            class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <svg
            class="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        <!-- Address Book Selection -->
        <select
          v-model="selectedAddressBook"
          class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Address Books</option>
          <option
            v-for="book in addressBooks"
            :key="book.id"
            :value="book.id"
          >
            {{ book.name }}
          </option>
        </select>

        <!-- Import/Export -->
        <div class="flex gap-2">
          <input
            type="file"
            ref="fileInput"
            accept=".csv"
            class="hidden"
            @change="handleFileImport"
          />
          <button
            @click="$refs.fileInput.click()"
            class="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Import
          </button>
          <button
            @click="exportContacts"
            class="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Export
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center h-96">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900 p-4 rounded-lg mb-8">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchContacts"
        class="mt-2 text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
      >
        Try again
      </button>
    </div>

    <!-- Contacts List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Contact Cards -->
      <div
        v-for="contact in filteredContacts"
        :key="contact.id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow"
      >
        <div class="p-6">
          <!-- Contact Header -->
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ contact.displayName || `${contact.firstName} ${contact.lastName}` }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ contact.organization || 'No organization' }}
              </p>
            </div>
            <button
              @click="openContactModal(contact)"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
          </div>

          <!-- Contact Details -->
          <div class="space-y-3">
            <div v-if="contact.email" class="flex items-center">
              <svg class="h-5 w-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <a
                :href="`mailto:${contact.email}`"
                class="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {{ contact.email }}
              </a>
            </div>

            <div v-if="contact.phone" class="flex items-center">
              <svg class="h-5 w-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                />
              </svg>
              <a
                :href="`tel:${contact.phone}`"
                class="text-gray-600 dark:text-gray-300 hover:underline"
              >
                {{ contact.phone }}
              </a>
            </div>

            <div v-if="contact.address" class="flex items-start">
              <svg class="h-5 w-5 text-gray-400 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span class="text-gray-600 dark:text-gray-300">
                {{ contact.address }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Contact Button -->
    <button
      @click="openContactModal()"
      class="fixed bottom-8 right-8 bg-blue-600 text-white rounded-full p-4 shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>

    <!-- Contact Modal -->
    <ContactModal
      v-if="showContactModal"
      :contact="selectedContact"
      :address-books="addressBooks"
      @close="closeContactModal"
      @save="saveContact"
      @delete="deleteContact"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ContactModal from '@/components/ContactModal.vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()

// State
const contacts = ref([])
const addressBooks = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const selectedAddressBook = ref('')
const showContactModal = ref(false)
const selectedContact = ref(null)

// Computed
const filteredContacts = computed(() => {
  let filtered = contacts.value

  // Filter by address book
  if (selectedAddressBook.value) {
    filtered = filtered.filter(contact => contact.addressBookId === selectedAddressBook.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(contact => {
      const searchableFields = [
        contact.firstName,
        contact.lastName,
        contact.displayName,
        contact.email,
        contact.phone,
        contact.organization,
        contact.address
      ].filter(Boolean)
      
      return searchableFields.some(field => field.toLowerCase().includes(query))
    })
  }

  return filtered
})

// Methods
const fetchAddressBooks = async () => {
  try {
    const response = await axios.get('/api/contacts/address-books')
    addressBooks.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load address books'
    console.error('Error fetching address books:', err)
  }
}

const fetchContacts = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get('/api/contacts/contacts', {
      params: {
        addressBookId: selectedAddressBook.value
      }
    })
    contacts.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to load contacts'
    console.error('Error fetching contacts:', err)
  } finally {
    loading.value = false
  }
}

function openContactModal(contact = null) {
  selectedContact.value = contact
  showContactModal.value = true
}

function closeContactModal() {
  showContactModal.value = false
  selectedContact.value = null
}

const saveContact = async (contactData) => {
  try {
    if (contactData.id) {
      await axios.put(`/api/contacts/contacts/${contactData.id}`, contactData)
    } else {
      await axios.post('/api/contacts/contacts', contactData)
    }
    await fetchContacts()
    showContactModal.value = false
    selectedContact.value = null
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to save contact'
    console.error('Error saving contact:', err)
  }
}

const deleteContact = async (contactId) => {
  try {
    await axios.delete(`/api/contacts/contacts/${contactId}`, {
      params: {
        addressBookId: selectedAddressBook.value
      }
    })
    await fetchContacts()
    showContactModal.value = false
    selectedContact.value = null
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to delete contact'
    console.error('Error deleting contact:', err)
  }
}

const handleFileImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)
  formData.append('addressBookId', selectedAddressBook.value)

  try {
    await axios.post('/api/contacts/contacts/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    await fetchContacts()
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to import contacts'
    console.error('Error importing contacts:', err)
  }
}

const exportContacts = async () => {
  try {
    const response = await axios.get('/api/contacts/contacts/export', {
      params: {
        addressBookId: selectedAddressBook.value
      },
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'contacts.vcf')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to export contacts'
    console.error('Error exporting contacts:', err)
  }
}

// Watch for address book changes to fetch new contacts
watch(selectedAddressBook, () => {
  fetchContacts()
})

// Initial load
onMounted(async () => {
  await fetchAddressBooks()
  await fetchContacts()
})
</script> 