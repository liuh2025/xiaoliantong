<template>
  <div class="opportunity-manage-page">
    <el-card>
      <template #header>
        <span>商机内容管理</span>
      </template>

      <!-- Filters -->
      <div class="filter-bar">
        <el-select v-model="filterType" placeholder="类型" clearable style="width: 120px" @change="fetchData">
          <el-option label="采购" value="buy" />
          <el-option label="供应" value="supply" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 120px" @change="fetchData">
          <el-option label="上线中" value="active" />
          <el-option label="已下线" value="offline" />
        </el-select>
      </div>

      <el-table :data="list" v-loading="loading" empty-text="暂无商机数据">
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="enterprise_name" label="所属企业" min-width="150" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="row.type === 'buy' ? 'warning' : 'success'" size="small">
              {{ row.type === 'buy' ? '采购' : '供应' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '上线' : '下线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览量" width="90" />
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">查看</el-button>
            <el-button
              v-if="row.status === 'active'"
              size="small"
              type="danger"
              @click="openOfflineDialog(row)"
            >下线</el-button>
          </template>
        </el-table-column>
      </el-table>

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
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="drawerVisible" title="商机详情" size="500px" destroy-on-close>
      <el-descriptions :column="1" border v-loading="detailLoading">
        <el-descriptions-item label="标题">{{ detail.title }}</el-descriptions-item>
        <el-descriptions-item label="所属企业">{{ detail.enterprise_name }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="detail.type === 'buy' ? 'warning' : 'success'" size="small">
            {{ detail.type === 'buy' ? '采购' : '供应' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="detail.status === 'active' ? 'success' : 'info'" size="small">
            {{ detail.status === 'active' ? '上线' : '下线' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="行业">{{ detail.industry_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地区">{{ detail.region_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="标签">
          <template v-if="detail.tags && detail.tags.length">
            <el-tag v-for="tag in detail.tags" :key="tag" size="small" type="info" style="margin-right:4px;">{{ tag }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="浏览量">{{ detail.view_count }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="详情描述">
          <div style="white-space:pre-wrap;line-height:1.6;">{{ detail.description || '暂无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="联系信息">
          <div v-if="detail.contact_name || detail.contact_phone">
            <p v-if="detail.contact_name">联系人：{{ detail.contact_name }}</p>
            <p v-if="detail.contact_phone">电话：{{ detail.contact_phone }}</p>
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-drawer>

    <!-- Offline Dialog -->
    <el-dialog v-model="offlineVisible" title="下线商机" width="480px" destroy-on-close>
      <el-form :model="offlineForm" label-width="80px">
        <el-form-item label="商机标题">
          <span>{{ currentRow?.title }}</span>
        </el-form-item>
        <el-form-item label="下线原因" required>
          <el-input v-model="offlineForm.reason" type="textarea" :rows="3" placeholder="请填写下线原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="offlineVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="submitOffline">确认下线</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getContentOpportunities, getContentOpportunityDetail, offlineContentOpportunity } from '../../api/platAdmin'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filterType = ref('')
const filterStatus = ref('')

const drawerVisible = ref(false)
const detailLoading = ref(false)
const detail = ref({})

const offlineVisible = ref(false)
const submitting = ref(false)
const currentRow = ref(null)
const offlineForm = ref({ reason: '' })

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterType.value) params.type = filterType.value
    if (filterStatus.value) params.status = filterStatus.value
    const { data: res } = await getContentOpportunities(params)
    if (res.code === 200) {
      list.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载商机列表失败')
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  drawerVisible.value = true
  detailLoading.value = true
  detail.value = {}
  try {
    const { data: res } = await getContentOpportunityDetail(row.id)
    if (res.code === 200) {
      detail.value = res.data || {}
    }
  } catch {
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

function openOfflineDialog(row) {
  currentRow.value = row
  offlineForm.value = { reason: '' }
  offlineVisible.value = true
}

async function submitOffline() {
  if (!offlineForm.value.reason) {
    ElMessage.warning('请填写下线原因')
    return
  }
  submitting.value = true
  try {
    const { data: res } = await offlineContentOpportunity(currentRow.value.id, { reason: offlineForm.value.reason })
    if (res.code === 200) {
      ElMessage.success('已下线')
      offlineVisible.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
