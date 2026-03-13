<template>
  <router-view />
</template>

<script setup>
// App component - Layout is now handled by AppLayout.vue
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--surface-ground);
  color: var(--text-color);
}

#app {
  min-height: 100vh;
}
</style>
