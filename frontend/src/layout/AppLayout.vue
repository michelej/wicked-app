<template>
  <div class="layout-wrapper" :class="containerClass">
    <AppTopbar />
    <div class="layout-sidebar">
      <AppSidebar />
    </div>
    <div class="layout-main-container">
      <div class="layout-main">
        <router-view />
      </div>
      <AppFooter />
    </div>
    <div class="layout-mask" v-if="isSidebarActive" @click="onMaskClick"></div>
    <Toast />
  </div>
</template>

<script setup>
import { computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppTopbar from './AppTopbar.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'
import { useLayout } from '@/layout/composables/layout.js'

const router = useRouter()
const { layoutConfig, layoutState, isSidebarActive, resetMenu } = useLayout()

watch(router.currentRoute, () => {
  resetMenu()
})

const containerClass = computed(() => ({
  'layout-overlay': layoutConfig.menuMode.value === 'overlay',
  'layout-static': layoutConfig.menuMode.value === 'static',
  'layout-static-inactive': layoutState.staticMenuInactive.value && layoutConfig.menuMode.value === 'static',
  'layout-overlay-active': layoutState.overlayMenuActive.value,
  'layout-mobile-active': layoutState.staticMenuMobileActive.value,
  'p-input-filled': false,
  'p-ripple-disabled': false
}))

const onMaskClick = () => {
  resetMenu()
}
</script>

<style scoped>
.layout-wrapper {
  min-height: 100vh;
}

.layout-main-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  justify-content: space-between;
  padding: 7rem 2rem 2rem 4rem;
  transition: margin-left 0.2s;
}

.layout-main {
  flex: 1 1 auto;
}

.layout-mask {
  z-index: 998;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
}

.layout-wrapper.layout-static .layout-main-container {
  margin-left: 300px;
}

.layout-wrapper.layout-static.layout-static-inactive .layout-main-container {
  margin-left: 0;
}

.layout-wrapper.layout-static.layout-static-inactive .layout-sidebar {
  transform: translateX(-100%);
}

.layout-wrapper.layout-overlay .layout-main-container {
  margin-left: 0;
}

.layout-wrapper.layout-overlay .layout-sidebar {
  transform: translateX(-100%);
  z-index: 999;
}

.layout-wrapper.layout-overlay.layout-overlay-active .layout-sidebar {
  transform: translateX(0);
}

.layout-wrapper.layout-mobile-active .layout-sidebar {
  transform: translateX(0);
}

@media (max-width: 991px) {
  .layout-wrapper .layout-main-container {
    margin-left: 0;
    padding-left: 2rem;
  }

  .layout-wrapper.layout-static .layout-main-container {
    margin-left: 0;
  }

  .layout-wrapper .layout-sidebar {
    transform: translateX(-100%);
  }

  .layout-wrapper.layout-mobile-active .layout-sidebar {
    transform: translateX(0);
  }
}
</style>
