<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <header v-if="isAuthenticated" class="sticky top-0 bg-white dark:bg-gray-900 shadow-md">
      <nav class="container mx-auto px-4 py-2 flex items-center justify-between">
        <!-- Logo and App Name -->
        <div class="flex items-center">
          <img src="@/assets/icons/app_logo.svg" alt="Baikal Manager" class="h-8 w-8 mr-2">
          <span class="text-xl font-semibold">{{ appName }}</span>
        </div>

        <!-- Navigation Links -->
        <div class="hidden md:flex space-x-4">
          <router-link to="/calendar" class="nav-link">Calendar</router-link>
          <router-link to="/contacts" class="nav-link">Contacts</router-link>
          <router-link to="/settings" class="nav-link">Settings</router-link>
        </div>

        <!-- User Info and Theme Toggle -->
        <div class="flex items-center space-x-4">
          <router-link to="/" class="text-sm">{{ userFullName }}</router-link>
          <button @click="toggleTheme" class="theme-toggle">
            <img :src="themeIcon" :alt="isDarkMode ? 'Light Mode' : 'Dark Mode'" class="h-6 w-6">
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
import { ref, computed } from 'vue'
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

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
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