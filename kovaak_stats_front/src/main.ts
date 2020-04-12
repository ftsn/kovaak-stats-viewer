import './assets/font-awesome/css/all.css'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import BootstrapVue from 'bootstrap-vue'
import axios from 'axios'
import { initNightMode } from './utils'

Vue.use(BootstrapVue)
import './custom.scss'

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
