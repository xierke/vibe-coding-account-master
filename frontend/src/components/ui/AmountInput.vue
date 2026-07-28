<!--
  AmountInput.vue — 金额输入组件
  大字号金额显示 + ¥ 货币符号前缀
  支持 v-model，自动处理千分位格式化
-->
<template>
  <div class="amount-input-wrapper" :class="{ 'amount-focus': isFocused }">
    <span class="currency-symbol">¥</span>
    <input
      ref="inputRef"
      type="text"
      inputmode="decimal"
      class="amount-input"
      :value="displayValue"
      :placeholder="placeholder"
      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  /** v-model 绑定的金额（数字） */
  modelValue: number | null
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const isFocused = ref(false)

/** 显示值：聚焦时显示原始数字，失焦时显示千分位格式 */
const displayValue = computed(() => {
  if (props.modelValue === null || props.modelValue === undefined) return ''
  if (isFocused.value) {
    return String(props.modelValue)
  }
  // 失焦时显示千分位
  return props.modelValue.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
})

function onFocus() {
  isFocused.value = true
}

function onBlur() {
  isFocused.value = false
}

function onInput(e: Event) {
  const target = e.target as HTMLInputElement
  // 移除千分位逗号和空格，只保留数字和小数点
  let raw = target.value.replace(/[^0-9.]/g, '')

  // 确保只有一个小数点
  const parts = raw.split('.')
  if (parts.length > 2) {
    raw = parts[0] + '.' + parts.slice(1).join('')
  }

  // 限制小数点后两位
  if (parts.length === 2 && parts[1].length > 2) {
    raw = parts[0] + '.' + parts[1].slice(0, 2)
  }

  const num = parseFloat(raw)
  emit('update:modelValue', isNaN(num) ? null : num)
}

/** 自动聚焦输入框（供父组件调用） */
function focus() {
  inputRef.value?.focus()
}

defineExpose({ focus })
</script>

<style scoped>
.amount-input-wrapper {
  display: flex;
  align-items: center;
  border: 2px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  padding: 16px 20px;
  height: 72px;
}

.amount-input-wrapper.amount-focus {
  border-color: var(--color-primary);
}

.currency-symbol {
  font-size: var(--font-2xl);
  color: var(--text-secondary);
  margin-right: 8px;
  flex-shrink: 0;
  font-weight: 500;
}

.amount-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: var(--font-4xl);
  font-weight: 600;
  color: var(--text-primary);
  outline: none;
  width: 100%;
  min-width: 0;
  font-family: var(--font-family);
}

.amount-input::placeholder {
  font-size: var(--font-base);
  font-weight: 400;
  color: var(--text-disabled);
}
</style>
