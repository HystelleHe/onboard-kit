<template>
  <div class="loading-container">
    <el-icon class="is-loading" :size="size">
      <Loading />
    </el-icon>
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  size?: number
  text?: string
}

withDefaults(defineProps<Props>(), {
  size: 40,
  text: '加载中...'
})
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-text {
  margin-top: 10px;
  color: #999;
}
</style>
