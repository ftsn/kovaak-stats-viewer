<template>
    <b-container>
        <div class="signup-header pb-2 mt-4 mb-4 border-bottom">
            <h1>Sign-up <small>Create your account</small></h1>
        </div>
        <div class="col-lg-10 offset-lg-1">
            <b-card header-tag="header">
                <h5 slot="header">Sign-up</h5>

                <b-form id="userCreateForm" ref="userCreateForm"
                        @submit.prevent="createUser"
                        @reset="resetCreationForm"
                        novalidate>
                    <b-alert variant="danger" dismissible :show="!!error">
                        {{ error }}
                    </b-alert>

                    <b-form-group label="Enter a username" label-for="username">
                        <b-form-input type="text" v-model="username" id="username" :state="validation_username" placeholder="Username" size="lg" required></b-form-input>
                        <b-form-invalid-feedback :state="validation_username">
                            Enter a username at least 3 characters long.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-form-group label="Enter an email address" label-for="email_addr">
                        <b-form-input type="text" v-model="email_addr" id="email_addr" :state="validation_email_addr" placeholder="Email address" size="lg" required></b-form-input>
                        <b-form-invalid-feedback :state="validation_email_addr">
                            Enter a valid email address.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-form-group label="Enter a password" label-for="password">
                        <b-form-input type="password" v-model="password" :state="validation_password" id=password placeholder="Password" aria-describedby="password-help-block" size="lg" required></b-form-input>
                        <b-form-text id="password-help-block">
                            Your password must be at least 6 characters long
                        </b-form-text>
                        <b-form-invalid-feedback :state="validation_password">
                            Enter a password.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-form-group label="Enter the same password" label-for="same_password">
                        <b-form-input type="password" v-model="same_password" :state="validation_password" id=password placeholder="Same password" size="lg" required></b-form-input>
                        <b-form-invalid-feedback :state="validation_password">
                            You must enter the same password.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-button type="submit" variant="primary" class="mr-2">Create</b-button>
                    <b-button type="reset" variant="outline-danger">Reset</b-button>
                </b-form>
            </b-card>
        </div>
    </b-container>

</template>

<script>
    import axios from "axios";

    export default {
        name: 'sign-up',
        data() {
            return {
                error: null,
                username: null,
                email_addr: null,
                password: null,
                same_password: null,
                reg: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/
            }
        },
        computed: {
            validation_password() {
                if (this.password !== null && this.same_password !== null) {
                    if (this.password !== this.same_password)
                        return false
                    else
                        return this.password.length >= 6;
                }
                return null
            },
            validation_username() {
                if (this.username !== null) {
                    return this.username.length >= 3;

                }
                return null
            },
            validation_email_addr() {
                if (this.email_addr !== null) {
                    return this.reg.test(this.email_addr);

                }
                return null
            },
        },
        methods: {
            createUser() {
                if (this.validation_password === true && this.validation_username === true) {
                    const payload = {
                        'username': this.username,
                        'email_addr': this.email_addr,
                        'password': this.password,
                    };

                    axios.post(process.env.VUE_APP_API_URL + 'users', payload)
                        .then((res) => {
                            this.$router.push('/')
                        })
                        .catch((error) => {
                            this.error = error.response.data.message;
                        });
                }
            },
            resetCreationForm() {
                this.username = null
                this.password = null
                this.email_addr = null
            },
        }
    };
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .signup-header small{
        color: #777;
    }
</style>
