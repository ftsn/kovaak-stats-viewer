<template>
    <b-container>
        <b-alert variant="warning" show>
            Page not found.
            <router-link to="/login" v-if="!this.$store.getters.isAuthenticated" class="alert-link"> Login.</router-link>
            <router-link to="/" v-if="this.$store.getters.isAuthenticated" class="alert-link"> Go back to the main page.</router-link>
        </b-alert>
    </b-container>
</template>

<script>
    export default {
        name: 'PageNotFound',
        data() {
            return {
            }
        },
    };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
