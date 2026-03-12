<template>
  <div class="guide-editor">
    <div class="editor-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ isNew ? '新建引导' : '编辑引导' }}</h2>
      <div class="actions">
        <el-button @click="handleSave" :loading="saving">保存</el-button>
        <el-button type="primary" @click="handlePreview">预览</el-button>
      </div>
    </div>

    <div class="editor-content">
      <div class="config-panel">
        <el-form :model="form" label-width="100px" label-position="left">
          <el-card class="section-card">
            <template #header>
              <span>基础信息</span>
            </template>

            <el-form-item label="引导名称">
              <el-input v-model="form.name" placeholder="请输入引导名称" />
            </el-form-item>

            <el-form-item label="描述">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="2"
                placeholder="请输入描述（可选）"
              />
            </el-form-item>

            <el-form-item label="目标URL">
              <el-input v-model="form.target_url" placeholder="https://example.com">
                <template #append>
                  <el-button @click="analyzePage" :loading="analyzing">分析页面</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-card>

          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>引导步骤</span>
                <el-button size="small" type="primary" @click="addStep">添加步骤</el-button>
              </div>
            </template>

            <div v-if="form.steps.length === 0" class="empty-steps">
              <el-empty description="还没有步骤">
                <el-button type="primary" @click="addStep">添加第一个步骤</el-button>
              </el-empty>
            </div>

            <el-collapse v-else v-model="activeStep">
              <el-collapse-item
                v-for="(step, index) in form.steps"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="step-title">
                    <span class="step-number">步骤 {{ index + 1 }}</span>
                    <span class="step-name">{{ step.title || '未命名' }}</span>
                    <el-button
                      size="small"
                      type="danger"
                      text
                      @click.stop="removeStep(index)"
                    >
                      删除
                    </el-button>
                  </div>
                </template>

                <el-form-item label="标题">
                  <el-input v-model="step.title" placeholder="请输入步骤标题" />
                </el-form-item>

                <el-form-item label="描述">
                  <el-input
                    v-model="step.description"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入步骤描述"
                  />
                </el-form-item>

                <el-form-item label="元素选择器">
                  <el-input
                    v-model="step.element_selector"
                    placeholder="#element-id 或 .class-name"
                  />
                  <div v-if="suggestedElements.length > 0" class="suggestions">
                    <el-text size="small">建议的元素：</el-text>
                    <el-tag
                      v-for="(elem, i) in suggestedElements.slice(0, 5)"
                      :key="i"
                      size="small"
                      style="margin: 5px"
                      @click="step.element_selector = elem.selector"
                    >
                      {{ elem.title }}
                    </el-tag>
                  </div>
                </el-form-item>

                <el-form-item label="提示位置">
                  <el-select v-model="step.position" placeholder="请选择位置">
                    <el-option label="上方" value="top" />
                    <el-option label="下方" value="bottom" />
                    <el-option label="左侧" value="left" />
                    <el-option label="右侧" value="right" />
                  </el-select>
                </el-form-item>

                <el-form-item label="顺序">
                  <el-input-number v-model="step.order" :min="1" />
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </el-card>

          <el-card class="section-card">
            <template #header>
              <span>高级配置</span>
            </template>

            <el-form-item label="发布状态">
              <el-switch v-model="form.is_published" />
            </el-form-item>
          </el-card>
        </el-form>
      </div>

      <div class="preview-panel">
        <div class="preview-header">
          <h3>预览</h3>
          <el-text size="small" type="info">保存后可查看完整预览</el-text>
        </div>
        <div class="preview-content">
          <iframe
            v-if="form.target_url"
            :src="form.target_url"
            frameborder="0"
            class="preview-iframe"
          />
          <el-empty v-else description="请输入目标URL" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGuideStore } from '@/stores/guide'
import { pageApi } from '@/api'
import type { Guide, Step, SuggestedElement } from '@/types'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const guideStore = useGuideStore()

const isNew = ref(!route.params.id)
const saving = ref(false)
const analyzing = ref(false)
const activeStep = ref<number[]>([])
const suggestedElements = ref<SuggestedElement[]>([])

const form = reactive<Partial<Guide>>({
  name: '',
  description: '',
  target_url: '',
  is_published: false,
  steps: []
})

onMounted(async () => {
  if (!isNew.value) {
    const guideId = Number(route.params.id)
    const guide = await guideStore.fetchGuide(guideId)
    if (guide) {
      Object.assign(form, guide)
    }
  }
})

const goBack = () => {
  router.back()
}

const addStep = () => {
  const newStep: Omit<Step, 'id' | 'guide_id' | 'created_at'> = {
    order: form.steps!.length + 1,
    title: '',
    description: '',
    element_selector: '',
    position: 'bottom',
    config: {}
  }
  form.steps!.push(newStep)
  activeStep.value = [form.steps!.length - 1]
}

const removeStep = (index: number) => {
  form.steps!.splice(index, 1)
  // 重新排序
  form.steps!.forEach((step, i) => {
    step.order = i + 1
  })
}

const analyzePage = async () => {
  if (!form.target_url) {
    ElMessage.warning('请先输入目标URL')
    return
  }

  analyzing.value = true
  try {
    const response = await pageApi.analyzePage({ url: form.target_url })
    suggestedElements.value = response.data.suggested_elements || []
    ElMessage.success('页面分析完成')
  } catch (error) {
    console.error('Analyze page error:', error)
  } finally {
    analyzing.value = false
  }
}

const handleSave = async () => {
  if (!form.name) {
    ElMessage.warning('请输入引导名称')
    return
  }

  if (!form.target_url) {
    ElMessage.warning('请输入目标URL')
    return
  }

  saving.value = true
  try {
    if (isNew.value) {
      const guide = await guideStore.createGuide(form as any)
      if (guide) {
        router.push({ name: 'GuideEdit', params: { id: guide.id } })
        isNew.value = false
      }
    } else {
      const guideId = Number(route.params.id)
      await guideStore.updateGuide(guideId, form)
    }
  } finally {
    saving.value = false
  }
}

const handlePreview = () => {
  if (!route.params.id) {
    ElMessage.warning('请先保存引导')
    return
  }
  router.push({ name: 'GuidePreview', params: { id: route.params.id } })
}
</script>

<style scoped>
.guide-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-bottom: 1px solid #e8e8e8;
}

.editor-header h2 {
  flex: 1;
  margin: 0;
}

.actions {
  display: flex;
  gap: 10px;
}

.editor-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  overflow: hidden;
}

.config-panel {
  overflow-y: auto;
  padding: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-steps {
  padding: 20px 0;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.step-number {
  font-weight: bold;
  color: #667eea;
}

.step-name {
  color: #666;
}

.suggestions {
  margin-top: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.preview-panel {
  display: flex;
  flex-direction: column;
  border-left: 1px solid #e8e8e8;
  background: #f5f7fa;
}

.preview-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
}

.preview-header h3 {
  margin: 0;
}

.preview-content {
  flex: 1;
  padding: 20px;
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 4px;
}
</style>
