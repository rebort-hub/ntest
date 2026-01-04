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
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}
</style>
