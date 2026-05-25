import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const MOBILE_BREAKPOINT = 768

export function useMobile() {
  const viewportWidth = ref(typeof window !== 'undefined' ? window.innerWidth : MOBILE_BREAKPOINT + 1)

  const updateViewportWidth = () => {
    viewportWidth.value = window.innerWidth
  }

  onMounted(() => {
    updateViewportWidth()
    window.addEventListener('resize', updateViewportWidth)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', updateViewportWidth)
  })

  const isMobileView = computed(() => viewportWidth.value <= MOBILE_BREAKPOINT)

  return {
    viewportWidth,
    isMobileView,
    mobileBreakpoint: MOBILE_BREAKPOINT
  }
}
