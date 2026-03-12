import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, UserCreate } from '@/types'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials)
      token.value = response.data.access_token
      localStorage.setItem('access_token', response.data.access_token)

      // 获取用户信息
      await fetchCurrentUser()

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const register = async (userData: UserCreate) => {
    try {
      await authApi.register(userData)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      console.error('Register error:', error)
      return false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    ElMessage.success('已退出登录')
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    } catch (error) {
      console.error('Fetch user error:', error)
      logout()
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})
