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
  transition: transform 0.25s ease, left 0.25s ease;
  background: color-mix(in srgb, var(--surface-card) 88%, transparent);
  backdrop-filter: blur(18px);
  border-right: 1px solid var(--surface-border);
  padding: 1.25rem;
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.45);
}

.layout-sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3), transparent 24%, transparent 76%, rgba(15, 139, 111, 0.05));
  pointer-events: none;
}

.layout-sidebar::-webkit-scrollbar {
  width: 8px;
}

.layout-sidebar::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.28);
  border-radius: 999px;
}

@media (max-width: 991px) {
  .layout-sidebar {
    transform: translateX(-100%);
  }
}
</style>
