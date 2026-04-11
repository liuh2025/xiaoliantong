<template>
  <div class="opportunity-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">商机广场</h1>
        <p class="page-subtitle">海量商机，快速匹配</p>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openPublishDialog('buy')">+ 发布采购需求</el-button>
        <el-button type="success" @click="openPublishDialog('supply')">+ 发布供应能力</el-button>
      </div>
    </div>

    <div class="content-layout">
      <!-- Sidebar Filters -->
      <aside class="filter-sidebar">
        <!-- Type -->
        <div class="filter-section">
          <h3 class="filter-title">商机类型</h3>
          <el-checkbox-group v-model="filters.types" @change="onFilterChange">
            <el-checkbox label="我要买" value="buy" />
            <el-checkbox label="我能供" value="supply" />
          </el-checkbox-group>
        </div>

        <!-- Industry -->
        <div class="filter-section">
          <h3 class="filter-title">行业筛选</h3>
          <el-select v-model="filters.industry" placeholder="选择一级行业" clearable style="width:100%" @change="onIndustryChange">
            <el-option v-for="item in industryOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
          <el-select v-if="subIndustryOptions.length" v-model="filters.sub_industry" placeholder="选择二级行业" clearable style="width:100%;margin-top:8px" @change="onFilterChange">
            <el-option v-for="item in subIndustryOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>

        <!-- Category -->
        <div class="filter-section">
          <h3 class="filter-title">业务品类</h3>
          <el-checkbox-group v-model="filters.categories" @change="onFilterChange">
            <el-checkbox v-for="item in categoryOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-checkbox-group>
        </div>

        <!-- Region -->
        <div class="filter-section">
          <h3 class="filter-title">地区筛选</h3>
          <el-select v-model="filters.province" placeholder="选择省份" clearable style="width:100%" @change="onProvinceChange">
            <el-option v-for="item in provinceOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
          <el-select v-if="cityOptions.length" v-model="filters.city" placeholder="选择城市" clearable style="width:100%;margin-top:8px" @change="onFilterChange">
            <el-option v-for="item in cityOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>

        <!-- Filter Summary -->
        <div class="filter-section" v-if="hasActiveFilters">
          <h3 class="filter-title">已选条件</h3>
          <div class="filter-summary">
            <el-tag
              v-for="(tag, idx) in activeFilterTags"
              :key="idx"
              size="small"
              closable
              style="margin:2px 4px;"
              @close="removeFilterTag(tag)"
            >{{ tag.label }}</el-tag>
          </div>
          <el-button size="small" text type="danger" style="margin-top:8px;" @click="resetFilters">重置筛选</el-button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <div class="result-count">共找到 <strong>{{ total }}</strong> 条商机</div>
        <div v-loading="loading">
          <div v-if="opportunities.length" class="opp-list">
            <div v-for="opp in opportunities" :key="opp.id" class="opp-card">
              <!-- Type Badge -->
              <div class="opp-type-badge" :class="opp.type === 'buy' ? 'badge-buy' : 'badge-supply'">
                <span class="badge-icon">{{ opp.type === 'buy' ? '🛒' : '📦' }}</span>
                <span class="badge-text">{{ opp.type === 'buy' ? '我要买' : '我能供' }}</span>
              </div>

              <!-- Content -->
              <div class="opp-content">
                <h3 class="opp-title">{{ opp.title }}</h3>
                <div class="opp-tags">
                  <span v-if="opp.industry_name" class="tag tag-primary">{{ opp.industry_name }}</span>
                  <span v-for="tag in (opp.tags || []).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
                </div>
                <div class="opp-meta">
                  <span class="opp-company" @click="openEnterpriseDrawer(opp.enterprise_id)">
                    <span class="company-avatar" :style="{ background: getAvatarColor(opp.enterprise_name) }">
                      {{ (opp.enterprise_name || '?').charAt(0) }}
                    </span>
                    <span class="company-name">{{ opp.enterprise_name }}</span>
                    <span v-if="opp.enterprise_verified" class="verified-badge">✓</span>
                  </span>
                  <span v-if="opp.region_name" class="opp-location">📍 {{ opp.region_name }}</span>
                  <span class="opp-time">🕐 {{ formatTime(opp.created_at) }}</span>
                </div>
              </div>

              <!-- Action -->
              <div class="opp-action">
                <el-button type="primary" @click="openContactDialog(opp.id)">获取联系方式</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无商机数据" />
        </div>

        <div class="pagination-wrap" v-if="total > 0">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="fetchData"
            @size-change="fetchData"
          />
        </div>
      </main>
    </div>

    <!-- Publish Dialog -->
    <el-dialog v-model="publishVisible" title="发布商机" width="700px" destroy-on-close>
      <el-form :model="publishForm" label-width="100px">
        <el-form-item label="商机类型" required>
          <el-radio-group v-model="publishForm.type">
            <el-radio value="buy">我要买</el-radio>
            <el-radio value="supply">我能供</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="publishForm.title" placeholder="请输入商机标题" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="一级行业">
          <el-select v-model="publishForm.industry_1" placeholder="请选择一级行业" style="width:100%" @change="onPublishIndustryChange">
            <el-option v-for="item in industryOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="二级行业">
          <el-select v-model="publishForm.industry_2" placeholder="请选择二级行业" style="width:100%">
            <el-option v-for="item in publishSubIndustries" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="业务品类">
          <el-select v-model="publishForm.category" placeholder="请选择业务品类" style="width:100%">
            <el-option v-for="item in categoryOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="省份">
          <el-select v-model="publishForm.province" placeholder="请选择省份" style="width:100%" @change="onPublishProvinceChange">
            <el-option v-for="item in provinceOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="城市">
          <el-select v-model="publishForm.city" placeholder="请选择城市" style="width:100%">
            <el-option v-for="item in publishCities" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="商机标签">
          <el-select v-model="publishForm.tags" multiple filterable allow-create default-first-option placeholder="输入标签后回车" style="width:100%" />
        </el-form-item>
        <el-form-item label="详情描述">
          <el-input v-model="publishForm.description" type="textarea" :rows="4" placeholder="请输入商机详情（至少20字）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishVisible = false">取消</el-button>
        <el-button type="primary" :loading="publishSaving" @click="submitPublish">立即发布</el-button>
      </template>
    </el-dialog>

    <!-- Contact Dialog -->
    <el-dialog v-model="contactVisible" :title="contactStep === 1 ? '获取联系方式' : '联系方式'" width="480px" destroy-on-close>
      <template v-if="contactStep === 1">
        <div style="text-align:center;padding:20px 0;">
          <p style="font-size:16px;margin-bottom:8px;">确认获取该商机发布者的联系方式？</p>
          <p style="color:var(--color-text-secondary);font-size:14px;">获取后系统将通知发布者，同时您也可以在消息中查看。</p>
        </div>
      </template>
      <template v-else>
        <div style="text-align:center;margin-bottom:16px;">
          <div style="font-size:40px;">✅</div>
          <p style="font-size:16px;color:var(--color-success);">获取成功</p>
        </div>
        <div class="contact-info-box">
          <div class="contact-row">
            <span class="contact-label">联系人</span>
            <span class="contact-value">{{ contactData.contact_name || '-' }}</span>
          </div>
          <div class="contact-row">
            <span class="contact-label">手机号</span>
            <span class="contact-value">{{ contactData.contact_phone || '-' }}</span>
            <el-button v-if="contactData.contact_phone" size="small" text type="primary" @click="handleCopy(contactData.contact_phone)">复制</el-button>
          </div>
          <div class="contact-row">
            <span class="contact-label">微信号</span>
            <span class="contact-value">{{ contactData.contact_wechat || '-' }}</span>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button v-if="contactStep === 1" @click="contactVisible = false">取消</el-button>
        <el-button v-if="contactStep === 1" type="primary" @click="confirmContact">确认获取</el-button>
        <el-button v-if="contactStep === 2" type="primary" @click="contactVisible = false">知道了</el-button>
      </template>
    </el-dialog>

    <!-- Enterprise Detail Drawer -->
    <el-drawer v-model="drawerVisible" title="企业详情" size="550px" destroy-on-close>
      <div v-loading="drawerLoading" v-if="drawerEnterprise">
        <div style="text-align:center;margin-bottom:20px;">
          <div class="drawer-logo" :style="{ background: getAvatarColor(drawerEnterprise.name) }">
            {{ (drawerEnterprise.name || '?').charAt(0) }}
          </div>
          <h3 style="margin:8px 0 4px;">
            {{ drawerEnterprise.name }}
            <span v-if="drawerEnterprise.auth_status === 'verified'" class="verified-badge">✓</span>
          </h3>
          <p style="color:var(--color-text-secondary);font-size:14px;">{{ drawerEnterprise.industry_name || '' }}</p>
        </div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="信用代码">{{ drawerEnterprise.credit_code || '-' }}</el-descriptions-item>
          <el-descriptions-item label="所在地区">{{ drawerEnterprise.region_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="行业领域">{{ drawerEnterprise.industry_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="企业标签">
            <template v-if="drawerEnterprise.tags && drawerEnterprise.tags.length">
              <el-tag v-for="tag in drawerEnterprise.tags" :key="tag" size="small" style="margin-right:4px;">{{ tag }}</el-tag>
            </template>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="企业简介" :span="2">
            {{ drawerEnterprise.description || '暂无简介' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOpportunityList, createOpportunity, getContact } from '../../api/opportunity'
import { getEnterpriseDetail, getDictIndustry, getDictCategory, getDictRegion } from '../../api/enterprise'

// List state
const loading = ref(false)
const opportunities = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

// Filters
const filters = ref({
  types: [], industry: '', sub_industry: '', categories: [], province: '', city: '',
})

// Dict data
const industryOptions = ref([])
const subIndustryOptions = ref([])
const categoryOptions = ref([])
const provinceOptions = ref([])
const cityOptions = ref([])

// Publish dialog
const publishVisible = ref(false)
const publishSaving = ref(false)
const publishForm = ref({
  type: 'buy', title: '', industry_1: '', industry_2: '', category: '',
  province: '', city: '', tags: [], description: '',
})
const publishSubIndustries = ref([])
const publishCities = ref([])

// Contact dialog
const contactVisible = ref(false)
const contactStep = ref(1)
const contactData = ref({})
const currentOppId = ref(null)

// Enterprise drawer
const drawerVisible = ref(false)
const drawerEnterprise = ref(null)
const drawerLoading = ref(false)

// Computed
const hasActiveFilters = computed(() => {
  const f = filters.value
  return f.types.length || f.industry || f.sub_industry || f.categories.length || f.province || f.city
})

const activeFilterTags = computed(() => {
  const tags = []
  const f = filters.value
  if (f.types.includes('buy')) tags.push({ key: 'type_buy', label: '我要买' })
  if (f.types.includes('supply')) tags.push({ key: 'type_supply', label: '我能供' })
  if (f.industry) {
    const ind = industryOptions.value.find(i => i.id === f.industry)
    if (ind) tags.push({ key: 'industry', label: ind.name })
  }
  if (f.sub_industry) {
    const sub = subIndustryOptions.value.find(i => i.id === f.sub_industry)
    if (sub) tags.push({ key: 'sub_industry', label: sub.name })
  }
  f.categories.forEach(cid => {
    const cat = categoryOptions.value.find(c => c.id === cid)
    if (cat) tags.push({ key: 'category_' + cid, label: cat.name })
  })
  if (f.province) {
    const prov = provinceOptions.value.find(p => p.id === f.province)
    if (prov) tags.push({ key: 'province', label: prov.name })
  }
  if (f.city) {
    const c = cityOptions.value.find(i => i.id === f.city)
    if (c) tags.push({ key: 'city', label: c.name })
  }
  return tags
})

// Helpers
function getAvatarColor(name) {
  if (!name) return '#1e88e5'
  const colors = ['#1e88e5', '#43a047', '#e53935', '#fb8c00', '#8e24aa', '#00897b', '#3949ab']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

function formatTime(t) {
  if (!t) return ''
  if (t.includes('T')) {
    const d = new Date(t)
    return `${d.getMonth() + 1}月${d.getDate()}日`
  }
  return t.slice(5, 10)
}

// Data loading
async function loadDictData() {
  try {
    const [indRes, catRes, regRes] = await Promise.all([
      getDictIndustry({ parent_id: '' }),
      getDictCategory(),
      getDictRegion({ parent_id: '' }),
    ])
    if (indRes.data.code === 200) industryOptions.value = indRes.data.data || []
    if (catRes.data.code === 200) categoryOptions.value = catRes.data.data || []
    if (regRes.data.code === 200) provinceOptions.value = regRes.data.data || []
  } catch { /* silent */ }
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.value.types.length === 1) params.type = filters.value.types[0]
    if (filters.value.industry) params.industry = filters.value.industry
    if (filters.value.sub_industry) params.sub_industry = filters.value.sub_industry
    if (filters.value.categories.length) params.category = filters.value.categories.join(',')
    if (filters.value.province) params.province = filters.value.province
    if (filters.value.city) params.city = filters.value.city
    const { data: res } = await getOpportunityList(params)
    if (res.code === 200) {
      opportunities.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载商机列表失败')
  } finally {
    loading.value = false
  }
}

// Filter handlers
async function onIndustryChange(val) {
  filters.value.sub_industry = ''
  subIndustryOptions.value = []
  if (!val) { onFilterChange(); return }
  try {
    const [subRes, catRes] = await Promise.all([
      getDictIndustry({ parent_id: val }),
      getDictCategory({ industry_id: val }),
    ])
    if (subRes.data.code === 200) subIndustryOptions.value = subRes.data.data || []
    if (catRes.data.code === 200) categoryOptions.value = catRes.data.data || []
  } catch { /* silent */ }
  onFilterChange()
}

async function onProvinceChange(val) {
  filters.value.city = ''
  cityOptions.value = []
  if (!val) { onFilterChange(); return }
  try {
    const { data: res } = await getDictRegion({ parent_id: val })
    if (res.code === 200) cityOptions.value = res.data || []
  } catch { /* silent */ }
  onFilterChange()
}

function onFilterChange() {
  page.value = 1
  fetchData()
}

function removeFilterTag(tag) {
  if (tag.key === 'type_buy') filters.value.types = filters.value.types.filter(t => t !== 'buy')
  else if (tag.key === 'type_supply') filters.value.types = filters.value.types.filter(t => t !== 'supply')
  else if (tag.key === 'industry') filters.value.industry = ''
  else if (tag.key === 'sub_industry') filters.value.sub_industry = ''
  else if (tag.key.startsWith('category_')) {
    const cid = tag.key.replace('category_', '')
    filters.value.categories = filters.value.categories.filter(c => c != cid)
  }
  else if (tag.key === 'province') filters.value.province = ''
  else if (tag.key === 'city') filters.value.city = ''
  onFilterChange()
}

function resetFilters() {
  filters.value = { types: [], industry: '', sub_industry: '', categories: [], province: '', city: '' }
  subIndustryOptions.value = []
  cityOptions.value = []
  onFilterChange()
}

// Publish
function openPublishDialog(type) {
  publishForm.value = { type, title: '', industry_1: '', industry_2: '', category: '', province: '', city: '', tags: [], description: '' }
  publishSubIndustries.value = []
  publishCities.value = []
  publishVisible.value = true
}

async function onPublishIndustryChange(val) {
  publishForm.value.industry_2 = ''
  publishSubIndustries.value = []
  if (!val) return
  try {
    const { data: res } = await getDictIndustry({ parent_id: val })
    if (res.code === 200) publishSubIndustries.value = res.data || []
  } catch { /* silent */ }
}

async function onPublishProvinceChange(val) {
  publishForm.value.city = ''
  publishCities.value = []
  if (!val) return
  try {
    const { data: res } = await getDictRegion({ parent_id: val })
    if (res.code === 200) publishCities.value = res.data || []
  } catch { /* silent */ }
}

async function submitPublish() {
  if (!publishForm.value.title) {
    ElMessage.warning('请输入商机标题')
    return
  }
  publishSaving.value = true
  try {
    const { data: res } = await createOpportunity(publishForm.value)
    if (res.code === 200) {
      ElMessage.success('发布成功')
      publishVisible.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '发布失败')
    }
  } catch {
    ElMessage.error('发布失败')
  } finally {
    publishSaving.value = false
  }
}

// Contact
function openContactDialog(oppId) {
  currentOppId.value = oppId
  contactStep.value = 1
  contactData.value = {}
  contactVisible.value = true
}

async function confirmContact() {
  try {
    const { data: res } = await getContact(currentOppId.value)
    if (res.code === 200) {
      contactData.value = res.data || {}
      contactStep.value = 2
    } else {
      ElMessage.error(res.message || '获取失败')
    }
  } catch {
    ElMessage.error('获取联系方式失败')
  }
}

function handleCopy(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// Enterprise Drawer
async function openEnterpriseDrawer(id) {
  if (!id) return
  drawerVisible.value = true
  drawerLoading.value = true
  drawerEnterprise.value = null
  try {
    const { data: res } = await getEnterpriseDetail(id)
    if (res.code === 200) drawerEnterprise.value = res.data || {}
  } catch { /* silent */ }
  finally { drawerLoading.value = false }
}

onMounted(() => {
  loadDictData()
  fetchData()
})
</script>

<style scoped>
/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 4px;
}
.page-subtitle {
  color: var(--color-text-secondary, #666);
  font-size: 14px;
  margin: 0;
}
.page-actions {
  display: flex;
  gap: 12px;
}

/* Layout */
.content-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
}

/* Sidebar */
.filter-sidebar {
  position: sticky;
  top: 20px;
  align-self: start;
  background: var(--color-white, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  padding: 16px;
  max-height: calc(100vh - 40px);
  overflow-y: auto;
}
.filter-section {
  margin-bottom: 20px;
}
.filter-section:last-child {
  margin-bottom: 0;
}
.filter-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
}
.filter-summary {
  display: flex;
  flex-wrap: wrap;
}

/* Main Content */
.main-content {
  min-width: 0;
}
.result-count {
  font-size: 14px;
  color: var(--color-text-secondary, #666);
  margin-bottom: 16px;
}

/* Opportunity Cards - Horizontal List */
.opp-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.opp-card {
  display: flex;
  align-items: stretch;
  background: var(--color-white, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.opp-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}

/* Type Badge (Left) */
.opp-type-badge {
  width: 80px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.badge-buy { background: #ef6c00; }
.badge-supply { background: #43a047; }
.badge-icon { font-size: 1.5rem; }
.badge-text { font-size: 12px; margin-top: 4px; }

/* Content Area */
.opp-content {
  flex: 1;
  padding: 16px;
  min-width: 0;
}
.opp-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}
.opp-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f0f0f0;
  color: #666;
}
.tag-primary {
  background: #e3f2fd;
  color: var(--color-primary, #1e88e5);
}
.opp-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-secondary, #666);
}
.opp-company {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.opp-company:hover .company-name {
  color: var(--color-primary, #1e88e5);
}
.company-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
.company-name {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: color 0.2s;
}
.verified-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #43a047;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}
.opp-location, .opp-time {
  font-size: 12px;
  color: var(--color-text-placeholder, #999);
}

/* Action Area */
.opp-action {
  display: flex;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
}

/* Pagination */
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Contact Info Box */
.contact-info-box {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}
.contact-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
}
.contact-row + .contact-row {
  border-top: 1px solid #eee;
}
.contact-label {
  width: 80px;
  color: var(--color-text-secondary, #666);
  font-size: 14px;
}
.contact-value {
  flex: 1;
  font-weight: 500;
}

/* Drawer Logo */
.drawer-logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 auto 12px;
}

@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
  .opp-card {
    flex-direction: column;
  }
  .opp-type-badge {
    width: 100%;
    min-height: 60px;
    flex-direction: row;
    gap: 8px;
  }
  .opp-action {
    padding: 12px 16px;
  }
}
</style>
