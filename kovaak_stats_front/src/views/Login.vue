<template>
    <div class="container">
	<div class="login-header pb-2 mt-4 mb-4 border-bottom">
	    <h1>Connection <small>Authenticate yourself</small></h1>
	</div>

	<div class="col-sm-10 offset-sm-1 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
	    <b-card header-tag="header">
		<h5 slot="header">Connection</h5>

		<b-form id="loginform" ref="loginform" v-on:submit.prevent="validate" v-bind:class="{ 'was-validated': isValidated }" role="form" novalidate>
		    <b-alert variant="danger" dismissible :show="!!error">
			{{ error }}
		    </b-alert>

		    <b-input-group class="mb-3">
				<b-input-group-text slot="prepend"><i class="fas fa-user"></i></b-input-group-text>
				<b-form-input type="text" v-model="username" placeholder="Username" aria-label="Username" required></b-form-input>
				<div class="invalid-feedback">Your username.</div>
		    </b-input-group>

		    <b-form-group description="BLABLA MES COUILLES LINK POUR RESET LE PASSWORD.">
				<b-input-group>
					<b-input-group-text slot="prepend"><i class="fas fa-lock"></i></b-input-group-text>
			    	<b-form-input type="password" v-model="password" placeholder="Password" aria-label="Password" required></b-form-input>
			    	<div class="invalid-feedback">Your password.</div>
				</b-input-group>
		    </b-form-group>

		    <b-button type="submit" variant="primary" block>Login</b-button>
		</b-form>

	    </b-card>
	</div>

    </div>

</template>

<script>
import names from "../store/auth_names"
import { mapActions } from "vuex"

export default {
     name: 'login',
     data() {
     	return {
     		'username': null,
	     	'password': null,
	     	'isValidated': false,
	     	'error': null,
	 	}
     },
     methods: {
     	...mapActions('auth', {
			'login': names.AUTH_REQUEST,
		}),
		validate() {
			this.error = null;
	     	this.isValidated = true;

	     	let form = this.$refs["loginform"];
	     	const payload = {
		 		'username': this.username,
		 		'password': this.password,
	     	};

	     	if (form.checkValidity() === true) {
				this.login(payload).then(() => {
					this.$router.push('/')
				}).catch((error) => {
					if (error.request.status === 401) {
						this.error = 'Invalid username/password.';
					}
					else {
						this.error = 'There was an error during the authentication.';
					}
				})
			}
	 	}
     }
 };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .login-header small{
     color: #777;
 }
</style>
