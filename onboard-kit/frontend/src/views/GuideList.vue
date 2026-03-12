<template>
  <div class="guide-list">
    <div class="page-header">
      <h2>我的引导</h2>
      <el-button type="primary" @click="createNewGuide">
        <el-icon><plus /></el-icon>
        新建引导
      </el-button>
    </div>

    <div v-if="guideStore.loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="guideStore.guides.length === 0" class="empty">
      <el-empty description="还没有引导配置">
        <el-button type="primary" @click="createNewGuide">创建第一个引导</el-button>
      </el-empty>
    </div>

    <el-table v-else :data="guideStore.guides" style="width: 100%">
      <el-table-column prop="name" label="名称" min-width="200" />
      <el-table-column prop="target_url" label="目标URL" min-width="300" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_published ? 'success' : 'info'">
            {{ row.is_published ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="步骤数" width="100">
        <template #default="{ row }">
          {{ row.steps?.length || 0 }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="editGuide(row.id)">编辑</el-button>
          <el-button size="small" @click="previewGuide(row.id)">预览</el-button>
          <el-popconfirm
            title="确定要删除这个引导吗？"
            @confirm="deleteGuide(row.id)"
          >
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGuideStore } from '@/stores/guide'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const guideStore = useGuideStore()

onMounted(() => {
  guideStore.fetchGuides()
})

const createNewGuide = () => {
  router.push({ name: 'GuideNew' })
}

const editGuide = (guideId: number) => {
  router.push({ name: 'GuideEdit', params: { id: guideId } })
}

const previewGuide = (guideId: number) => {
  router.push({ name: 'GuidePreview', params: { id: guideId } })
}

const deleteGuide = async (guideId: number) => {
  await guideStore.deleteGuide(guideId)
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.guide-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.loading,
.empty {
  padding: 40px 0;
}
</style>
