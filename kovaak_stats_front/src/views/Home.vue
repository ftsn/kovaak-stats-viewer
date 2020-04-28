<template>
  <div class="home">
    <b-button v-on:click="toggleNightMode" variant="warning">ta race putain {{ access_token }} {{ isAuthenticated }}</b-button><br />
    <b-button v-on:click="toggleNightMode" variant="warning"> {{ username }} {{ status }} {{api_url}} {{ Date.now() }}</b-button><br />
    <button v-on:click="getUsersPoggers">get stp bg {{night_mode}}</button>
    <b-jumbotron class="full-page">
      <template v-slot:header>BootstrapVue</template>

      <template v-slot:lead>
        This is a simple hero unit, a simple jumbotron-style component for calling extra attention to
        featured content or information.
      </template>

      <hr class="my-4">

      <p>
        It uses utility classes for typography and spacing to space content out within the larger
        container.
      </p>

      <b-button variant="primary" href="#">Do Something</b-button>
      <b-button variant="success" href="#">Do Something Else</b-button>
    </b-jumbotron>
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
import { hasRight, toggleNightMode } from "../utils";
import axios from "axios"
import { mapState, mapGetters } from "vuex"

export default {
  name: 'home',
  components: {
    HelloWorld
  },
  data() {
    return {
      toggleNightMode: toggleNightMode,
      api_url: process.env.VUE_APP_API_URL
    }
  },
  computed: {
    ...mapState('auth', [
            'access_token',
            'username',
            'status'
    ]),
    ...mapState('main', [
            'night_mode',
    ]),
    ...mapGetters('auth', [
            'isAuthenticated'
    ])
  },
  methods: {
    getUsersPoggers: function () {
      console.log(process.env.VUE_APP_API_URL)
      console.log(hasRight('users.create'))
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .full-page {
    min-height: 80vh;
  }
</style>
