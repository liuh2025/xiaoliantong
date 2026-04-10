<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">连接校友资源，共创商业价值</h1>
        <p class="hero-subtitle">校链通是一个专为校友企业打造的轻量级供需撮合平台。在这里，您可以快速发布采购需求、展示供应能力，基于校友信任纽带，实现高效的业务对接与合作。</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="openPublishDialog('buy')">+ 发布采购需求</el-button>
          <el-button size="large" @click="openPublishDialog('supply')">+ 发布供应能力</el-button>
        </div>
        <div class="hero-tags">
          <span class="hot-label">🔥 热门检索：</span>
          <span
            v-for="tag in hotTags"
            :key="tag"
            class="hot-tag"
            @click="searchByTag(tag)"
          >{{ tag }}</span>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🏢</div>
          <div class="stat-number">{{ stats.total_enterprises || '---' }}</div>
          <div class="stat-label">入驻校友企业</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📋</div>
          <div class="stat-number">{{ stats.total_opportunities || '---' }}</div>
          <div class="stat-label">累计发布商机</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🤝</div>
          <div class="stat-number">{{ stats.total_matchmaking || '---' }}</div>
          <div class="stat-label">成功撮合对接</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-number">{{ stats.total_users || '---' }}</div>
          <div class="stat-label">活跃校友人数</div>
        </div>
      </div>
    </section>

    <!-- Content Section: Main + Sidebar -->
    <section class="content-section">
      <div class="content-grid">
        <!-- Main Area -->
        <div class="content-main">
          <div class="section-header">
            <h2 class="section-title">智能匹配推荐</h2>
            <router-link to="/opportunity" class="section-more">查看更多 →</router-link>
          </div>
          <div v-loading="oppLoading">
            <div v-if="recommendedOpps.length" class="opp-grid">
              <div
                v-for="opp in recommendedOpps"
                :key="opp.id"
                class="opp-card"
                @click="openContactDialog(opp.id)"
              >
                <div class="opp-card-top">
                  <span class="opp-type-badge" :class="opp.type === 'buy' ? 'badge-buy' : 'badge-supply'">
                    {{ opp.type === 'buy' ? '我要买' : '我能供' }}
                  </span>
                  <span class="opp-time">{{ formatTime(opp.created_at) }}</span>
                </div>
                <h3 class="opp-title">{{ opp.title }}</h3>
                <div class="opp-tags">
                  <span v-if="opp.industry_name" class="tag tag-primary">{{ opp.industry_name }}</span>
                  <span v-for="tag in (opp.tags || []).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
                </div>
                <div class="opp-meta">
                  <span class="opp-company" @click.stop="openEnterpriseDrawer(opp.enterprise_id)">
                    <span class="company-avatar" :style="{ background: getAvatarColor(opp.enterprise_name) }">
                      {{ (opp.enterprise_name || '?').charAt(0) }}
                    </span>
                    <span class="company-name">{{ opp.enterprise_name }}</span>
                    <span v-if="opp.enterprise_verified" class="verified-badge">✓</span>
                  </span>
                  <span class="opp-location" v-if="opp.region_name">📍 {{ opp.region_name }}</span>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无推荐商机" />
          </div>
        </div>

        <!-- Sidebar -->
        <aside class="content-sidebar">
          <!-- New Enterprises -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <h3>新入驻企业</h3>
            </div>
            <div class="sidebar-list" v-loading="entLoading">
              <div
                v-for="ent in newestEnts.slice(0, 5)"
                :key="ent.id"
                class="sidebar-ent-item"
                @click="openEnterpriseDrawer(ent.id)"
              >
                <span class="ent-avatar" :style="{ background: getAvatarColor(ent.name) }">
                  {{ (ent.name || '?').charAt(0) }}
                </span>
                <div class="ent-info">
                  <div class="ent-name">{{ ent.name }}</div>
                  <div class="ent-sub">{{ ent.industry_name || '' }}</div>
                </div>
              </div>
              <el-empty v-if="!entLoading && !newestEnts.length" description="暂无入驻企业" :image-size="60" />
            </div>
          </div>

          <!-- Alumni Feeds -->
          <div class="sidebar-card">
            <div class="sidebar-header">
              <h3>校友动态</h3>
            </div>
            <div class="sidebar-list" v-loading="feedLoading">
              <div
                v-for="feed in newestFeeds.slice(0, 5)"
                :key="feed.id"
                class="sidebar-feed-item"
              >
                <div class="feed-top">
                  <span class="feed-avatar" :style="{ background: getAvatarColor(feed.publisher_name) }">
                    {{ (feed.publisher_name || '?').charAt(0) }}
                  </span>
                  <div class="feed-user">
                    <span class="feed-name">{{ feed.publisher_name }}</span>
                    <span class="feed-time">{{ formatTime(feed.created_at) }}</span>
                  </div>
                </div>
                <p class="feed-text">{{ truncateText(feed.content, 80) }}</p>
              </div>
              <el-empty v-if="!feedLoading && !newestFeeds.length" description="暂无动态" :image-size="60" />
            </div>
          </div>
        </aside>
      </div>
    </section>

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
            <el-option v-for="item in subIndustryOptions" :key="item.id" :label="item.name" :value="item.id" />
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
            <el-option v-for="item in cityOptions" :key="item.id" :label="item.name" :value="item.id" />
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRecommended, createOpportunity, getContact } from '../../api/opportunity'
import { getNewestEnterprise, getEnterpriseDetail, getDictIndustry, getDictCategory, getDictRegion } from '../../api/enterprise'
import { getNewestFeed } from '../../api/feed'

const router = useRouter()

const stats = ref({})
const recommendedOpps = ref([])
const newestEnts = ref([])
const newestFeeds = ref([])
const oppLoading = ref(false)
const entLoading = ref(false)
const feedLoading = ref(false)

const hotTags = ['智能制造', '新能源', '汽车零部件', '专精特新', '源头工厂']

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

// Contact dialog
const contactVisible = ref(false)
const contactStep = ref(1)
const contactData = ref({})
const currentOppId = ref(null)

// Enterprise drawer
const drawerVisible = ref(false)
const drawerEnterprise = ref(null)
const drawerLoading = ref(false)

function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

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

function searchByTag(tag) {
  router.push({ path: '/opportunity', query: { search: tag } })
}

// ---- Data loading ----
async function loadRecommendedOpps() {
  oppLoading.value = true
  try {
    const { data } = await getRecommended()
    if (data.code === 200) {
      recommendedOpps.value = (data.data && data.data.items) || data.data || []
    }
  } finally {
    oppLoading.value = false
  }
}

async function loadNewestEnts() {
  entLoading.value = true
  try {
    const { data } = await getNewestEnterprise()
    if (data.code === 200) {
      newestEnts.value = (data.data && data.data.items) || data.data || []
    }
  } finally {
    entLoading.value = false
  }
}

async function loadNewestFeeds() {
  feedLoading.value = true
  try {
    const { data } = await getNewestFeed()
    if (data.code === 200) {
      newestFeeds.value = (data.data && data.data.items) || data.data || []
    }
  } finally {
    feedLoading.value = false
  }
}

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

// ---- Publish ----
function openPublishDialog(type) {
  publishForm.value = { type, title: '', industry_1: '', industry_2: '', category: '', province: '', city: '', tags: [], description: '' }
  subIndustryOptions.value = []
  cityOptions.value = []
  publishVisible.value = true
}

async function onPublishIndustryChange(val) {
  publishForm.value.industry_2 = ''
  subIndustryOptions.value = []
  if (!val) return
  try {
    const { data: res } = await getDictIndustry({ parent_id: val })
    if (res.code === 200) subIndustryOptions.value = res.data || []
  } catch { /* silent */ }
}

async function onPublishProvinceChange(val) {
  publishForm.value.city = ''
  cityOptions.value = []
  if (!val) return
  try {
    const { data: res } = await getDictRegion({ parent_id: val })
    if (res.code === 200) cityOptions.value = res.data || []
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
      await loadRecommendedOpps()
    } else {
      ElMessage.error(res.message || '发布失败')
    }
  } catch {
    ElMessage.error('发布失败')
  } finally {
    publishSaving.value = false
  }
}

// ---- Contact ----
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

// ---- Enterprise Drawer ----
async function openEnterpriseDrawer(id) {
  if (!id) return
  drawerVisible.value = true
  drawerLoading.value = true
  drawerEnterprise.value = null
  try {
    const { data: res } = await getEnterpriseDetail(id)
    if (res.code === 200) {
      drawerEnterprise.value = res.data || {}
    }
  } catch { /* silent */ }
  finally {
    drawerLoading.value = false
  }
}

onMounted(() => {
  loadRecommendedOpps()
  loadNewestEnts()
  loadNewestFeeds()
  loadDictData()
})
</script>

<style scoped>
.home-page {
  padding-bottom: var(--spacing-2xl, 32px);
}

/* Hero */
.hero-section {
  background: linear-gradient(135deg, #1e88e5, #0d47a1);
  color: #fff;
  padding: 48px 32px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 24px;
}
.hero-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 12px;
}
.hero-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: 24px;
  max-width: 680px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.8;
}
.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 20px;
}
.hero-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}
.hot-label {
  font-size: 14px;
  opacity: 0.8;
}
.hot-tag {
  background: rgba(255,255,255,0.2);
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}
.hot-tag:hover {
  background: rgba(255,255,255,0.35);
}

/* Stats */
.stats-section {
  margin-bottom: 24px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  background: var(--color-white, #fff);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}
.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary, #1e88e5);
}
.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary, #666);
  margin-top: 4px;
}

/* Content Layout */
.content-section {
  margin-bottom: 24px;
}
.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}
.content-main {
  min-width: 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-title {
  font-size: 1.125rem;
  font-weight: 600;
}
.section-more {
  font-size: 14px;
  color: var(--color-primary, #1e88e5);
  text-decoration: none;
}

/* Opportunity Cards */
.opp-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.opp-card {
  background: var(--color-white, #fff);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}
.opp-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  transform: translateY(-2px);
}
.opp-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.opp-type-badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  color: #fff;
}
.badge-buy { background: #ef6c00; }
.badge-supply { background: #43a047; }
.opp-time {
  font-size: 12px;
  color: var(--color-text-placeholder, #999);
}
.opp-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
.opp-location {
  font-size: 12px;
  color: var(--color-text-placeholder, #999);
}

/* Sidebar */
.content-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.sidebar-card {
  background: var(--color-white, #fff);
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  overflow: hidden;
}
.sidebar-header {
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
}
.sidebar-header h3 {
  margin: 0;
  font-size: 15px;
}
.sidebar-list {
  padding: 8px 0;
}
.sidebar-ent-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.sidebar-ent-item:hover {
  background: #f5f5f5;
}
.ent-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}
.ent-info {
  min-width: 0;
}
.ent-name {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ent-sub {
  font-size: 12px;
  color: var(--color-text-secondary, #999);
}
.sidebar-feed-item {
  padding: 10px 16px;
}
.feed-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.feed-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}
.feed-user {
  display: flex;
  flex-direction: column;
}
.feed-name {
  font-size: 13px;
  font-weight: 500;
}
.feed-time {
  font-size: 11px;
  color: var(--color-text-placeholder, #bbb);
}
.feed-text {
  font-size: 13px;
  color: var(--color-text-secondary, #666);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
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
  .content-grid {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .opp-grid {
    grid-template-columns: 1fr;
  }
}
</style>
