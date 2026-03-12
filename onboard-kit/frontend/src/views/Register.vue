<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">注册 OnboardKit</h1>
      <p class="subtitle">开始创建您的用户引导</p>

      <el-form :model="form" :rules="rules" ref="formRef" class="register-form">
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="邮箱"
            size="large"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
          />
        </el-form-item>

        <el-form-item prop="full_name">
          <el-input
            v-model="form.full_name"
            placeholder="姓名（可选）"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="company">
          <el-input
            v-model="form.company"
            placeholder="公司（可选）"
            size="large"
            prefix-icon="OfficeBuilding"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="register-button"
          :loading="loading"
          @click="handleRegister"
        >
          注册
        </el-button>

        <div class="footer">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
  full_name: '',
  company: ''
})

const rules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      const success = await authStore.register(form)
      loading.value = false

      if (success) {
        router.push({ name: 'Login' })
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.title {
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}

.register-form {
  margin-top: 20px;
}

.register-button {
  width: 100%;
  margin-top: 10px;
}

.footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.link {
  color: #667eea;
  text-decoration: none;
  margin-left: 5px;
}

.link:hover {
  text-decoration: underline;
}
</style>
