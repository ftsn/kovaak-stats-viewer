import axios from "axios";
import jwt_decode from 'jwt-decode';
import names  from './auth_names'

const auth = {
    namespaced: true,
    state: {
        access_token: localStorage.getItem('access-token') || '',
        access_token_exp: null,
        refresh_token: localStorage.getItem('refresh-token') || '',
        refresh_token_exp: null,
        username: null,
        login_via_google: null,
        rights: [],
        status: '',
    },
    mutations: {
        [names.AUTH_REQUEST]: (state) => {
            state.status = 'loading'
        },
        [names.AUTH_SUCCESS]: (state, tokens) => {
            state.status = 'success'
            state.access_token = tokens.access_token.value
            state.access_token_exp = tokens.decoded_jwt.exp
            state.username = tokens.decoded_jwt.sub
            state.rights = tokens.decoded_jwt.rights
            state.refresh_token = tokens.refresh_token.value
            state.refresh_token_exp = tokens.refresh_token.expiration_time
            state.login_via_google = false
        },
        [names.GOOGLE_AUTH_SUCCESS]: (state, res) => {
            state.status = 'success'
            state.access_token = res.access_token
            state.username = res.name
            state.rights = res.rights
            state.login_via_google = true
        },
        [names.AUTH_ERROR]: (state) => {
            state.status = 'error'
        },
        [names.AUTH_LOGOUT]: (state) => {
            state.status = 'disconnected'
            state.access_token = ''
            state.access_token_exp = null
            state.refresh_token = ''
            state.refresh_token_exp = null
            state.username = null
            state.login_via_google = null
        },
    },
    getters: {
        isAuthenticated: state => !!(state.access_token && (state.access_token_exp === null || parseInt(state.access_token_exp) * 1000 > Date.now())),
        authStatus: state => state.status,
    },
    actions: {
        [names.AUTH_REQUEST]: ({commit, dispatch}, user) => {
            return new Promise((resolve, reject) => {
                commit(names.AUTH_REQUEST)
                axios.post(process.env.VUE_APP_API_URL + 'auth/token-pair', user)
                    .then(resp => {
                        localStorage.setItem('access-token', resp.data.access_token.value)
                        localStorage.setItem('refresh-token', resp.data.refresh_token.value)
                        const decoded_jwt = jwt_decode(resp.data.access_token.value)
                        axios.defaults.headers.common['Authorization'] = ' Bearer ' + resp.data.access_token.value
                        commit(names.AUTH_SUCCESS, {
                            'access_token': resp.data.access_token,
                            'decoded_jwt': decoded_jwt,
                            'refresh_token': resp.data.refresh_token
                        })
                        resolve(resp)
                    })
                    .catch(err => {
                        commit(names.AUTH_ERROR, err)
                        localStorage.removeItem('access-token')
                        localStorage.removeItem('refresh-token')
                        reject(err)
                    })
            })
        },
        [names.GOOGLE_AUTH_REQUEST]: ({commit, dispatch}, data) => {
            return new Promise((resolve, reject) => {
                commit(names.AUTH_REQUEST)
                data.vm.$gAuth.signOut()
                    .then(resp => {
                    })
                    .catch(error => {
                        reject(error)
                    });
                data.vm.$gAuth.getAuthCode()
                    .then(resp => {
                        axios.post(process.env.VUE_APP_API_URL + 'auth/google-tokens', {'auth': resp})
                            .then(resp => {
                                localStorage.setItem('access-token', resp.data.access_token)
                                axios.defaults.headers.common['Authorization'] = ' Bearer ' + resp.data.access_token
                                commit(names.GOOGLE_AUTH_SUCCESS, {
                                    'access_token': resp.data.access_token,
                                    'name': resp.data.name,
                                    'rights': resp.data.rights,
                                })
                                resolve(resp)
                            })
                            .catch(error => {
                                reject(error)
                            });
                    })
                    .catch(error => {
                        reject(error)
                    });
            })
        },
        [names.AUTH_LOGOUT]: ({commit, dispatch}) => {
            return new Promise((resolve, reject) => {
                commit(names.AUTH_LOGOUT)
                localStorage.removeItem('access-token')
                localStorage.removeItem('refresh-token')
                delete axios.defaults.headers.common['Authorization']
                resolve()
            })
        }
    }
}

export default auth