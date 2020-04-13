<template>
    <b-container>
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
                 hover
                 bordered
                 striped
                 caption="User list"
                 show-empty
                 stacked="md"
                 no-provider-paging
                 no-provider-sorting
                 no-provider-filtering
                 :busy.sync="busy"
                 :items="getRights"
                 :fields="fieldsRights"
                 :current-page="currentPage"
                 :per-page="perPage"
                 :filter="filter"
                 :sort-by.sync="sortBy"
                 :sort-desc.sync="sortDesc"
                 :sort-direction="sortDirection"
                 @filtered="onFiltered">
            <template v-slot:cell(creation_time)="data">{{ timestampToDate(data.item.creation_time) }}</template>
            <template v-slot:cell(modification_time)="data">{{ timestampToDate(data.item.modification_time) }}</template>
            <template v-slot:cell(actions)="row">
                <b-button variant="outline-danger" size="sm" :id="'rightDeletePopover-' + row.index" click.stop=''>
                    <i class="fas fa-trash-alt"></i>
                </b-button>
                <b-popover :target="'rightDeletePopover-' + row.index"
                           triggers="click"
                           placement="auto">
                    <template v-slot:title>
                        <b-btn @click="onDeleteRightPopoverClose('rightDeletePopover-' + row.index)" class="close" aria-label="Close">
                            <span class="d-inline-block" aria-hidden="true">&times;</span>
                        </b-btn>
                        Delete {{row.item.name}}
                    </template>
                    <div>
                        <b-alert show variant="warning" class="small">
                            <strong>This action can't be reverted</strong><br>
                            Don't check the box unless you are absolutely sure you want to delete this right.
                        </b-alert>
                        <b-form-checkbox @change="deleteRight(row.item.name, 'rightDeletePopover-' + row.index)"
                                         v-model="deleteState"
                                         class="mb-2">
                            Delete the right
                        </b-form-checkbox>
                    </div>
                </b-popover>
            </template>
        </b-table>

        <b-row>
            <b-col md="6" class="my-1">
                <b-pagination :total-rows="totalRows" :per-page="perPage" v-model="currentPage" class="my-0" />
            </b-col>
        </b-row>

    </b-container>
</template>

<script>
    import axios from "axios";
    import { hasRight, timestampToDate, isIn } from "../utils";

    export default {
        name: "ManageRights",
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
                fieldsRights: [
                    { key: 'name', label: 'Name', sortable: true, sortDirection: 'desc' },
                    { key: 'creation_time', label: 'Creation date', sortable: true, 'class': 'text-center' },
                    { key: 'modification_time', label: 'Modification date', sortable: true, 'class': 'text-center' },
                    { key: 'actions', label: 'Actions', 'class': 'text-center'},
                ],
                deleteState: false,
            }
        },
        computed: {
            sortOptions () {
                return this.fieldsRights.filter(f => f.sortable).map(f => { return { text: f.label, value: f.key } })
            },
        },
        methods: {
            onFiltered (filteredItems) {
                // Trigger pagination to update the number of buttons/pages due to filtering
                this.totalRows = filteredItems.length
                this.currentPage = 1
            },
            onDeleteRightPopoverClose (triggerId) {
                this.$root.$emit('bv::hide::popover', triggerId);
            },
            getRights(ctx, callback) {
                this.busy = true
                axios.get(process.env.VUE_APP_API_URL + 'rights')
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
            deleteRight(rightId, triggerId) {
                axios.delete(process.env.VUE_APP_API_URL + 'rights/' + rightId)
                    .then((res) => {
                        this.alertVariant = 'success';
                        this.alertMessage = rightId + ' has been successfully deleted.';
                        this.deleteState = false;
                        this.onDeleteRightPopoverClose(triggerId);
                        this.$refs.usersTable.refresh();
                    })
                    .catch((error) => {
                        this.deleteState = false;
                        this.alertVariant = 'danger';
                        this.alertMessage = error.response ? error.response.data.message : error;
                        this.onDeleteRightPopoverClose(triggerId);
                    });
            },
        }
    }
</script>

<style scoped>

</style>