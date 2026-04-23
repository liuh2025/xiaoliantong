<template>
  <div class="enterprise-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-inner">
        <div class="page-header-left">
          <h1 class="page-title">企业名录</h1>
          <p class="page-subtitle">结构化校友企业名片，快速定位合作伙伴</p>
        </div>
        <div class="page-header-actions">
          <el-button class="btn-outline" @click="openClaimDialog">
            认领已有企业
          </el-button>
          <el-button type="primary" @click="openCreateDialog">
            创建新企业
          </el-button>
        </div>
      </div>
    </div>

    <!-- Content Layout -->
    <div class="content-layout">
      <!-- Sidebar Filters -->
      <aside class="filter-sidebar">
        <!-- Industry Filter -->
        <div class="filter-group">
          <div class="filter-group-title">行业分类</div>
          <el-select
            v-model="filters.industry"
            placeholder="选择一级行业"
            clearable
            style="width: 100%"
            @change="onIndustryChange"
          >
            <el-option
              v-for="item in industryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-model="filters.sub_industry"
            placeholder="选择二级行业"
            clearable
            style="width: 100%; margin-top: 8px"
            :disabled="!filters.industry"
            @change="onFilterChange"
          >
            <el-option
              v-for="item in subIndustryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <!-- Category Filter -->
        <div class="filter-group">
          <div class="filter-group-title">业务品类</div>
          <div class="category-checkbox-group">
            <el-checkbox
              v-model="categoryAllChecked"
              @change="onCategoryAllChange"
            >
              全部品类
            </el-checkbox>
            <el-checkbox-group
              v-model="filters.categoryList"
              @change="onCategoryChange"
            >
              <el-checkbox
                v-for="item in categoryOptions"
                :key="item.id"
                :label="item.id"
              >
                {{ item.name }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>

        <!-- Region Filter -->
        <div class="filter-group">
          <div class="filter-group-title">所在地区</div>
          <el-select
            v-model="filters.province"
            placeholder="选择省份"
            clearable
            style="width: 100%"
            @change="onProvinceChange"
          >
            <el-option
              v-for="item in provinceOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-select
            v-model="filters.city"
            placeholder="选择城市"
            clearable
            style="width: 100%; margin-top: 8px"
            :disabled="!filters.province"
            @change="onFilterChange"
          >
            <el-option
              v-for="item in cityOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>

        <!-- Hot Tags -->
        <div class="filter-group">
          <div class="filter-group-title">热门标签</div>
          <div class="hot-tags">
            <span
              v-for="tag in hotTagOptions"
              :key="tag"
              class="hot-tag"
              :class="{ active: filters.tags.includes(tag) }"
              @click="toggleHotTag(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>

        <!-- Filter Summary -->
        <div v-if="filterSummaryTags.length" class="filter-summary">
          <div class="filter-summary-title">已选条件</div>
          <div class="filter-summary-tags">
            <span
              v-for="(ftag, idx) in filterSummaryTags"
              :key="idx"
              class="filter-summary-tag"
            >
              {{ ftag.label }}
              <span class="remove" @click="removeFilterSummary(ftag.type, ftag.value)">x</span>
            </span>
          </div>
        </div>

        <!-- Reset -->
        <el-button
          class="reset-btn"
          style="width: 100%; margin-top: 16px"
          @click="resetFilters"
        >
          重置筛选
        </el-button>
      </aside>

      <!-- Main Content -->
      <main class="enterprise-main">
        <div class="result-count">
          共找到 <strong>{{ total }}</strong> 家企业
        </div>

        <div v-loading="loading">
          <div v-if="enterprises.length" class="enterprise-grid">
            <div
              v-for="ent in enterprises"
              :key="ent.id"
              class="enterprise-card"
              @click="openDetail(ent)"
            >
              <div class="enterprise-card-top">
                <div
                  class="enterprise-logo"
                  :style="{ background: getAvatarColor(ent.name) }"
                >
                  {{ ent.name ? ent.name.charAt(0) : '' }}
                </div>
                <div class="enterprise-info">
                  <div class="enterprise-name">
                    {{ ent.name }}
                    <span v-if="ent.auth_status === 'VERIFIED'" class="auth-badge">&#10003; 已认证</span>
                    <span v-else-if="ent.auth_status === 'PENDING'" class="auth-badge" style="background:#e6a23c;color:#fff;">&#9203; 待审核</span>
                    <span v-else-if="ent.auth_status === 'REJECTED'" class="auth-badge" style="background:#f56c6c;color:#fff;">&#10007; 已拒绝</span>
                  </div>
                  <div class="enterprise-field">
                    {{ ent.business_field || ent.industry_name || '' }}
                  </div>
                  <div v-if="ent.tags && ent.tags.length" class="enterprise-tags">
                    <span
                      v-for="tag in ent.tags.slice(0, 4)"
                      :key="tag"
                      class="ent-tag"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="enterprise-card-footer">
                <span class="enterprise-meta">校友企业</span>
                <span class="enterprise-action">查看详情 ></span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无企业数据" />
        </div>

        <!-- Pagination -->
        <div v-if="total > 0" class="pagination-wrap">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 36, 48]"
            :total="total"
            layout="total, sizes, prev, pager, next"
            @current-change="loadEnterprises"
            @size-change="onPageSizeChange"
          />
        </div>
      </main>
    </div>

    <!-- Enterprise Detail Drawer -->
    <el-drawer
      v-model="drawerVisible"
      title="企业详情"
      size="550px"
      direction="rtl"
    >
      <div v-loading="detailLoading" class="drawer-content">
        <template v-if="detailData">
          <!-- Header -->
          <div class="drawer-header-section">
            <div
              class="drawer-logo"
              :style="{ background: getAvatarColor(detailData.name) }"
            >
              {{ detailData.name ? detailData.name.charAt(0) : '' }}
            </div>
            <h2 class="drawer-name">
              {{ detailData.name }}
              <span v-if="detailData.auth_status === 'VERIFIED'" class="verified-badge-lg">已认证 &#10003;</span>
              <span v-else-if="detailData.auth_status === 'PENDING'" class="verified-badge-lg" style="background:#e6a23c;color:#fff;">&#9203; 待审核</span>
              <span v-else-if="detailData.auth_status === 'REJECTED'" class="verified-badge-lg" style="background:#f56c6c;color:#fff;">&#10007; 已拒绝</span>
            </h2>
            <p class="drawer-field">{{ detailData.business_field || detailData.industry_name || '' }}</p>
          </div>

          <!-- Basic Info -->
          <div class="drawer-info-grid">
            <div class="info-item">
              <span class="info-label">信用代码</span>
              <span class="info-value">{{ detailData.credit_code || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">地区</span>
              <span class="info-value">{{ detailData.region_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">行业领域</span>
              <span class="info-value">{{ detailData.industry_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">企业标签</span>
              <span class="info-value">
                <template v-if="detailData.tags && detailData.tags.length">
                  <span v-for="tag in detailData.tags" :key="tag" class="ent-tag">{{ tag }}</span>
                </template>
                <template v-else>-</template>
              </span>
            </div>
          </div>

          <!-- Description -->
          <div class="drawer-section">
            <h4 class="drawer-section-title">企业简介</h4>
            <p class="drawer-desc">
              {{ detailData.description || '暂无简介' }}
            </p>
          </div>

          <!-- Opportunities -->
          <div class="drawer-section">
            <h4 class="drawer-section-title">
              该企业发布的商机
              <span v-if="detailData.opportunities" class="count-badge">
                {{ detailData.opportunities.length }}
              </span>
            </h4>
            <div
              v-if="detailData.opportunities && detailData.opportunities.length"
              class="drawer-opp-list"
            >
              <div
                v-for="opp in detailData.opportunities"
                :key="opp.id"
                class="drawer-opp-item"
                @click="openContactDialog(opp.id)"
              >
                <span
                  class="opp-type-tag"
                  :class="opp.type === 'buy' ? 'type-buy' : 'type-supply'"
                >
                  {{ opp.type === 'buy' ? '我要买' : '我能供' }}
                </span>
                <p class="opp-title-text">{{ opp.title }}</p>
                <span class="opp-time">{{ opp.created_at || '' }}</span>
              </div>
            </div>
            <div v-else class="drawer-opp-empty">暂无发布的商机</div>
          </div>
        </template>
      </div>
    </el-drawer>

    <!-- Claim Enterprise Dialog -->
    <el-dialog
      v-model="claimDialogVisible"
      :title="claimStep === 1 ? '认领已有企业' : '认领企业 - 提交材料'"
      width="600px"
      @close="onClaimDialogClose"
    >
      <!-- Step 1: Select Enterprise -->
      <template v-if="claimStep === 1">
        <p class="claim-tip">请选择您要认领的企业（仅显示未认领的企业）</p>
        <div v-loading="claimLoading" class="claim-ent-list">
          <template v-if="unclaimedEnts.length">
            <div
              v-for="ent in unclaimedEnts"
              :key="ent.id"
              class="claim-ent-item"
              :class="{ selected: selectedClaimEnt && selectedClaimEnt.id === ent.id }"
              @click="onSelectClaimEnt(ent)"
            >
              <div
                class="claim-ent-logo"
                :style="{ background: getAvatarColor(ent.name) }"
              >
                {{ ent.name ? ent.name.charAt(0) : '' }}
              </div>
              <div class="claim-ent-info">
                <div class="claim-ent-name">{{ ent.name }}</div>
                <div class="claim-ent-industry">{{ ent.industry_name || '' }}</div>
              </div>
            </div>
          </template>
          <el-empty v-else description="暂无可认领的企业" />
        </div>
      </template>

      <!-- Step 2: Submit Materials -->
      <template v-if="claimStep === 2">
        <div class="claim-selected-info">
          <div class="claim-selected-label">已选择（不可修改）</div>
          <div class="claim-selected-grid">
            <span class="claim-grid-label">企业全称</span>
            <span>{{ selectedClaimEnt?.name || '-' }}</span>
            <span class="claim-grid-label">信用代码</span>
            <span>{{ selectedClaimEnt?.credit_code || '-' }}</span>
            <span class="claim-grid-label">行业领域</span>
            <span>{{ selectedClaimEnt?.industry_name || '-' }}</span>
          </div>
        </div>
        <el-form :model="claimForm" label-width="100px" style="margin-top: 20px">
          <el-form-item label="法人姓名" required>
            <el-input v-model="claimForm.legal_representative" placeholder="请输入企业法人姓名" />
          </el-form-item>
          <el-form-item label="营业执照" required>
            <el-upload
              :auto-upload="false"
              :limit="1"
              accept=".jpg,.jpeg,.png,.pdf"
              :on-change="onClaimLicenseChange"
              :file-list="claimLicenseFiles"
              list-type="picture"
            >
              <div class="upload-area">
                <div class="upload-icon">&#128196;</div>
                <p>点击或拖拽上传文件</p>
                <p class="upload-hint">支持 JPG、PNG、PDF，大小不超过 5MB</p>
              </div>
            </el-upload>
            <p class="form-hint">请上传加盖公章的营业执照扫描件</p>
          </el-form-item>
          <el-form-item label="您的职务" required>
            <el-input v-model="claimForm.position" placeholder="请输入您在公司的职务" />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <template v-if="claimStep === 1">
          <el-button @click="claimDialogVisible = false">取消</el-button>
        </template>
        <template v-if="claimStep === 2">
          <el-button @click="claimStep = 1">返回选择</el-button>
          <el-button @click="claimDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="claimSubmitting" @click="submitClaim">
            提交申请
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- Create Enterprise Dialog -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建企业"
      width="700px"
      @close="onCreateDialogClose"
    >
      <el-form :model="createForm" label-width="140px">
        <el-form-item label="企业全称" required>
          <el-input v-model="createForm.name" placeholder="请输入企业全称" />
        </el-form-item>
        <el-form-item label="统一社会信用代码" required>
          <el-input v-model="createForm.credit_code" placeholder="请输入18位信用代码" />
        </el-form-item>
        <el-form-item label="所属行业" required>
          <div style="display: flex; gap: 8px; width: 100%">
            <el-select
              v-model="createForm.industry"
              placeholder="选择行业"
              clearable
              style="flex: 1"
              @change="onCreateIndustryChange"
            >
              <el-option
                v-for="item in industryOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
            <el-select
              v-model="createForm.sub_industry"
              placeholder="选择子行业"
              clearable
              style="flex: 1"
              :disabled="!createForm.industry"
            >
              <el-option
                v-for="item in createSubIndustryOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="主营业务品类" required>
          <el-select
            v-model="createForm.category"
            placeholder="请选择品类"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="item in createCategoryOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所在地区" required>
          <div style="display: flex; gap: 8px; width: 100%">
            <el-select
              v-model="createForm.province"
              placeholder="省份"
              clearable
              style="flex: 1"
              @change="onCreateProvinceChange"
            >
              <el-option
                v-for="item in provinceOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
            <el-select
              v-model="createForm.city"
              placeholder="城市"
              clearable
              style="flex: 1"
              :disabled="!createForm.province"
            >
              <el-option
                v-for="item in createCityOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="企业标签">
          <el-select
            v-model="createForm.tags"
            multiple
            filterable
            allow-create
            placeholder="输入标签后回车"
            style="width: 100%"
          >
            <el-option
              v-for="tag in allTagSuggestions"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="企业Logo">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".jpg,.jpeg,.png"
            :on-change="onCreateLogoChange"
            :file-list="createLogoFiles"
            list-type="picture"
          >
            <div class="upload-area upload-area-sm">
              <div class="upload-icon-sm">&#128247;</div>
              <p class="upload-hint">点击上传</p>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="企业简介">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入企业简介，不少于50字"
          />
        </el-form-item>

        <!-- Applicant Section -->
        <div class="form-divider">
          <h4>申请人信息</h4>
        </div>

        <el-form-item label="法人姓名" required>
          <el-input v-model="createForm.legal_representative" placeholder="请输入企业法人姓名" />
        </el-form-item>
        <el-form-item label="营业执照" required>
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".jpg,.jpeg,.png,.pdf"
            :on-change="onCreateLicenseChange"
            :file-list="createLicenseFiles"
            list-type="picture"
          >
            <div class="upload-area">
              <div class="upload-icon">&#128196;</div>
              <p>点击或拖拽上传文件</p>
              <p class="upload-hint">支持 JPG、PNG、PDF，大小不超过 5MB</p>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="您的职务" required>
          <el-input v-model="createForm.position" placeholder="请输入您在公司的职务" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSaving" @click="submitCreate">
          提交创建
        </el-button>
      </template>
    </el-dialog>

    <!-- Contact Dialog -->
    <el-dialog
      v-model="contactVisible"
      title="获取联系方式"
      width="420px"
    >
      <!-- Step 1: Confirm -->
      <template v-if="contactStep === 1">
        <div class="contact-confirm">
          <div class="contact-icon">&#128222;</div>
          <p class="contact-text">您即将获取该企业发布人的真实联系方式。</p>
          <p class="contact-sub">确认获取吗？</p>
        </div>
      </template>
      <!-- Step 2: Result -->
      <template v-if="contactStep === 2">
        <div class="contact-result">
          <div class="contact-icon success">&#10003;</div>
          <p class="contact-text">获取成功</p>
          <div class="contact-info-card">
            <div class="contact-info-row">
              <span class="contact-info-label">联系人</span>
              <span>{{ contactData.contact_person || '-' }}</span>
            </div>
            <div class="contact-info-row">
              <span class="contact-info-label">联系电话</span>
              <span>{{ contactData.contact_phone || '-' }}</span>
              <el-button
                size="small"
                type="primary"
                link
                @click="copyText(contactData.contact_phone)"
              >
                复制
              </el-button>
            </div>
            <div class="contact-info-row">
              <span class="contact-info-label">微信号</span>
              <span>{{ contactData.wechat || '-' }}</span>
            </div>
          </div>
        </div>
      </template>
      <template #footer>
        <template v-if="contactStep === 1">
          <el-button @click="contactVisible = false">取消</el-button>
          <el-button type="primary" :loading="contactLoading" @click="fetchContact">
            确认获取
          </el-button>
        </template>
        <template v-if="contactStep === 2">
          <el-button type="primary" @click="contactVisible = false">确定</el-button>
        </template>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'
import {
  getEnterpriseList,
  getEnterpriseDetail,
  createEnterprise,
  claimEnterprise,
  getDictIndustry,
  getDictCategory,
  getDictRegion,
} from '../../api/enterprise'
import { getContact } from '../../api/opportunity'

const authStore = useAuthStore()

// ==================== Enterprise List ====================
const enterprises = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// ==================== Filters ====================
const filters = reactive({
  industry: '',
  sub_industry: '',
  categoryList: [],
  province: '',
  city: '',
  tags: [],
  search: '',
})

const industryOptions = ref([])
const subIndustryOptions = ref([])
const categoryOptions = ref([])
const provinceOptions = ref([])
const cityOptions = ref([])

const hotTagOptions = ['专精特新', '高新技术企业', '上市公司', '源头工厂', '外贸企业']
const allTagSuggestions = [
  '专精特新', '高新技术企业', '上市公司', '世界500强', '中国500强',
  '民营企业500强', '瞪羚企业', '独角兽企业', '国产替代', '出口供应',
  'OEM配套', '研发合作', '产能合作', '渠道合作',
]

const categoryAllChecked = ref(true)

// ==================== Filter Summary ====================
const filterSummaryTags = computed(() => {
  const tags = []

  if (filters.industry) {
    const ind = industryOptions.value.find(i => i.id === filters.industry)
    if (ind) tags.push({ type: 'industry', value: filters.industry, label: ind.name })
  }
  if (filters.sub_industry) {
    const sub = subIndustryOptions.value.find(i => i.id === filters.sub_industry)
    if (sub) tags.push({ type: 'sub_industry', value: filters.sub_industry, label: sub.name })
  }
  filters.categoryList.forEach(catId => {
    const cat = categoryOptions.value.find(c => c.id === catId)
    if (cat) tags.push({ type: 'category', value: catId, label: cat.name })
  })
  if (filters.province) {
    const prov = provinceOptions.value.find(p => p.id === filters.province)
    if (prov) tags.push({ type: 'province', value: filters.province, label: prov.name })
  }
  if (filters.city) {
    const c = cityOptions.value.find(ci => ci.id === filters.city)
    if (c) tags.push({ type: 'city', value: filters.city, label: c.name })
  }
  filters.tags.forEach(tag => {
    tags.push({ type: 'tag', value: tag, label: tag })
  })

  return tags
})

function removeFilterSummary(type, value) {
  switch (type) {
    case 'industry':
      filters.industry = ''
      filters.sub_industry = ''
      subIndustryOptions.value = []
      break
    case 'sub_industry':
      filters.sub_industry = ''
      break
    case 'category':
      filters.categoryList = filters.categoryList.filter(c => c !== value)
      if (filters.categoryList.length === 0) categoryAllChecked.value = true
      break
    case 'province':
      filters.province = ''
      filters.city = ''
      cityOptions.value = []
      break
    case 'city':
      filters.city = ''
      break
    case 'tag':
      filters.tags = filters.tags.filter(t => t !== value)
      break
  }
  onFilterChange()
}

// ==================== Detail Drawer ====================
const drawerVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)

// ==================== Claim Dialog ====================
const claimDialogVisible = ref(false)
const claimStep = ref(1)
const claimLoading = ref(false)
const claimSubmitting = ref(false)
const unclaimedEnts = ref([])
const selectedClaimEnt = ref(null)
const claimForm = reactive({
  legal_representative: '',
  business_license: null,
  position: '',
})
const claimLicenseFiles = ref([])

// ==================== Create Dialog ====================
const createDialogVisible = ref(false)
const createSaving = ref(false)
const createForm = reactive({
  name: '',
  credit_code: '',
  industry: '',
  sub_industry: '',
  category: '',
  province: '',
  city: '',
  tags: [],
  logo: null,
  description: '',
  legal_representative: '',
  business_license: null,
  position: '',
})
const createSubIndustryOptions = ref([])
const createCategoryOptions = ref([])
const createCityOptions = ref([])
const createLogoFiles = ref([])
const createLicenseFiles = ref([])

// ==================== Contact Dialog ====================
const contactVisible = ref(false)
const contactStep = ref(1)
const contactLoading = ref(false)
const contactData = ref({})
const currentContactOppId = ref(null)

// ==================== Helpers ====================
function truncateText(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function authStatusLabel(status) {
  const map = { unclaimed: '未认领', pending: '审核中', verified: '已认证', rejected: '已驳回' }
  return map[status] || status
}

function getAvatarColor(name) {
  if (!name) return 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))'
  const colors = [
    'linear-gradient(135deg, #2563EB, #1D4ED8)',
    'linear-gradient(135deg, #4CAF50, #2E7D32)',
    'linear-gradient(135deg, #FF9800, #E65100)',
    'linear-gradient(135deg, #9C27B0, #6A1B9A)',
    'linear-gradient(135deg, #00BCD4, #00838F)',
    'linear-gradient(135deg, #3F51B5, #1A237E)',
    'linear-gradient(135deg, #E91E63, #AD1457)',
    'linear-gradient(135deg, #607D8B, #37474F)',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

function copyText(text) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// ==================== Dict Loading ====================
async function loadIndustries() {
  try {
    const { data } = await getDictIndustry({ parent_id: 0 })
    if (data.code === 200) {
      industryOptions.value = data.data || []
    }
  } catch { /* ignore */ }
}

async function loadSubIndustries(parentId) {
  try {
    const { data } = await getDictIndustry({ parent_id: parentId })
    if (data.code === 200) {
      subIndustryOptions.value = data.data || []
    }
  } catch { /* ignore */ }
}

async function loadCategories(industryId) {
  try {
    const params = {}
    if (industryId) params.industry_id = industryId
    const { data } = await getDictCategory(params)
    if (data.code === 200) {
      categoryOptions.value = data.data || []
    }
  } catch { /* ignore */ }
}

async function loadProvinces() {
  try {
    const { data } = await getDictRegion({ parent_id: 0 })
    if (data.code === 200) {
      provinceOptions.value = data.data || []
    }
  } catch { /* ignore */ }
}

async function loadCities(parentId) {
  try {
    const { data } = await getDictRegion({ parent_id: parentId })
    if (data.code === 200) {
      cityOptions.value = data.data || []
    }
  } catch { /* ignore */ }
}

// ==================== Filter Handlers ====================
function onIndustryChange(val) {
  filters.sub_industry = ''
  subIndustryOptions.value = []
  if (val) {
    loadSubIndustries(val)
    loadCategories(val)
  } else {
    loadCategories()
  }
  onFilterChange()
}

function onProvinceChange(val) {
  filters.city = ''
  cityOptions.value = []
  if (val) {
    loadCities(val)
  }
  onFilterChange()
}

function onCategoryAllChange(val) {
  if (val) {
    filters.categoryList = []
    onFilterChange()
  }
}

function onCategoryChange(val) {
  if (val.length > 0) {
    categoryAllChecked.value = false
  } else {
    categoryAllChecked.value = true
  }
  onFilterChange()
}

function toggleHotTag(tag) {
  const idx = filters.tags.indexOf(tag)
  if (idx >= 0) {
    filters.tags.splice(idx, 1)
  } else {
    filters.tags.push(tag)
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
  filters.categoryList = []
  filters.province = ''
  filters.city = ''
  filters.tags = []
  filters.search = ''
  subIndustryOptions.value = []
  cityOptions.value = []
  categoryAllChecked.value = true
  currentPage.value = 1
  loadCategories()
  loadEnterprises()
}

// ==================== Enterprise List ====================
async function loadEnterprises() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.industry) params.industry_id = filters.industry
    if (filters.sub_industry) params.sub_industry_id = filters.sub_industry
    if (filters.categoryList.length > 0) params.category_id = filters.categoryList.join(',')
    if (filters.province) params.province_id = filters.province
    if (filters.city) params.region_id = filters.city
    if (filters.tags.length) params.tags = filters.tags.join(',')
    if (filters.search) params.keyword = filters.search

    const { data } = await getEnterpriseList(params)
    if (data.code === 200) {
      enterprises.value = data.data.items || data.data || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

function onPageSizeChange() {
  currentPage.value = 1
  loadEnterprises()
}

// ==================== Detail Drawer ====================
async function openDetail(ent) {
  drawerVisible.value = true
  detailLoading.value = true
  detailData.value = null
  try {
    const { data } = await getEnterpriseDetail(ent.id)
    if (data.code === 200) {
      detailData.value = data.data
    }
  } finally {
    detailLoading.value = false
  }
}

// ==================== Claim Dialog ====================
function requireLogin() {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return false
  }
  return true
}

async function openClaimDialog() {
  if (!requireLogin()) return
  claimStep.value = 1
  selectedClaimEnt.value = null
  claimForm.legal_representative = ''
  claimForm.business_license = null
  claimForm.position = ''
  claimLicenseFiles.value = []
  claimDialogVisible.value = true
  await loadUnclaimedEnts()
}

async function loadUnclaimedEnts() {
  claimLoading.value = true
  try {
    const { data } = await getEnterpriseList({ auth_status: 'UNCLAIMED', page_size: 50 })
    if (data.code === 200) {
      unclaimedEnts.value = data.data.items || data.data || []
    }
  } finally {
    claimLoading.value = false
  }
}

function onSelectClaimEnt(ent) {
  selectedClaimEnt.value = ent
  claimStep.value = 2
}

function onClaimLicenseChange(file) {
  claimForm.business_license = file.raw
}

async function submitClaim() {
  if (!claimForm.legal_representative) {
    ElMessage.warning('请输入法人姓名')
    return
  }
  if (!claimForm.position) {
    ElMessage.warning('请输入您的职务')
    return
  }
  claimSubmitting.value = true
  try {
    const payload = {
      enterprise_id: selectedClaimEnt.value.id,
      legal_representative: claimForm.legal_representative,
      position: claimForm.position,
      business_license: '',
    }
    const { data } = await claimEnterprise(payload)
    if (data.code === 200) {
      ElMessage.success('认领申请已提交，请等待审核')
      claimDialogVisible.value = false
    } else {
      ElMessage.error(data.message || '认领失败')
    }
  } catch {
    ElMessage.error('认领请求失败')
  } finally {
    claimSubmitting.value = false
  }
}

function onClaimDialogClose() {
  claimStep.value = 1
  selectedClaimEnt.value = null
}

// ==================== Create Dialog ====================
function openCreateDialog() {
  if (!requireLogin()) return
  createForm.name = ''
  createForm.credit_code = ''
  createForm.industry = ''
  createForm.sub_industry = ''
  createForm.category = ''
  createForm.province = ''
  createForm.city = ''
  createForm.tags = []
  createForm.logo = null
  createForm.description = ''
  createForm.legal_representative = ''
  createForm.business_license = null
  createForm.position = ''
  createSubIndustryOptions.value = []
  createCategoryOptions.value = []
  createCityOptions.value = []
  createLogoFiles.value = []
  createLicenseFiles.value = []
  createDialogVisible.value = true
}

async function onCreateIndustryChange(val) {
  createForm.sub_industry = ''
  createForm.category = ''
  createSubIndustryOptions.value = []
  createCategoryOptions.value = []
  if (val) {
    try {
      const [subRes, catRes] = await Promise.all([
        getDictIndustry({ parent_id: val }),
        getDictCategory({ industry_id: val }),
      ])
      if (subRes.data.code === 200) createSubIndustryOptions.value = subRes.data.data || []
      if (catRes.data.code === 200) createCategoryOptions.value = catRes.data.data || []
    } catch { /* ignore */ }
  }
}

async function onCreateProvinceChange(val) {
  createForm.city = ''
  createCityOptions.value = []
  if (val) {
    try {
      const { data } = await getDictRegion({ parent_id: val })
      if (data.code === 200) createCityOptions.value = data.data || []
    } catch { /* ignore */ }
  }
}

function onCreateLogoChange(file) {
  createForm.logo = file.raw
}

function onCreateLicenseChange(file) {
  createForm.business_license = file.raw
}

async function submitCreate() {
  if (!createForm.name) {
    ElMessage.warning('请输入企业名称')
    return
  }
  if (!createForm.credit_code) {
    ElMessage.warning('请输入统一社会信用代码')
    return
  }
  if (!createForm.legal_representative) {
    ElMessage.warning('请输入法人姓名')
    return
  }
  createSaving.value = true
  try {
    const payload = {
      name: createForm.name,
      credit_code: createForm.credit_code,
      legal_representative: createForm.legal_representative,
      business_license: '',
      industry_id: createForm.industry || 0,
      sub_industry_id: createForm.sub_industry || 0,
      category_id: createForm.category || 0,
      province_id: createForm.province || 0,
      region_id: createForm.city || 0,
      tags: createForm.tags || [],
      description: createForm.description || '',
    }
    if (createForm.position) payload.position = createForm.position

    const { data } = await createEnterprise(payload)
    if (data.code === 200) {
      ElMessage.success('企业创建成功')
      createDialogVisible.value = false
      loadEnterprises()
    } else {
      ElMessage.error(data.message || '创建失败')
    }
  } catch {
    ElMessage.error('创建请求失败')
  } finally {
    createSaving.value = false
  }
}

function onCreateDialogClose() {
  createForm.name = ''
  createForm.credit_code = ''
  createForm.industry = ''
  createForm.sub_industry = ''
  createForm.category = ''
  createForm.province = ''
  createForm.city = ''
  createForm.tags = []
  createForm.logo = null
  createForm.description = ''
  createForm.legal_representative = ''
  createForm.business_license = null
  createForm.position = ''
}

// ==================== Contact Dialog ====================
function openContactDialog(oppId) {
  contactStep.value = 1
  contactData.value = {}
  currentContactOppId.value = oppId
  contactVisible.value = true
}

async function fetchContact() {
  if (!currentContactOppId.value) return
  contactLoading.value = true
  try {
    const { data } = await getContact(currentContactOppId.value)
    if (data.code === 200) {
      contactData.value = data.data || {}
      contactStep.value = 2
    } else {
      ElMessage.error(data.message || '获取联系方式失败')
    }
  } catch {
    ElMessage.error('获取联系方式失败')
  } finally {
    contactLoading.value = false
  }
}

// ==================== Init ====================
onMounted(() => {
  loadIndustries()
  loadCategories()
  loadProvinces()
  loadEnterprises()
})
</script>

<style scoped>
/* ===== Page Header ===== */
.page-header {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  padding: var(--spacing-xl) 0;
  margin-bottom: var(--spacing-lg);
  border-radius: var(--radius-lg);
}

.page-header-inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-xs);
}

.page-subtitle {
  font-size: var(--font-size-sm);
  opacity: 0.9;
}

.page-header-actions {
  display: flex;
  gap: var(--spacing-md);
}

.page-header-actions .btn-outline {
  background: transparent;
  border: 1px solid var(--color-white);
  color: var(--color-white);
}

.page-header-actions .btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* ===== Content Layout ===== */
.content-layout {
  display: flex;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  gap: var(--spacing-lg);
}

/* ===== Filter Sidebar ===== */
.filter-sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  height: fit-content;
  position: sticky;
  top: 20px;
  box-shadow: var(--shadow-sm);
}

.filter-group {
  margin-bottom: var(--spacing-lg);
}

.filter-group:last-of-type {
  margin-bottom: 0;
}

.filter-group-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-primary);
}

.category-checkbox-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

/* Hot Tags */
.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.hot-tag {
  padding: 4px 10px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.hot-tag:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.hot-tag.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-white);
}

/* Filter Summary */
.filter-summary {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-top: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.filter-summary-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  margin-bottom: var(--spacing-sm);
}

.filter-summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-summary-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.filter-summary-tag .remove {
  cursor: pointer;
  color: var(--color-text-placeholder);
  font-size: 10px;
}

.filter-summary-tag .remove:hover {
  color: var(--color-error);
}

.reset-btn {
  margin-top: 16px;
}

/* ===== Main Content ===== */
.enterprise-main {
  flex: 1;
  min-width: 0;
}

.result-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-placeholder);
  margin-bottom: var(--spacing-md);
}

.result-count strong {
  color: var(--color-text-primary);
}

/* ===== Enterprise Cards ===== */
.enterprise-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.enterprise-card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.enterprise-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.enterprise-card-top {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.enterprise-logo {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  flex-shrink: 0;
}

.enterprise-info {
  flex: 1;
  min-width: 0;
}

.enterprise-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-xs);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  word-break: break-all;
}

.verified-badge {
  color: var(--color-success);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
}

.auth-badge {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 1px 6px;
  background: #ECFDF5;
  color: #43a047;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

.enterprise-field {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}

.enterprise-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.ent-tag {
  display: inline-block;
  padding: 2px 8px;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: 11px;
  line-height: 1.5;
}

.enterprise-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
  margin-top: auto;
}

.enterprise-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

.enterprise-action {
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
}

/* ===== Pagination ===== */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-xl);
}

/* ===== Detail Drawer ===== */
.drawer-content {
  padding: var(--spacing-sm) 0;
}

.drawer-header-section {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.drawer-logo {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: var(--font-weight-bold);
  margin: 0 auto var(--spacing-md);
}

.drawer-name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.verified-badge-lg {
  display: inline-block;
  padding: 2px 8px;
  background: #ECFDF5;
  color: var(--color-success);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.drawer-field {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.drawer-info-grid {
  background: var(--color-bg);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-lg);
  display: grid;
  gap: var(--spacing-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.info-label {
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.info-value {
  text-align: right;
  word-break: break-all;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: flex-end;
}

.drawer-section {
  margin-bottom: var(--spacing-lg);
}

.drawer-section-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  background: var(--color-primary);
  color: var(--color-white);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  padding: 0 6px;
}

.drawer-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.drawer-opp-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.drawer-opp-item {
  padding: var(--spacing-md);
  background: var(--color-white);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
}

.drawer-opp-item:hover {
  border-color: var(--color-primary);
}

.opp-type-tag {
  display: inline-block;
  font-size: 11px;
  margin-bottom: 4px;
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.opp-type-tag.type-buy {
  background: #FFF7ED;
  color: var(--color-accent-buy);
}

.opp-type-tag.type-supply {
  background: #ECFDF5;
  color: var(--color-accent-supply);
}

.opp-title-text {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: 2px;
}

.opp-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

.drawer-opp-empty {
  text-align: center;
  color: var(--color-text-placeholder);
  font-size: var(--font-size-sm);
  padding: var(--spacing-lg) 0;
}

/* ===== Claim Dialog ===== */
.claim-tip {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
}

.claim-ent-list {
  max-height: 400px;
  overflow-y: auto;
}

.claim-ent-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: var(--spacing-sm);
}

.claim-ent-item:hover {
  border-color: var(--color-primary);
}

.claim-ent-item.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.claim-ent-logo {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  flex-shrink: 0;
}

.claim-ent-name {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
}

.claim-ent-industry {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
}

.claim-selected-info {
  background: var(--color-bg);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-primary-bg);
}

.claim-selected-label {
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
}

.claim-selected-grid {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.claim-grid-label {
  color: var(--color-text-secondary);
}

/* ===== Upload Area ===== */
.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-area:hover {
  border-color: var(--color-primary);
}

.upload-area-sm {
  padding: var(--spacing-md);
}

.upload-icon {
  font-size: 2rem;
  margin-bottom: var(--spacing-sm);
}

.upload-icon-sm {
  font-size: 1.25rem;
  margin-bottom: var(--spacing-xs);
}

.upload-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  margin-top: var(--spacing-xs);
}

.form-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-placeholder);
  margin-top: var(--spacing-sm);
}

/* ===== Form Divider ===== */
.form-divider {
  border-top: 1px solid var(--color-border-light);
  padding-top: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}

.form-divider h4 {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

/* ===== Contact Dialog ===== */
.contact-confirm,
.contact-result {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.contact-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary-bg);
  margin: 0 auto var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.contact-icon.success {
  background: #ECFDF5;
  color: var(--color-success);
}

.contact-text {
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-sm);
}

.contact-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.contact-info-card {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  text-align: left;
}

.contact-info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border-light);
  font-size: var(--font-size-sm);
}

.contact-info-row:last-child {
  border-bottom: none;
}

.contact-info-label {
  color: var(--color-text-secondary);
  min-width: 60px;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .page-header-inner {
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-md);
  }

  .content-layout {
    flex-direction: column;
  }

  .filter-sidebar {
    width: 100%;
    position: static;
  }

  .enterprise-grid {
    grid-template-columns: 1fr;
  }
}
</style>
