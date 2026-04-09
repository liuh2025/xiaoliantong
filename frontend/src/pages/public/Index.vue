<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">校链通 - 校友企业互联互通</h1>
        <p class="hero-subtitle">连接校友资源，共享商业机遇，构建校友企业生态圈</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/enterprise')">
            浏览企业名录
          </el-button>
          <el-button size="large" @click="$router.push('/opportunity')">
            查看商机广场
          </el-button>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalEnterprises }}</div>
          <div class="stat-label">入驻企业</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.activeOpportunities }}</div>
          <div class="stat-label">活跃商机</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalFeeds }}</div>
          <div class="stat-label">校友动态</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.alumniUsers }}</div>
          <div class="stat-label">注册校友</div>
        </div>
      </div>
    </section>

    <!-- Recommended Opportunities Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">推荐商机</h2>
        <router-link to="/opportunity" class="section-more">查看更多</router-link>
      </div>
      <div v-loading="oppLoading">
        <div v-if="recommendedOpps.length" class="cards-grid">
          <el-card
            v-for="opp in recommendedOpps"
            :key="opp.id"
            class="opp-card"
            shadow="hover"
            @click="$router.push(`/opportunity/${opp.id}`)"
          >
            <div class="opp-card-header">
              <el-tag :type="opp.type === 'buy' ? 'warning' : 'success'" size="small">
                {{ opp.type === 'buy' ? '采购' : '供应' }}
              </el-tag>
              <span class="opp-views">{{ opp.view_count || 0 }} 次浏览</span>
            </div>
            <h3 class="opp-title">{{ opp.title }}</h3>
            <p class="opp-enterprise">{{ opp.enterprise_name }}</p>
            <p class="opp-desc">{{ truncateText(opp.description, 80) }}</p>
          </el-card>
        </div>
        <el-empty v-else description="暂无推荐商机" />
      </div>
    </section>

    <!-- Newest Enterprises Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">最新入驻企业</h2>
        <router-link to="/enterprise" class="section-more">查看更多</router-link>
      </div>
      <div v-loading="entLoading">
        <div v-if="newestEnts.length" class="cards-grid">
          <el-card
            v-for="ent in newestEnts"
            :key="ent.id"
            class="ent-card"
            shadow="hover"
            @click="$router.push('/enterprise')"
          >
            <div class="ent-card-header">
              <h3 class="ent-name">{{ ent.name }}</h3>
              <el-tag
                :type="authStatusTagType(ent.auth_status)"
                size="small"
              >
                {{ authStatusLabel(ent.auth_status) }}
              </el-tag>
            </div>
            <p class="ent-info">{{ ent.industry_name || '' }} {{ ent.region_name ? '| ' + ent.region_name : '' }}</p>
            <p class="ent-desc">{{ truncateText(ent.description, 60) }}</p>
            <div v-if="ent.tags && ent.tags.length" class="ent-tags">
              <el-tag v-for="tag in ent.tags.slice(0, 3)" :key="tag" size="small" type="info" class="ent-tag">
                {{ tag }}
              </el-tag>
            </div>
          </el-card>
        </div>
        <el-empty v-else description="暂无入驻企业" />
      </div>
    </section>

    <!-- Newest Feeds Section -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-title">校友圈动态</h2>
        <router-link to="/feed" class="section-more">查看更多</router-link>
      </div>
      <div v-loading="feedLoading">
        <div v-if="newestFeeds.length" class="feed-list">
          <div v-for="feed in newestFeeds" :key="feed.id" class="feed-item">
            <div class="feed-meta">
              <span class="feed-author">{{ feed.publisher_name }}</span>
              <span v-if="feed.enterprise_name" class="feed-ent">{{ feed.enterprise_name }}</span>
              <span class="feed-time">{{ feed.created_at }}</span>
            </div>
            <p class="feed-content">{{ truncateText(feed.content, 120) }}</p>
          </div>
        </div>
        <el-empty v-else description="暂无动态" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecommended } from '../../api/opportunity'
import { getNewestEnterprise } from '../../api/enterprise'
import { getNewestFeed } from '../../api/feed'

const stats = ref({
  totalEnterprises: '---',
  activeOpportunities: '---',
  totalFeeds: '---',
  alumniUsers: '---',
})

const recommendedOpps = ref([])
const newestEnts = ref([])
const newestFeeds = ref([])
const oppLoading = ref(false)
const entLoading = ref(false)
const feedLoading = ref(false)

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

onMounted(() => {
  loadRecommendedOpps()
  loadNewestEnts()
  loadNewestFeeds()
})
</script>

<style scoped>
.home-page {
  padding-bottom: var(--spacing-2xl);
}

.hero-section {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-white);
  padding: var(--spacing-2xl) var(--spacing-lg);
  border-radius: var(--radius-lg);
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.hero-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.hero-subtitle {
  font-size: var(--font-size-lg);
  opacity: 0.9;
  margin-bottom: var(--spacing-lg);
}

.hero-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

.stats-section {
  margin-bottom: var(--spacing-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.stat-card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.stat-number {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: var(--spacing-xs);
}

.section {
  margin-bottom: var(--spacing-xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.section-more {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.opp-card,
.ent-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.opp-card:hover,
.ent-card:hover {
  box-shadow: var(--shadow-hover);
}

.opp-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.opp-views {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.opp-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
}

.opp-enterprise {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.opp-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.ent-card-header {
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

.feed-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.feed-item {
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
}

.feed-author {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.feed-ent {
  color: var(--color-primary);
}

.feed-time {
  color: var(--color-text-placeholder);
  margin-left: auto;
}

.feed-content {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
