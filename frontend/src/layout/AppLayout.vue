<template>
  <div class="layout-wrapper" :class="containerClass">
    <div class="layout-backdrop" aria-hidden="true">
      <span class="backdrop-orb orb-primary"></span>
      <span class="backdrop-orb orb-accent"></span>
      <span class="backdrop-grid"></span>
    </div>
    <AppTopbar />
    <div class="layout-sidebar">
      <AppSidebar />
    </div>
    <div class="layout-main-container">
      <div class="layout-main">
        <div class="layout-page-shell">
          <router-view />
        </div>
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
  position: relative;
  overflow: hidden;
}

.layout-backdrop {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.backdrop-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(14px);
  opacity: 0.55;
}

.orb-primary {
  top: -9rem;
  right: -8rem;
  width: 26rem;
  height: 26rem;
  background: radial-gradient(circle, rgba(15, 139, 111, 0.22) 0%, rgba(15, 139, 111, 0) 72%);
}

.orb-accent {
  bottom: 8rem;
  left: -10rem;
  width: 24rem;
  height: 24rem;
  background: radial-gradient(circle, rgba(217, 119, 6, 0.18) 0%, rgba(217, 119, 6, 0) 72%);
}

.backdrop-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(95, 75, 45, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(95, 75, 45, 0.04) 1px, transparent 1px);
  background-size: 72px 72px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.3), transparent 88%);
}

.layout-main-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  justify-content: space-between;
  padding: 6.75rem 2rem 2rem 3.75rem;
  transition: margin-left 0.3s ease;
  position: relative;
  z-index: 1;
}

.layout-sidebar {
  position: relative;
  z-index: 1002;
}

.layout-main {
  flex: 1 1 auto;
  width: 100%;
  max-width: 1480px;
  margin: 0 auto;
}

.layout-page-shell {
  width: 100%;
}

.layout-mask {
  z-index: 1001;
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
  z-index: 1002;
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
    padding: 6.25rem 1rem 1.5rem;
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

  .orb-primary {
    width: 18rem;
    height: 18rem;
    top: -6rem;
    right: -5rem;
  }

  .orb-accent {
    width: 16rem;
    height: 16rem;
    bottom: 4rem;
    left: -6rem;
  }
}
</style>
