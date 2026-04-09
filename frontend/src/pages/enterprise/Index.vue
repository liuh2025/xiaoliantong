<template>
  <div class="enterprise-page">
    <div class="page-layout">
      <!-- Sidebar Filters -->
      <aside class="filter-sidebar">
        <div class="filter-section">
          <h3 class="filter-title">行业筛选</h3>
          <el-select
            v-model="filters.industry"
            placeholder="选择行业"
            clearable
            style="width: 100%"
            @change="onIndustryChange"
          >
            <el-option
              v-for="item in industries"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-if="subIndustries.length"
            v-model="filters.sub_industry"
            placeholder="选择子行业"
            clearable
            style="width: 100%; margin-top: 8px"
            @change="onFilterChange"
          >
            <el-option
              v-for="item in subIndustries"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <div class="filter-section">
          <h3 class="filter-title">地区筛选</h3>
          <el-select
            v-model="filters.province"
            placeholder="选择省份"
            clearable
            style="width: 100%"
            @change="onProvinceChange"
          >
            <el-option
              v-for="item in provinces"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-if="regions.length"
            v-model="filters.region"
            placeholder="选择城市"
            clearable
            style="width: 100%; margin-top: 8px"
            @change="onFilterChange"
          >
            <el-option
              v-for="item in regions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <div class="filter-section">
          <h3 class="filter-title">企业类别</h3>
          <el-select
            v-model="filters.category"
            placeholder="选择类别"
            clearable
            style="width: 100%"
            @change="onFilterChange"
          >
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <el-button style="width: 100%; margin-top: 16px" @click="resetFilters">
          重置筛选
        </el-button>
      </aside>

      <!-- Main Content -->
      <main class="ent-main">
        <div v-loading="loading">
          <div v-if="enterprises.length" class="ent-grid">
            <el-card
              v-for="ent in enterprises"
              :key="ent.id"
              class="ent-card"
              shadow="hover"
              @click="openDetail(ent.id)"
            >
              <div class="ent-card-top">
                <h3 class="ent-name">{{ ent.name }}</h3>
                <el-tag :type="authStatusTagType(ent.auth_status)" size="small">
                  {{ authStatusLabel(ent.auth_status) }}
                </el-tag>
              </div>
              <p class="ent-info">
                {{ ent.industry_name || '' }}
                {{ ent.region_name ? '| ' + ent.region_name : '' }}
              </p>
              <p class="ent-desc">{{ truncateText(ent.description, 80) }}</p>
              <div v-if="ent.tags && ent.tags.length" class="ent-tags">
                <el-tag
                  v-for="tag in ent.tags.slice(0, 3)"
                  :key="tag"
                  size="small"
                  type="info"
                  class="ent-tag"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </el-card>
          </div>
          <el-empty v-else description="暂无企业数据" />
        </div>

        <!-- Pagination -->
        <div v-if="total > pageSize" class="pagination-wrap">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            @current-change="loadEnterprises"
          />
        </div>
      </main>
    </div>

    <!-- Detail Drawer -->
    <el-drawer
      v-model="drawerVisible"
      :title="detailData?.name || '企业详情'"
      size="480px"
      direction="rtl"
    >
      <div v-loading="detailLoading" class="detail-content">
        <template v-if="detailData">
          <div class="detail-field">
            <label>企业名称</label>
            <span>{{ detailData.name }}</span>
          </div>
          <div class="detail-field">
            <label>认证状态</label>
            <el-tag :type="authStatusTagType(detailData.auth_status)" size="small">
              {{ authStatusLabel(detailData.auth_status) }}
            </el-tag>
          </div>
          <div class="detail-field">
            <label>行业</label>
            <span>{{ detailData.industry_name || '-' }}</span>
          </div>
          <div class="detail-field">
            <label>地区</label>
            <span>{{ detailData.region_name || '-' }}</span>
          </div>
          <div class="detail-field">
            <label>企业类别</label>
            <span>{{ detailData.category_name || '-' }}</span>
          </div>
          <div class="detail-field">
            <label>企业简介</label>
            <p>{{ detailData.description || '暂无简介' }}</p>
          </div>
          <div v-if="detailData.tags && detailData.tags.length" class="detail-field">
            <label>标签</label>
            <div class="detail-tags">
              <el-tag v-for="tag in detailData.tags" :key="tag" size="small" type="info">
                {{ tag }}
              </el-tag>
            </div>
          </div>

          <div class="detail-actions">
            <el-button
              v-if="detailData.auth_status === 'unclaimed'"
              type="primary"
              @click="handleClaim"
            >
              认领企业
            </el-button>
            <el-button @click="handleCreate">创建新企业</el-button>
          </div>
        </template>
      </div>
    </el-drawer>

    <!-- Claim Dialog -->
    <el-dialog v-model="claimDialogVisible" title="认领企业" width="440px">
      <el-form :model="claimForm" label-width="100px">
        <el-form-item label="企业名称">
          <el-input :value="detailData?.name" disabled />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="claimForm.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="claimForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="证明材料">
          <el-input v-model="claimForm.proof" type="textarea" placeholder="请说明您与该企业的关系" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="claimDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitClaim">提交认领</el-button>
      </template>
    </el-dialog>

    <!-- Create Dialog -->
    <el-dialog v-model="createDialogVisible" title="创建企业" width="440px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="企业名称">
          <el-input v-model="createForm.name" placeholder="请输入企业名称" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="createForm.industry" placeholder="选择行业" style="width: 100%">
            <el-option v-for="item in industries" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-select v-model="createForm.province" placeholder="选择省份" style="width: 100%">
            <el-option v-for="item in provinces" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="企业简介">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="请输入企业简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">提交创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import { useDict } from '../../composables/useDict'
import { getEnterpriseList, getEnterpriseDetail, createEnterprise, claimEnterprise } from '../../api/enterprise'

const authStore = useAuthStore()
const {
  industries, subIndustries, categories, provinces, regions,
  fetchIndustries, fetchCategories, fetchRegions,
} = useDict()

const enterprises = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const filters = reactive({
  industry: '',
  sub_industry: '',
  province: '',
  region: '',
  category: '',
})

// Detail drawer
const drawerVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)

// Claim dialog
const claimDialogVisible = ref(false)
const claimForm = reactive({
  contact_person: '',
  contact_phone: '',
  proof: '',
})

// Create dialog
const createDialogVisible = ref(false)
const createForm = reactive({
  name: '',
  industry: '',
  province: '',
  description: '',
})

function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function authStatusLabel(status) {
  const map = { unclaimed: '未认领', pending: '审核中', verified: '已认证', rejected: '已驳回' }
  return map[status] || status
}

function authStatusTagType(status) {
  const map = { unclaimed: 'info', pending: 'warning', verified: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

async function loadEnterprises() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.industry) params.industry = filters.industry
    if (filters.sub_industry) params.sub_industry = filters.sub_industry
    if (filters.province) params.province = filters.province
    if (filters.region) params.region = filters.region
    if (filters.category) params.category = filters.category

    const { data } = await getEnterpriseList(params)
    if (data.code === 200) {
      enterprises.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

async function openDetail(id) {
  drawerVisible.value = true
  detailLoading.value = true
  detailData.value = null
  try {
    const { data } = await getEnterpriseDetail(id)
    if (data.code === 200) {
      detailData.value = data.data
    }
  } finally {
    detailLoading.value = false
  }
}

function onIndustryChange(val) {
  filters.sub_industry = ''
  subIndustries.value = []
  if (val) {
    fetchIndustries(val)
  }
  onFilterChange()
}

function onProvinceChange(val) {
  filters.region = ''
  regions.value = []
  if (val) {
    fetchRegions(val)
  }
  onFilterChange()
}

function onFilterChange() {
  currentPage.value = 1
  loadEnterprises()
}

function resetFilters() {
  filters.industry = ''
  filters.sub_industry = ''
  filters.province = ''
  filters.region = ''
  filters.category = ''
  subIndustries.value = []
  regions.value = []
  currentPage.value = 1
  loadEnterprises()
}

function handleClaim() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  claimDialogVisible.value = true
}

async function submitClaim() {
  try {
    const { data } = await claimEnterprise({
      enterprise_id: detailData.value.id,
      ...claimForm,
    })
    if (data.code === 200) {
      ElMessage.success('认领申请已提交，请等待审核')
      claimDialogVisible.value = false
      drawerVisible.value = false
    } else {
      ElMessage.error(data.message || '认领失败')
    }
  } catch {
    ElMessage.error('认领请求失败')
  }
}

function handleCreate() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }
  createDialogVisible.value = true
}

async function submitCreate() {
  if (!createForm.name) {
    ElMessage.warning('请输入企业名称')
    return
  }
  try {
    const { data } = await createEnterprise(createForm)
    if (data.code === 200) {
      ElMessage.success('企业创建成功')
      createDialogVisible.value = false
      loadEnterprises()
    } else {
      ElMessage.error(data.message || '创建失败')
    }
  } catch {
    ElMessage.error('创建请求失败')
  }
}

onMounted(() => {
  fetchIndustries()
  fetchCategories()
  fetchRegions()
  loadEnterprises()
})
</script>

<style scoped>
.enterprise-page {
  padding-bottom: var(--spacing-2xl);
}

.page-layout {
  display: flex;
  gap: var(--spacing-lg);
}

.filter-sidebar {
  width: 220px;
  flex-shrink: 0;
}

.filter-section {
  margin-bottom: var(--spacing-lg);
}

.filter-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.ent-main {
  flex: 1;
  min-width: 0;
}

.ent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.ent-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.ent-card:hover {
  box-shadow: var(--shadow-hover);
}

.ent-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xs);
}

.ent-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  flex: 1;
  margin-right: var(--spacing-sm);
}

.ent-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.ent-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin-bottom: var(--spacing-sm);
}

.ent-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.ent-tag {
  border-radius: var(--radius-sm);
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}

/* Detail Drawer */
.detail-content {
  padding: var(--spacing-sm) 0;
}

.detail-field {
  margin-bottom: var(--spacing-md);
}

.detail-field label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.detail-field span,
.detail-field p {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.detail-tags {
  display: flex;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.detail-actions {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
  display: flex;
  gap: var(--spacing-sm);
}

@media (max-width: 768px) {
  .page-layout {
    flex-direction: column;
  }
  .filter-sidebar {
    width: 100%;
  }
  .ent-grid {
    grid-template-columns: 1fr;
  }
}
</style>
