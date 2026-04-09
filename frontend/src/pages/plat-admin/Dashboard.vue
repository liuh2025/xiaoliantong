<template>
  <div class="dashboard-page">
    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card" v-for="stat in statsConfig" :key="stat.key">
        <div class="stat-value">{{ stats[stat.key] ?? '-' }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Pending Tasks -->
    <el-card class="section-card">
      <template #header>
        <span>待处理任务</span>
      </template>
      <el-table :data="pendingAudits" v-loading="auditLoading" empty-text="暂无待处理任务">
        <el-table-column prop="name" label="企业名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="credit_code" label="统一社会信用代码" min-width="200" />
        <el-table-column prop="legal_representative" label="法定代表人" min-width="120" />
        <el-table-column prop="created_at" label="申请时间" min-width="170" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <router-link :to="{ name: 'Audit' }">
              <el-button size="small" type="primary">去审核</el-button>
            </router-link>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Trend Placeholder -->
    <el-card class="section-card">
      <template #header>
        <span>数据趋势</span>
      </template>
      <div class="trend-placeholder">
        <el-empty description="趋势图表（待接入图表组件）" :image-size="80" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getAuditList } from '../../api/platAdmin'

const stats = ref({
  total_users: 0,
  total_enterprises: 0,
  total_opportunities: 0,
  pending_audits: 0,
})

const statsConfig = [
  { key: 'total_users', label: '用户总数' },
  { key: 'total_enterprises', label: '企业总数' },
  { key: 'total_opportunities', label: '商机总数' },
  { key: 'pending_audits', label: '待审核' },
]

const auditLoading = ref(false)
const pendingAudits = ref([])

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

async function fetchPendingAudits() {
  auditLoading.value = true
  try {
    const { data: res } = await getAuditList({ status: 'pending', page: 1, page_size: 5 })
    if (res.code === 200) {
      pendingAudits.value = res.data.items || []
    }
  } catch {
    // silent
  } finally {
    auditLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchPendingAudits()
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

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.section-card {
  margin-bottom: 16px;
}

.trend-placeholder {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
