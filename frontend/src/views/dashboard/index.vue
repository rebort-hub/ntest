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
  min-height: 100%;
  padding: 14px;
  background: var(--system-container-background);
  display: flex;
  justify-content: center;
}

.dashboard :deep(.dashboard-container) {
  width: 100%;
  max-width: 1440px;
}
</style>
