<template>
  <section class="mobile-home-launcher">
    <div class="launcher-hero">
      <div class="launcher-brand-mark">
        <i class="pi pi-bolt"></i>
      </div>
      <span class="launcher-kicker">Wicked App</span>
      <h1>Tu acceso principal en móvil.</h1>
      <p>Abre directamente las secciones que más usas con botones grandes y táctiles.</p>
    </div>

    <div class="launcher-grid">
      <router-link
        v-for="item in items"
        :key="item.key"
        :to="item.to"
        class="launcher-card"
        :class="`is-${item.tone}`"
      >
        <span class="launcher-card-icon">
          <i :class="item.icon"></i>
        </span>

        <span class="launcher-card-copy">
          <strong>{{ item.label }}</strong>
          <small>{{ item.description }}</small>
        </span>

        <i class="pi pi-angle-right launcher-card-chevron"></i>
      </router-link>
    </div>
  </section>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.mobile-home-launcher {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  animation: launcherFadeIn 0.35s ease;
}

@keyframes launcherFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.launcher-hero,
.launcher-card {
  border: 1px solid var(--surface-border);
  background: color-mix(in srgb, var(--surface-card) 88%, transparent);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
}

.launcher-hero {
  padding: 1.35rem;
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(214, 145, 65, 0.14), transparent 30%),
    radial-gradient(circle at left bottom, rgba(15, 139, 111, 0.12), transparent 26%),
    linear-gradient(145deg, rgba(255, 251, 244, 0.96) 0%, rgba(241, 247, 245, 0.96) 100%);
}

.launcher-brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3.25rem;
  height: 3.25rem;
  margin-bottom: 1rem;
  border-radius: 18px;
  background: linear-gradient(145deg, #0f8b6f 0%, #126f75 100%);
  color: white;
  font-size: 1.2rem;
  box-shadow: 0 14px 24px rgba(15, 139, 111, 0.24);
}

.launcher-kicker {
  display: inline-flex;
  margin-bottom: 0.55rem;
  padding: 0.38rem 0.78rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  color: #0f8b6f;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  font-weight: 700;
}

.launcher-hero h1 {
  margin: 0;
  font-size: clamp(2rem, 10vw, 2.9rem);
  line-height: 0.96;
  letter-spacing: -0.05em;
  color: var(--heading-color);
}

.launcher-hero p {
  margin-top: 0.8rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.launcher-grid {
  display: grid;
  gap: 0.9rem;
}

.launcher-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 0.9rem;
  min-height: 5.9rem;
  padding: 1rem 1.05rem;
  border-radius: 24px;
  color: inherit;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.launcher-card:active {
  transform: scale(0.99);
}

.launcher-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.1);
}

.launcher-card-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3.2rem;
  height: 3.2rem;
  border-radius: 18px;
  color: white;
  background: linear-gradient(145deg, #0f8b6f 0%, #d97706 100%);
  font-size: 1.2rem;
  box-shadow: 0 10px 18px rgba(15, 139, 111, 0.2);
}

.launcher-card.is-registry .launcher-card-icon {
  background: linear-gradient(145deg, #2563eb 0%, #0ea5e9 100%);
}

.launcher-card.is-media .launcher-card-icon {
  background: linear-gradient(145deg, #db2777 0%, #7c3aed 100%);
}

.launcher-card-copy {
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
  min-width: 0;
}

.launcher-card-copy strong {
  font-size: 1.05rem;
  color: var(--heading-color);
}

.launcher-card-copy small {
  color: var(--text-color-secondary);
  line-height: 1.45;
}

.launcher-card-chevron {
  color: var(--text-color-secondary);
  font-size: 1rem;
}

@media (max-width: 480px) {
  .launcher-hero,
  .launcher-card {
    border-radius: 24px;
  }

  .launcher-hero {
    padding: 1.15rem;
  }

  .launcher-card {
    min-height: 5.5rem;
    padding: 0.95rem;
  }
}
</style>
