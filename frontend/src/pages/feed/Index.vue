<template>
  <div class="feed-page">
    <!-- Page Header -->
    <div class="feeds-page-header">
      <div>
        <h1 class="feeds-title">校友圈</h1>
        <p class="feeds-subtitle">校友动态、资讯、合作机会</p>
      </div>
      <el-button type="primary" @click="handleCreate">+ 发布动态</el-button>
    </div>

    <!-- Feed List -->
    <div v-loading="loading">
      <div v-if="feeds.length" class="feed-list">
        <div v-for="feed in feeds" :key="feed.id" class="feed-card">
          <div class="feed-author-section">
            <div class="feed-author-avatar" :style="{ background: getAvatarColor(feed.publisher_name) }">
              {{ feed.publisher_name ? feed.publisher_name.charAt(0) : '?' }}
            </div>
            <div class="feed-author-info">
              <div class="feed-author-name">
                {{ feed.publisher_name }}
                <el-tag v-if="getTitleBadge(feed)" :type="getTitleBadge(feed).type" size="small" class="title-badge">
                  {{ getTitleBadge(feed).label }}
                </el-tag>
              </div>
              <div class="feed-author-company" v-if="feed.enterprise_name">{{ feed.enterprise_name }}</div>
            </div>
            <div class="feed-time">{{ feed.created_at }}</div>
          </div>
          <div class="feed-content">{{ feed.content }}</div>
          <div v-if="feed.images && feed.images.length" :class="['feed-images-grid', getImageGridClass(feed.images.length)]">
            <img
              v-for="(img, idx) in feed.images.slice(0, 9)"
              :key="idx"
              :src="img"
              class="feed-image"
              @click="previewImage(feed.images, idx)"
            />
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无动态" />
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadFeeds"
      />
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="createDialogVisible" title="发布动态" width="540px" @close="resetForm">
      <el-form :model="createForm" label-position="top">
        <el-form-item label="动态内容" required>
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="5"
            placeholder="分享你的行业见解、经验或动态..."
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="图片">
          <div class="upload-area">
            <div v-for="(img, idx) in createForm.imagePreviews" :key="idx" class="preview-item">
              <img :src="img" class="preview-img" />
              <span class="preview-remove" @click="removeImage(idx)">&times;</span>
            </div>
            <div v-if="createForm.imagePreviews.length < 9" class="upload-trigger" @click="triggerUpload">
              +
            </div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              multiple
              style="display: none"
              @change="handleFileSelect"
            />
          </div>
          <p class="upload-tip">最多上传 9 张图片，支持 JPG/PNG 格式</p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreate">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { getFeedList, createFeed } from '../../api/feed'

const router = useRouter()
const authStore = useAuthStore()

const feeds = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const submitting = ref(false)
const fileInput = ref(null)

const createDialogVisible = ref(false)
const createForm = reactive({
  content: '',
  imagePreviews: [],
  imageFiles: [],
})

async function loadFeeds() {
  loading.value = true
  try {
    const { data } = await getFeedList({
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (data.code === 200) {
      feeds.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/feed' } })
    return
  }
  createDialogVisible.value = true
}

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(event) {
  const files = Array.from(event.target.files || [])
  const remaining = 9 - createForm.imagePreviews.length
  const toAdd = files.slice(0, remaining)

  toAdd.forEach((file) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      createForm.imagePreviews.push(e.target.result)
    }
    reader.readAsDataURL(file)
    createForm.imageFiles.push(file)
  })

  event.target.value = ''
}

function removeImage(idx) {
  createForm.imagePreviews.splice(idx, 1)
  createForm.imageFiles.splice(idx, 1)
}

function resetForm() {
  createForm.content = ''
  createForm.imagePreviews = []
  createForm.imageFiles = []
}

async function submitCreate() {
  if (!createForm.content.trim()) {
    ElMessage.warning('请输入动态内容')
    return
  }
  submitting.value = true
  try {
    const payload = { content: createForm.content }
    if (createForm.imageFiles.length) {
      payload.images = createForm.imageFiles
    }
    const { data } = await createFeed(payload)
    if (data.code === 200) {
      ElMessage.success('动态发布成功')
      createDialogVisible.value = false
      loadFeeds()
    } else {
      ElMessage.error(data.message || '发布失败')
    }
  } catch {
    ElMessage.error('发布请求失败')
  } finally {
    submitting.value = false
  }
}

function previewImage(images, index) {
  window.open(images[index], '_blank')
}

const avatarColors = ['#1E88E5', '#4CAF50', '#FF9800', '#9C27B0', '#3F51B5', '#00BCD4', '#F44336', '#795548']
function getAvatarColor(name) {
  if (!name) return avatarColors[0]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

const titleBadgeMap = [
  { keywords: ['CEO', '总经理', '总裁'], label: 'CEO', type: 'success' },
  { keywords: ['教授', '博导', '院长'], label: '教授', type: '' },
  { keywords: ['总监', 'CTO', 'CFO', 'COO'], label: '总监', type: 'warning' },
  { keywords: ['博士', '研究员'], label: '博士', type: 'danger' },
]
function getTitleBadge(feed) {
  const title = feed.publisher_title || ''
  if (!title) return null
  for (const badge of titleBadgeMap) {
    if (badge.keywords.some(k => title.includes(k))) return badge
  }
  return { label: title, type: 'info' }
}

function getImageGridClass(count) {
  if (count === 1) return 'cols-1'
  if (count === 2) return 'cols-2'
  return 'cols-3'
}

onMounted(() => {
  loadFeeds()
})
</script>

<style scoped>
.feed-page {
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: var(--spacing-2xl);
}

.feeds-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.feeds-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.feeds-subtitle {
  color: var(--color-text-placeholder);
  font-size: 0.9375rem;
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.feed-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.feed-author-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: var(--spacing-md);
}

.feed-author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 600;
  flex-shrink: 0;
}

.feed-author-info {
  flex: 1;
  min-width: 0;
}

.feed-author-name {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-badge {
  font-size: 0.6875rem;
}

.feed-author-company {
  font-size: 0.8125rem;
  color: var(--color-text-placeholder);
  margin-top: 2px;
}

.feed-time {
  font-size: 0.75rem;
  color: var(--color-text-placeholder);
  flex-shrink: 0;
}

.feed-content {
  font-size: 0.9375rem;
  line-height: 1.8;
  color: var(--color-text-primary);
  white-space: pre-wrap;
}

.feed-images-grid {
  display: grid;
  gap: 8px;
  margin-top: var(--spacing-md);
}

.feed-images-grid.cols-1 {
  grid-template-columns: 1fr;
}

.feed-images-grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.feed-images-grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.feed-images-grid.cols-1 .feed-image {
  aspect-ratio: 16 / 9;
}

.feed-images-grid:not(.cols-1) .feed-image {
  aspect-ratio: 1;
}

.feed-image {
  width: 100%;
  object-fit: cover;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: opacity 0.2s;
}

.feed-image:hover {
  opacity: 0.9;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}

/* Upload area */
.upload-area {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.upload-trigger {
  width: 80px;
  height: 80px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--color-text-placeholder);
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-trigger:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.preview-item {
  width: 80px;
  height: 80px;
  position: relative;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--radius-sm);
}

.preview-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  background: var(--color-error);
  color: var(--color-white);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
}

.upload-tip {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  margin-top: var(--spacing-xs);
}
</style>
