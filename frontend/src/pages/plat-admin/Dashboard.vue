<template>
  <div class="dashboard-page">
    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in statsConfig" :key="stat.key">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-value">{{ stats[stat.key] ?? '-' }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-trend" v-if="stats[stat.trendKey]" :class="stats[stat.trendKey] > 0 ? 'up' : 'down'">
          {{ stats[stat.trendKey] > 0 ? '↑' : '↓' }} {{ Math.abs(stats[stat.trendKey]) }}%
        </div>
      </div>
    </div>

    <!-- Trend Chart -->
    <el-card class="section-card">
      <template #header>
        <span>商机趋势近30天</span>
      </template>
      <div class="trend-chart" v-loading="trendLoading">
        <div class="chart-bars">
          <div v-for="(item, idx) in trendData" :key="idx" class="chart-bar-item">
            <div class="chart-bar" :style="{ height: barHeight(item.count) + '%' }" />
            <span class="chart-label">{{ item.label }}</span>
          </div>
        </div>
        <el-empty v-if="!trendLoading && trendData.length === 0" description="暂无趋势数据" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getDashboardTrend } from '../../api/platAdmin'

const stats = ref({
  enterprise_count: 0,
  opportunity_count: 0,
  deal_count: 0,
  active_user_count: 0,
  enterprise_trend: 0,
  opportunity_trend: 0,
  deal_trend: 0,
})

const statsConfig = [
  { key: 'enterprise_count', label: '入驻企业', icon: '🏢', trendKey: 'enterprise_trend' },
  { key: 'opportunity_count', label: '发布商机', icon: '📋', trendKey: 'opportunity_trend' },
  { key: 'deal_count', label: '成功撮合', icon: '🤝', trendKey: 'deal_trend' },
  { key: 'active_user_count', label: '活跃用户', icon: '👥', trendKey: '' },
]

const trendLoading = ref(false)
const trendData = ref([])
const maxCount = ref(1)

function barHeight(count) {
  if (maxCount.value === 0) return 0
  return Math.max((count / maxCount.value) * 100, 2)
}

async function fetchStats() {
  try {
    const { data: res } = await getDashboardStats()
    if (res.code === 200) {
      stats.value = res.data || {}
    }
  } catch {
    ElMessage.error('加载统计数据失败')
  }
}

async function fetchTrend() {
  trendLoading.value = true
  try {
    const { data: res } = await getDashboardTrend({ period: 30, type: 'opportunity' })
    if (res.code === 200) {
      const items = res.data?.opportunity_trend || []
      maxCount.value = Math.max(...items.map(i => i.count), 1)
      trendData.value = items.map(item => ({
        label: item.date.slice(5),
        count: item.count,
      }))
    }
  } catch {
    // silent
  } finally {
    trendLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchTrend()
})
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  box-shadow: var(--shadow-sm);
}

.stat-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stat-trend {
  font-size: 0.75rem;
  margin-top: 4px;
}

.stat-trend.up {
  color: var(--color-success);
}

.stat-trend.down {
  color: var(--color-error);
}

.section-card {
  margin-bottom: 16px;
}

.trend-chart {
  min-height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px 0;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  width: 100%;
  height: 160px;
}

.chart-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
}

.chart-bar {
  width: 100%;
  max-width: 20px;
  background: linear-gradient(180deg, var(--color-primary), rgba(30, 136, 229, 0.3));
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.chart-label {
  font-size: 0.6rem;
  color: var(--color-text-placeholder);
  margin-top: 4px;
  transform: rotate(-45deg);
  white-space: nowrap;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
