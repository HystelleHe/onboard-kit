import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Guide, GuideCreate } from '@/types'
import { guideApi } from '@/api'
import { ElMessage } from 'element-plus'

export const useGuideStore = defineStore('guide', () => {
  const guides = ref<Guide[]>([])
  const currentGuide = ref<Guide | null>(null)
  const loading = ref(false)

  const fetchGuides = async () => {
    loading.value = true
    try {
      const response = await guideApi.getGuides()
      guides.value = response.data
    } catch (error) {
      console.error('Fetch guides error:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchGuide = async (guideId: number) => {
    loading.value = true
    try {
      const response = await guideApi.getGuide(guideId)
      currentGuide.value = response.data
      return response.data
    } catch (error) {
      console.error('Fetch guide error:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  const createGuide = async (guideData: GuideCreate) => {
    loading.value = true
    try {
      const response = await guideApi.createGuide(guideData)
      guides.value.push(response.data)
      ElMessage.success('引导创建成功')
      return response.data
    } catch (error) {
      console.error('Create guide error:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  const updateGuide = async (guideId: number, guideData: Partial<Guide>) => {
    loading.value = true
    try {
      const response = await guideApi.updateGuide(guideId, guideData)
      const index = guides.value.findIndex((g) => g.id === guideId)
      if (index !== -1) {
        guides.value[index] = response.data
      }
      if (currentGuide.value?.id === guideId) {
        currentGuide.value = response.data
      }
      ElMessage.success('引导更新成功')
      return response.data
    } catch (error) {
      console.error('Update guide error:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  const deleteGuide = async (guideId: number) => {
    loading.value = true
    try {
      await guideApi.deleteGuide(guideId)
      guides.value = guides.value.filter((g) => g.id !== guideId)
      if (currentGuide.value?.id === guideId) {
        currentGuide.value = null
      }
      ElMessage.success('引导删除成功')
      return true
    } catch (error) {
      console.error('Delete guide error:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    guides,
    currentGuide,
    loading,
    fetchGuides,
    fetchGuide,
    createGuide,
    updateGuide,
    deleteGuide
  }
})
