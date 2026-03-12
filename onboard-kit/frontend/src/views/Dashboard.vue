<template>
  <el-container class="dashboard-container">
    <el-header class="header">
      <div class="header-content">
        <h2 class="logo">OnboardKit</h2>
        <div class="user-info">
          <el-dropdown>
            <span class="user-name">
              {{ authStore.user?.full_name || authStore.user?.email }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <span v-if="authStore.user?.is_trial">
                    试用版 - {{ daysLeft }}天剩余
                  </span>
                  <span v-else>专业版</span>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <el-container>
      <el-aside width="200px" class="sidebar">
        <el-menu
          :default-active="currentRoute"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><list /></el-icon>
            <span>我的引导</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ArrowDown, List } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const currentRoute = computed(() => route.path)

const daysLeft = computed(() => {
  if (!authStore.user?.trial_expires_at) return 0
  const expiresAt = new Date(authStore.user.trial_expires_at)
  const now = new Date()
  const diff = expiresAt.getTime() - now.getTime()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
})

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'Login' })
}

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchCurrentUser()
  }
})
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.sidebar {
  background: #f5f7fa;
  border-right: 1px solid #e8e8e8;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.main-content {
  background: #fff;
  padding: 20px;
}
</style>
