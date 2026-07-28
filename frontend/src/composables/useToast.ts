/**
 * Toast 提示 composable
 *
 * 提供全局即时提示功能（无动画，2.5 秒自动消失）。
 * 通过 provide/inject 在 App.vue 层级提供。
 */

import { ref, inject, type InjectionKey, type Ref } from 'vue'

/** Toast 类型 */
export type ToastType = 'success' | 'error' | 'info'

/** Toast 消息 */
export interface ToastMessage {
  id: number
  text: string
  type: ToastType
}

/** Toast Store 接口 */
interface ToastStore {
  messages: Ref<ToastMessage[]>
  show: (text: string, type?: ToastType) => void
  remove: (id: number) => void
}

export const TOAST_KEY: InjectionKey<ToastStore> = Symbol('toast')

let nextId = 0

/** 创建 Toast Store（在 App.vue 中调用） */
export function createToastStore(): ToastStore {
  const messages = ref<ToastMessage[]>([])

  function show(text: string, type: ToastType = 'info') {
    const id = nextId++
    messages.value.push({ id, text, type })
    // 2.5 秒后自动移除
    setTimeout(() => remove(id), 2500)
  }

  function remove(id: number) {
    messages.value = messages.value.filter(m => m.id !== id)
  }

  return { messages, show, remove }
}

/** 在子组件中使用 Toast */
export function useToast() {
  const toastStore = inject(TOAST_KEY)
  if (!toastStore) {
    // 降级：如果没有 inject，返回空操作
    console.warn('useToast: Toast store not provided')
    return {
      success: (_text: string) => {},
      error: (_text: string) => {},
      info: (_text: string) => {}
    }
  }

  return {
    success(text: string) { toastStore.show(text, 'success') },
    error(text: string) { toastStore.show(text, 'error') },
    info(text: string) { toastStore.show(text, 'info') }
  }
}
