<template>
  <div class="opportunity-page">
    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-select
          v-model="filters.type"
          placeholder="商机类型"
          clearable
          style="width: 140px"
          @change="onFilterChange"
        >
          <el-option label="采购" value="buy" />
          <el-option label="供应" value="supply" />
        </el-select>

        <el-select
          v-model="filters.industry"
          placeholder="行业"
          clearable
          style="width: 160px"
          @change="onFilterChange"
        >
          <el-option
            v-for="item in industries"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>

        <el-select
          v-model="filters.region"
          placeholder="地区"
          clearable
          style="width: 160px"
          @change="onFilterChange"
        >
          <el-option
            v-for="item in provinces"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>

      <el-button type="primary" @click="handleCreate">
        发布商机
      </el-button>
    </div>

    <!-- Opportunity Cards -->
    <div v-loading="loading">
      <div v-if="opportunities.length" class="opp-grid">
        <el-card
          v-for="opp in opportunities"
          :key="opp.id"
          class="opp-card"
          shadow="hover"
          @click="$router.push(`/opportunity/${opp.id}`)"
        >
          <div class="opp-header">
            <span
              class="opp-type-badge"
              :class="opp.type === 'buy' ? 'type-buy' : 'type-supply'"
            >
              {{ opp.type === 'buy' ? '采购' : '供应' }}
            </span>
            <span class="opp-views">{{ opp.view_count || 0 }} 次浏览</span>
          </div>
          <h3 class="opp-title">{{ opp.title }}</h3>
          <p class="opp-enterprise">{{ opp.enterprise_name || '匿名企业' }}</p>
          <p class="opp-desc">{{ truncateText(opp.description, 80) }}</p>
          <div v-if="opp.tags && opp.tags.length" class="opp-tags">
            <el-tag
              v-for="tag in opp.tags.slice(0, 3)"
              :key="tag"
              size="small"
              type="info"
            >
              {{ tag }}
            </el-tag>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无商机" />
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadOpportunities"
      />
    </div>

    <!-- Create Dialog -->
    <el-dialog v-model="createDialogVisible" title="发布商机" width="520px" @close="resetForm">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="商机类型" required>
          <el-radio-group v-model="createForm.type">
            <el-radio value="buy">采购</el-radio>
            <el-radio value="supply">供应</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="商机标题" required>
          <el-input v-model="createForm.title" placeholder="请输入商机标题" />
        </el-form-item>
        <el-form-item label="详细描述" required>
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            placeholder="请描述您的采购/供应需求"
          />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="createForm.industry" placeholder="选择行业" style="width: 100%">
            <el-option v-for="item in industries" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="createForm.region" placeholder="选择地区" style="width: 100%">
            <el-option v-for="item in provinces" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="createForm.tags"
            multiple
            filterable
            allow-create
            placeholder="输入标签后回车"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="createForm.contact_person" placeholder="联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="createForm.contact_phone" placeholder="联系电话" />
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
import { useDict } from '../../composables/useDict'
import { getOpportunityList, createOpportunity } from '../../api/opportunity'

const router = useRouter()
const authStore = useAuthStore()
const { industries, provinces, fetchIndustries, fetchRegions } = useDict()

const opportunities = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const submitting = ref(false)

const filters = reactive({
  type: '',
  industry: '',
  region: '',
})

const createDialogVisible = ref(false)
const createForm = reactive({
  type: 'buy',
  title: '',
  description: '',
  industry: '',
  region: '',
  tags: [],
  contact_person: '',
  contact_phone: '',
})

function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function onFilterChange() {
  currentPage.value = 1
  loadOpportunities()
}

async function loadOpportunities() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.type) params.type = filters.type
    if (filters.industry) params.industry = filters.industry
    if (filters.region) params.region = filters.region

    const { data } = await getOpportunityList(params)
    if (data.code === 200) {
      opportunities.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push({ name: 'Login', query: { redirect: '/opportunity' } })
    return
  }
  createDialogVisible.value = true
}

function resetForm() {
  createForm.type = 'buy'
  createForm.title = ''
  createForm.description = ''
  createForm.industry = ''
  createForm.region = ''
  createForm.tags = []
  createForm.contact_person = ''
  createForm.contact_phone = ''
}

async function submitCreate() {
  if (!createForm.title || !createForm.description) {
    ElMessage.warning('请填写商机标题和描述')
    return
  }
  submitting.value = true
  try {
    const { data } = await createOpportunity(createForm)
    if (data.code === 200) {
      ElMessage.success('商机发布成功')
      createDialogVisible.value = false
      loadOpportunities()
    } else {
      ElMessage.error(data.message || '发布失败')
    }
  } catch {
    ElMessage.error('发布请求失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchIndustries()
  fetchRegions()
  loadOpportunities()
})
</script>

<style scoped>
.opportunity-page {
  padding-bottom: var(--spacing-2xl);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  background: var(--color-white);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.filter-group {
  display: flex;
  gap: var(--spacing-sm);
}

.opp-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.opp-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.opp-card:hover {
  box-shadow: var(--shadow-hover);
}

.opp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.opp-type-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
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

.opp-views {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

.opp-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
}

.opp-enterprise {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xs);
}

.opp-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--spacing-sm);
}

.opp-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  .filter-group {
    flex-wrap: wrap;
  }
  .opp-grid {
    grid-template-columns: 1fr;
  }
}
</style>
