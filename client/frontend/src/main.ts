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

import UserData from './components/Scripts/UserData';
const userData = UserData.userDataString;

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

    if (userData) {
        const user = JSON.parse(userData);
        const isLoggedIn = !!user.isLoggedIn; // Ensure this is a boolean

        if (!isLoggedIn && to.name !== 'login') {
            next({ name: 'login' }); // Redirect to login if not logged in
        } else if (isLoggedIn && to.name === 'login') {
            next({ name: 'dashboard' }); // Redirect to dashboard if already logged in
        } else {
            next(); // Proceed as normal
        }
    } else {
        if (to.name !== 'login') {
            next({ name: 'login' }); // If no userData, redirect to login
        } else {
            next(); // Allow access to login
        }
    }
});

// Use the router and Vuetify plugin
app.use(router).use(vuetify).mount('#app') // Mount Vue app to the DOM
