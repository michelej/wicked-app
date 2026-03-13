<template>
  <div class="layout-topbar">
    <router-link to="/" class="layout-topbar-logo">
      <div class="logo-icon">
        <i class="pi pi-bolt"></i>
      </div>
      <span class="logo-text">Wicked<span class="logo-accent">App</span></span>
    </router-link>

    <button class="p-link layout-menu-button layout-topbar-button" @click="onMenuToggle">
      <i class="pi pi-bars"></i>
    </button>

    <button class="p-link layout-topbar-menu-button layout-topbar-button" @click="showProfileSidebar">
      <i class="pi pi-ellipsis-v"></i>
    </button>

    <div class="layout-topbar-menu" :class="topbarMenuClasses">
      <button @click="toggleDarkMode" class="p-link layout-topbar-button theme-toggle">
        <i :class="['pi', isDarkTheme ? 'pi-sun' : 'pi-moon']"></i>
        <span>{{ isDarkTheme ? 'Light' : 'Dark' }}</span>
      </button>
      
      <button class="p-link layout-topbar-button">
        <i class="pi pi-bell"></i>
        <span>Notifications</span>
        <span class="notification-badge">3</span>
      </button>
      
      <button class="p-link layout-topbar-button profile-button">
        <div class="profile-avatar">
          <i class="pi pi-user"></i>
        </div>
        <span>Profile</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLayout } from '@/layout/composables/layout'

const { onMenuToggle, toggleDarkMode, isDarkTheme, layoutState } = useLayout()

const topbarMenuClasses = computed(() => ({
  'layout-topbar-menu-mobile-active': layoutState.profileSidebarVisible.value
}))

const showProfileSidebar = () => {
  layoutState.profileSidebarVisible.value = !layoutState.profileSidebarVisible.value
}
</script>

<style scoped>
.layout-topbar {
  position: fixed;
  height: 5rem;
  z-index: 997;
  left: 0;
  top: 0;
  width: 100%;
  padding: 0 2rem;
  background: var(--surface-card);
  transition: left 0.2s;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--surface-border);
}

.layout-topbar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 800;
  width: 300px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.layout-topbar-logo:hover {
  transform: translateY(-1px);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.logo-text {
  font-size: 1.375rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-color);
}

.logo-accent {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
}

.layout-topbar-button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  position: relative;
  color: var(--text-color-secondary);
  border-radius: 10px;
  height: 2.75rem;
  padding: 0 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.9375rem;
}

.layout-topbar-button:hover {
  color: var(--text-color);
  background-color: var(--surface-hover);
  transform: translateY(-1px);
}

.layout-topbar-button i {
  font-size: 1.125rem;
}

.layout-topbar-button span {
  font-size: 0.9375rem;
  display: none;
}

.theme-toggle {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background: #ef4444;
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
  padding: 0.125rem 0.375rem;
  border-radius: 10px;
  min-width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-button {
  gap: 0.625rem;
}

.profile-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
}

.layout-menu-button {
  margin-left: 2rem;
}

.layout-topbar-menu-button {
  display: none;
}

.layout-topbar-menu {
  margin: 0 0 0 auto;
  padding: 0;
  list-style: none;
  display: flex;
  gap: 0.5rem;
}

@media (min-width: 992px) {
  .layout-topbar-button span {
    display: inline;
  }
}

@media (max-width: 991px) {
  .layout-topbar {
    justify-content: space-between;
  }

  .layout-topbar-logo {
    width: auto;
  }

  .logo-text {
    display: none;
  }

  .layout-menu-button {
    margin-left: 0;
  }

  .layout-topbar-menu-button {
    display: inline-flex;
  }

  .layout-topbar-menu {
    position: absolute;
    flex-direction: column;
    background-color: var(--surface-overlay);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    border-radius: 12px;
    padding: 1rem;
    right: 2rem;
    top: 5.5rem;
    min-width: 200px;
    display: none;
    gap: 0.25rem;
  }

  .layout-topbar-menu.layout-topbar-menu-mobile-active {
    display: flex;
    animation: slideDown 0.3s ease-out;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .layout-topbar-menu .layout-topbar-button {
    margin-left: 0;
    display: flex;
    width: 100%;
    height: auto;
    justify-content: flex-start;
    border-radius: 8px;
    padding: 0.75rem 1rem;
  }

  .layout-topbar-menu .layout-topbar-button i {
    font-size: 1rem;
  }

  .layout-topbar-menu .layout-topbar-button span {
    font-weight: 600;
    display: inline;
  }

  .notification-badge {
    position: static;
    margin-left: auto;
  }

  .profile-avatar {
    width: 28px;
    height: 28px;
  }
}
</style>
