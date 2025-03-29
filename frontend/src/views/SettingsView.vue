<template>
  <div class="settings-view">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>
    
    <!-- Success Message -->
    <div v-if="showSuccessMessage" class="mb-4 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-md">
      Settings saved successfully!
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
            <label for="baikalUrl" class="label">Baikal Server URL</label>
            <input
              id="baikalUrl"
              v-model="serverSettings.baikalUrl"
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
          
          <div class="flex space-x-4">
            <button type="submit" class="btn-primary">
              Save Server Settings
            </button>
            <button type="button" @click="testConnection" class="btn-secondary">
              Test Connection
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
              <label for="username" class="label">Username</label>
              <input
                id="username"
                v-model="userSettings.username"
                type="text"
                class="input"
                required
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
                  />
                  <span class="ml-2">Light</span>
                </label>
                <label class="inline-flex items-center">
                  <input
                    type="radio"
                    v-model="appSettings.theme"
                    value="dark"
                    class="form-radio"
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
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const showSuccessMessage = ref(false)
const errorMessage = ref('')

const serverSettings = ref({
  baikalUrl: '',
  authType: 'basic',
  username: '',
  password: '',
  addressBookPath: '',
  calendarPath: ''
})

const userSettings = ref({
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
    const settings = await authStore.getSettings()
    serverSettings.value = {
      baikalUrl: settings.baikalUrl || '',
      authType: settings.authType || 'basic',
      username: settings.username || '',
      password: settings.password || '',
      addressBookPath: settings.addressBookPath || '',
      calendarPath: settings.calendarPath || ''
    }
    userSettings.value = {
      username: settings.username || '',
      password: ''
    }
    appSettings.value = {
      theme: settings.theme || 'light',
      timeout: settings.timeout || 10
    }
  } catch (error) {
    errorMessage.value = 'Failed to load settings: ' + error.message
  }
}

// Show success message temporarily
const showSuccess = () => {
  showSuccessMessage.value = true
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 3000)
}

// Save settings
const saveServerSettings = async () => {
  try {
    await authStore.updateServerSettings({ 
      serverUrl: serverSettings.value.baikalUrl,
      authType: serverSettings.value.authType,
      username: serverSettings.value.username,
      password: serverSettings.value.password,
      addressBookPath: serverSettings.value.addressBookPath,
      calendarPath: serverSettings.value.calendarPath
    })
    showSuccess()
  } catch (error) {
    errorMessage.value = 'Failed to save server settings: ' + error.message
  }
}

const saveUserSettings = async () => {
  try {
    await authStore.updateSettings({
      username: userSettings.value.username,
      ...(userSettings.value.password && { password: userSettings.value.password })
    })
    showSuccess()
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
    showSuccess()
  } catch (error) {
    errorMessage.value = 'Failed to save app settings: ' + error.message
  }
}

// Add test connection function
const testConnection = async () => {
  try {
    const response = await fetch('/api/settings/test-baikal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        serverUrl: serverSettings.value.baikalUrl,
        username: serverSettings.value.username,
        password: serverSettings.value.password
      })
    })
    
    const data = await response.json()
    if (response.ok) {
      showSuccessMessage.value = true
      setTimeout(() => {
        showSuccessMessage.value = false
      }, 3000)
    } else {
      errorMessage.value = data.error || 'Failed to connect to server'
    }
  } catch (error) {
    errorMessage.value = 'Failed to test connection: ' + error.message
  }
}

// Load settings on component mount
loadSettings()
</script> 