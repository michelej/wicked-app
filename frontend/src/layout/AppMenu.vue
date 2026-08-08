<template>
  <div class="sidebar-menu-shell">    

    <ul class="layout-menu">
      <template v-for="(item, i) in model" :key="item.label">
        <app-menu-item v-if="!item.separator" :item="item" :index="i" :root="true"></app-menu-item>
        <li v-if="item.separator" class="menu-separator"></li>
      </template>
    </ul>    
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppMenuItem from './AppMenuItem.vue'
import { createSidebarNavigationModel } from '@/constants/navigation'

const router = useRouter()

const model = createSidebarNavigationModel(router)
</script>

<style scoped>
.sidebar-menu-shell {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.menu-intro {
  padding: 1.25rem;
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.16), transparent 34%),
    linear-gradient(145deg, rgba(255, 251, 244, 0.96) 0%, rgba(239, 247, 241, 0.92) 100%);
  border: 1px solid rgba(124, 97, 61, 0.12);
  box-shadow: 0 18px 34px rgba(30, 41, 59, 0.08);
}

.menu-kicker {
  display: inline-flex;
  margin-bottom: 0.6rem;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--primary-color);
}

.menu-intro h2 {
  font-size: 1.15rem;
  line-height: 1.2;
  margin-bottom: 0.5rem;
}

.menu-intro p {
  font-size: 0.92rem;
  color: var(--text-color-secondary);
}

.layout-menu {
  margin: 0;
  padding: 0;
  list-style-type: none;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.menu-separator {
  border-top: 1px solid var(--surface-border);
  margin: 0.75rem 0;
}

.menu-support-card {
  padding: 1rem 1.1rem;
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(248, 250, 252, 0.9) 0%, rgba(255, 255, 255, 0.74) 100%);
  border: 1px solid var(--surface-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.support-label {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--text-color-secondary);
}

.menu-support-card strong {
  font-size: 0.93rem;
  line-height: 1.45;
  color: var(--text-color);
}
</style>
