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
          // Update server settings from session if available
          if (response.data.serverSettings) {
            this.serverSettings = response.data.serverSettings
            localStorage.setItem('serverSettings', JSON.stringify(this.serverSettings))
          }
          this.startActivityMonitor()
        }
        return !!this.user
      } catch (err) {
        this.user = null
        return false
      }
    },

    async getSettings() {
      try {
        // Add timestamp to prevent caching
        const response = await axios.get('/api/settings', {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'If-None-Match': '',  // Prevent 304 responses
            'If-Modified-Since': ''  // Prevent 304 responses
          }
        })
        this.settings = response.data
        // Sync with serverSettings if they exist in the response
        if (response.data?.baikal) {
          this.serverSettings = response.data.baikal
          localStorage.setItem('serverSettings', JSON.stringify(response.data.baikal))
        } else if (this.serverSettings) {
          // If we have serverSettings but they're not in the response, update the response
          this.settings = { ...response.data, baikal: this.serverSettings }
          // Also persist these settings back to server to ensure consistency
          await axios.post('/api/settings', this.settings)
        }
        return this.settings
      } catch (err) {
        console.error('Error fetching settings:', err)
        // If server fetch fails, use cached settings
        return {
          ...this.settings,
          baikal: this.serverSettings
        }
      }
    },

    async updateSettings(settings) {
      const response = await axios.post('/api/settings/app', settings)
      this.settings = response.data
      return response.data
    },

    async updateServerSettings(settings) {
      const response = await axios.post('/api/settings/baikal', settings)
      if (response.data?.message?.includes('Settings saved')) {
        this.serverSettings = settings
        localStorage.setItem('serverSettings', JSON.stringify(settings))
        this.settings = { ...this.settings || {}, baikal: settings }
      }
      return response.data
    },

    async ensureSettings() {
      // First try to load from localStorage
      const stored = localStorage.getItem('serverSettings')
      if (stored) {
        this.serverSettings = JSON.parse(stored)
      }
      
      // Then get latest from server and sync
      await this.getSettings()
      
      return {
        settings: this.settings,
        serverSettings: this.serverSettings
      }
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