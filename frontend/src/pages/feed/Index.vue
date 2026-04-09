<template>
  <div class="feed-page">
    <!-- Header with Create Button -->
    <div class="feed-header">
      <h2>校友圈</h2>
      <el-button type="primary" @click="handleCreate">发布动态</el-button>
    </div>

    <!-- Feed List -->
    <div v-loading="loading">
      <div v-if="feeds.length" class="feed-list">
        <div v-for="feed in feeds" :key="feed.id" class="feed-card">
          <div class="feed-card-header">
            <div class="feed-author-info">
              <span class="feed-author">{{ feed.publisher_name }}</span>
              <span v-if="feed.enterprise_name" class="feed-ent">{{ feed.enterprise_name }}</span>
            </div>
            <span class="feed-time">{{ feed.created_at }}</span>
          </div>
          <div class="feed-content">{{ feed.content }}</div>
          <div v-if="feed.images && feed.images.length" class="feed-images">
            <img
              v-for="(img, idx) in feed.images.slice(0, 3)"
              :key="idx"
              :src="img"
              class="feed-image"
              @click="previewImage(feed.images, idx)"
            />
            <span v-if="feed.images.length > 3" class="image-more">
              +{{ feed.images.length - 3 }}
            </span>
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
  // Simple preview - in production use ElImageViewer
  window.open(images[index], '_blank')
}

onMounted(() => {
  loadFeeds()
})
</script>

<style scoped>
.feed-page {
  max-width: 700px;
  margin: 0 auto;
  padding-bottom: var(--spacing-2xl);
}

.feed-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.feed-header h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.feed-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.feed-card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.feed-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.feed-author-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.feed-author {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-base);
}

.feed-ent {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
}

.feed-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

.feed-content {
  font-size: var(--font-size-base);
  line-height: 1.7;
  color: var(--color-text-primary);
  white-space: pre-wrap;
}

.feed-images {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  flex-wrap: wrap;
  position: relative;
}

.feed-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.image-more {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: var(--color-white);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-lg);
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
