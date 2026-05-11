<template>
  <el-switch
    v-model="isDark"
    inline-prompt
    active-text="🌙"
    inactive-text="☀️"
    @change="toggleTheme"
  />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useStore } from 'pinia'

const store = useStore()
const isDark = ref(false)

const toggleTheme = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Initialize theme from localStorage
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else if (!savedTheme) {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }
})

// Watch for external theme changes
watch(() => store.theme, (newTheme) => {
  isDark.value = newTheme === 'dark'
  toggleTheme()
})
</script>