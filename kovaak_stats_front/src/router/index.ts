import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '../store'

Vue.use(VueRouter)

const ifNotAuthenticated = (to, from, next) => {
    if (!store.getters['auth/isAuthenticated']) {
        next()
        return
    }
    next('/')
}

const ifAuthenticated = (to, from, next) => {
    if (store.getters['auth/isAuthenticated']) {
        next()
        return
    }
    next('/login')
}

const Home = () => import('../views/Home.vue')
const Login = () => import('../views/Login.vue')
const Logout = () => import('../views/Logout.vue')
const PageNotFound = () => import('../components/PageNotFound.vue')
const Sidebar = () => import('../components/Sidebar.vue')

const routes = [
    {
        path: '/',
        name: 'home',
        components: {
            default: Home,
            sidebar: Sidebar
        }
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
        beforeEnter: ifNotAuthenticated
    },
    {
        path: '/logout',
        name: 'logout',
        component: Logout,
        beforeEnter: ifAuthenticated
    },
    {
        path: "*",
        component: PageNotFound
    }
]

const router = new VueRouter({
  routes
})

export default router
