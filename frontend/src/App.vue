<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <header v-if="isAuthenticated" class="sticky top-0 bg-white dark:bg-gray-900 shadow-md">
      <nav class="container mx-auto px-4 py-4 flex items-center justify-between">
        <!-- Logo and App Name -->
        <div class="flex items-center">
          <img src="@/assets/icons/app_logo.svg" alt="Baikal Manager" class="h-12 w-12 mr-3">
          <span class="text-2xl font-semibold text-gray-900 dark:text-white">{{ appName }}</span>
        </div>

        <!-- Navigation Links -->
        <div class="hidden md:flex space-x-4">
          <router-link to="/calendar" class="nav-link">Calendar</router-link>
          <router-link to="/contacts" class="nav-link">Contacts</router-link>
          <router-link to="/settings" class="nav-link">Settings</router-link>
        </div>

        <!-- User Info, Theme Toggle, and Logout -->
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-sm text-gray-700 dark:text-gray-300">{{ userFullName }}</router-link>
          <button @click="toggleTheme" class="theme-toggle">
            <img :src="themeIcon" :alt="isDarkMode ? 'Light Mode' : 'Dark Mode'" class="h-6 w-6">
          </button>
          <button @click="logout" class="text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
            Logout
          </button>
        </div>

        <!-- Mobile Menu Button -->
        <button @click="toggleMobileMenu" class="md:hidden">
          <span class="sr-only">Menu</span>
          <!-- Hamburger Icon -->
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </nav>

      <!-- Mobile Menu -->
      <div v-if="isMobileMenuOpen" class="md:hidden">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <router-link to="/calendar" class="mobile-nav-link" @click="toggleMobileMenu">Calendar</router-link>
          <router-link to="/contacts" class="mobile-nav-link" @click="toggleMobileMenu">Contacts</router-link>
          <router-link to="/settings" class="mobile-nav-link" @click="toggleMobileMenu">Settings</router-link>
          <button @click="logout" class="w-full text-left mobile-nav-link">Logout</button>
        </div>
      </div>
    </header>

    <main class="container mx-auto px-4 py-8">
      <router-view></router-view>
    </main>

    <footer class="mt-auto py-4">
      <hr class="w-11/12 mx-auto border-gray-200 dark:border-gray-700">
      <div class="text-center text-xs mt-2">
        Created by 
        <a href="https://github.com/BuggyPasta" target="_blank" rel="noopener" class="text-blue-600 dark:text-blue-400">BuggyPasta</a>
        |
        <a href="https://github.com/BuggyPasta/Baikal-Manager" target="_blank" rel="noopener" class="text-blue-600 dark:text-blue-400">GitHub</a>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import modeDarkIcon from '@/assets/icons/mode_dark.svg'
import modeLightIcon from '@/assets/icons/mode_light.svg'

const router = useRouter()
const authStore = useAuthStore()

const isMobileMenuOpen = ref(false)
const isDarkMode = ref(false)
const appName = import.meta.env.VITE_APP_NAME || 'Baikal-Manager'

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userFullName = computed(() => authStore.userFullName)

const themeIcon = computed(() => 
  isDarkMode.value ? modeLightIcon : modeDarkIcon
)

// Initialize theme from environment variable or localStorage
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  const defaultMode = import.meta.env.VITE_DEFAULT_MODE || 'light'
  
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
  } else {
    isDarkMode.value = defaultMode === 'dark'
  }
  
  // Apply theme to document
  document.documentElement.classList.toggle('dark', isDarkMode.value)
})

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

// Add logout function
async function logout() {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style>
.nav-link {
  @apply px-3 py-2 rounded-md text-sm font-medium;
  @apply text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white;
}

.mobile-nav-link {
  @apply block px-3 py-2 rounded-md text-base font-medium;
  @apply text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white;
}

.theme-toggle {
  @apply p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700;
}
</style> 