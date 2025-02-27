<template>
<v-container>
  <v-alert
      id="nav-alert"
      icon="mdi-alert"
      elevation=8
      v-if="!userBrowser.is_allowed"
    >
    <div class="alert-title">Browser Upgrade Recommended</div>
    You are using an unsupported browser, and may have a degraded experience. To increase performance and access all features please use a modern browser.
  </v-alert>
  <v-container fill-height fluid>
  <v-row align="center"
      justify="center">
      <p>How many people are ahead of me?</p>
  </v-row>
  <v-row align="center"
      justify="center">
      <p><strong>Please note:</strong> booked appointments take priority and will move to the top of queue </p>
  </v-row>
  <v-row>
    <v-col> </v-col>
    <v-col align="center"
      v-if="(showEstimate === 'True')"
      justify="center">Est. time</v-col>
    <!-- <v-col align="center"
      justify="center">Tot. time</v-col> -->
  </v-row>
  <v-row v-for="(Q, index) in theWalkinQ"
        :key="Q.citizen_id">
    <!--ticket number column start -->
    <v-col>
      <v-card
        class="pa-md-4 mx-lg-auto"
        :color="myColor(Q)"
      >
        <v-card-text
          align="center"
          justify="center"
          :color="myColor(Q)"
          >
          <span v-if="Q.flag === 'agenda_panel'">{{ getAppTime(Q) }} </span>
          <span v-else>{{ index + 1  }}</span>
          <!-- <span v-else>{{ Q.ticket_number }}</span> -->
        </v-card-text>
      </v-card>
    </v-col>
    <!--ticket number column end -->
    <!-- estimate time column start -->
    <v-col v-if="(showEstimate === 'True')">
      <v-card
        class="pa-md-4 mx-lg-auto"
        :color="myColor(Q)"
      >
        <v-card-text
          align="center"
          justify="center">
          <!-- estimate time show -->
        </v-card-text>
      </v-card>
    </v-col>
    <!-- estimate time column end -->
    <!--total time column start -->
    <v-col>
      <v-card
        class="pa-md-4 mx-lg-auto"
        :color="myColor(Q)"
      >
        <v-card-text
          v-if="((Q.service_begin_seconds) && !amI(Q.walkin_unique_id))"
          align="center"
          justify="center">
          <span>{{ toHHMMSS(Q.service_begin_seconds) }}</span>
        </v-card-text>
        <v-card-text
          v-else-if="!amI(Q.walkin_unique_id)"
          align="center"
          justify="center">
          <span v-if="Q.flag === 'booked_app'">Booked Appointment</span>
          <span v-if="Q.flag === 'agenda_panel'">Booked Appointment</span>
          <span v-if="Q.flag === 'walkin_app'">Waiting for Service</span>
        </v-card-text>
        <v-card-text
           v-else-if="amI(Q.walkin_unique_id)"
          align="center"
          justify="center">
          <v-btn
              icon
              color="red lighten-2"
          >
            <v-icon
                large
                color="blue darken-2"
              >
            mdi-account
            </v-icon>
            Me
          </v-btn>
          <!-- <v-btn text  v-if="Q.flag === 'serving_app'">
          <span>{{ toHHMMSS(Q.service_begin_seconds) }}</span>
          </v-btn> -->
         </v-card-text>
      </v-card>
    </v-col>
    <!--total time column end -->
  </v-row>
</v-container>
<p v-if="lastRefresh"><strong>Page last updated at: {{ lastRefresh }}</strong></p>
</v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import CommonUtils from '@/utils/common-util'
import { WalkinModule } from '@/store/modules'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'
import { th } from 'date-fns/locale'

@Component({
  methods: {
    ...mapActions('walkin', [
      'getAllWalkin'
    ])
  }
})

export default class WalkinQ extends Vue {
  @Prop({ default: '' }) uniqueId!: string

  private readonly getAllWalkin!: (uniqueId: string) => Promise<any>
  private WalkinModule = getModule(WalkinModule, this.$store)

  private theWalkinQ: any = {}
  private showEstimate: any = ''
  private lastRefresh: any = ''
  private userBrowser = {
    is_allowed: true,
    current_browser: '',
    current_version: '',
    allowed_browsers: ''
  }

  mounted () {
    this.userBrowser = CommonUtils.isAllowedBrowsers()
    window.setInterval(() => {
      this.getAllQ()
      this.lastRefresh = new Date().toLocaleTimeString()
    }, 60000)
  }

  private created () {
    this.getAllQ()
  }

  private async getAllQ () {
    const resp = await this.getAllWalkin(this.uniqueId)
    if (resp?.status === 200) {
      this.theWalkinQ = resp?.data?.citizen
      this.showEstimate = resp?.data?.show_estimate
      if ((!resp?.data) || (Object.keys(resp?.data).length <= 0)) {
        this.$router.push('/no-content/not-in-Q')
      }
    } else {
      this.$router.push('/no-content/not-in-Q')
    }
  }

  private getAppTime (Q) {
    if (Q.start_time) {
      return new Date(Q.start_time).toLocaleTimeString()
    }
    return Q.start_time
  }

  private amI (ID: string) {
    if (ID) {
      if (ID === this.uniqueId) {
        return 'secondary'
      }
    }
    return null
  }

  private myColor (Q: any) {
    let color = null
    if (Q.walkin_unique_id) {
      color = this.amI(Q.walkin_unique_id)
    }
    if (!color) {
      if (Q.flag === 'walkin_app') {
        // Waiting for Service- white
        color = 'white'
      } else if (Q.flag === 'booked_app') {
        // booked checkin- green
        color = '#98FB98'
      } else if (Q.flag === 'agenda_panel') {
        // grey-in agenda panel
        color = '#d3d3d3'
      }
    }
    return color
  }

  private toHHMMSS (secs: any) {
    const secNum = parseInt(secs, 10)
    const hours = Math.floor(secNum / 3600)
    const minutes = Math.floor(secNum / 60) % 60
    const seconds = secNum % 60

    return [hours, minutes, seconds]
      .map(v => v < 10 ? '0' + v : v)
      .filter((v, i) => v !== '00' || i > 0)
      .join(':')
  }
}
</script>

<style lang="scss" scoped>
// @import "@/assets/scss/theme.scss";
// .card-animation-serving  {
//   background-color: #C9A0DC;
//   animation-name: serving_now;
//   animation-duration: 1s;
//   animation-iteration-count:infinite;
// }

// @keyframes serving_now {
//   from {background-color: #C9A0DC;}
//   to {background-color: white;}
// }
</style>
