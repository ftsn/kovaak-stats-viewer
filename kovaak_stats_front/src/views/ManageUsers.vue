<template>
    <div>
        <b-alert :variant="alertVariant" dismissible :show="!!alertMessage">
            {{ alertMessage }}
        </b-alert>

        <b-row>
            <b-col md="6" class="my-1">
                <b-form-group horizontal label="Filter" class="mb-0">
                    <b-input-group>
                        <b-form-input v-model="filter" placeholder="Search" />
                        <b-input-group-append>
                            <b-btn :disabled="!filter" @click="filter = ''">Reset</b-btn>
                        </b-input-group-append>
                    </b-input-group>
                </b-form-group>
            </b-col>
            <b-col md="6" class="my-1">
                <b-form-group horizontal label="Sort" class="mb-0">
                    <b-input-group>
                        <b-form-select v-model="sortBy" :options="sortOptions">
                            <option slot="first" :value="null">-- None --</option>
                        </b-form-select>
                        <b-form-select :disabled="!sortBy" v-model="sortDesc" slot="append">
                            <option :value="false">Asc</option>
                            <option :value="true">Desc</option>
                        </b-form-select>
                    </b-input-group>
                </b-form-group>
            </b-col>
            <b-col md="6" class="my-1">
                <b-form-group horizontal label="Sort order" class="mb-0">
                    <b-input-group>
                        <b-form-select v-model="sortDirection" slot="append">
                            <option value="asc">Asc</option>
                            <option value="desc">Desc</option>
                            <option value="last">Last</option>
                        </b-form-select>
                    </b-input-group>
                </b-form-group>
            </b-col>
            <b-col md="6" class="my-1">
                <b-form-group horizontal label="Per page" class="mb-0">
                    <b-form-select :options="pageOptions" v-model="perPage" />
                </b-form-group>
            </b-col>
        </b-row>
        <br>
        <b-table ref="usersTable"
                 responsive
                 hover
                 borderless
                 striped
                 caption="User list"
                 show-empty
                 no-provider-paging
                 no-provider-sorting
                 no-provider-filtering
                 :busy.sync="busy"
                 :items="getUsers"
                 :fields="fieldsUsers"
                 :current-page="currentPage"
                 :per-page="perPage"
                 :filter="filter"
                 :sort-by.sync="sortBy"
                 :sort-desc.sync="sortDesc"
                 :sort-direction="sortDirection"
                 @filtered="onFiltered">
            <template v-slot:cell(creation_time)="data">{{ timestampToDate(data.item.creation_time) }}</template>
            <template v-slot:cell(modification_time)="data">{{ timestampToDate(data.item.modification_time) }}</template>
            <template v-slot:cell(rights)="data">
                <div class="rights_list_group">
                    <b-list-group>
                        <b-list-group-item v-for="right in data.item.rights" v-bind:key="right">{{right}}</b-list-group-item>
                    </b-list-group>
                </div>
            </template>
            <template v-slot:cell(actions)="row">
                <b-button variant="outline-primary" size="sm" class="m-2" @click.stop="showModif(row)">
                    <i class="fas fa-pen"></i>
                </b-button>

                <b-button variant="outline-danger" class="m-2" size="sm" :id="'userDeletePopover-' + row.index" click.stop=''>
                    <i class="fas fa-trash-alt"></i>
                </b-button>
                <b-popover :target="'userDeletePopover-' + row.index"
                           triggers="click"
                           placement="auto">
                    <template v-slot:title>
                        <b-btn @click="onDeleteUserPopoverClose('userDeletePopover-' + row.index)" class="close" aria-label="Close">
                            <span class="d-inline-block" aria-hidden="true">&times;</span>
                        </b-btn>
                        Delete {{row.item.name}}
                    </template>
                    <div>
                        <b-alert show variant="warning" class="small">
                            <strong>This action can't be reverted</strong><br>
                            Don't check the box unless you are absolutely sure you want to delete this user.
                        </b-alert>
                        <b-form-checkbox @change="deleteUser(row.item.name, 'userDeletePopover-' + row.index)"
                                         v-model="deleteState"
                                         class="mb-2">
                            Delete the user
                        </b-form-checkbox>
                    </div>
                </b-popover>
            </template>

            <template v-slot:row-details="row">
                <b-form id="userModifyForm"
                        ref="userModifyForm"
                        @submit.prevent="modifyUser(row)"
                        novalidate>
                    <b-form-group label="Enter a username" label-for="username">
                        <b-form-input type="text" v-model="modifData[row.item.name].username" id="username" :state="validation_username(row)" placeholder="Username" size="lg" required></b-form-input>
                        <b-form-invalid-feedback :state="validation_username(row)">
                            Enter a username at least 3 characters long.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-form-group label="Enter an email address" label-for="email_addr">
                        <b-form-input type="text" v-model="modifData[row.item.name].email_addr" id="email_addr" :state="validation_email_addr(row)" placeholder="Email address" size="lg" required></b-form-input>
                        <b-form-invalid-feedback :state="validation_email_addr(row)">
                            Enter a valid email address.
                        </b-form-invalid-feedback>
                    </b-form-group>

                    <b-form-group label="Select and unselect the rights you want" label-for="rights">
                        <b-form-select v-model="modifData[row.item.name].rights" id="rights" :options="rightsOptions(rightlist, row.item.rights)" :value="null" size="lg" multiple :select-size="10">
                            <template slot="first">
                                <!-- this slot appears above the options from 'options' prop -->
                                <option :value="null" disabled>-- Rights of the user --</option>
                            </template>
                        </b-form-select>
                    </b-form-group>

                    <b-button :disabled="!validation_username(row) || !validation_email_addr(row)"
                              type="submit" variant="primary" class="mr-2">Modify</b-button>
                    <b-button @click="resetModifForm(row)" variant="outline-danger">Reset</b-button>
                </b-form>
            </template>
        </b-table>

        <b-row>
            <b-col md="6" class="my-1">
                <b-pagination :total-rows="totalRows" :per-page="perPage" v-model="currentPage" class="my-0" />
            </b-col>
        </b-row>

    </div>
</template>

<script>
    import axios from "axios";
    import { hasRight, timestampToDate, isIn } from "../utils";

    export default {
        name: "ManageUsers",
        data() {
            return {
                hasRight: hasRight,
                timestampToDate: timestampToDate,
                alertVariant: 'primary',
                alertMessage: null,
                busy: false,
                currentPage: 1,
                perPage: 5,
                totalRows: 1,
                pageOptions: [ 5, 10, 15 ],
                sortBy: null,
                sortDesc: false,
                sortDirection: 'asc',
                filter: null,
                fieldsUsers: [
                    { key: 'name', label: 'Username', sortable: true, sortDirection: 'desc' },
                    { key: 'email_addr', label: 'Email address', sortable: true, sortDirection: 'desc' },
                    { key: 'creation_time', label: 'Creation date', sortable: true },
                    { key: 'modification_time', label: 'Modification date', sortable: true },
                    { key: 'rights', label: 'Rights' },
                    { key: 'actions', label: 'Actions', 'class': 'text-center'},
                ],
                deleteState: false,
                modifData: {},
                reg: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$/,
                rightlist: [],
            }
        },
        created() {
            axios.get(process.env.VUE_APP_API_URL + 'rights')
                .then(resp => {
                    this.rightlist = resp.data
                    this.rightlist = this.toRightList(resp.data)
                })
                .catch(error => {
                    this.alertVariant = 'danger';
                    this.alertMessage = error.response ? error.response.data.message : error;
                })
        },
        computed: {
            sortOptions () {
                return this.fieldsUsers.filter(f => f.sortable).map(f => { return { text: f.label, value: f.key } })
            },
        },
        methods: {
            rightsOptions (rightsArray, usersRights) {
                return rightsArray.map(f => { return { text: f, value: f, selected: isIn(f, usersRights) } })
            },
            toRightList (objList) {
                return objList.map(f => { return f.name })
            },
            validation_username(row) {
                if (this.modifData[row.item.name].username !== null) {
                    return this.modifData[row.item.name].username.length >= 3;
                }
                return null
            },
            validation_email_addr(row) {
                if (this.modifData[row.item.name].email_addr !== null) {
                    return this.reg.test(this.modifData[row.item.name].email_addr);
                }
                return null
            },
            resetModifForm(row) {
                this.modifData[row.item.name].username = row.item.name
                this.modifData[row.item.name].email_addr = row.item.email_addr
                this.modifData[row.item.name].rights = row.item.rights
            },
            showModif(row) {
                row.toggleDetails();
                if (!(row.item.name in this.modifData)) {
                    this.$set(this.modifData, row.item.name, {
                        'username': row.item.name,
                        'email_addr': row.item.email_addr,
                        'rights': row.item.rights
                    });
                }

            },
            onFiltered (filteredItems) {
                // Trigger pagination to update the number of buttons/pages due to filtering
                this.totalRows = filteredItems.length
                this.currentPage = 1
            },
            onDeleteUserPopoverClose (triggerId) {
                this.$root.$emit('bv::hide::popover', triggerId);
            },
            getUsers(ctx, callback) {
                this.busy = true
                axios.get(process.env.VUE_APP_API_URL + 'users')
                    .then(resp => {
                        this.totalRows = resp.data.length
                        this.busy = false
                        callback(resp.data)
                    })
                    .catch(error => {
                        this.alertVariant = 'danger';
                        this.alertMessage = error.response ? error.response.data.message : error;
                        this.busy = false
                        callback([])
                    })
                return null
            },
            deleteUser(userId, triggerId) {
                axios.delete(process.env.VUE_APP_API_URL + 'users/' + userId)
                    .then((res) => {
                        this.alertVariant = 'success';
                        this.alertMessage = userId + ' has been successfully deleted.';
                        this.deleteState = false;
                        this.onDeleteUserPopoverClose(triggerId);
                        this.$refs.usersTable.refresh();
                    })
                    .catch((error) => {
                        this.deleteState = false;
                        this.alertVariant = 'danger';
                        this.alertMessage = error.response ? error.response.data.message : error;
                        this.onDeleteUserPopoverClose(triggerId);
                    });
            },
            modifyUser(row) {
                if (this.validation_username(row) && this.validation_email_addr(row)) {
                    const changes = [
                        { "op": "replace", "path": "/name", "value": this.modifData[row.item.name].username },
                        { "op": "replace", "path": "/email_addr", "value": this.modifData[row.item.name].email_addr },
                        { "op": "replace", "path": "/rights", "value": this.modifData[row.item.name].rights}
                    ]
                    const payload = {
                        'changes': JSON.stringify(changes)
                    }
                    axios.patch(process.env.VUE_APP_API_URL + 'users/' + row.item.name, payload)
                        .then((res) => {
                            this.alertVariant = 'success';
                            this.alertMessage = row.item.name + ' has been successfully modified.';
                            this.$refs.usersTable.refresh();
                        })
                        .catch((error) => {
                            this.alertVariant = 'danger';
                            this.alertMessage = error.response ? error.response.data.message : error;
                        });
                }
            }

        }
    }
</script>

<style scoped>
    .rights_list_group {
        overflow: auto;
        max-height: 150px;
    }
</style>