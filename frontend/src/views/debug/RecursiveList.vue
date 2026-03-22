<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  items: Array,
});
</script>

<template>
  <ul>
    <li v-for="item in items" :key="item.id">
      {{ item.name }}
      <!-- 如果有子项，递归地渲染当前组件 -->
      <RecursiveList v-if="item.children && item.children.length" :items="item.children" />
    </li>
  </ul>
</template>
