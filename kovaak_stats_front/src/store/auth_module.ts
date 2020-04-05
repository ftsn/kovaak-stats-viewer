import axios from "axios";

const AUTH_REQUEST = 'LOGIN'
const AUTH_LOGOUT = 'LOGOUT'
const AUTH_SUCCESS = 'LOGIN_SUCCESSFUL'
const AUTH_ERROR = 'LOGIN_UNSUCCESSFUL'

const auth = {
    state: {
        access_token: localStorage.getItem('access-token') || '',
        refresh_token: localStorage.getItem('refresh-token') || '',
        status: '',
    },
    mutations: {
        [AUTH_REQUEST]: (state) => {
            state.status = 'loading'
        },
        [AUTH_SUCCESS]: (state, tokens) => {
            state.status = 'success'
            state.access_token = tokens.access_token
            state.refresh_token = tokens.refresh_token

        },
        [AUTH_ERROR]: (state) => {
            state.status = 'error'
        },
        [AUTH_LOGOUT]: (state) => {
            state.status = 'disconnected'
            state.access_token = ''
            state.refresh_token = ''
        },
    },
    getters: {
        isAuthenticated: state => !!state.access_token,
        authStatus: state => state.status,
    },
    actions: {
        [AUTH_REQUEST]: ({commit, dispatch}, user) => {
            return new Promise((resolve, reject) => {
                commit(AUTH_REQUEST)
                axios.post('http://0.0.0.0:9999/api/auth/token-pair', user)
                    .then(resp => {
                        localStorage.setItem('access-token', resp.data.access_token)
                        localStorage.setItem('refresh-token', resp.data.refresh_token)
                        axios.defaults.headers.common['Authorization'] = ' Bearer ' + resp.data.access_token
                        commit(AUTH_SUCCESS, {
                            'access_token': resp.data.access_token,
                            'refresh_token': resp.data.refresh_token
                        })
                        resolve(resp)
                    })
                    .catch(err => {
                        commit(AUTH_ERROR, err)
                        localStorage.removeItem('access-token')
                        localStorage.removeItem('refresh-token')
                        reject(err)
                    })
            })
        },
        [AUTH_LOGOUT]: ({commit, dispatch}) => {
            return new Promise((resolve, reject) => {
                commit(AUTH_LOGOUT)
                localStorage.removeItem('access-token')
                localStorage.removeItem('refresh-token')
                delete axios.defaults.headers.common['Authorization']
                resolve()
            })
        }
    }
}

export default auth