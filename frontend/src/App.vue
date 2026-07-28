<!--
  App.vue — 根组件
  提供 Toast 全局提示 + Router 视图
-->
<template>
  <router-view />
  <!-- 全局 Toast 提示（通过 provide/inject） -->
  <Toast />
</template>

<script setup lang="ts">
import { provide } from 'vue'
import { createToastStore, TOAST_KEY } from '@/composables/useToast'
import Toast from '@/components/ui/Toast.vue'

// 创建全局 Toast Store，通过 provide 注入到所有子组件
const toastStore = createToastStore()
provide(TOAST_KEY, toastStore)
</script>
