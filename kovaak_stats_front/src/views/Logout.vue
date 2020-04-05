<template>
    <b-container>
        <b-alert variant="warning" show>
            Disconnecting the account...
        </b-alert>
    </b-container>
</template>

<script>
    export default {
        name: 'logout',
        data() {
            return {
            }
        },
        mounted() {
            this.$store.dispatch('LOGOUT')
                .then(() => {
                    this.$router.replace('/login').catch(err => { console.log(err) })
                })
        },
    };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>