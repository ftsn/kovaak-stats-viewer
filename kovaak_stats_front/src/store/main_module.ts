import names from './main_names'

const main = {
    namespaced: true,
    state: {
        night_mode: true,
    },
    mutations: {
        [names.TOGGLE_NIGHT_MODE]: (state) => {
            state.night_mode = !state.night_mode
        },
    },
    getters: {},
    actions: {}
}

export default main