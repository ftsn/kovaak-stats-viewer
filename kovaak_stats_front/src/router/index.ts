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
const Signup = () => import('../views/Signup.vue')
const Manage = () => import('../views/Manage.vue')
const ManageUsers = () => import('../views/ManageUsers.vue')
const ManageRights = () => import('../views/ManageRights.vue')
const Dashboard = () => import('../views/Dashboard.vue')
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
        path: '/signup',
        name: 'signup',
        component: Signup,
        beforeEnter: ifNotAuthenticated
    },
    {
        path: '/manage/',
        name: 'manage',
        components: {
            default: Manage,
            sidebar: Sidebar
        },
        beforeEnter: ifAuthenticated,
        children: [
            {
                path: 'users',
                name: 'users',
                components: {
                    default: ManageUsers,
                    sidebar: Sidebar
                }
            },
            {
                path: 'rights',
                name: 'rights',
                components: {
                    default: ManageRights,
                    sidebar: Sidebar
                }
            }
        ]
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        components: {
            default: Dashboard,
            sidebar: Sidebar,
        },
        beforeEnter: ifAuthenticated
    },
    {
        path: "*",
        component: PageNotFound
    }
]

const router = new VueRouter({
    mode: 'history',
    routes
})

export default router
