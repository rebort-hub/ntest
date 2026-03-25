<template>
  <div class="dashboard">
    <Card/>
  </div>
</template>

<script lang="ts" setup>
import Card from './card.vue'
</script>

<style lang="scss" scoped>
.dashboard {
  box-sizing: border-box;
  width: 100%;
  min-height: 100%;
  padding: 14px;
  background: var(--system-container-background);
}
</style>
