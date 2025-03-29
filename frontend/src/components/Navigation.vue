<template>
  <nav class="bg-white dark:bg-gray-800 shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side -->
        <div class="flex">
          <!-- Logo -->
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-900 dark:text-white">
              Baikal Manager
            </router-link>
          </div>

          <!-- Navigation Links -->
          <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
            <router-link
              to="/"
              class="nav-link"
              :class="{ 'active-link': $route.path === '/' }"
            >
              Home
            </router-link>
            
            <router-link
              to="/calendar"
              class="nav-link"
              :class="{ 'active-link': $route.path === '/calendar' }"
            >
              Calendar
            </router-link>
            
            <router-link
              to="/contacts"
              class="nav-link"
              :class="{ 'active-link': $route.path === '/contacts' }"
            >
              Contacts
            </router-link>
          </div>
        </div>

        <!-- Right side -->
        <div class="flex items-center">
          <!-- Theme Toggle -->
          <button
            @click="toggleTheme"
            class="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white focus:outline-none"
          >
            <svg
              v-if="isDarkMode"
              class="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
              />
            </svg>
            <svg
              v-else
              class="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
              />
            </svg>
          </button>

          <!-- Settings and Logout -->
          <div class="ml-3 relative">
            <div class="flex space-x-4">
              <router-link
                to="/settings"
                class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white p-2"
              >
                <svg
                  class="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </router-link>

              <button
                @click="logout"
                class="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white p-2"
              >
                <svg
                  class="h-6 w-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div class="flex items-center sm:hidden">
          <button
            @click="isOpen = !isOpen"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
          >
            <svg
              class="h-6 w-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                v-if="!isOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div
      v-show="isOpen"
      class="sm:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="pt-2 pb-3 space-y-1">
        <router-link
          to="/"
          class="mobile-nav-link"
          :class="{ 'active-mobile-link': $route.path === '/' }"
          @click="isOpen = false"
        >
          Home
        </router-link>
        
        <router-link
          to="/calendar"
          class="mobile-nav-link"
          :class="{ 'active-mobile-link': $route.path === '/calendar' }"
          @click="isOpen = false"
        >
          Calendar
        </router-link>
        
        <router-link
          to="/contacts"
          class="mobile-nav-link"
          :class="{ 'active-mobile-link': $route.path === '/contacts' }"
          @click="isOpen = false"
        >
          Contacts
        </router-link>
        
        <router-link
          to="/settings"
          class="mobile-nav-link"
          :class="{ 'active-mobile-link': $route.path === '/settings' }"
          @click="isOpen = false"
        >
          Settings
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isOpen = ref(false)
const isDarkMode = ref(false)

// Initialize theme
onMounted(() => {
  isDarkMode.value = document.documentElement.classList.contains('dark')
})

// Toggle theme
function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

// Logout function
async function logout() {
  try {
    const response = await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    
    if (response.ok) {
      router.push('/login')
    }
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
.nav-link {
  @apply inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white border-b-2 border-transparent;
}

.active-link {
  @apply border-blue-500 text-gray-900 dark:text-white;
}

.mobile-nav-link {
  @apply block pl-3 pr-4 py-2 text-base font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700;
}

.active-mobile-link {
  @apply bg-blue-50 dark:bg-blue-900 text-blue-700 dark:text-blue-100;
}
</style> 