import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Message from '../views/Message.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: { title: 'Login' },
    },
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
      meta: { title: 'Dashboard' },
    },
    {
      path: '/message',
      name: 'message',
      component: Message,
      meta: { title: 'Messages' },
      // Temporarily remove the `beforeEnter` guard
    },
  ],
})

export default router
