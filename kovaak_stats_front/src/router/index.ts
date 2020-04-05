import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Logout from '../views/Logout.vue'
import PageNotFound from '../components/PageNotFound.vue'
import Sidebar from '../components/Sidebar.vue'
import store from '../store'

Vue.use(VueRouter)

const ifNotAuthenticated = (to, from, next) => {
    if (!store.getters.isAuthenticated) {
        next()
        return
    }
    next('/')
}

const ifAuthenticated = (to, from, next) => {
    if (store.getters.isAuthenticated) {
        next()
        return
    }
    next('/login')
}

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
