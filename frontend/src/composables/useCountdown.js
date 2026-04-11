import { ref, onUnmounted } from 'vue'

export function useCountdown(seconds = 60) {
  const remaining = ref(0)
  const isCounting = ref(false)
  let timer = null

  function start() {
    remaining.value = seconds
    isCounting.value = true
    timer = setInterval(() => {
      remaining.value--
      if (remaining.value <= 0) {
        stop()
      }
    }, 1000)
  }

  function stop() {
    clearInterval(timer)
    timer = null
    remaining.value = 0
    isCounting.value = false
  }

  onUnmounted(stop)

  return { remaining, isCounting, start, stop }
}
