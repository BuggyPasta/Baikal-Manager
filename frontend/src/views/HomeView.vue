<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">
      Welcome, {{ userFullName }}
    </h1>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <!-- Contacts Stats -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Contacts</h2>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            Last synced: {{ formatDate(contactsLastSync) }}
          </span>
        </div>
        <p class="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-4">
          {{ contactsCount }}
        </p>
        <router-link
          to="/contacts"
          class="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
        >
          View all contacts
          <svg class="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </router-link>
      </div>

      <!-- Calendar Stats -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Calendar</h2>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            Last synced: {{ formatDate(calendarLastSync) }}
          </span>
        </div>
        <p class="text-4xl font-bold text-blue-600 dark:text-blue-400 mb-4">
          {{ upcomingEventsCount }} upcoming
        </p>
        <router-link
          to="/calendar"
          class="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
        >
          View calendar
          <svg class="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </router-link>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <router-link
          to="/contacts?action=new"
          class="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Add New Contact
        </router-link>
        <router-link
          to="/calendar?action=new"
          class="flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Add New Event
        </router-link>
      </div>
    </div>

    <!-- Server Status -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Server Status</h2>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-gray-600 dark:text-gray-400">Baikal Server</span>
          <span :class="[
            'px-2 py-1 text-sm rounded-full',
            isServerConnected ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
          ]">
            {{ isServerConnected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-gray-600 dark:text-gray-400">Last Login</span>
          <span class="text-gray-900 dark:text-white">{{ formatDate(lastLogin) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'

const authStore = useAuthStore()
const userFullName = ref(authStore.userFullName)

// Stats
const contactsCount = ref(0)
const upcomingEventsCount = ref(0)
const contactsLastSync = ref(null)
const calendarLastSync = ref(null)
const isServerConnected = computed(() => {
  const serverSettings = authStore.serverSettings
  return serverSettings && serverSettings.serverUrl && serverSettings.username && serverSettings.password
})
const lastLogin = ref(authStore.user?.last_login || null)

function formatDate(timestamp) {
  if (!timestamp) return 'Never'
  return format(new Date(timestamp), 'MMM d, yyyy HH:mm')
}

onMounted(async () => {
  try {
    // TODO: Implement API calls to get these values
    // For now, using placeholder values
    contactsCount.value = '...'
    upcomingEventsCount.value = '...'
    contactsLastSync.value = Date.now()
    calendarLastSync.value = Date.now()
    isServerConnected.value = isServerConnected.value
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script> 