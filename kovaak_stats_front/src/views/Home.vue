<template>
  <div class="home">
    <b-button v-on:click="toggleDarkMode" variant="warning">ta race putain {{ access_token }} {{ isAuthenticated }}</b-button><br />
    <b-button v-on:click="toggleDarkMode" variant="warning"> {{ username }} {{ status }}</b-button><br />
    <button v-on:click="getUsersPoggers">get stp bg</button>
    <div class="container">
      <b-alert show dismissible variant="primary">Default Alert</b-alert>
      <b-alert show dismissible variant="secondary">Default Alert</b-alert>
      <b-alert show dismissible variant="success">Default Alert</b-alert>
      <b-alert show dismissible variant="info">Default Alert</b-alert>
      <b-alert show dismissible variant="warning">Default Alert</b-alert>
      <b-alert show dismissible variant="danger">Default Alert</b-alert>
      <b-alert show dismissible variant="light">Default Alert</b-alert>
      <b-alert show dismissible variant="dark">Default Alert</b-alert>
    </div>
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
import axios from "axios"
import { mapState, mapGetters } from "vuex"

export default {
  name: 'home',
  components: {
    HelloWorld
  },
  computed: {
    ...mapState('auth', [
            'access_token',
            'username',
            'status'
    ]),
    ...mapGetters('auth', [
            'isAuthenticated'
    ])
  },
  methods: {
    toggleDarkMode: function () {
      let html_div = document.getElementsByTagName('html')[0];
      html_div.classList.toggle("night-mode");
    },
    getUsersPoggers: function () {
      axios.get('http://0.0.0.0:9999/api/users')
              .then(resp => {
                console.log(resp.data)
              })
              .catch(err => {
                console.log("échec cuisant sa mere")
              })
    }
  }
}
</script>
