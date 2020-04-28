<template>
    <div class="wrapper">
        <!--<div class="menu">
            <div class="menu-wrapper">
                <div class="menu-header">
                    <h2>Pages</h2>
                </div>
                <b-nav vertical class="w-100 menu-content">
                    <b-nav-item active><i class="fas fa-user-cog"></i> Users</b-nav-item>
                    <b-nav-item><i class="fas fa-balance-scale-left"></i> rights</b-nav-item>
                </b-nav>
            </div>
        </div>-->
        <div class="content">
            <b-container fluid>
                <div class="manage-header pb-2 mt-4 mb-4 border-bottom">
                    <h1>Manage <small>Operate actions on the {{ $route.name }}</small></h1>
                </div>
                <router-view></router-view>
            </b-container>
        </div>
    </div>
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
    }/*
    .wrapper {
        position: relative;
        top: 0;
        height: 100vh;
    }
    .menu {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        width: 260px;
        background-size: cover;
        background-position: 50%;
        color: #6a6c70;
    }
    .menu h2 {
        color: #adb5bd;
        font-size: 1.3rem;
        text-transform: uppercase;
        font-weight: 400;
    }
    .menu .menu-wrapper {
        background-color: rgba(45, 48, 53, 1);
        height: 100%;
        width: 100%;
        position: relative;
    }
    .menu .menu-header {
        padding: 10px 5px;
        margin: 0px 20px;
        border-bottom: 1px solid hsla(0, 0%, 100%, .3);
        text-align: center;
    }
    .menu .menu-content {
        margin-top: 20px;
    }
    .menu .menu-wrapper .nav-link {
        color: #6a6c70;
        margin: 5px 15px;
        padding: 10px 15px;
        font-size: 15px;
        text-transform: uppercase;
    }
    .menu .menu-wrapper .nav-link:not(.active):hover {
        background-color: rgba(52, 55, 61, 1);
        border-left: 2px solid hsl(27, 80%, 45%);
        padding-left: 13px;
    }
    .menu .menu-wrapper .nav-link:hover i {
        color: hsl(27, 80%, 45%);
    }
    .menu .menu-wrapper i {
        width: 40px;
        font-size: 20px;
        margin-right: 15px;
        border-right: 1px solid #454649;
    }
    .menu .menu-wrapper .active {
        border-left: 2px solid hsl(27, 80%, 45%);
        background-color: rgba(52, 55, 61, 1);
    }
    .menu .menu-wrapper .active i {
        color: hsl(27, 80%, 45%);
    }
    .content {
        width: calc(100% - 260px);
        float: right;
    }*/
</style>