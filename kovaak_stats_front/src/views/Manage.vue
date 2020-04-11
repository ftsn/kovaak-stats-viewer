<template>
    <b-container>
        <div class="manage-header pb-2 mt-4 mb-4 border-bottom">
            <h1>Manage <small>Operate actions on the {{ $route.name }}</small></h1>
        </div>
        <router-view></router-view>
    </b-container>
</template>

<script>
    export default {
        name: 'manage',
    };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .manage-header small{
        color: #777;
    }
</style>