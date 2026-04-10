<template>
  <div class="dashboard-page">
    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in statsConfig" :key="stat.key">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-value">{{ stats[stat.key] ?? '-' }}</div>
        <div class="stat-label">{{ stat.label }}</div>
        <div class="stat-trend" v-if="stat.trend" :class="stat.trend > 0 ? 'up' : 'down'">
          {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
        </div>
      </div>
    </div>

    <!-- Trend Chart -->
    <el-card class="section-card">
      <template #header>
        <span>最近7天商机趋势</span>
      </template>
      <div class="trend-chart">
        <div class="chart-bars">
          <div v-for="(val, idx) in trendData" :key="idx" class="chart-bar-item">
            <div class="chart-bar" :style="{ height: val + '%' }" />
            <span class="chart-label">{{ trendLabels[idx] }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Recent Enterprises -->
    <el-card class="section-card">
      <template #header>
        <span>最新企业入驻</span>
      </template>
      <el-table :data="recentEnterprises" v-loading="entLoading" empty-text="暂无入驻数据">
        <el-table-column prop="name" label="企业名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="industry_name" label="行业" min-width="120" />
        <el-table-column prop="province_name" label="地区" min-width="120" />
        <el-table-column prop="auth_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.auth_status === 'verified' ? 'success' : row.auth_status === 'pending' ? 'warning' : 'info'" size="small">
              {{ row.auth_status === 'verified' ? '已认证' : row.auth_status === 'pending' ? '审核中' : '未认领' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入驻时间" min-width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getAuditList } from '../../api/platAdmin'

const stats = ref({
  total_enterprises: 0,
  total_opportunities: 0,
  total_matchmaking: 0,
  total_users: 0,
})

const statsConfig = [
  { key: 'total_enterprises', label: '入驻企业', icon: '🏢', trend: 12 },
  { key: 'total_opportunities', label: '累计商机', icon: '📋', trend: 8 },
  { key: 'total_matchmaking', label: '成功撮合', icon: '🤝', trend: 15 },
  { key: 'total_users', label: '活跃校友', icon: '👥', trend: 5 },
]

const trendData = ref([40, 65, 55, 80, 70, 90, 85])
const trendLabels = ref(['周一', '周二', '周三', '周四', '周五', '周六', '周日'])

const entLoading = ref(false)
const recentEnterprises = ref([])

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

async function fetchRecentEnterprises() {
  entLoading.value = true
  try {
    const { data: res } = await getAuditList({ page: 1, page_size: 5 })
    if (res.code === 200) {
      recentEnterprises.value = res.data.items || []
    }
  } catch {
    // silent
  } finally {
    entLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchRecentEnterprises()
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
  gap: 24px;
  width: 100%;
  max-width: 600px;
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
  max-width: 40px;
  background: linear-gradient(180deg, var(--color-primary), rgba(30, 136, 229, 0.3));
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.chart-label {
  font-size: 0.75rem;
  color: var(--color-text-placeholder);
  margin-top: 8px;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
