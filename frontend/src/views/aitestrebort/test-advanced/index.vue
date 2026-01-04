<template>
  <div class="test-advanced">
    <h1>高级功能测试页面</h1>
    <p>如果你能看到这个页面，说明路由配置是正确的。</p>
    <p>项目ID: {{ $route.params.projectId }}</p>
    <el-button @click="$router.back()">返回</el-button>
  </div>
</template>

<script setup lang="ts">
// 简单的测试页面
</script>

<style scoped>
.test-advanced {
  padding: 20px;
  text-align: center;
}
</style>