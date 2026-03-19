<template>
  <div class="guide-editor-v2">
    <div class="editor-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ isNew ? '新建引导' : '编辑引导' }}</h2>
      <div class="actions">
        <el-button @click="handleSave" :loading="saving">保存</el-button>
        <el-button type="primary" @click="handlePreview">预览</el-button>
      </div>
    </div>

    <div class="editor-content">
      <!-- 左侧：基础信息 + 步骤列表 -->
      <div class="left-panel">
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
                  <el-button @click="analyzePage" :loading="analyzing" type="primary">
                    分析页面
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-card>

          <el-card class="section-card">
            <template #header>
              <div class="card-header">
                <span>引导步骤 ({{ form.steps?.length || 0 }})</span>
                <el-button size="small" @click="addManualStep">+ 手动选择</el-button>
              </div>
            </template>

            <div v-if="!form.steps || form.steps.length === 0" class="empty-steps">
              <el-empty description="还没有步骤">
                <el-text type="info">点击右侧截图上的推荐区域添加</el-text>
              </el-empty>
            </div>

            <div v-else class="steps-list">
              <div
                v-for="(step, index) in form.steps"
                :key="index"
                :class="['step-item', { active: activeStepIndex === index }]"
                @click="activeStepIndex = index"
              >
                <div class="step-header">
                  <span class="step-number">{{ index + 1 }}</span>
                  <span class="step-title">{{ step.title || '未命名' }}</span>
                  <el-button
                    size="small"
                    type="danger"
                    text
                    @click.stop="removeStep(index)"
                  >
                    删除
                  </el-button>
                </div>
                <div class="step-detail">
                  <el-tag size="small" type="info">{{ step.element_selector }}</el-tag>
                  <el-tag v-if="step.is_manual_selection" size="small" type="warning">手动</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-form>
      </div>

      <!-- 右侧：截图预览 + 交互 -->
      <div class="right-panel">
        <div v-if="!screenshotData" class="empty-screenshot">
          <el-empty description="请输入URL并点击分析">
            <el-icon :size="48" color="#ccc"><Picture /></el-icon>
          </el-empty>
        </div>

        <div v-else class="screenshot-container">
          <div class="screenshot-header">
            <el-text type="info">💡 点击推荐区域快速添加步骤</el-text>
            <el-button size="small" @click="clearSelection">清除选择</el-button>
          </div>

          <div
            class="screenshot-wrapper"
            ref="screenshotWrapper"
            @mousedown="handleMouseDown"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
          >
            <img
              :src="screenshotData.screenshot"
              :style="{ width: screenshotData.width + 'px', height: screenshotData.height + 'px' }"
              class="screenshot-img"
              draggable="false"
            />

            <!-- 推荐区域高亮 -->
            <div
              v-for="(region, index) in suggestedRegions"
              :key="'suggested-' + index"
              :class="['region-box', 'suggested', { added: region.is_added }]"
              :style="{
                left: region.x + 'px',
                top: region.y + 'px',
                width: region.width + 'px',
                height: region.height + 'px'
              }"
              @click.stop="addStepFromRegion(region)"
            >
              <span class="region-label">{{ region.is_added ? '✓' : index + 1 }}</span>
              <div v-if="!region.is_added" class="region-tooltip">
                {{ region.title }}
                <br />
                <small>点击添加</small>
              </div>
            </div>

            <!-- 已添加的步骤区域 -->
            <template v-for="(step, index) in form.steps" :key="'step-' + index">
              <div
                v-if="step.screenshot_region"
                :class="['region-box', 'added-step', { active: activeStepIndex === index }]"
                :style="step.screenshot_region ? {
                  left: step.screenshot_region.x + 'px',
                  top: step.screenshot_region.y + 'px',
                  width: step.screenshot_region.width + 'px',
                  height: step.screenshot_region.height + 'px'
                } : {}"
                @click.stop="activeStepIndex = index"
              >
                <span class="region-label">{{ index + 1 }}</span>
              </div>
            </template>

            <!-- 手动框选区域 -->
            <div
              v-if="isSelecting && selectionBox"
              class="region-box selecting"
              :style="{
                left: selectionBox.x + 'px',
                top: selectionBox.y + 'px',
                width: selectionBox.width + 'px',
                height: selectionBox.height + 'px'
              }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 手动添加步骤对话框 -->
    <el-dialog
      v-model="manualDialogVisible"
      title="添加新步骤"
      width="500px"
    >
      <el-form :model="manualForm" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="manualForm.title" placeholder="请输入步骤标题" />
        </el-form-item>
        <el-form-item label="选择器">
          <el-input v-model="manualForm.element_selector" placeholder="#element-id 或 .class-name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="manualForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入步骤描述"
          />
        </el-form-item>
        <el-form-item label="提示位置">
          <el-select v-model="manualForm.position" placeholder="请选择位置">
            <el-option label="上方" value="top" />
            <el-option label="下方" value="bottom" />
            <el-option label="左侧" value="left" />
            <el-option label="右侧" value="right" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manualDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmManualStep">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useGuideStore } from '@/stores/guide'
import { screenshotApi } from '@/api'
import type { Guide, Step, ScreenshotRegion, ScreenshotAnalysisResponse } from '@/types'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const guideStore = useGuideStore()

const isNew = ref(!route.params.id)
const saving = ref(false)
const analyzing = ref(false)
const activeStepIndex = ref<number>(-1)

const form = reactive<Guide>({
  name: '',
  description: '',
  target_url: '',
  is_published: false,
  steps: []
})

// V2: 截图相关
const screenshotData = ref<ScreenshotAnalysisResponse | null>(null)
const suggestedRegions = ref<ScreenshotRegion[]>([])
const screenshotWrapper = ref<HTMLElement | null>(null)

// 手动框选相关
const isSelecting = ref(false)
const selectionStart = ref({ x: 0, y: 0 })
const selectionBox = ref<{ x: number; y: number; width: number; height: number } | null>(null)

// 手动添加对话框
const manualDialogVisible = ref(false)
const manualForm = reactive({
  title: '',
  element_selector: '',
  description: '',
  position: 'bottom' as const,
  screenshot_region: null as { x: number; y: number; width: number; height: number } | null
})

onMounted(async () => {
  if (!isNew.value) {
    const guideId = Number(route.params.id)
    const guide = await guideStore.fetchGuide(guideId)
    if (guide) {
      Object.assign(form, guide)
      // 如果有 target_url，自动分析
      if (guide.target_url) {
        await analyzePage()
      }
    }
  }
})

const goBack = () => {
  router.back()
}

// V2: 分析页面（使用截图 API）
const analyzePage = async () => {
  if (!form.target_url) {
    ElMessage.warning('请先输入目标URL')
    return
  }

  analyzing.value = true
  try {
    const guideId = isNew.value ? undefined : Number(route.params.id)
    const response = await screenshotApi.analyzeWithScreenshot({
      url: form.target_url,
      guide_id: guideId
    })
    screenshotData.value = response.data
    suggestedRegions.value = response.data.suggested_regions.map(r => ({
      ...r,
      is_added: false
    }))
    ElMessage.success('页面分析完成，点击推荐区域添加步骤')
  } catch (error) {
    console.error('Analyze page error:', error)
    ElMessage.error('页面分析失败')
  } finally {
    analyzing.value = false
  }
}

// V2: 从推荐区域添加步骤
const addStepFromRegion = (region: ScreenshotRegion) => {
  if (region.is_added) {
    ElMessage.info('该步骤已添加')
    return
  }

  const newStep: Omit<Step, 'id' | 'guide_id' | 'created_at'> = {
    order: form.steps.length + 1,
    title: region.title,
    description: `请${region.title}`,
    element_selector: region.selector,
    position: 'bottom',
    config: {},
    screenshot_region: {
      x: region.x,
      y: region.y,
      width: region.width,
      height: region.height
    },
    is_manual_selection: false
  }

  form.steps.push(newStep)
  region.is_added = true
  activeStepIndex.value = form.steps.length - 1
  ElMessage.success(`已添加步骤：${region.title}`)
}

// 手动添加步骤（按钮）
const addManualStep = () => {
  manualForm.title = ''
  manualForm.element_selector = ''
  manualForm.description = ''
  manualForm.position = 'bottom'
  manualForm.screenshot_region = null
  manualDialogVisible.value = true
}

// 确认手动添加
const confirmManualStep = () => {
  if (!manualForm.title || !manualForm.element_selector) {
    ElMessage.warning('请填写标题和选择器')
    return
  }

  const newStep: Omit<Step, 'id' | 'guide_id' | 'created_at'> = {
    order: form.steps.length + 1,
    title: manualForm.title,
    description: manualForm.description,
    element_selector: manualForm.element_selector,
    position: manualForm.position,
    config: {},
    screenshot_region: manualForm.screenshot_region || undefined,
    is_manual_selection: true
  }

  form.steps.push(newStep)
  manualDialogVisible.value = false
  activeStepIndex.value = form.steps.length - 1
  ElMessage.success('已添加手动步骤')
}

// 删除步骤
const removeStep = (index: number) => {
  const step = form.steps[index]
  
  // 如果是从推荐区域添加的，恢复推荐区域状态
  const regionData = step.screenshot_region
  if (!step.is_manual_selection && regionData) {
    const region = suggestedRegions.value.find(r => 
      r.x === regionData.x && 
      r.y === regionData.y
    )
    if (region) {
      region.is_added = false
    }
  }

  form.steps.splice(index, 1)
  // 重新排序
  form.steps.forEach((step, i) => {
    step.order = i + 1
  })
  
  if (activeStepIndex.value === index) {
    activeStepIndex.value = -1
  }
}

// 鼠标事件处理（手动框选）
const handleMouseDown = (e: MouseEvent) => {
  if (!screenshotWrapper.value) return
  
  const rect = screenshotWrapper.value.getBoundingClientRect()
  selectionStart.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  isSelecting.value = true
  selectionBox.value = {
    x: selectionStart.value.x,
    y: selectionStart.value.y,
    width: 0,
    height: 0
  }
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isSelecting.value || !screenshotWrapper.value || !selectionBox.value) return
  
  const rect = screenshotWrapper.value.getBoundingClientRect()
  const currentX = e.clientX - rect.left
  const currentY = e.clientY - rect.top
  
  selectionBox.value = {
    x: Math.min(selectionStart.value.x, currentX),
    y: Math.min(selectionStart.value.y, currentY),
    width: Math.abs(currentX - selectionStart.value.x),
    height: Math.abs(currentY - selectionStart.value.y)
  }
}

const handleMouseUp = () => {
  if (!isSelecting.value || !selectionBox.value) return
  
  // 如果框选区域足够大，打开手动添加对话框
  if (selectionBox.value.width > 30 && selectionBox.value.height > 30) {
    manualForm.screenshot_region = { ...selectionBox.value }
    manualForm.title = ''
    manualForm.element_selector = ''
    manualForm.description = ''
    manualForm.position = 'bottom'
    manualDialogVisible.value = true
  }
  
  isSelecting.value = false
  selectionBox.value = null
}

const clearSelection = () => {
  isSelecting.value = false
  selectionBox.value = null
}

// 保存
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
        router.push({ name: 'GuideEditV2', params: { id: guide.id } })
        isNew.value = false
      }
    } else {
      const guideId = Number(route.params.id)
      await guideStore.updateGuide(guideId, form)
      ElMessage.success('保存成功')
    }
  } finally {
    saving.value = false
  }
}

// 预览
const handlePreview = () => {
  if (!route.params.id) {
    ElMessage.warning('请先保存引导')
    return
  }
  router.push({ name: 'GuidePreview', params: { id: route.params.id } })
}
</script>

<style scoped>
.guide-editor-v2 {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px 20px;
  border-bottom: 1px solid #e8e8e8;
  background: #fff;
}

.editor-header h2 {
  flex: 1;
  margin: 0;
  font-size: 18px;
}

.actions {
  display: flex;
  gap: 10px;
}

.editor-content {
  flex: 1;
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 0;
  overflow: hidden;
}

.left-panel {
  overflow-y: auto;
  padding: 15px;
  background: #f5f7fa;
  border-right: 1px solid #e8e8e8;
}

.section-card {
  margin-bottom: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-steps {
  padding: 30px 0;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-item {
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.step-item:hover {
  border-color: #409eff;
}

.step-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.step-title {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.step-detail {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.right-panel {
  overflow: auto;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
}

.empty-screenshot {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.screenshot-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.screenshot-header {
  padding: 12px 20px;
  background: #2a2a2a;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.screenshot-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  padding: 20px;
}

.screenshot-img {
  display: block;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.region-box {
  position: absolute;
  border: 2px dashed;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.region-box.suggested {
  border-color: #409eff;
  background: rgba(64, 158, 255, 0.1);
}

.region-box.suggested:hover {
  background: rgba(64, 158, 255, 0.2);
  border-style: solid;
}

.region-box.suggested.added {
  border-color: #67c23a;
  border-style: solid;
  background: rgba(103, 194, 58, 0.15);
}

.region-box.added-step {
  border-color: #e6a23c;
  border-style: solid;
  background: rgba(230, 162, 60, 0.15);
}

.region-box.added-step.active {
  border-color: #f56c6c;
  background: rgba(245, 108, 108, 0.2);
  animation: pulse 1.5s infinite;
}

.region-box.selecting {
  border-color: #fff;
  border-style: dashed;
  background: rgba(255, 255, 255, 0.1);
}

.region-label {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.added-step .region-label {
  background: #e6a23c;
}

.added-step.active .region-label {
  background: #f56c6c;
}

.suggested.added .region-label {
  background: #67c23a;
}

.region-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #2a2a2a;
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s;
  margin-bottom: 8px;
  z-index: 10;
}

.region-box:hover .region-tooltip {
  opacity: 1;
  visibility: visible;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(245, 108, 108, 0);
  }
}
</style>
