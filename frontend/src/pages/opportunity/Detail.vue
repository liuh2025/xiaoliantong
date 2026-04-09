<template>
  <div class="opp-detail-page">
    <div v-loading="loading" class="detail-container">
      <template v-if="detail">
        <!-- Back -->
        <el-button text @click="$router.push('/opportunity')">
          &lt; 返回商机列表
        </el-button>

        <!-- Main Info -->
        <div class="detail-card">
          <div class="detail-top">
            <span
              class="type-badge"
              :class="detail.type === 'buy' ? 'type-buy' : 'type-supply'"
            >
              {{ detail.type === 'buy' ? '采购' : '供应' }}
            </span>
            <h1 class="detail-title">{{ detail.title }}</h1>
          </div>

          <div class="detail-meta">
            <span class="meta-item">
              <label>企业</label>
              <span>{{ detail.enterprise_name || '-' }}</span>
            </span>
            <span class="meta-item">
              <label>行业</label>
              <span>{{ detail.industry_name || '-' }}</span>
            </span>
            <span class="meta-item">
              <label>地区</label>
              <span>{{ detail.region_name || '-' }}</span>
            </span>
            <span class="meta-item">
              <label>浏览</label>
              <span>{{ detail.view_count || 0 }} 次</span>
            </span>
            <span class="meta-item">
              <label>发布时间</label>
              <span>{{ detail.created_at || '-' }}</span>
            </span>
          </div>

          <div v-if="detail.tags && detail.tags.length" class="detail-tags">
            <el-tag v-for="tag in detail.tags" :key="tag" size="small" type="info">
              {{ tag }}
            </el-tag>
          </div>

          <div class="detail-description">
            <h3>详细描述</h3>
            <p>{{ detail.description || '暂无描述' }}</p>
          </div>
        </div>

        <!-- Contact Section -->
        <div class="contact-card">
          <h3>联系信息</h3>
          <div class="contact-info">
            <div class="contact-row">
              <label>联系人</label>
              <span>{{ maskedContact(contactData?.contact_person) || '登录后查看' }}</span>
            </div>
            <div class="contact-row">
              <label>联系电话</label>
              <span>{{ maskedContact(contactData?.contact_phone) || '138****8000' }}</span>
            </div>
          </div>
          <el-button
            type="primary"
            :loading="contactLoading"
            @click="handleGetContact"
          >
            获取联系方式
          </el-button>
        </div>

        <!-- Contact Dialog -->
        <el-dialog v-model="contactDialogVisible" title="联系方式" width="400px">
          <div class="contact-dialog-content">
            <div class="contact-row">
              <label>联系人</label>
              <span>{{ contactData?.contact_person || '-' }}</span>
            </div>
            <div class="contact-row">
              <label>联系电话</label>
              <span>{{ contactData?.contact_phone || '-' }}</span>
            </div>
          </div>
          <template #footer>
            <el-button type="primary" @click="contactDialogVisible = false">确定</el-button>
          </template>
        </el-dialog>
      </template>

      <el-empty v-else-if="!loading" description="商机不存在或已下架" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { getOpportunityDetail, getContact } from '../../api/opportunity'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const detail = ref(null)
const loading = ref(false)
const contactData = ref(null)
const contactLoading = ref(false)
const contactDialogVisible = ref(false)

function maskedContact(value) {
  if (!value) return null
  if (value.length <= 3) return value
  return value[0] + '****' + value.slice(-1)
}

async function loadDetail() {
  loading.value = true
  try {
    const id = route.params.id
    const { data } = await getOpportunityDetail(id)
    if (data.code === 200) {
      detail.value = data.data
    }
  } finally {
    loading.value = false
  }
}

async function handleGetContact() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: route.fullPath } })
    return
  }

  contactLoading.value = true
  try {
    const { data } = await getContact(route.params.id)
    if (data.code === 200) {
      contactData.value = data.data
      contactDialogVisible.value = true
    } else {
      ElMessage.error(data.message || '获取联系方式失败')
    }
  } catch {
    ElMessage.error('获取联系方式失败')
  } finally {
    contactLoading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.opp-detail-page {
  padding-bottom: var(--spacing-2xl);
}

.detail-container {
  max-width: 800px;
  margin: 0 auto;
}

.detail-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--spacing-lg);
  margin-top: var(--spacing-md);
}

.detail-top {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.type-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  flex-shrink: 0;
}

.type-buy {
  background: #FFF7ED;
  color: var(--color-accent-buy);
  border: 1px solid var(--color-accent-buy);
}

.type-supply {
  background: #ECFDF5;
  color: var(--color-accent-supply);
  border: 1px solid var(--color-accent-supply);
}

.detail-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
  padding: var(--spacing-md) 0;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  margin-bottom: var(--spacing-md);
}

.meta-item {
  display: flex;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
}

.meta-item label {
  color: var(--color-text-secondary);
}

.meta-item span {
  color: var(--color-text-primary);
}

.detail-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
}

.detail-description h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

.detail-description p {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  line-height: 1.8;
  white-space: pre-wrap;
}

.contact-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.contact-card h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
}

.contact-info {
  margin-bottom: var(--spacing-md);
}

.contact-row {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  font-size: var(--font-size-base);
}

.contact-row label {
  color: var(--color-text-secondary);
  min-width: 80px;
}

.contact-dialog-content .contact-row {
  padding: var(--spacing-sm) 0;
}
</style>
