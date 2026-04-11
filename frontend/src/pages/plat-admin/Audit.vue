<template>
  <div class="audit-page">
    <el-card>
      <template #header>
        <span>企业审核</span>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待审核" name="pending" />
        <el-tab-pane label="已通过" name="approved" />
        <el-tab-pane label="已拒绝" name="rejected" />
      </el-tabs>

      <el-table :data="list" v-loading="loading" empty-text="暂无审核数据">
        <el-table-column prop="enterprise_name" label="企业名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="credit_code" label="统一社会信用代码" min-width="200" />
        <el-table-column prop="legal_representative" label="法定代表人" min-width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" min-width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="openApproveDialog(row)">通过</el-button>
              <el-button size="small" type="danger" @click="openRejectDialog(row)">拒绝</el-button>
            </template>
            <span v-else class="text-secondary">已处理</span>
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

    <!-- Approve Dialog -->
    <el-dialog v-model="approveVisible" title="审核通过" width="600px" destroy-on-close>
      <div v-if="currentRow" class="audit-detail">
        <h4 style="margin-bottom:12px;">企业信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="企业名称">{{ currentRow.name }}</el-descriptions-item>
          <el-descriptions-item label="信用代码">{{ currentRow.credit_code }}</el-descriptions-item>
          <el-descriptions-item label="法定代表人">{{ currentRow.legal_representative }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ currentRow.created_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-form :model="approveForm" label-width="80px" style="margin-top:16px;">
        <el-form-item label="备注">
          <el-input v-model="approveForm.reason" type="textarea" :rows="3" placeholder="可选填写通过备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveVisible = false">取消</el-button>
        <el-button type="success" :loading="submitting" @click="submitApprove">确认通过</el-button>
      </template>
    </el-dialog>

    <!-- Reject Dialog -->
    <el-dialog v-model="rejectVisible" title="审核拒绝" width="600px" destroy-on-close>
      <div v-if="currentRow" class="audit-detail">
        <h4 style="margin-bottom:12px;">企业信息</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="企业名称">{{ currentRow.name }}</el-descriptions-item>
          <el-descriptions-item label="信用代码">{{ currentRow.credit_code }}</el-descriptions-item>
          <el-descriptions-item label="法定代表人">{{ currentRow.legal_representative }}</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ currentRow.created_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <el-form :model="rejectForm" label-width="80px" style="margin-top:16px;">
        <el-form-item label="拒绝原因" required>
          <el-input v-model="rejectForm.reason" type="textarea" :rows="3" placeholder="请填写拒绝原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="submitReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuditList, approveEnterprise, rejectEnterprise } from '../../api/platAdmin'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const activeTab = ref('all')

const approveVisible = ref(false)
const rejectVisible = ref(false)
const submitting = ref(false)
const currentRow = ref(null)
const approveForm = ref({ reason: '' })
const rejectForm = ref({ reason: '' })

const statusMap = {
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
  verified: { label: '已认证', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' },
  unclaimed: { label: '未认领', type: 'info' },
}

function statusType(status) {
  return statusMap[status]?.type || 'info'
}

function statusLabel(status) {
  return statusMap[status]?.label || status || '-'
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }
    const { data: res } = await getAuditList(params)
    if (res.code === 200) {
      list.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载审核列表失败')
  } finally {
    loading.value = false
  }
}

function handleTabChange() {
  page.value = 1
  fetchData()
}

function openApproveDialog(row) {
  currentRow.value = row
  approveForm.value = { reason: '' }
  approveVisible.value = true
}

function openRejectDialog(row) {
  currentRow.value = row
  rejectForm.value = { reason: '' }
  rejectVisible.value = true
}

async function submitApprove() {
  submitting.value = true
  try {
    const { data: res } = await approveEnterprise(currentRow.value.id, approveForm.value)
    if (res.code === 200) {
      ElMessage.success('审核通过')
      approveVisible.value = false
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

async function submitReject() {
  if (!rejectForm.value.reason) {
    ElMessage.warning('请填写拒绝原因')
    return
  }
  submitting.value = true
  try {
    const { data: res } = await rejectEnterprise(currentRow.value.id, rejectForm.value)
    if (res.code === 200) {
      ElMessage.success('已拒绝')
      rejectVisible.value = false
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
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.text-secondary {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style>
