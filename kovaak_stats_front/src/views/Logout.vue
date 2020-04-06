<template>
    <b-container>
        <b-alert variant="warning" show>
            Disconnecting the account...
        </b-alert>
    </b-container>
</template>

<script>
    import names from "../store/auth_names"
    import {mapActions} from "vuex";

    export default {
        name: 'logout',
        data() {
            return {
            }
        },
        methods: {
            ...mapActions('auth', {
                'logout': names.AUTH_LOGOUT
            }),
        },
        mounted() {
            this.logout()
                .then(() => {
                    this.$router.replace('/login').catch(err => { console.log(err) })
                })
        },
    };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>