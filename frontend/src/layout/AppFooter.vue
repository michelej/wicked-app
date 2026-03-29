<template>
  <div class="layout-footer">
    <div class="footer-brand">
      <span class="font-medium">Wicked App</span>
      <span>Dashboard financiero con enfoque operativo</span>
    </div>
    <span class="footer-meta">Presupuestos, transacciones y planeacion mensual</span>
  </div>
</template>

<style scoped>
.layout-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  background-color: color-mix(in srgb, var(--surface-card) 78%, transparent);
  border: 1px solid var(--surface-border);
  border-radius: 20px;
  color: var(--text-color-secondary);
  backdrop-filter: blur(14px);
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.font-medium {
  font-weight: 700;
  color: var(--text-color);
}

.footer-meta {
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .layout-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
