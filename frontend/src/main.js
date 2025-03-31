import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Import our CSS
import './assets/main.css'

// Configure axios
axios.defaults.withCredentials = true
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app') 