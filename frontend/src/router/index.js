import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Views
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import CalendarView from '@/views/CalendarView.vue'
import ContactsView from '@/views/ContactsView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { auth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { guest: true }
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: CalendarView,
    meta: { auth: true }
  },
  {
    path: '/contacts',
    name: 'contacts',
    component: ContactsView,
    meta: { auth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { auth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const isAuthenticated = auth.isAuthenticated || await auth.checkAuth()
  
  if (to.meta.auth && !isAuthenticated) return '/login'
  if (to.meta.guest && isAuthenticated) return '/'
})

export default router 