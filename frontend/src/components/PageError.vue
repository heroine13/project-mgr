<template>
  <div class="page-error">
    <el-result
      icon="warning"
      :title="title"
      :sub-title="message"
    >
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: '页面加载失败'
  },
  message: {
    type: String,
    default: '抱歉，页面加载时出现错误，请稍后重试'
  }
})

const router = useRouter()

const goHome = () => {
  router.push('/dashboard')
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.page-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 40px;
}
</style>
