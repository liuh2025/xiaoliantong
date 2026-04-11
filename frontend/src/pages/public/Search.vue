<template>
  <div class="search-page">
    <!-- Search Bar -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索商机、企业、动态..."
        size="large"
        clearable
        @keyup.enter="doSearch"
      >
        <template #append>
          <el-button @click="doSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" @tab-change="onTabChange">
      <el-tab-pane label="商机" name="opportunity" />
      <el-tab-pane label="企业" name="enterprise" />
      <el-tab-pane label="动态" name="feed" />
    </el-tabs>

    <!-- Results -->
    <div v-loading="loading" class="search-results">
      <div v-if="results.length" class="results-list">
        <!-- Opportunity results -->
        <template v-if="activeTab === 'opportunity'">
          <el-card
            v-for="item in results"
            :key="item.id"
            class="result-card"
            shadow="hover"
            @click="$router.push(`/opportunity/${item.id}`)"
          >
            <div class="result-header">
              <el-tag :type="item.type === 'buy' ? 'warning' : 'success'" size="small">
                {{ item.type === 'buy' ? '采购' : '供应' }}
              </el-tag>
              <span class="result-title">{{ item.title }}</span>
            </div>
            <p class="result-sub">{{ item.enterprise_name }}</p>
            <p class="result-desc">{{ truncateText(item.description, 100) }}</p>
          </el-card>
        </template>

        <!-- Enterprise results -->
        <template v-if="activeTab === 'enterprise'">
          <el-card
            v-for="item in results"
            :key="item.id"
            class="result-card"
            shadow="hover"
            @click="$router.push('/enterprise')"
          >
            <div class="result-header">
              <span class="result-title">{{ item.name }}</span>
              <el-tag :type="authStatusTagType(item.auth_status)" size="small">
                {{ authStatusLabel(item.auth_status) }}
              </el-tag>
            </div>
            <p class="result-sub">{{ item.industry_name || '' }} {{ item.region_name ? '| ' + item.region_name : '' }}</p>
            <p class="result-desc">{{ truncateText(item.description, 100) }}</p>
          </el-card>
        </template>

        <!-- Feed results -->
        <template v-if="activeTab === 'feed'">
          <el-card
            v-for="item in results"
            :key="item.id"
            class="result-card"
            shadow="hover"
            @click="$router.push('/feed')"
          >
            <div class="result-header">
              <span class="result-author">{{ item.publisher_name }}</span>
              <span class="result-time">{{ item.created_at }}</span>
            </div>
            <p class="result-desc">{{ truncateText(item.content, 150) }}</p>
          </el-card>
        </template>
      </div>

      <el-empty v-else-if="!loading && searched" description="未找到相关结果" />
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="doSearch"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { search } from '../../api/search'

const route = useRoute()
const router = useRouter()

const keyword = ref(route.query.q || '')
const activeTab = ref(route.query.tab || 'opportunity')
const results = ref([])
const loading = ref(false)
const searched = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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

function onTabChange(tab) {
  currentPage.value = 1
  results.value = []
  searched.value = false
  router.replace({ query: { q: keyword.value, tab } })
  if (keyword.value) {
    doSearch()
  }
}

async function doSearch() {
  if (!keyword.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const { data } = await search({
      q: keyword.value,
      type: activeTab.value,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    if (data.code === 200) {
      results.value = data.data.items || []
      total.value = data.data.total || 0
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (keyword.value) {
    doSearch()
  }
})
</script>

<style scoped>
.search-page {
  padding-bottom: var(--spacing-2xl);
}

.search-bar {
  margin-bottom: var(--spacing-lg);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.result-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.result-card:hover {
  box-shadow: var(--shadow-hover);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.result-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.result-sub {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.result-author {
  font-weight: var(--font-weight-medium);
}

.result-time {
  color: var(--color-text-placeholder);
  margin-left: auto;
  font-size: var(--font-size-sm);
}

.result-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--spacing-lg);
}
</style>
