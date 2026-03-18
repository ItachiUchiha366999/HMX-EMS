import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import { useSessionStore } from './stores/session.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// One-time boot fetch — populate session store before first route render
const sessionStore = useSessionStore()
sessionStore.fetchSession().then(() => {
  app.mount('#app')
})
