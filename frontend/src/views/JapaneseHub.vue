<template>
  <div class="japanese-hub">
    <section class="japanese-hero">
      <div class="hero-copy">
        <span class="hero-kicker">Japones</span>
        <h1>{{ currentView.title }}</h1>
        <p>{{ currentView.description }}</p>
      </div>

      <div class="hero-practice-card">
        <span class="summary-label">Modo de uso</span>
        <strong>{{ practiceSummary }}</strong>
        <small>La mini app ya incluye listas mock de palabras, frases y una practica local sencilla.</small>
      </div>
    </section>

    <section class="japanese-shell">
      <div class="japanese-nav-strip">
        <button
          v-for="item in navItems"
          :key="item.routeName"
          type="button"
          class="nav-pill"
          :class="{ active: route.name === item.routeName }"
          @click="router.push({ name: item.routeName })"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </button>
      </div>

      <template v-if="route.name === 'japanese-hub'">
        <div class="overview-grid">
          <Card class="overview-main-card">
            <template #content>
              <div class="section-header">
                <div>
                  <span class="section-kicker">Resumen</span>
                  <h2>Panorama del modulo</h2>
                </div>
              </div>

              <div class="stat-grid">
                <div class="stat-card">
                  <span>Palabras</span>
                  <strong>{{ words.length }}</strong>
                </div>
                <div class="stat-card">
                  <span>Frases</span>
                  <strong>{{ phrases.length }}</strong>
                </div>
                <div class="stat-card">
                  <span>Temas</span>
                  <strong>{{ uniqueThemes.length }}</strong>
                </div>
                <div class="stat-card">
                  <span>Sesion sugerida</span>
                  <strong>5 items</strong>
                </div>
              </div>

              <div class="list-preview">
                <div class="list-item" v-for="item in overviewPreview" :key="item.jp">
                  <div>
                    <strong>{{ item.jp }}</strong>
                    <small>{{ item.reading }}</small>
                  </div>
                  <span>{{ item.es }}</span>
                </div>
              </div>
            </template>
          </Card>

          <Card class="overview-side-card">
            <template #content>
              <div class="section-header compact-header">
                <div>
                  <span class="section-kicker">Principios</span>
                  <h2>Micro UX</h2>
                </div>
              </div>

              <div class="mini-stack">
                <div class="mini-card" v-for="principle in principles" :key="principle.title">
                  <strong>{{ principle.title }}</strong>
                  <p>{{ principle.text }}</p>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </template>

      <template v-else-if="route.name === 'japanese-words'">
        <Card class="content-card-shell">
          <template #content>
            <div class="section-header wrap-header">
              <div>
                <span class="section-kicker">Palabras</span>
                <h2>Vocabulario filtrable</h2>
              </div>

              <input v-model.trim="wordSearch" class="search-input" type="text" placeholder="Buscar por japones, lectura o significado" />
            </div>

            <div class="filter-pill-row">
              <button
                v-for="theme in ['all', ...uniqueThemes]"
                :key="theme"
                type="button"
                class="filter-pill"
                :class="{ active: selectedWordTheme === theme }"
                @click="selectedWordTheme = theme"
              >
                {{ theme === 'all' ? 'Todos' : theme }}
              </button>
            </div>

            <div class="list-grid">
              <div class="list-card" v-for="word in filteredWords" :key="word.jp">
                <span class="theme-pill">{{ word.theme }}</span>
                <strong>{{ word.jp }}</strong>
                <small>{{ word.reading }}</small>
                <p>{{ word.es }}</p>
              </div>

              <div v-if="filteredWords.length === 0" class="empty-local-state">
                No hay palabras que coincidan con la busqueda actual.
              </div>
            </div>
          </template>
        </Card>
      </template>

      <template v-else-if="route.name === 'japanese-phrases'">
        <Card class="content-card-shell">
          <template #content>
            <div class="section-header wrap-header">
              <div>
                <span class="section-kicker">Frases</span>
                <h2>Biblioteca de expresiones</h2>
              </div>

              <input v-model.trim="phraseSearch" class="search-input" type="text" placeholder="Buscar por contexto o significado" />
            </div>

            <div class="phrase-stack">
              <div class="phrase-card" v-for="phrase in filteredPhrases" :key="phrase.jp">
                <div class="phrase-top-row">
                  <span class="theme-pill warm-pill">{{ phrase.context }}</span>
                  <small>{{ phrase.reading }}</small>
                </div>
                <strong>{{ phrase.jp }}</strong>
                <p>{{ phrase.es }}</p>
              </div>

              <div v-if="filteredPhrases.length === 0" class="empty-local-state">
                No hay frases que coincidan con la busqueda actual.
              </div>
            </div>
          </template>
        </Card>
      </template>

      <template v-else>
        <div class="practice-grid">
          <Card class="practice-main-card">
            <template #content>
              <div class="section-header wrap-header">
                <div>
                  <span class="section-kicker">Practica</span>
                  <h2>Sesion corta de repeticion</h2>
                </div>

                <div class="filter-pill-row compact-pills">
                  <button
                    v-for="mode in practiceModes"
                    :key="mode.value"
                    type="button"
                    class="filter-pill"
                    :class="{ active: practiceMode === mode.value }"
                    @click="setPracticeMode(mode.value)"
                  >
                    {{ mode.label }}
                  </button>
                </div>
              </div>

              <div class="practice-card">
                <span class="practice-counter">{{ practiceIndex + 1 }} / {{ practiceItems.length }}</span>
                <strong>{{ currentPracticeItem.jp }}</strong>
                <small>{{ currentPracticeItem.reading }}</small>

                <div v-if="showPracticeAnswer" class="practice-answer">
                  <p>{{ currentPracticeItem.es }}</p>
                  <span>{{ currentPracticeItem.context || currentPracticeItem.theme }}</span>
                </div>
                <div v-else class="practice-hidden">
                  Pulsa revelar para ver el significado.
                </div>

                <div class="practice-actions">
                  <Button label="Revelar" icon="pi pi-eye" severity="warning" outlined @click="showPracticeAnswer = true" />
                  <Button label="Siguiente" icon="pi pi-arrow-right" severity="success" @click="goToNextPracticeItem" />
                </div>
              </div>
            </template>
          </Card>

          <Card class="practice-side-card">
            <template #content>
              <div class="section-header compact-header">
                <div>
                  <span class="section-kicker">Sesion</span>
                  <h2>Reglas simples</h2>
                </div>
              </div>

              <div class="mini-stack">
                <div class="mini-card" v-for="tip in practiceTips" :key="tip.title">
                  <strong>{{ tip.title }}</strong>
                  <p>{{ tip.text }}</p>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { routeName: 'japanese-hub', label: 'Vista general', icon: 'pi pi-compass' },
  { routeName: 'japanese-words', label: 'Palabras', icon: 'pi pi-list-check' },
  { routeName: 'japanese-phrases', label: 'Frases', icon: 'pi pi-comment' },
  { routeName: 'japanese-practice', label: 'Practicar', icon: 'pi pi-bolt' }
]

const viewMap = {
  'japanese-hub': {
    title: 'Una micro app para volver muchas veces al dia sin friccion.',
    description: 'Vista general del modulo con foco en consumo rapido, repeticion breve y estructura ligera.',
  },
  'japanese-words': {
    title: 'Palabras organizadas para escaneo y repeticion inmediata.',
    description: 'Listado mock filtrable por tema y busqueda textual.',
  },
  'japanese-phrases': {
    title: 'Frases utiles para memorizar patron y contexto a la vez.',
    description: 'Coleccion mock de frases cortas para lectura rapida y retorno frecuente.',
  },
  'japanese-practice': {
    title: 'Practica breve con rondas pequenas y ritmo muy ligero.',
    description: 'Una sesion local simple para demostrar el comportamiento de una mini utilidad diaria.',
  }
}

const currentView = computed(() => viewMap[route.name] || viewMap['japanese-hub'])

const words = [
  { jp: '旅行', reading: 'りょこう', es: 'viaje', theme: 'viaje' },
  { jp: '買い物', reading: 'かいもの', es: 'compra', theme: 'compras' },
  { jp: '電車', reading: 'でんしゃ', es: 'tren', theme: 'transporte' },
  { jp: '朝ごはん', reading: 'あさごはん', es: 'desayuno', theme: 'comida' },
  { jp: '勉強', reading: 'べんきょう', es: 'estudio', theme: 'rutina' },
  { jp: '天気', reading: 'てんき', es: 'tiempo / clima', theme: 'diario' }
]

const phrases = [
  { jp: '今日は忙しいです。', reading: 'きょうはいそがしいです。', es: 'Hoy estoy ocupado.', context: 'rutina' },
  { jp: 'これはいくらですか。', reading: 'これはいくらですか。', es: 'Cuanto cuesta esto?', context: 'compras' },
  { jp: '駅はどこですか。', reading: 'えきはどこですか。', es: 'Donde esta la estacion?', context: 'transporte' },
  { jp: '水をください。', reading: 'みずをください。', es: 'Agua, por favor.', context: 'restaurante' },
  { jp: '写真を撮ってもいいですか。', reading: 'しゃしんをとってもいいですか。', es: 'Puedo hacer una foto?', context: 'viaje' }
]

const principles = [
  { title: 'Ligero', text: 'Abrir y consumir sin preparar una sesion larga.' },
  { title: 'Repetible', text: 'Volver varias veces al dia debe sentirse natural.' },
  { title: 'Simple', text: 'Cada pantalla resuelve una sola accion principal.' }
]

const practiceTips = [
  { title: 'Rondas cortas', text: 'Cinco elementos son suficientes para mantener la constancia.' },
  { title: 'Primero recordar', text: 'Intenta resolver antes de pulsar revelar.' },
  { title: 'Salir rapido', text: 'La practica gana valor cuando puedes volver muchas veces.' }
]

const wordSearch = ref('')
const phraseSearch = ref('')
const selectedWordTheme = ref('all')
const practiceMode = ref('mixed')
const practiceIndex = ref(0)
const showPracticeAnswer = ref(false)

const uniqueThemes = computed(() => [...new Set(words.map((word) => word.theme))])

const filteredWords = computed(() => {
  const query = wordSearch.value.toLowerCase()

  return words.filter((word) => {
    const matchesTheme = selectedWordTheme.value === 'all' || word.theme === selectedWordTheme.value
    const haystack = `${word.jp} ${word.reading} ${word.es} ${word.theme}`.toLowerCase()
    const matchesQuery = !query || haystack.includes(query)
    return matchesTheme && matchesQuery
  })
})

const filteredPhrases = computed(() => {
  const query = phraseSearch.value.toLowerCase()

  return phrases.filter((phrase) => {
    const haystack = `${phrase.jp} ${phrase.reading} ${phrase.es} ${phrase.context}`.toLowerCase()
    return !query || haystack.includes(query)
  })
})

const overviewPreview = computed(() => [...words.slice(0, 2), { ...phrases[0], theme: phrases[0].context }])

const practiceModes = [
  { value: 'mixed', label: 'Mixto' },
  { value: 'words', label: 'Palabras' },
  { value: 'phrases', label: 'Frases' }
]

const practiceItems = computed(() => {
  if (practiceMode.value === 'words') {
    return words
  }

  if (practiceMode.value === 'phrases') {
    return phrases
  }

  return [
    ...words,
    ...phrases.map((phrase) => ({ ...phrase, theme: phrase.context }))
  ]
})

const currentPracticeItem = computed(() => practiceItems.value[practiceIndex.value] || practiceItems.value[0])

const practiceSummary = computed(() => {
  if (route.name === 'japanese-practice') {
    return `Sesion ${practiceMode.value} con ${practiceItems.value.length} items disponibles`
  }

  return `${words.length} palabras y ${phrases.length} frases listas para revisar`
})

const setPracticeMode = (mode) => {
  practiceMode.value = mode
  practiceIndex.value = 0
  showPracticeAnswer.value = false
}

const goToNextPracticeItem = () => {
  practiceIndex.value = (practiceIndex.value + 1) % practiceItems.value.length
  showPracticeAnswer.value = false
}
</script>

<style scoped>
.japanese-hub {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.japanese-hero,
.japanese-nav-strip,
.overview-main-card,
.overview-side-card,
.content-card-shell,
.practice-main-card,
.practice-side-card {
  border: 1px solid var(--surface-border);
  border-radius: 30px;
  background: color-mix(in srgb, var(--surface-card) 86%, transparent);
  box-shadow: 0 18px 32px rgba(15, 23, 42, 0.08);
}

.japanese-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.85fr);
  gap: 1rem;
  padding: 1.4rem;
  background:
    radial-gradient(circle at top right, rgba(249, 115, 22, 0.18), transparent 32%),
    linear-gradient(145deg, rgba(255, 252, 244, 0.96) 0%, rgba(250, 247, 242, 0.96) 100%);
}

.hero-kicker,
.section-kicker,
.nav-pill,
.filter-pill,
.theme-pill,
.practice-counter {
  display: inline-flex;
  width: fit-content;
  padding: 0.42rem 0.8rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
}

.hero-kicker,
.section-kicker,
.theme-pill,
.practice-counter {
  background: rgba(255, 255, 255, 0.74);
  color: #d97706;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}

.hero-copy h1,
.section-header h2 {
  margin: 0.65rem 0 0.4rem;
  color: var(--heading-color);
}

.hero-copy h1 {
  max-width: 12ch;
  font-size: clamp(2.1rem, 4vw, 3.2rem);
  line-height: 0.98;
  letter-spacing: -0.05em;
}

.hero-copy p,
.hero-practice-card small,
.list-item span,
.list-item small,
.study-card p,
.mini-card p,
.phrase-card p,
.phrase-card small,
.practice-hidden,
.practice-answer span,
.empty-local-state {
  color: var(--text-color-secondary);
  line-height: 1.65;
}

.hero-practice-card {
  padding: 1.1rem;
  border-radius: 24px;
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.76);
}

.summary-label {
  display: block;
  margin-bottom: 0.45rem;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--text-color-secondary);
}

.hero-practice-card strong,
.list-item strong,
.study-card strong,
.mini-card strong,
.phrase-card strong,
.stat-card strong,
.practice-card strong {
  display: block;
  color: var(--heading-color);
}

.japanese-shell {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.japanese-nav-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.9rem;
}

.nav-pill,
.filter-pill {
  border: 1px solid rgba(124, 97, 61, 0.12);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-color-secondary);
  cursor: pointer;
}

.nav-pill {
  align-items: center;
  gap: 0.45rem;
}

.nav-pill.active,
.filter-pill.active {
  border-color: rgba(217, 119, 6, 0.24);
  background: rgba(254, 243, 199, 0.65);
  color: #b45309;
}

.overview-grid,
.practice-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 1rem;
}

.overview-main-card :deep(.p-card-body),
.overview-main-card :deep(.p-card-content),
.overview-side-card :deep(.p-card-body),
.overview-side-card :deep(.p-card-content),
.content-card-shell :deep(.p-card-body),
.content-card-shell :deep(.p-card-content),
.practice-main-card :deep(.p-card-body),
.practice-main-card :deep(.p-card-content),
.practice-side-card :deep(.p-card-body),
.practice-side-card :deep(.p-card-content) {
  padding: 0;
}

.overview-main-card :deep(.p-card-content),
.overview-side-card :deep(.p-card-content),
.content-card-shell :deep(.p-card-content),
.practice-main-card :deep(.p-card-content),
.practice-side-card :deep(.p-card-content) {
  padding: 1.2rem;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.wrap-header {
  flex-wrap: wrap;
}

.stat-grid,
.list-preview,
.mini-stack,
.list-grid,
.phrase-stack {
  display: grid;
  gap: 0.85rem;
}

.stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 1rem;
}

.stat-card,
.list-item,
.study-card,
.mini-card,
.list-card,
.phrase-card,
.practice-card {
  border: 1px solid rgba(124, 97, 61, 0.12);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.66);
}

.stat-card,
.list-item,
.study-card,
.mini-card,
.list-card,
.phrase-card,
.practice-card {
  padding: 1rem;
}

.stat-card span,
.practice-answer p,
.practice-answer span {
  color: var(--text-color-secondary);
}

.list-item,
.phrase-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.list-item small {
  display: block;
  margin-top: 0.2rem;
}

.search-input {
  width: min(100%, 340px);
  border: 1px solid var(--surface-border);
  border-radius: 14px;
  padding: 0.72rem 0.9rem;
  background: rgba(255, 255, 255, 0.82);
}

.filter-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  margin-bottom: 1rem;
}

.compact-pills {
  margin-bottom: 0;
}

.list-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.list-card strong {
  margin: 0.65rem 0 0.25rem;
  font-size: 1.15rem;
}

.list-card small {
  display: block;
  margin-bottom: 0.45rem;
}

.theme-pill,
.warm-pill {
  background: rgba(255, 247, 237, 0.82);
}

.phrase-card strong {
  margin: 0.45rem 0 0.25rem;
  font-size: 1.08rem;
}

.practice-card {
  text-align: center;
}

.practice-card strong {
  margin: 0.9rem 0 0.35rem;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1;
}

.practice-card small {
  display: block;
  margin-bottom: 1rem;
  color: var(--text-color-secondary);
}

.practice-hidden,
.practice-answer {
  min-height: 88px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.35rem;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.84);
  padding: 1rem;
}

.practice-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.empty-local-state {
  padding: 1rem;
  border-radius: 20px;
  background: rgba(248, 250, 252, 0.82);
  border: 1px dashed var(--surface-border);
}

@media (max-width: 1100px) {
  .japanese-hero,
  .overview-grid,
  .practice-grid,
  .stat-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .list-item,
  .phrase-top-row,
  .practice-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .practice-card {
    text-align: left;
  }

  .search-input {
    width: 100%;
  }
}
</style>
