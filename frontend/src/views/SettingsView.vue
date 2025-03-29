<template>
  <div class="settings-view">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>
    
    <div class="grid gap-6">
      <!-- Server Settings -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Server Settings</h2>
        <form @submit.prevent="saveServerSettings" class="space-y-4">
          <div class="form-group">
            <label for="baikalUrl" class="label">Baikal Server URL</label>
            <input
              id="baikalUrl"
              v-model="serverSettings.baikalUrl"
              type="url"
              class="input"
              placeholder="https://your-baikal-server.com"
              required
            />
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
          
          <button type="submit" class="btn-primary">
            Save Server Settings
          </button>
        </form>
      </div>

      <!-- User Settings -->
      <div class="card">
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
      <div class="card">
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
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const serverSettings = ref({
  baikalUrl: '',
  authType: 'basic'
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
      authType: settings.authType || 'basic'
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
    console.error('Failed to load settings:', error)
  }
}

// Save settings
const saveServerSettings = async () => {
  try {
    await authStore.updateSettings({ 
      baikalUrl: serverSettings.value.baikalUrl,
      authType: serverSettings.value.authType
    })
  } catch (error) {
    console.error('Failed to save server settings:', error)
  }
}

const saveUserSettings = async () => {
  try {
    await authStore.updateSettings({
      username: userSettings.value.username,
      ...(userSettings.value.password && { password: userSettings.value.password })
    })
  } catch (error) {
    console.error('Failed to save user settings:', error)
  }
}

const saveAppSettings = async () => {
  try {
    await authStore.updateSettings({
      theme: appSettings.value.theme,
      timeout: appSettings.value.timeout
    })
  } catch (error) {
    console.error('Failed to save app settings:', error)
  }
}

// Load settings on component mount
loadSettings()
</script> 