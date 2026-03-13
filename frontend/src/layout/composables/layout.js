import { toRefs, reactive, computed } from 'vue'

const layoutConfig = reactive({
  preset: 'Aura',
  primary: 'emerald',
  surface: null,
  darkTheme: false,
  menuMode: 'static'
})

const layoutState = reactive({
  staticMenuInactive: false,
  overlayMenuActive: false,
  profileSidebarVisible: false,
  configSidebarVisible: false,
  staticMenuMobileActive: false,
  menuHoverActive: false,
  activeMenuItem: null
})

export function useLayout() {
  const setPrimary = (value) => {
    layoutConfig.primary = value
  }

  const setSurface = (value) => {
    layoutConfig.surface = value
  }

  const setPreset = (value) => {
    layoutConfig.preset = value
  }

  const setActiveMenuItem = (item) => {
    layoutState.activeMenuItem = item.value || item
  }

  const setMenuMode = (mode) => {
    layoutConfig.menuMode = mode
  }

  const toggleDarkMode = () => {
    if (!document.startViewTransition) {
      executeDarkModeToggle()
      return
    }

    document.startViewTransition(() => executeDarkModeToggle())
  }

  const executeDarkModeToggle = () => {
    layoutConfig.darkTheme = !layoutConfig.darkTheme
    document.documentElement.classList.toggle('app-dark')
  }

  const onMenuToggle = () => {
    if (layoutConfig.menuMode === 'overlay') {
      layoutState.overlayMenuActive = !layoutState.overlayMenuActive
    }

    if (window.innerWidth > 991) {
      layoutState.staticMenuInactive = !layoutState.staticMenuInactive
    } else {
      layoutState.staticMenuMobileActive = !layoutState.staticMenuMobileActive
    }
  }

  const resetMenu = () => {
    layoutState.overlayMenuActive = false
    layoutState.staticMenuMobileActive = false
    layoutState.menuHoverActive = false
  }

  const isSidebarActive = computed(() => layoutState.overlayMenuActive || layoutState.staticMenuMobileActive)

  const isDarkTheme = computed(() => layoutConfig.darkTheme)

  const isDesktop = computed(() => window.innerWidth > 991)

  return {
    layoutConfig: toRefs(layoutConfig),
    layoutState: toRefs(layoutState),
    setPrimary,
    setSurface,
    setPreset,
    setActiveMenuItem,
    setMenuMode,
    toggleDarkMode,
    onMenuToggle,
    resetMenu,
    isSidebarActive,
    isDarkTheme,
    isDesktop
  }
}
