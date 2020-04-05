<template>
	<div>
		<b-navbar toggleable="md" type="light" variant="light">
			<b-navbar-toggle target="nav_collapse"></b-navbar-toggle>
			<b-navbar-brand><i class="fas fa-chart-line"></i> Kovaak stats viewer</b-navbar-brand>
		  	<b-collapse is-nav id="nav_collapse">
	      	<!-- Right aligned nav items -->
				<b-navbar-nav class="ml-auto">
				  	<b-nav-item-dropdown right>
						<!-- Using button-content slot -->
						<template slot="button-content">
						  	<i class="fas fa-user"></i> USERNAME
					  	</template>
						<b-dropdown-item><router-link to="/logout">Logout</router-link></b-dropdown-item>
				  	</b-nav-item-dropdown>
			  	</b-navbar-nav>
		  	</b-collapse>
	  	</b-navbar>
  	</div>
</template>

<script>
 export default {
     name: 'sidebar',
     data() {
	 	return {
	 	};
     },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
