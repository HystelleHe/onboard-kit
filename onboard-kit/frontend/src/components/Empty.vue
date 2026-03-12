<template>
  <div class="empty-container">
    <el-empty :image-size="imageSize" :description="description">
      <slot></slot>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
interface Props {
  description?: string
  imageSize?: number
}

withDefaults(defineProps<Props>(), {
  description: '暂无数据',
  imageSize: 200
})
</script>

<style scoped>
.empty-container {
  padding: 40px;
}
</style>
