<template>
    <div class="container">
	<div class="login-header pb-2 mt-4 mb-4 border-bottom">
	    <h1>Connection <small>Authenticate yourself</small></h1>
	</div>

	<div class="col-sm-10 offset-sm-1 col-md-8 offset-md-2 col-lg-6 offset-lg-3">
	    <b-card header-tag="header">
			<h5 slot="header">{{action}}</h5>
			<b-form v-if="!step"
					id="loginform" ref="loginform"
					@submit.prevent="validate"
					v-bind:class="{ 'was-validated': isValidated }" role="form" novalidate>
				<b-alert :variant="alertVariant" dismissible :show="!!alertMessage">
					{{ alertMessage }}
				</b-alert>

				<div class="mb-2">
					<b-link @click="authGoogle">Click here to login via google</b-link>
				</div>
				<b-input-group class="mb-3">
					<b-input-group-text slot="prepend"><i class="fas fa-user"></i></b-input-group-text>
					<b-form-input type="text" v-model="username" placeholder="Username" aria-label="Username"
								  required></b-form-input>
					<div class="invalid-feedback">Your username.</div>
				</b-input-group>

				<b-input-group>
					<b-input-group-text slot="prepend"><i class="fas fa-lock"></i></b-input-group-text>
					<b-form-input type="password" v-model="password" placeholder="Password" aria-label="Password"
								  required></b-form-input>
					<div class="invalid-feedback">Your password.</div>
				</b-input-group>

				<div class="mt-2 mb-3">
					<b-link @click="requestChangePassword">Click here to change your password</b-link>
				</div>

				<b-button type="submit" variant="primary" block>Login</b-button>
			</b-form>

			<b-form v-else-if="step==='username'"
					id="codeform" ref="codeform"
					@submit.prevent="send_code"
					novalidate>
				<b-alert :variant="alertVariant" dismissible :show="!!alertMessage">
					{{ alertMessage }}
				</b-alert>

				<b-input-group class="mb-3">
					<b-input-group-text slot="prepend"><i class="fas fa-user"></i></b-input-group-text>
					<b-form-input type="text" v-model="username_change_password" id="username_change_password"
								  :state="validation_username_change_password"
								  placeholder="Enter your username" required></b-form-input>
					<b-form-invalid-feedback :state="validation_username_change_password">
						Enter the username associated with your account.
					</b-form-invalid-feedback>
				</b-input-group>

				<b-button type="submit" variant="primary" class="mr-2"
						  :disabled="!validation_username_change_password" block>
					Next step (2/2)
				</b-button>
			</b-form>

			<b-form v-else-if="step==='change_password'"
					id="changepasswordform" ref="changepasswordform"
					@submit.prevent="validate_change_password"
					novalidate>
				<b-alert :variant="alertVariant" dismissible :show="!!alertMessage">
					{{ alertMessage }}
				</b-alert>
				<b-input-group class="mb-3">
					<b-input-group-text slot="prepend"><i class="fas fa-shield-alt"></i></b-input-group-text>
					<b-form-input type="text" v-model="code" placeholder="The code sent by email"
								  aria-label="code" :state="validation_code"
								  required></b-form-input>
					<b-form-invalid-feedback :state="validation_code">
						Enter the 6 characters code.
					</b-form-invalid-feedback>
				</b-input-group>
				<b-input-group class="mb-3">
					<b-input-group-text slot="prepend"><i class="fas fa-key"></i></b-input-group-text>
					<b-form-input type="password" v-model="new_password" :state="validation_new_password"
								  placeholder="Your new password" required></b-form-input>
					<b-form-invalid-feedback :state="validation_new_password">
						Enter a password.
					</b-form-invalid-feedback>
				</b-input-group>
				<b-input-group class="mb-3">
					<b-input-group-text slot="prepend"><i class="fas fa-key"></i></b-input-group-text>
					<b-form-input type="password" v-model="same_new_password" :state="validation_new_password"
								  placeholder="Confirm your  new password" required></b-form-input>
					<b-form-invalid-feedback :state="validation_new_password">
						Confirm the password.
					</b-form-invalid-feedback>
				</b-input-group>
				<b-button type="submit" variant="primary" :disabled="!validation_new_password || !validation_code"
						  class="mr-2" block>
					Change password
				</b-button>
			</b-form>

	    </b-card>
	</div>

    </div>

</template>

<script>
import names from "../store/auth_names"
import {mapActions, mapState} from "vuex"
import axios from "axios";

export default {
	name: 'login',
	data() {
		return {
			action: 'Connection',
			username: null,
	     	password: null,
	     	isValidated: false,
			alertVariant: 'primary',
			alertMessage: null,
			step: null,
			codeIsValidated: false,
			code: null,
			new_password: null,
			same_new_password: null,
			username_change_password: null,
			isValidatedChange: false,
		}
	},
	computed: {
		validation_new_password() {
			if (this.new_password !== null && this.same_new_password !== null) {
				if (this.new_password !== this.same_new_password)
					return false
				else
					return this.new_password.length >= 6;
			}
			return null
		},
		validation_username_change_password() {
			if (this.username_change_password !== null) {
				return this.username_change_password.length >= 3;

			}
			return null
		},
		validation_code() {
			if (this.code !== null)
				return this.code.length === 6;
			return null
		},
	},
	methods: {
		...mapActions('auth', {
			'login': names.AUTH_REQUEST,
			'google_login': names.GOOGLE_AUTH_REQUEST
		}),
		authGoogle() {
			this.google_login({vm: this})
					.then(() => {
						this.$router.push('/dashboard').catch((err) => {});
					})
					.catch((error) => {
						this.alertVariant = 'danger';
						this.alertMessage = 'There was an error during the authentication.'
					})
		},
		validate() {
			this.error = null;
	     	this.isValidated = true;

	     	let form = this.$refs["loginform"];
	     	const payload = {
		 		'username': this.username,
		 		'password': this.password,
	     	};

	     	if (form.checkValidity() === true) {
	     		this.login(payload)
						.then(() => {
							this.$router.push('/dashboard').catch((err) => {});
						})
						.catch((error) => {
							if (error.request.status === 401) {
								this.alertVariant = 'danger';
								this.alertMessage = error.response ? error.response.data.message : error;
							}
							else {
								this.alertVariant = 'danger';
								this.alertMessage = 'There was an error during the authentication.';
							}
						})
	     	}
		},
		requestChangePassword() {
			this.alertMessage = ''
			this.action = 'Change password'
			this.step = 'username'
		},
		send_code() {
			axios.get(process.env.VUE_APP_API_URL + 'users/' + this.username_change_password + '/recover')
					.then(resp => {
						this.alertVariant = 'info';
						this.alertMessage = 'A code has been sent to your by email';
						this.step = 'change_password'
					})
					.catch(error => {
						this.alertVariant = 'danger';
						this.alertMessage = error.response ? error.response.data.message : error;
					});
		},
		validate_change_password() {
			const payload = {
				'recovery_code': this.code,
				'new_password': this.new_password,
			};

			axios.post(process.env.VUE_APP_API_URL + 'users/' + this.username_change_password + '/recover', payload)
					.then((res) => {
						this.username_change_password = null
						this.code = null
						this.new_password = null
						this.same_new_password = null
						this.step = null
						this.alertVariant = 'success'
						this.alertMessage = 'Your password has been successfully changed'

					})
					.catch((error) => {
						this.alertVariant = 'danger'
						this.alertMessage = error.response.data.message;
					});
		},
	}
 };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
 .login-header small{
     color: #777;
 }
</style>
