import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const lastActivity = ref(Date.now())
  const inactivityTimeout = ref(10) // minutes

  // Computed
  const isAuthenticated = computed(() => !!user.value)
  const userFullName = computed(() => user.value?.fullName ?? '')

  // Actions
  async function login(username, password) {
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.post('/api/auth/login', { username, password })
      user.value = response.data.user
      startActivityMonitor()
    } catch (err) {
      error.value = err.response?.data?.message || 'Login failed'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }

  async function register(username, password, fullName) {
    isLoading.value = true
    error.value = null
    try {
      const response = await axios.post('/api/auth/register', {
        username,
        password,
        fullName
      })
      user.value = response.data.user
      startActivityMonitor()
    } catch (err) {
      error.value = err.response?.data?.message || 'Registration failed'
      throw error.value
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await axios.post('/api/auth/logout')
    } finally {
      user.value = null
      stopActivityMonitor()
    }
  }

  async function checkAuth() {
    try {
      const response = await axios.get('/api/auth/check')
      user.value = response.data.user
      if (user.value) {
        startActivityMonitor()
      }
      return !!user.value
    } catch (err) {
      user.value = null
      return false
    }
  }

  // Settings management
  async function getSettings() {
    try {
      const [baikalResponse, appResponse] = await Promise.all([
        axios.get('/api/settings/baikal'),
        axios.get('/api/settings/app')
      ])
      
      return {
        ...baikalResponse.data,
        ...appResponse.data
      }
    } catch (err) {
      throw new Error(err.response?.data?.error || 'Failed to load settings')
    }
  }

  async function updateSettings(settings) {
    try {
      if ('baikalUrl' in settings) {
        await axios.post('/api/settings/baikal', {
          serverUrl: settings.baikalUrl,
          username: settings.username,
          password: settings.password,
          addressBookPath: settings.addressBookPath,
          calendarPath: settings.calendarPath,
          authType: settings.authType
        })
      } else if ('theme' in settings || 'timeout' in settings) {
        await axios.post('/api/settings/app', {
          theme: settings.theme,
          autoLogoutMinutes: settings.timeout
        })
        if (settings.timeout) {
          setInactivityTimeout(settings.timeout)
        }
        if (settings.theme) {
          document.documentElement.classList.toggle('dark', settings.theme === 'dark')
        }
      }
    } catch (err) {
      throw new Error(err.response?.data?.error || 'Failed to save settings')
    }
  }

  // Activity monitoring
  let activityInterval
  function updateLastActivity() {
    lastActivity.value = Date.now()
  }

  function startActivityMonitor() {
    stopActivityMonitor()
    updateLastActivity()
    
    // Check for inactivity every minute
    activityInterval = setInterval(() => {
      const inactiveTime = (Date.now() - lastActivity.value) / 1000 / 60 // minutes
      if (inactiveTime >= inactivityTimeout.value) {
        logout()
      }
    }, 60000) // Check every minute

    // Add activity listeners
    window.addEventListener('mousemove', updateLastActivity)
    window.addEventListener('keydown', updateLastActivity)
    window.addEventListener('click', updateLastActivity)
    window.addEventListener('scroll', updateLastActivity)
  }

  function stopActivityMonitor() {
    if (activityInterval) {
      clearInterval(activityInterval)
      window.removeEventListener('mousemove', updateLastActivity)
      window.removeEventListener('keydown', updateLastActivity)
      window.removeEventListener('click', updateLastActivity)
      window.removeEventListener('scroll', updateLastActivity)
    }
  }

  function setInactivityTimeout(minutes) {
    inactivityTimeout.value = minutes
  }

  return {
    // State
    user,
    isLoading,
    error,
    inactivityTimeout,
    
    // Computed
    isAuthenticated,
    userFullName,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
    getSettings,
    updateSettings,
    setInactivityTimeout,
    updateLastActivity
  }
}) 