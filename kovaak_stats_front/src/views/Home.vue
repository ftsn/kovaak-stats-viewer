<template>
  <div>
    <div class="bg-filler"></div>
  <b-row align-h="center" class="home m-0">
    <b-col cols="4" offset="8" class="text-right pt-2">
      <b-button @click="toggleNightMode" v-if="!night_mode" variant="outline-secondary" size="sm"><i class="far fa-moon"></i></b-button>
      <b-button @click="toggleNightMode" v-else variant="outline-secondary" size="sm"><i class="fas fa-sun"></i></b-button>
    </b-col>
    <b-col>
    <b-jumbotron class="full-page mb-0" fluid>
      <template v-slot:header>Kovaak stats viewer</template>

      <template v-slot:lead>
        Register an account, upload your stats files and analyze your gameplay
      </template>

      <hr class="my-4">

      <h5 class="mb-4">
        It only takes a few clicks to get ready
      </h5>
      <div class="text-center mb-4">
        <router-link to="/login"><b-button variant="outline-dark" class="mr-2 mb-2" size="lg">Sign-in</b-button></router-link>
        <router-link to="/signup"><b-button variant="primary" class="mr-2 mb-2" size="lg">Sign-up</b-button></router-link>
      </div>

      <h5 class="mb-4">
        You can also use the Windows 10 compatible GUI to upload your stats more easily after having created your account
      </h5>
      <div class="text-center mb-4">
        <b-link href="https://github.com/ftsn/kovaak-stats-viewer/blob/master/gui/main.exe">
          <b-button variant="outline-primary" class="mb-2" size="lg">Download it here</b-button>
        </b-link>
      </div>
    </b-jumbotron>
    </b-col>
  </b-row>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
import {mapState} from "vuex";
import { toggleNightMode } from "../utils";

export default {
  name: 'home',
  components: {
    HelloWorld
  },
  data() {
    return {
      toggleNightMode: toggleNightMode,
    }
  },
  computed: {
    ...mapState('main', [
      'night_mode'
    ])
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .home {
    height: 100vh;
  }
  .bg-filler {
    height: 100%;
    width: 100%;
    position: fixed;
    background-image: url("../assets/fps_aim_trainer_logo.png");
    background-size: cover;
    opacity: 0.25;
  }
  .night-mode {
    .bg-filler {
      opacity: 0.09;
    }
  }
  .full-page {
    background-color: transparent;
  }
</style>
