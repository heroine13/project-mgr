<template>
  <div class="ai-assistant">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🤖 AI 智能助手</span>
          <el-button size="small" @click="clearChat" link>清空对话</el-button>
        </div>
      </template>

      <div class="chat-container" ref="chatContainer">
        <div v-if="messages.length === 0" class="welcome-message">
          <h3>欢迎使用 AI 智能助手</h3>
          <p>我可以帮助您：</p>
          <ul>
            <li>📊 分析项目进度和风险</li>
            <li>💡 提供任务管理建议</li>
            <li>👥 分析团队绩效</li>
            <li>📝 生成会议纪要</li>
            <li>🔗 建议任务依赖关系</li>
          </ul>
          <p class="tip">请在下方输入您的问题</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text typing">
              <span class="dot">.</span>
              <span class="dot">.</span>
              <span class="dot">.</span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题..."
          @keydown.enter.ctrl="sendMessage"
          :disabled="loading"
        />
        <el-button
          type="primary"
          :loading="loading"
          @click="sendMessage"
          :disabled="!userInput.trim()"
        >
          发送
        </el-button>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <el-button
          v-for="action in quickActions"
          :key="action.label"
          size="small"
          @click="executeQuickAction(action.action)"
        >
          {{ action.label }}
        </el-button>
      </div>
    </el-card>

    <!-- Project Selector -->
    <el-dialog v-model="showProjectSelector" title="选择项目" width="400px">
      <el-select v-model="selectedProject" placeholder="选择项目" style="width: 100%">
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="showProjectSelector = false">取消</el-button>
        <el-button type="primary" @click="confirmProject">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const userInput = ref('')
const loading = ref(false)
const messages = ref([])
const chatContainer = ref(null)
const showProjectSelector = ref(false)
const selectedProject = ref(null)
const projects = ref([])
const currentAction = ref(null)

const quickActions = [
  { label: '📊 项目摘要', action: 'summarize' },
  { label: '💡 任务建议', action: 'suggestions' },
  { label: '👥 团队分析', action: 'team' },
  { label: '📝 会议纪要', action: 'notes' }
]

const formatMessage = (text) => {
  // Simple markdown-like formatting
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return

  const userMessage = userInput.value.trim()
  userInput.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  loading.value = true
  scrollToBottom()

  try {
    const response = await api.post('/ai/chat', {
      message: userMessage,
      project_id: selectedProject.value
    })

    messages.value.push({
      role: 'assistant',
      content: response.message,
      timestamp: new Date()
    })
  } catch (error) {
    ElMessage.error('AI 响应失败，请稍后重试')
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我暂时无法回答您的问题。请稍后重试。',
      timestamp: new Date()
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const executeQuickAction = async (action) => {
  currentAction.value = action

  if (action === 'summarize' || action === 'suggestions' || action === 'team') {
    // Need to select a project first
    showProjectSelector.value = true
    await fetchProjects()
  } else {
    // Execute directly
    if (action === 'notes') {
      userInput.value = '请帮我生成会议纪要'
      sendMessage()
    }
  }
}

const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/overview/summary')
    projects.value = response.projects || []
  } catch (error) {
    console.error('获取项目失败', error)
    projects.value = []
  }
}

const confirmProject = () => {
  if (!selectedProject.value) {
    ElMessage.warning('请选择一个项目')
    return
  }

  showProjectSelector.value = false

  switch (currentAction.value) {
    case 'summarize':
      userInput.value = '请帮我总结这个项目的状态'
      break
    case 'suggestions':
      userInput.value = '请给我一些任务建议'
      break
    case 'team':
      userInput.value = '请分析团队绩效'
      break
  }

  sendMessage()
}

const clearChat = () => {
  messages.value = []
}

onMounted(() => {
  // Check for stored project
  const storedProject = localStorage.getItem('ai_assistant_project')
  if (storedProject) {
    selectedProject.value = parseInt(storedProject)
  }
})
</script>

<style scoped>
.ai-assistant {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-container {
  height: 400px;
  overflow-y: auto;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 15px;
}

.welcome-message {
  text-align: center;
  color: #606266;
  padding: 20px;
}

.welcome-message h3 {
  color: #409eff;
  margin-bottom: 15px;
}

.welcome-message ul {
  text-align: left;
  display: inline-block;
  list-style: none;
  padding: 0;
}

.welcome-message li {
  margin: 8px 0;
}

.tip {
  margin-top: 20px;
  color: #909399;
  font-size: 12px;
}

.message {
  display: flex;
  margin-bottom: 15px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin: 0 10px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.message.assistant .message-avatar {
  background: #409eff;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: #fff;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  word-break: break-word;
}

.message.user .message-text {
  background: #409eff;
  color: #fff;
}

.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 5px;
}

.message.user .message-time {
  text-align: right;
}

.typing .dot {
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing .dot:nth-child(1) { animation-delay: -0.32s; }
.typing .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area .el-input {
  flex: 1;
}

.quick-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quick-actions .el-button {
  margin: 0;
}
</style>