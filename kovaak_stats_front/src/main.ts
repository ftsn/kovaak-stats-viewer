import './assets/font-awesome/css/all.css'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import BootstrapVue from 'bootstrap-vue'
import axios from 'axios'
import GAuth from 'vue-google-oauth2'
import { initNightMode } from './utils'

Vue.use(BootstrapVue)
import './custom.scss'

const gauthOption = {
  clientId: process.env.VUE_APP_GOOGLE_CLIENT_ID,
  scope: 'profile email',
  prompt: 'consent',
  fetch_basic_profile: true
}
Vue.use(GAuth, gauthOption)

Vue.config.productionTip = false
const token = localStorage.getItem('access-token')
if (token) {
  axios.defaults.headers.common['Authorization'] = 'Bearer ' + token
}
initNightMode()

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
