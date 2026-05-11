<template>
  <div class="task-comments">
    <div class="comments-header">
      <h3>评论 ({{ comments.length }})</h3>
      <div class="header-actions">
        <el-button
          size="small"
          icon="el-icon-refresh"
          @click="refreshComments"
          :loading="isLoading"
        >
          刷新
        </el-button>
        <el-button
          size="small"
          icon="el-icon-sort"
          @click="toggleSortOrder"
        >
          {{ sortAscending ? '最新优先' : '最早优先' }}
        </el-button>
      </div>
    </div>
    
    <!-- 评论输入框 -->
    <div class="comment-input">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="添加评论... (支持@提及成员)"
        :autosize="{ minRows: 3, maxRows: 6 }"
        @focus="handleInputFocus"
        @blur="handleInputBlur"
        @input="handleInputTyping"
      />
      
      <div class="input-actions">
        <div class="mention-selector">
          <el-button
            size="small"
            icon="el-icon-user"
            @click="toggleMentionSelector"
          >
            提及
          </el-button>
          <div v-if="showMentionSelector" class="mention-dropdown">
            <div
              v-for="user in projectUsers"
              :key="user.id"
              class="mention-option"
              @click="insertMention(user)"
            >
              <el-avatar size="small" :src="user.avatar">
                {{ user.name.charAt(0) }}
              </el-avatar>
              <span class="user-name">{{ user.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="reaction-selector">
          <el-button
            size="small"
            icon="el-icon-star-off"
            @click="toggleReactionSelector"
          >
            表情
          </el-button>
          <div v-if="showReactionSelector" class="reaction-dropdown">
            <div
              v-for="reaction in reactionTypes"
              :key="reaction.type"
              class="reaction-option"
              @click="insertReaction(reaction.emoji)"
            >
              <span class="reaction-emoji">{{ reaction.emoji }}</span>
              <span class="reaction-name">{{ reaction.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="submit-action">
          <el-button
            type="primary"
            size="small"
            :loading="isSubmitting"
            @click="submitComment"
            :disabled="!newComment.trim()"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 评论列表 -->
    <div class="comments-list">
      <el-scrollbar>
        <div v-if="comments.length === 0" class="empty-comments">
          <el-empty description="暂无评论，快来添加第一条评论吧！" />
        </div>
        
        <div
          v-for="comment in sortedComments"
          :key="comment.id"
          class="comment-item"
          :class="{ 'comment-mentioned': isMentioned(comment) }"
        >
          <div class="comment-header">
            <div class="comment-user">
              <el-avatar
                size="small"
                :src="comment.user?.avatar"
                :style="{ backgroundColor: getUserColor(comment.user_id) }"
              >
                {{ comment.user?.name?.charAt(0) || '?' }}
              </el-avatar>
              <div class="user-info">
                <span class="user-name">{{ comment.user?.name || `用户${comment.user_id}` }}</span>
                <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
              </div>
            </div>
            
            <div class="comment-actions">
              <el-dropdown @command="handleCommentCommand(comment.id, $event)">
                <el-button size="small" icon="el-icon-more" circle />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="reply">回复</el-dropdown-item>
                    <el-dropdown-item command="edit" v-if="comment.user_id === currentUserId">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete" v-if="comment.user_id === currentUserId">删除</el-dropdown-item>
                    <el-dropdown-item command="copy">复制内容</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <div class="comment-content">
            <div v-if="comment.is_edited" class="edited-badge">
              <el-tag size="small" type="info">已编辑</el-tag>
            </div>
            <div class="content-text" v-html="renderCommentContent(comment.content)"></div>
            
            <!-- 提及用户标签 -->
            <div v-if="comment.mentions" class="mention-tags">
              <el-tag
                v-for="userId in parseMentions(comment.mentions)"
                :key="userId"
                size="small"
                type="info"
                class="mention-tag"
              >
                @{{ getUserName(userId) }}
              </el-tag>
            </div>
          </div>
          
          <!-- 反应区域 -->
          <div class="comment-reactions">
            <div
              v-for="reaction in comment.reactions || []"
              :key="reaction.id"
              class="reaction-item"
              :class="{ 'reaction-active': reaction.user_id === currentUserId }"
              @click="toggleReaction(comment.id, reaction.reaction_type)"
            >
              <span class="reaction-emoji">{{ getReactionEmoji(reaction.reaction_type) }}</span>
              <span class="reaction-count" v-if="getReactionCount(comment.id, reaction.reaction_type) > 1">
                {{ getReactionCount(comment.id, reaction.reaction_type) }}
              </span>
            </div>
            
            <el-dropdown @command="handleAddReaction(comment.id, $event)">
              <el-button size="small" icon="el-icon-plus" circle />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="reaction in reactionTypes"
                    :key="reaction.type"
                    :command="reaction.type"
                  >
                    <span class="reaction-emoji">{{ reaction.emoji }}</span>
                    {{ reaction.name }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
            <div
              v-for="reply in comment.replies"
              :key="reply.id"
              class="reply-item"
            >
              <div class="reply-header">
                <el-avatar
                  size="small"
                  :src="reply.user?.avatar"
                  :style="{ backgroundColor: getUserColor(reply.user_id) }"
                >
                  {{ reply.user?.name?.charAt(0) || '?' }}
                </el-avatar>
                <div class="reply-info">
                  <span class="user-name">{{ reply.user?.name || `用户${reply.user_id}` }}</span>
                  <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                </div>
              </div>
              <div class="reply-content" v-html="renderCommentContent(reply.content)"></div>
            </div>
          </div>
        </div>
        
        <!-- 加载更多 -->
        <div v-if="hasMoreComments" class="load-more">
          <el-button
            type="text"
            @click="loadMoreComments"
            :loading="isLoading"
          >
            加载更多评论
          </el-button>
        </div>
      </el-scrollbar>
    </div>
    
    <!-- 正在输入的用户 -->
    <div v-if="typingUsers.length > 0" class="typing-users">
      <div class="typing-indicator">
        <span class="typing-text">
          {{ formatTypingUsers(typingUsers) }} 正在输入...
        </span>
        <div class="typing-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useWebSocket } from '@/websocket/websocket'
import type { Comment, TypingStatus } from '@/types/gantt'
import type { ReactionType } from '@/types/websocket'

interface Props {
  taskId: number
  projectId: number
  currentUserId: number
}

interface User {
  id: number
  name: string
  avatar?: string
}

const props = defineProps<Props>()

// WebSocket
const { sendComment, sendTypingStatus, sendReaction, on, off } = useWebSocket()

// 状态
const comments = ref<Comment[]>([])
const newComment = ref('')
const isSubmitting = ref(false)
const isLoading = ref(false)
const sortAscending = ref(false) // false: 最新优先, true: 最早优先
const showMentionSelector = ref(false)
const showReactionSelector = ref(false)
const typingUsers = ref<TypingStatus[]>([])
const hasMoreComments = ref(false)
const commentPage = ref(1)
const commentLimit = 20

// 项目用户（简化，实际应该从API获取）
const projectUsers = ref<User[]>([
  { id: 1, name: '张工', avatar: '' },
  { id: 2, name: '李工', avatar: '' },
  { id: 3, name: '王经理', avatar: '' },
  { id: 4, name: '赵总监', avatar: '' }
])

// 反应类型
const reactionTypes = ref([
  { type: 'like', name: '点赞', emoji: '👍' },
  { type: 'love', name: '爱心', emoji: '❤️' },
  { type: 'laugh', name: '大笑', emoji: '😄' },
  { type: 'wow', name: '惊讶', emoji: '😮' },
  { type: 'sad', name: '难过', emoji: '😢' },
  { type: 'angry', name: '生气', emoji: '😠' }
])

// 计算属性
const sortedComments = computed(() => {
  const sorted = [...comments.value]
  sorted.sort((a, b) => {
    const timeA = new Date(a.created_at).getTime()
    const timeB = new Date(b.created_at).getTime()
    return sortAscending.value ? timeA - timeB : timeB - timeA
  })
  return sorted
})

// 生命周期
onMounted(() => {
  loadComments()
  setupWebSocketListeners()
})

onUnmounted(() => {
  // 清除输入状态
  sendTypingStatus(props.taskId, false)
})

// 设置WebSocket监听器
const setupWebSocketListeners = () => {
  // 监听新评论
  on('new_comment', (event: any) => {
    if (event.data.task_id === props.taskId) {
      comments.value.unshift(event.data)
    }
  })
  
  // 监听用户输入状态
  on('user_typing', (event: any) => {
    if (event.data.task_id === props.taskId) {
      updateTypingUsers(event.data)
    }
  })
  
  // 监听反应
  on('reaction', (event: any) => {
    if (event.data.comment_id) {
      updateCommentReaction(event.data)
    }
  })
  
  // 监听提及通知
  on('mention_notification', (event: any) => {
    if (event.data.mentioned_user_id === props.currentUserId) {
      showMentionNotification(event.data)
    }
  })
}

// 加载评论
const loadComments = async () => {
  isLoading.value = true
  try {
    // TODO: 调用API获取评论
    // 暂时使用模拟数据
    comments.value = [
      {
        id: 1,
        task_id: props.taskId,
        project_id: props.projectId,
        user_id: 1,
        content: '这个任务进度不错，继续保持！',
        mentions: '2,3',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_edited: 0,
        parent_id: null,
        user: { id: 1, name: '张工' },
        replies: [],
        reactions: [
          { id: 1, comment_id: 1, user_id: 2, reaction_type: 'like', created_at: new Date().toISOString() }
        ]
      },
      {
        id: 2,
        task_id: props.taskId,
        project_id: props.projectId,
        user_id: 2,
        content: '@张工 好的，我会注意时间节点',
        mentions: '1',
        created_at: new Date(Date.now() - 3600000).toISOString(),
        updated_at: new Date(Date.now() - 3600000).toISOString(),
        is_edited: 0,
        parent_id: null,
        user: { id: 2, name: '李工' },
        replies: [],
        reactions: []
      }
    ]
    
    hasMoreComments.value = comments.value.length >= commentLimit
  } catch (error) {
    console.error('加载评论失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 提交评论
const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  isSubmitting.value = true
  
  try {
    // 提取提及的用户ID
    const mentions = extractMentions(newComment.value)
    
    // 发送WebSocket消息
    const success = sendComment(props.taskId, newComment.value, mentions)
    
    if (success) {
      // 添加临时评论到列表
      const tempComment: Comment = {
        id: Date.now(), // 临时ID
        task_id: props.taskId,
        project_id: props.projectId,
        user_id: props.currentUserId,
        content: newComment.value,
        mentions: mentions.join(','),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_edited: 0,
        parent_id: null,
        user: { 
          id: props.currentUserId, 
          name: '当前用户' 
        }
      }
      
      comments.value.unshift(tempComment)
      newComment.value = ''
      
      // 清除输入状态
      sendTypingStatus(props.taskId, false)
      
      // TODO: 实际应该等待服务器确认后更新评论ID
    }
  } catch (error) {
    console.error('提交评论失败:', error)
  } finally {
    isSubmitting.value = false
  }
}

// 处理输入状态
const handleInputFocus = () => {
  sendTypingStatus(props.taskId, true)
}

const handleInputBlur = () => {
  // 延迟清除输入状态，避免频繁切换
  setTimeout(() => {
    sendTypingStatus(props.taskId, false)
  }, 1000)
}

const handleInputTyping = () => {
  // 每次输入都更新输入状态
  sendTypingStatus(props.taskId, true)
  
  // 重置清除计时器
  clearTimeout(typingTimer)
  typingTimer = setTimeout(() => {
    sendTypingStatus(props.taskId, false)
  }, 3000)
}

let typingTimer: number

// 更新输入用户列表
const updateTypingUsers = (typingData: any) => {
  const existingIndex = typingUsers.value.findIndex(
    user => user.user_id === typingData.user_id
  )
  
  if (typingData.is_typing) {
    if (existingIndex === -1) {
      typingUsers.value.push({
        user_id: typingData.user_id,
        task_id: typingData.task_id,
        is_typing: 1,
        last_activity: new Date().toISOString(),
        user_name: `用户${typingData.user_id}`
      })
    } else {
      typingUsers.value[existingIndex].last_activity = new Date().toISOString()
    }
  } else {
    if (existingIndex !== -1) {
      typingUsers.value.splice(existingIndex, 1)
    }
  }
  
  // 清理超过10秒没有活动的用户
  const now = new Date().getTime()
  typingUsers.value = typingUsers.value.filter(user => {
    const lastActivity = new Date(user.last_activity).getTime()
    return now - lastActivity < 10000
  })
}

// 切换反应
const toggleReaction = (commentId: number, reactionType: string) => {
  // 检查用户是否已经添加了这个反应
  const comment = comments.value.find(c => c.id === commentId)
  if (!comment) return
  
  const existingReaction = comment.reactions?.find(
    r => r.user_id === props.currentUserId && r.reaction_type === reactionType
  )
  
  if (existingReaction) {
    // 移除反应
    sendReaction(commentId, reactionType, 'remove')
  } else {
    // 添加反应
    sendReaction(commentId, reactionType, 'add')
  }
}

// 更新评论反应
const updateCommentReaction = (reactionData: any) => {
  const comment = comments.value.find(c => c.id === reactionData.comment_id)
  if (!comment) return
  
  if (!comment.reactions) {
    comment.reactions = []
  }
  
  if (reactionData.action === 'add') {
    // 添加或更新反应
    const existingIndex = comment.reactions.findIndex(
      r => r.user_id === reactionData.user_id
    )
    
    if (existingIndex === -1) {
      comment.reactions.push({
        id: Date.now(), // 临时ID
        comment_id: reactionData.comment_id,
        user_id: reactionData.user_id,
        reaction_type: reactionData.reaction,
        created_at: new Date().toISOString()
      })
    } else {
      comment.reactions[existingIndex].reaction_type = reactionData.reaction
      comment.reactions[existingIndex].created_at = new Date().toISOString()
    }
  } else {
    // 移除反应
    comment.reactions = comment.reactions.filter(
      r => r.user_id !== reactionData.user_id
    )
  }
}

// 辅助函数
const extractMentions = (text: string): number[] => {
  const mentionRegex = /@(\w+)/g
  const matches = text.match(mentionRegex) || []
  
  const userIds: number[] = []
  matches.forEach(match => {
    const username = match.substring(1)
    const user = projectUsers.value.find(u => u.name === username)
    if (user) {
      userIds.push(user.id)
    }
  })
  
  return userIds
}

const parseMentions = (mentions: string): number[] => {
  if (!mentions) return []
  return (mentions || '').split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
}

const insertMention = (user: User) => {
  const textarea = document.querySelector('.comment-input textarea') as HTMLTextAreaElement
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const mentionText = `@${user.name} `
    
    newComment.value = 
      newComment.value.substring(0, start) + 
      mentionText + 
      newComment.value.substring(end)
    
    // 移动光标到插入位置之后
    setTimeout(() => {
      textarea.focus()
      textarea.selectionStart = textarea.selectionEnd = start + mentionText.length
    }, 0)
  }
  
  showMentionSelector.value = false
}

const insertReaction = (emoji: string) => {
  newComment.value += ` ${emoji} `
  showReactionSelector.value = false
}

const renderCommentContent = (content: string): string => {
  // 转换提及为链接或高亮
  let rendered = content.replace(/@(\w+)/g, '<span class="mention-highlight">@$1</span>')
  
  // 转换URL为链接
  rendered = rendered.replace(
    /(https?:\/\/[^\s]+)/g,
    '<a href="$1" target="_blank" class="comment-link">$1</a>'
  )
  
  // 转换换行
  rendered = rendered.replace(/\n/g, '<br>')
  
  return rendered
}

const formatTime = (time: string): string => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const formatTypingUsers = (users: TypingStatus[]): string => {
  if (users.length === 0) return ''
  if (users.length === 1) return users[0].user_name || `用户${users[0].user_id}`
  if (users && users.length === 2) return users.map(u => u.user_name || `用户${u.user_id}`).join('和')
  return `${users[0].user_name || `用户${users[0].user_id}`}等${users.length}人`
}

const getUserColor = (userId: number): string => {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3']
  return colors[userId % colors.length]
}

const getUserName = (userId: number): string => {
  const user = projectUsers.value.find(u => u.id === userId)
  return user ? user.name : `用户${userId}`
}

const getReactionEmoji = (reactionType: string): string => {
  const reaction = reactionTypes.value.find(r => r.type === reactionType)
  return reaction ? reaction.emoji : '👍'
}

const getReactionCount = (commentId: number, reactionType: string): number => {
  const comment = comments.value.find(c => c.id === commentId)
  if (!comment || !comment.reactions) return 0
  return comment.reactions.filter(r => r.reaction_type === reactionType).length
}

const isMentioned = (comment: Comment): boolean => {
  if (!comment.mentions) return false
  const mentionedIds = parseMentions(comment.mentions)
  return mentionedIds.includes(props.currentUserId)
}

const showMentionNotification = (mentionData: any) => {
  // TODO: 显示提及通知
  console.log('您被提及了:', mentionData)
}

// UI操作
const toggleSortOrder = () => {
  sortAscending.value = !sortAscending.value
}

const toggleMentionSelector = () => {
  showMentionSelector.value = !showMentionSelector.value
  if (showMentionSelector.value) {
    showReactionSelector.value = false
  }
}

const toggleReactionSelector = () => {
  showReactionSelector.value = !showReactionSelector.value
  if (showReactionSelector.value) {
    showMentionSelector.value = false
  }
}

const refreshComments = () => {
  loadComments()
}

const loadMoreComments = () => {
  commentPage.value++
  // TODO: 加载更多评论
}

const handleCommentCommand = (commentId: number, command: string) => {
  switch (command) {
    case 'reply':
      // 回复评论
      newComment.value = `回复评论: `
      break
    case 'edit':
      // 编辑评论
      break
    case 'delete':
      // 删除评论
      break
    case 'copy':
      // 复制内容
      break
  }
}

const handleAddReaction = (commentId: number, reactionType: string) => {
  sendReaction(commentId, reactionType, 'add')
}
</script>

<style scoped>
.task-comments {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-left: 1px solid #e8e8e8;
  background-color: #ffffff;
}

.comments-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fafafa;
}

.comments-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.comment-input {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mention-selector,
.reaction-selector {
  position: relative;
}

.mention-dropdown,
.reaction-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.mention-option {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.mention-option:hover {
  background-color: #f5f5f5;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.reaction-option {
  padding: 8px 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.reaction-option:hover {
  background-color: #f5f5f5;
}

.reaction-emoji {
  font-size: 16px;
}

.reaction-name {
  font-size: 14px;
  color: #666;
}

.submit-action {
  margin-left: auto;
}

.comments-list {
  flex: 1;
  overflow: hidden;
  padding: 8px 0;
}

.empty-comments {
  padding: 40px 20px;
  text-align: center;
}

.comment-item {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.comment-item:hover {
  background-color: #fafafa;
}

.comment-mentioned {
  background-color: #e3f2fd;
  border-left: 4px solid #2196f3;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.comment-item:hover .comment-actions {
  opacity: 1;
}

.comment-content {
  margin-bottom: 12px;
}

.edited-badge {
  margin-bottom: 4px;
}

.content-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.content-text :deep(.mention-highlight) {
  color: #2196f3;
  font-weight: 500;
  background-color: #e3f2fd;
  padding: 1px 4px;
  border-radius: 2px;
}

.content-text :deep(.comment-link) {
  color: #2196f3;
  text-decoration: none;
}

.content-text :deep(.comment-link:hover) {
  text-decoration: underline;
}

.mention-tags {
  margin-top: 8px;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.mention-tag {
  font-size: 12px;
}

.comment-reactions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.reaction-item {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  background-color: #f5f5f5;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.reaction-item:hover {
  background-color: #e0e0e0;
}

.reaction-active {
  background-color: #e3f2fd;
}

.reaction-emoji {
  font-size: 14px;
}

.reaction-count {
  font-size: 11px;
  color: #666;
}

.comment-replies {
  margin-top: 16px;
  padding-left: 20px;
  border-left: 2px solid #e0e0e0;
}

.reply-item {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reply-info {
  display: flex;
  flex-direction: column;
}

.reply-content {
  font-size: 13px;
  line-height: 1.5;
  color: #666;
}

.load-more {
  padding: 16px;
  text-align: center;
}

.typing-users {
  padding: 8px 20px;
  border-top: 1px solid #e8e8e8;
  background-color: #fafafa;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.typing-text {
  font-size: 12px;
  color: #666;
}

.typing-dots {
  display: flex;
  gap: 2px;
}

.dot {
  width: 4px;
  height: 4px;
  background-color: #999;
  border-radius: 50%;
  animation: typing-dot 1.4s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-dot {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}
</style>