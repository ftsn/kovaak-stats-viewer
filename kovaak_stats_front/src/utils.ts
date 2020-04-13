import store from './store'
import names from './store/main_names'
import moment from 'moment'

const state = store.state as any

function isIn(arg, arr) {
    return arr.indexOf(arg) > -1
}

function hasRight(right) {
    return isIn(right, state.auth.rights)
}

function applyNightMode() {
    let html_div = document.getElementsByTagName('html')[0];
    html_div.classList.toggle("night-mode");
}

function toggleNightMode () {
    applyNightMode()
    store.commit('main/' + names.TOGGLE_NIGHT_MODE)
}

function initNightMode () {
    if (state.main.night_mode === true)
        applyNightMode()
}

function timestampToDate (value) {
    return moment(value * 1000).format('DD/MM/YYYY HH:mm:ss')
}

export { isIn, hasRight, applyNightMode, initNightMode, toggleNightMode, timestampToDate }