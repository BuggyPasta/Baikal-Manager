<template>
  <div class="settings-view">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>
    
    <!-- Success Message -->
    <div v-if="showSuccessMessage" class="mb-4 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-md">
      {{ successMessage }}
    </div>

    <!-- Loading Message -->
    <div v-if="loadingMessage" class="mb-4 p-4 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-md flex items-center">
      <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      {{ loadingMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-md">
      {{ errorMessage }}
    </div>

    <div class="settings-container">
      <!-- Server Settings -->
      <div class="settings-card">
        <h2 class="text-xl font-semibold mb-4">Server Settings</h2>
        <form @submit.prevent="saveServerSettings" class="space-y-4">
          <div class="form-group">
            <label for="serverUrl" class="label">Baikal Server URL</label>
            <input
              id="serverUrl"
              v-model="serverSettings.serverUrl"
              type="url"
              class="input"
              placeholder="https://your-baikal-server.com/dav.php"
              required
            />
            <p class="form-hint">The base URL of your Baikal server (e.g., http://10.13.88.6:1910/dav.php)</p>
          </div>
          
          <div class="form-group">
            <label for="authType" class="label">Authentication Type</label>
            <select
              id="authType"
              v-model="serverSettings.authType"
              class="input"
              required
            >
              <option value="basic">Basic Auth</option>
              <option value="digest">Digest Auth</option>
            </select>
          </div>

          <div class="form-group">
            <label for="username" class="label">Server Username</label>
            <input
              id="username"
              v-model="serverSettings.username"
              type="text"
              class="input"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password" class="label">Server Password</label>
            <input
              id="password"
              v-model="serverSettings.password"
              type="password"
              class="input"
              required
            />
          </div>

          <div class="form-group">
            <label for="addressBookPath" class="label">Address Book Path</label>
            <input
              id="addressBookPath"
              v-model="serverSettings.addressBookPath"
              type="text"
              class="input"
              placeholder="/addressbooks/username/default/"
              required
            />
            <p class="form-hint">e.g /addressbooks/YOUR_BAIKAL_USERNAME/default/</p>
          </div>

          <div class="form-group">
            <label for="calendarPath" class="label">Calendar Path</label>
            <input
              id="calendarPath"
              v-model="serverSettings.calendarPath"
              type="text"
              class="input"
              placeholder="/calendars/username/default/"
              required
            />
            <p class="form-hint">e.g /calendars/YOUR_BAIKAL_USERNAME/default/</p>
          </div>
          
          <div class="form-actions">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="testConnection"
              :disabled="testingConnection"
            >
              <span v-if="testingConnection" class="spinner-border spinner-border-sm me-1"></span>
              {{ testingConnection ? 'Testing...' : 'Test Connection' }}
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              {{ saving ? 'Saving...' : 'Save Server Settings' }}
            </button>
          </div>
        </form>
      </div>

      <div class="space-y-6">
        <!-- User Settings -->
        <div class="settings-card">
          <h2 class="text-xl font-semibold mb-4">User Settings</h2>
          <form @submit.prevent="saveUserSettings" class="space-y-4">
            <div class="form-group">
              <label for="fullName" class="label">Full Name</label>
              <input
                id="fullName"
                v-model="userSettings.fullName"
                type="text"
                class="input"
                required
              />
            </div>

            <div class="form-group">
              <label for="username" class="label">Username</label>
              <input
                id="username"
                v-model="userSettings.username"
                type="text"
                class="input"
                required
                :value="authStore.user?.username"
              />
            </div>
            
            <div class="form-group">
              <label for="password" class="label">Password</label>
              <input
                id="password"
                v-model="userSettings.password"
                type="password"
                class="input"
                placeholder="Enter new password"
                :value="authStore.user?.password ? '••••••••' : ''"
              />
              <p class="form-hint">Leave empty to keep current password</p>
            </div>
            
            <button type="submit" class="btn-primary">
              Save User Settings
            </button>
          </form>
        </div>

        <!-- App Settings -->
        <div class="settings-card">
          <h2 class="text-xl font-semibold mb-4">Application Settings</h2>
          <form @submit.prevent="saveAppSettings" class="space-y-4">
            <div class="form-group">
              <label class="label">Theme</label>
              <div class="flex space-x-4">
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    v-model="appSettings.theme"
                    value="light"
                    class="form-radio"
                    @change="handleThemeChange"
                  />
                  <span class="ml-2">Light</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    v-model="appSettings.theme"
                    value="dark"
                    class="form-radio"
                    @change="handleThemeChange"
                  />
                  <span class="ml-2">Dark</span>
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label for="timeout" class="label">Auto Logout Timeout (minutes)</label>
              <input
                id="timeout"
                v-model.number="appSettings.timeout"
                type="number"
                min="1"
                class="input"
                required
              />
            </div>
            
            <button type="submit" class="btn-primary">
              Save App Settings
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showSuccessMessage = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const loadingMessage = ref('')

const serverSettings = ref({
  serverUrl: '',
  authType: 'basic',
  username: '',
  password: '',
  addressBookPath: '',
  calendarPath: ''
})

const userSettings = ref({
  fullName: '',
  username: '',
  password: ''
})

const appSettings = ref({
  theme: 'light',
  timeout: 10
})

// Load current settings
const loadSettings = async () => {
  try {
    loadingMessage.value = 'Loading settings...'
    const settings = await authStore.getSettings()
    
    // Load server settings
    if (settings?.baikal) {
      serverSettings.value = { ...settings.baikal }
    } else if (authStore.serverSettings) {
      serverSettings.value = { ...authStore.serverSettings }
    }
    
    // Load user settings
    userSettings.value = {
      fullName: authStore.user?.fullName || '',
      username: authStore.user?.username || '',
      password: '' // Don't load password
    }
    
    // Load app settings
    if (settings?.app) {
      appSettings.value = {
        theme: settings.app.theme || 'light',
        timeout: settings.app.timeout || 10
      }
    }
    
    loadingMessage.value = ''
  } catch (err) {
    errorMessage.value = 'Failed to load settings'
    console.error('Error loading settings:', err)
    loadingMessage.value = ''
  }
}

// Show success message temporarily
const showSuccess = (message) => {
  showSuccessMessage.value = true
  successMessage.value = message
  setTimeout(() => {
    showSuccessMessage.value = false
    successMessage.value = ''
  }, 3000)
}

// Save settings
const saveServerSettings = async () => {
  try {
    setLoading(true, 'Saving settings...')
    errorMessage.value = ''
    
    const response = await fetch('/api/settings/baikal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(serverSettings.value)
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      errorMessage.value = data.details || data.error || 'Failed to save settings'
      return
    }
    
    showSuccess('Settings saved successfully')
    await authStore.getSettings() // Refresh settings from server
  } catch (error) {
    console.error('Error saving settings:', error)
    errorMessage.value = error.message || 'Failed to save settings'
  } finally {
    setLoading(false)
  }
}

const saveUserSettings = async () => {
  try {
    await authStore.updateSettings({
      fullName: userSettings.value.fullName,
      username: userSettings.value.username,
      ...(userSettings.value.password && { password: userSettings.value.password })
    })
    showSuccess('User settings saved successfully')
  } catch (error) {
    errorMessage.value = 'Failed to save user settings: ' + error.message
  }
}

const saveAppSettings = async () => {
  try {
    await authStore.updateSettings({
      theme: appSettings.value.theme,
      timeout: appSettings.value.timeout
    })
    showSuccess('App settings saved successfully')
  } catch (error) {
    errorMessage.value = 'Failed to save app settings: ' + error.message
  }
}

// Add test connection function
const testConnection = async () => {
  try {
    setLoading(true, 'Testing connection...')
    errorMessage.value = ''
    
    const response = await fetch('/api/settings/baikal/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(serverSettings.value)
    })
    
    let data
    try {
      data = await response.json()
    } catch (parseError) {
      console.error('Raw response:', await response.text())
      errorMessage.value = 'Server returned an invalid response. Please check if the URL points to the correct Baikal DAV endpoint (usually ending in dav.php). If the issue persists, check the server logs for more details.'
      return
    }
    
    if (response.ok) {
      showSuccess('Connection successful! All paths verified.')
    } else {
      // Check if the error message contains retry information
      if (data.details?.includes('Attempt')) {
        setLoading(true, data.details)
        // Keep showing the retry message
        return
      }
      errorMessage.value = `${data.error}${data.details ? ': ' + data.details : ''}`
    }
  } catch (error) {
    // Check if the error message contains retry information
    if (error.message?.includes('Attempt')) {
      setLoading(true, error.message)
      // Keep showing the retry message
      return
    }
    errorMessage.value = error.message || 'Failed to test connection'
  } finally {
    if (!loadingMessage.value?.includes('Attempt')) {
      setLoading(false)
    }
  }
}

const setLoading = (isLoading, message = '') => {
  document.body.style.cursor = isLoading ? 'wait' : 'default'
  loadingMessage.value = message
}

// Add handleThemeChange function
const handleThemeChange = () => {
  // Update theme immediately
  document.documentElement.classList.toggle('dark', appSettings.value.theme === 'dark')
  // Store in localStorage for persistence
  localStorage.setItem('theme', appSettings.value.theme)
}

// Initialize settings on mount
onMounted(async () => {
  await loadSettings()
})

// Watch for server settings changes
watch(() => authStore.serverSettings, (newSettings) => {
  if (newSettings) {
    serverSettings.value = { ...newSettings }
  }
}, { immediate: true })

// Watch for user changes
watch(() => authStore.user, (newUser) => {
  if (newUser) {
    userSettings.value = {
      fullName: newUser.fullName || '',
      username: newUser.username || '',
      password: '' // Don't load password
    }
  }
}, { immediate: true })
</script> 