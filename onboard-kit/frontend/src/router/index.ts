import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'GuideList',
        component: () => import('@/views/GuideList.vue')
      },
      {
        path: 'guide/new',
        name: 'GuideNew',
        component: () => import('@/views/GuideEditor.vue')
      },
      {
        path: 'guide/:id',
        name: 'GuideEdit',
        component: () => import('@/views/GuideEditor.vue')
      },
      {
        path: 'preview/:id',
        name: 'GuidePreview',
        component: () => import('@/views/GuidePreview.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (!to.meta.requiresAuth && authStore.isAuthenticated && to.name !== 'Dashboard') {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
