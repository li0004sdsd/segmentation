import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/register', component: () => import('../views/RegisterView.vue'), meta: { public: true } },
  { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/profiles', component: () => import('../views/ProfilesView.vue') },
  { path: '/profiles/:id', component: () => import('../views/ProfileDetailView.vue') },
  { path: '/tags', component: () => import('../views/TagsView.vue') },
  { path: '/rules', component: () => import('../views/RulesView.vue') },
  { path: '/rules/:id', component: () => import('../views/RuleDetailView.vue') },
  { path: '/results', component: () => import('../views/ResultsView.vue') },
  { path: '/results/:id', component: () => import('../views/ResultDetailView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }
  if (to.meta.public && auth.isAuthenticated) {
    return '/dashboard'
  }
})

export default router
