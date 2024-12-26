import './assets/main.css'
import './assets/tailwind.css'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

// Create Vue app instance
const app = createApp(App)

// Vuetify setup
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',  // Use Material Design Icons (mdi)
    aliases,
    sets: {
      mdi,
    },
  },
})

router.beforeEach((to, from, next) => {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
  
    if (!isLoggedIn && to.name !== 'login') {
      next({ name: 'login' });
    } else {
      next();
    }
  });
  

// Use the router and Vuetify plugin
app
  .use(router)  // Use the router instance
  .use(vuetify) // Use Vuetify
  .mount('#app') // Mount Vue app to the DOM
