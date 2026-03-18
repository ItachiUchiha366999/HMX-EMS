<template>
  <div
    class="skeleton"
    :style="{
      width: circle ? height : width,
      height: height,
      borderRadius: circle ? '50%' : borderRadius,
    }"
  />
</template>

<script setup>
defineProps({
  width: {
    type: String,
    default: '100%',
  },
  height: {
    type: String,
    default: '16px',
  },
  borderRadius: {
    type: String,
    default: 'var(--radius-lg)',
  },
  circle: {
    type: Boolean,
    default: false,
  },
})
</script>
