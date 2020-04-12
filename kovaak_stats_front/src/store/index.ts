import Vue from 'vue'
import Vuex from 'vuex'
import auth from "@/store/auth_module"
import main from "@/store/main_module"
import createPersistedState from "vuex-persistedstate"

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    auth,
    main,
  },
  plugins: [createPersistedState()]
})
