import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoading: false,
    error: null,
    lastActivity: ref(Date.now()),
    inactivityTimeout: ref(10), // minutes
    settings: null,
    serverSettings: JSON.parse(localStorage.getItem('serverSettings')) || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userFullName: (state) => state.user?.fullName || '',
  },

  actions: {
    async login(username, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await axios.post('/api/auth/login', { username, password })
        this.user = response.data.user
        this.settings = response.data.settings
        if (response.data.serverSettings) {
          this.serverSettings = response.data.serverSettings
          localStorage.setItem('serverSettings', JSON.stringify(this.serverSettings))
        }
        this.startActivityMonitor()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
        throw this.error
      } finally {
        this.isLoading = false
      }
    },

    async register(username, password, fullName) {
      this.isLoading = true
      this.error = null
      try {
        const response = await axios.post('/api/auth/register', {
          username,
          password,
          fullName
        })
        this.user = response.data.user
        this.settings = response.data.settings
        if (response.data.serverSettings) {
          this.serverSettings = response.data.serverSettings
          localStorage.setItem('serverSettings', JSON.stringify(this.serverSettings))
        }
        this.startActivityMonitor()
        return response.data
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed'
        throw this.error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        await axios.post('/api/auth/logout')
      } finally {
        this.user = null
        this.settings = null
        this.serverSettings = null
        localStorage.removeItem('serverSettings')
        this.stopActivityMonitor()
      }
    },

    async checkAuth() {
      try {
        const response = await axios.get('/api/auth/check')
        this.user = response.data.user
        if (this.user) {
          this.startActivityMonitor()
        }
        return !!this.user
      } catch (err) {
        this.user = null
        return false
      }
    },

    async getSettings() {
      if (!this.settings) {
        const response = await axios.get('/api/settings')
        this.settings = response.data
      }
      return this.settings
    },

    async updateSettings(settings) {
      const response = await axios.post('/api/settings/app', settings)
      this.settings = response.data
      return response.data
    },

    async updateServerSettings(settings) {
      const response = await axios.post('/api/settings/baikal', settings)
      this.serverSettings = response.data
      localStorage.setItem('serverSettings', JSON.stringify(this.serverSettings))
      // Reload settings to ensure we have the latest state
      await this.getSettings()
      return response.data
    },

    // Activity monitoring
    activityInterval: null,
    updateLastActivity() {
      this.lastActivity = Date.now()
    },

    startActivityMonitor() {
      this.stopActivityMonitor()
      this.updateLastActivity()
      
      // Check for inactivity every minute
      this.activityInterval = setInterval(() => {
        const inactiveTime = (Date.now() - this.lastActivity) / 1000 / 60 // minutes
        if (inactiveTime >= this.inactivityTimeout) {
          this.logout()
        }
      }, 60000) // Check every minute

      // Add activity listeners
      window.addEventListener('mousemove', this.updateLastActivity)
      window.addEventListener('keydown', this.updateLastActivity)
      window.addEventListener('click', this.updateLastActivity)
      window.addEventListener('scroll', this.updateLastActivity)
    },

    stopActivityMonitor() {
      if (this.activityInterval) {
        clearInterval(this.activityInterval)
        window.removeEventListener('mousemove', this.updateLastActivity)
        window.removeEventListener('keydown', this.updateLastActivity)
        window.removeEventListener('click', this.updateLastActivity)
        window.removeEventListener('scroll', this.updateLastActivity)
      }
    },

    setInactivityTimeout(minutes) {
      this.inactivityTimeout = minutes
    }
  }
}) 