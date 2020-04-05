<template>
  <div class="home">
    <button v-on:click="toto">ta race putain {{ lolbite }}</button><br />
    <button v-on:click="getUsersPoggers">get stp bg</button>
    <div class="container">
      <b-alert show dismissible variant="primary" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="secondary" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="success" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="info" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="warning" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="danger" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="light" v-on:click="toto">Default Alert</b-alert>
      <b-alert show dismissible variant="dark" v-on:click="toto">Default Alert</b-alert>
    </div>
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
import axios from "axios"

export default {
  name: 'home',
  components: {
    HelloWorld
  },
  computed: {
    lolbite() {
      return this.$store.state.auth.access_token
    }
  },
  methods: {
    toto: function () {
      let html_div = document.getElementsByTagName('html')[0];
      html_div.classList.toggle("night-mode");
      console.log(html_div)
    },
    getUsersPoggers: function () {
      console.log(this.$store)
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
