<template>
    <b-container fluid>
        <div class="manage-header pb-2 mt-4 mb-4 border-bottom">
            <h1>Dashboard <small>Analyze your kovaak stats</small></h1>
        </div>
        <b-alert :variant="alertVariant" dismissible :show="!!alertMessage">
            {{ alertMessage }}
        </b-alert>
        <b-row align-h="center" style="height: 800px;" class="mb-3">
            <b-col cols="11">
                <canvas id="chart"></canvas>
            </b-col>
        </b-row>
        <b-row align-h="between">
            <b-col cols="12" md="6">
                <b-card header-tag="header" class="mb-3">
                    <template v-slot:header>
                        <h6 class="mb-0">Filter by date</h6>
                    </template>
                    <b-form novalidate>
                        <b-form-group label="Enter a start date" label-for="datepicker-start">
                            <b-form-input type="text" v-model="filter_start_date" id="datepicker-start"
                                          :state="validation_start_date()" placeholder="Start date" required></b-form-input>
                            <b-form-invalid-feedback :state="validation_start_date()">
                                Enter a start date following the YY-MM-DD HH:mm:ss format.
                            </b-form-invalid-feedback>
                        </b-form-group>
                        <b-form-group label="Enter an end date" label-for="datepicker-end">
                            <b-form-input type="text" v-model="filter_end_date" id="datepicker-end"
                                          :state="validation_end_date()" placeholder="End date" required></b-form-input>
                            <b-form-invalid-feedback :state="validation_end_date()">
                                Enter an end date following the YY-MM-DD HH:mm:ss format.
                            </b-form-invalid-feedback>
                        </b-form-group>
                        <b-button @click="filterStats" variant="primary">Filter</b-button>
                    </b-form>
                </b-card>
                <b-card title="Title" header-tag="header" class="mb-3">
                    <template v-slot:header>
                        <h6 class="mb-0">Upload your stats files</h6>
                    </template>
                    <b-form novalidate>
                        <b-form-file
                                class="mb-3"
                                accept=".csv"
                                v-model="files"
                                multiple
                                placeholder="Upload stat files..."
                                drop-placeholder="Drop files here..."
                        ></b-form-file>
                        <b-button @click="sendFiles" variant="outline-secondary" class="mr-2">Upload</b-button>
                    </b-form>
                </b-card>
            </b-col>
            <b-col cols="12" md="6">
                <b-card header-tag="header">
                    <template v-slot:header>
                        <h6 class="mb-0">Select the scenarii appearing on the chart</h6>
                    </template>
                    <b-form novalidate>
                        <b-form-group :label="statsObj['scenarii'].length > 0 ? 'Check or uncheck the boxes to add / remove the corresponding lines on the chart' : 'No scenario played yet'">
                            <b-form-checkbox-group
                                    id="scenarii-checkboxes"
                                    v-model="selected"
                                    :options="scenariiOptions()"
                                    name="scenarii-checkboxes"
                                    switches
                                    stacked
                            ></b-form-checkbox-group>
                        </b-form-group>
                    </b-form>
                </b-card>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
    import axios from "axios";
    import Chart from "chart.js"
    import "chartjs-plugin-zoom"
    import { mapState } from "vuex"
    import { isIn } from "../utils";

    export default {
        name: "Dashboard",
        data() {
            return {
                alertVariant: 'primary',
                alertMessage: null,
                ctx: null,
                chart: null,
                statsObj: {
                    "scenarii": []
                },
                selected: [],
                files: [],
                filter_start_date: null,
                filter_end_date: null,
                reg: /^([0-9]{4})-([0-1][0-9])-([0-3][0-9])\s([0-1][0-9]|[2][0-3]):([0-5][0-9]):([0-5][0-9])$/,
            }
        },
        computed: {
            ...mapState('auth', [
                'username',
            ]),
        },
        mounted() {
            this.getStats()
            this.ctx = document.getElementById('chart').getContext('2d');
            this.chart = new Chart(this.ctx, {
                type: 'line',
                data: {
                    datasets: []
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                        text: 'Accuracy in % per scenario played over time.'
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                max: 100,
                                min: 0,
                                stepSize: 10,
                            }
                        }],
                        xAxes: [{
                            type: 'time'
                        }]
                    },
                    plugins: {
                        zoom: {
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            },
                            zoom: {
                                enabled: true,
                                mode: 'xy',
                            }
                        }
                    }
                }
            })
        },
        methods: {
            scenariiOptions () {
                return this.statsObj["scenarii"].map(f => {
                    return {
                        text: f,
                        value: f
                    }
                })
            },
            validation_start_date() {
                if (this.filter_start_date !== null)
                    return this.reg.test(this.filter_start_date);
                return null
            },
            validation_end_date() {
                if (this.filter_end_date !== null)
                    return this.reg.test(this.filter_end_date);
                return null
            },
            getRandomRgb() {
                const r = Math.floor(Math.random() * Math.floor(255));
                const g = Math.floor(Math.random() * Math.floor(255));
                const b = Math.floor(Math.random() * Math.floor(255));
                return 'rgba(' + r + ', ' + g + ', ' + b + ', 0.7)'
            },
            getStatFromAccuracy(scenario, accuracy) {
                for (const stat of this.statsObj[scenario]) {
                    if (stat["total_accuracy"] === accuracy)
                        return stat
                }
                return null
            },
            updateChart() {
                this.generateDatasets()
                this.generateOptions()
                this.chart.update()
            },
            generateDatasets() {
                let res = []
                for (const [scenario, stats] of Object.entries(this.statsObj)) {
                    if (scenario !== "scenarii" && isIn(scenario, this.selected)) {
                        // iterate over the stat objects
                        // we need create the base options for the dataset corresponding to the current scenario
                        let curDataset = {
                            "label": scenario,
                            "borderColor": this.getRandomRgb(),
                            "data": [],
                            "fill": false,
                        }
                        for (const stat of stats) {
                            let out_of_range = false
                            if (this.validation_start_date()) {
                                const startDate = new Date(this.filter_start_date)
                                const curDate = new Date(stat["execution_date"])
                                if (startDate > curDate)
                                    out_of_range = true
                            }
                            if (this.validation_end_date()) {
                                const endDate = new Date(this.filter_end_date)
                                const curDate = new Date(stat["executed_date"])
                                if (endDate < curDate)
                                    out_of_range = true
                            }

                            if (out_of_range === false) {
                                curDataset.data.push({
                                    t: new Date(stat["execution_date"]),
                                    y: stat["total_accuracy"]
                                })
                            }
                        }
                        res.push(curDataset)
                    }
                }
                console.log(res)
                this.chart.data.datasets = res
            },
            generateOptions() {
                const self = this
                this.chart.options = {
                    responsive: true,
                    maintainAspectRatio: false,
                    title: {
                        display: true,
                            text: 'Accuracy in % per scenario played over time.'
                    },
                    elements: {
                        line: {
                            tension: 0
                        }
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                max: 100,
                                min: 0,
                                stepSize: 10,
                            }
                        }],
                        xAxes: [{
                            type: 'time'
                        }]
                    },
                    plugins: {
                        zoom: {
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            },
                            zoom: {
                                enabled: true,
                                mode: 'xy',
                            }
                        }
                    },
                    tooltips: {
                        callbacks: {
                            afterBody: function(tooltipItem, data) {
                                const res = self.getStatFromAccuracy(data.datasets[tooltipItem[0].datasetIndex].label, tooltipItem[0].yLabel)
                                return [
                                    'Horizontal sensitivity: ' + res["horiz_sens"].toString(),
                                    'Vertical sensitivity: ' + res["vert_sens"].toString(),
                                    'Sensitivity scale: ' + res["sens_scale"].toString(),
                                    'FOV: ' + res["fov"].toString(),
                                    'Score: ' + res["score"].toString(),
                                    'Input lag: ' + res["input_lag"].toString()
                                ];
                            },
                            label: function(tooltipItem, data) {
                                const res = self.getStatFromAccuracy(data.datasets[tooltipItem.datasetIndex].label,tooltipItem.yLabel)
                                return 'Accuracy: ' + res["total_accuracy"].toString()
                            }
                        },
                    }
                }
            },
            filterStats() {
                this.updateChart()
            },
            getStats() {
                axios.get(process.env.VUE_APP_API_URL + 'users/' + this.username + '/stats')
                    .then(resp => {
                        this.statsObj = resp.data
                        this.selected = this.statsObj["scenarii"]
                        setTimeout(() => { this.updateChart() }, 500);
                    })
                    .catch(error => {
                        this.alertVariant = 'danger';
                        this.alertMessage = error.response ? error.response.data.message : error;
                    });
            },
            sendFiles() {
                if (this.files.length === 0) {
                    return ;
                }
                const formData = new FormData();
                this.files.forEach(file => {
                    formData.append("files", file)
                })

                axios.post(process.env.VUE_APP_API_URL + 'users/' + this.username + '/stats', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    }
                }).then(resp => {
                }).catch(error => {
                    this.alertVariant = 'danger';
                    this.alertMessage = error.response ? error.response.data.message : error;
                });
                this.getStats()
            },
        }
    }
</script>

<style scoped>
    .manage-header small{
        color: #777;
    }
</style>