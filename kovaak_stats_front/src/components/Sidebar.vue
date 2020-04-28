<template>
	<div style="margin-bottom: 75px;">
		<b-navbar class="main-navbar" fixed="top" toggleable="md" :type="night_mode ? '' : 'light'" :variant="night_mode ? '' : 'light'">
			<b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
			<b-navbar-brand href="/"><i class="fas fa-chart-line"></i> Kovaak stats viewer</b-navbar-brand>
		  	<b-collapse is-nav id="nav_collapse">
	      	<!-- Right aligned nav items -->
				<b-navbar-nav class="ml-auto">
				  	<b-nav-item-dropdown right>
						<!-- Using button-content slot -->
						<template slot="button-content">
							<b-avatar size="sm"></b-avatar> {{username}}
					  	</template>
						<b-dropdown-item><router-link to="/dashboard">Stats dashboard</router-link></b-dropdown-item>
						<b-dropdown-divider></b-dropdown-divider>
						<b-dropdown-item v-if="hasRight('users.get')"><router-link to="/manage/users"><i class="fas fa-user-cog"></i> Manage users</router-link></b-dropdown-item>
						<b-dropdown-item v-if="hasRight('rights.get')"><router-link to="/manage/rights"><i class="fas fa-balance-scale-left"></i> Manage rights</router-link></b-dropdown-item>
						<b-dropdown-divider></b-dropdown-divider>
						<b-dropdown-item><router-link to="/logout">Logout</router-link></b-dropdown-item>
				  	</b-nav-item-dropdown>
					<b-nav-item right class="p-0" @click="toggleNightMode" v-if="!night_mode"><b-button variant="outline-primary" size="sm"><i class="far fa-moon"></i></b-button></b-nav-item>
					<b-nav-item right class="p-0" @click="toggleNightMode" v-else><b-button variant="outline-secondary" size="sm"><i class="fas fa-sun"></i></b-button></b-nav-item>
			  	</b-navbar-nav>
		  	</b-collapse>
	  	</b-navbar>
  	</div>
</template>

<script>
 import {mapState} from "vuex";
 import { hasRight, toggleNightMode  } from "../utils";

 export default {
     name: 'sidebar',
     data() {
	 	return {
			toggleNightMode: toggleNightMode,
	 		hasRight: hasRight,
	 	};
     },
	 computed: {
     	...mapState('auth', [
     			'username',
				'rights'
		 ]),
		 ...mapState('main', [
		 		'night_mode'
		 ])
	 },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
	.night-mode {
		.main-navbar {
			background-color: rgb(39, 42, 46);
		}

		.main-navbar .navbar-brand {
			color: hsl(27, 80%, 45%); /*rgba(163, 179, 194, 0.9);*/
		}

		.main-navbar a {
			color: hsl(27, 80%, 45%);
		}
		.main-navbar a.dropdown-item:active {
			background-color: rgb(31, 35, 38);
		}
		.main-navbar .navbar-toggler {
			border: 1px solid hsla(27, 80%, 45%, 0.9);
		}
		.main-navbar .navbar-toggler-icon {
			background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 30 30'%3e%3cpath stroke='hsla(27, 80%, 45%, 0.9)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
		}
	}

	.main-navbar a {
		color: rgba(0, 0, 0, 0.5);
	}
	.main-navbar a.dropdown-item:active {
		background-color: #adb5bd;
	}
</style>
