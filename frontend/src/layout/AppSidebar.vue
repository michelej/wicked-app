<template>
  <div class="layout-sidebar">
    <AppMenu />
  </div>
</template>

<script setup>
import AppMenu from './AppMenu.vue'
</script>

<style scoped>
.layout-sidebar {
  position: fixed;
  width: 300px;
  height: calc(100vh - 5rem);
  z-index: 999;
  overflow-y: auto;
  user-select: none;
  top: 5rem;
  left: 0;
  transition: transform 0.2s, left 0.2s;
  background-color: var(--surface-card);
  border-right: 1px solid var(--surface-border);
  padding: 1.5rem;
}

@media (max-width: 991px) {
  .layout-sidebar {
    transform: translateX(-100%);
  }
}
</style>
