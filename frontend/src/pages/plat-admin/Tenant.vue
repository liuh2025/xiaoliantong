<template>
  <div class="tenant-page">
    <el-card>
      <template #header>
        <span>企业租户管理</span>
      </template>

      <!-- Search & Filter -->
      <div class="filter-bar">
        <el-input
          v-model="searchKey"
          placeholder="搜索企业名称"
          clearable
          style="width: 240px"
          @clear="fetchData"
          @keyup.enter="fetchData"
        />
        <el-select v-model="filterStatus" placeholder="认证状态" clearable style="width: 160px" @change="fetchData">
          <el-option label="已认证" value="verified" />
          <el-option label="待审核" value="pending" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="未认领" value="unclaimed" />
        </el-select>
        <el-button type="primary" @click="fetchData">搜索</el-button>
      </div>

      <el-table :data="list" v-loading="loading" empty-text="暂无企业数据">
        <el-table-column prop="name" label="企业名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="credit_code" label="统一社会信用代码" min-width="200" />
        <el-table-column prop="auth_status" label="认证状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.auth_status)">{{ statusLabel(row.auth_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active !== false ? 'success' : 'info'">
              {{ row.is_active !== false ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openMemberDialog(row)">成员管理</el-button>
            <el-button size="small" type="warning" @click="handleToggleStatus(row)">
              {{ row.is_active !== false ? '停用' : '启用' }}
            </el-button>
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

    <!-- Member Management Dialog -->
    <el-dialog
      v-model="memberDialogVisible"
      :title="`成员管理 - ${currentEnt?.name || ''}`"
      width="720px"
      destroy-on-close
    >
      <div class="member-dialog-header">
        <el-button size="small" type="primary" @click="openAddMember">添加成员</el-button>
      </div>
      <el-table :data="members" v-loading="membersLoading" size="small" empty-text="暂无成员">
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="phone" label="手机号" min-width="130" />
        <el-table-column prop="role" label="角色" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'enterprise_admin' ? 'danger' : ''" size="small">
              {{ row.role === 'enterprise_admin' ? '管理员' : '普通员工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <el-button size="small" @click="openEditMember(row)">编辑角色</el-button>
            <el-button size="small" type="warning" @click="handleResetPassword(row)">重置密码</el-button>
            <el-button size="small" type="danger" @click="handleUnbindMember(row)">解绑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="memberDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Add / Edit Member Sub-Dialog -->
    <el-dialog
      v-model="memberFormVisible"
      :title="isEditMember ? '编辑成员角色' : '添加成员'"
      width="480px"
      destroy-on-close
      append-to-body
    >
      <el-form :model="memberForm" label-width="80px">
        <el-form-item v-if="!isEditMember" label="手机号" required>
          <el-input v-model="memberForm.phone" placeholder="请输入手机号" maxlength="11" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="memberForm.role" style="width: 100%">
            <el-option label="普通员工" value="employee" />
            <el-option label="管理员" value="enterprise_admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="memberFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="memberSaving" @click="submitMember">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getTenantList,
  getTenantMembers,
  createTenantMember,
  updateTenantMember,
  resetTenantMemberPassword,
  unbindTenantMember,
  toggleTenantStatus,
} from '../../api/platAdmin'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKey = ref('')
const filterStatus = ref('')

// Member dialog
const memberDialogVisible = ref(false)
const membersLoading = ref(false)
const members = ref([])
const currentEnt = ref(null)

// Member form sub-dialog
const memberFormVisible = ref(false)
const memberSaving = ref(false)
const isEditMember = ref(false)
const currentMember = ref(null)
const memberForm = ref({ phone: '', role: 'employee' })

const statusMap = {
  verified: { label: '已认证', type: 'success' },
  pending: { label: '待审核', type: 'warning' },
  approved: { label: '已通过', type: 'success' },
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
    if (searchKey.value) params.search = searchKey.value
    if (filterStatus.value) params.auth_status = filterStatus.value
    const { data: res } = await getTenantList(params)
    if (res.code === 200) {
      list.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch {
    ElMessage.error('加载企业列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchMembers() {
  if (!currentEnt.value) return
  membersLoading.value = true
  try {
    const { data: res } = await getTenantMembers(currentEnt.value.id, { page: 1, page_size: 100 })
    if (res.code === 200) {
      members.value = res.data.items || []
    }
  } catch {
    // silent
  } finally {
    membersLoading.value = false
  }
}

async function openMemberDialog(row) {
  currentEnt.value = row
  members.value = []
  memberDialogVisible.value = true
  await fetchMembers()
}

async function handleToggleStatus(row) {
  const action = row.is_active !== false ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(
      `确定要${action}企业 "${row.name}" 吗？`,
      `${action}企业`,
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await toggleTenantStatus(row.id)
    if (res.code === 200) {
      ElMessage.success(`${action}成功`)
      await fetchData()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch {
    // cancelled
  }
}

function openAddMember() {
  isEditMember.value = false
  currentMember.value = null
  memberForm.value = { phone: '', role: 'employee' }
  memberFormVisible.value = true
}

function openEditMember(memberRow) {
  isEditMember.value = true
  currentMember.value = memberRow
  memberForm.value = { role: memberRow.role }
  memberFormVisible.value = true
}

async function submitMember() {
  memberSaving.value = true
  try {
    let res
    if (isEditMember.value) {
      res = await updateTenantMember(currentEnt.value.id, currentMember.value.id, memberForm.value)
    } else {
      if (!memberForm.value.phone) {
        ElMessage.warning('请输入手机号')
        return
      }
      res = await createTenantMember(currentEnt.value.id, memberForm.value)
    }
    if (res.data.code === 200) {
      ElMessage.success(isEditMember.value ? '更新成功' : '添加成功')
      memberFormVisible.value = false
      await fetchMembers()
    } else {
      ElMessage.error(res.data.message || '操作失败')
    }
  } catch {
    ElMessage.error('操作失败')
  } finally {
    memberSaving.value = false
  }
}

async function handleResetPassword(memberRow) {
  try {
    await ElMessageBox.confirm(
      `确定要重置成员 "${memberRow.username || memberRow.phone}" 的密码吗？`,
      '重置密码',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await resetTenantMemberPassword(memberRow.id)
    if (res.code === 200) {
      ElMessage.success('密码已重置')
    } else {
      ElMessage.error(res.message || '重置失败')
    }
  } catch {
    // cancelled
  }
}

async function handleUnbindMember(memberRow) {
  try {
    await ElMessageBox.confirm(
      `确定要解绑成员 "${memberRow.username || memberRow.phone}" 吗？此操作不可恢复。`,
      '解绑成员',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
    const { data: res } = await unbindTenantMember(memberRow.id)
    if (res.code === 200) {
      ElMessage.success('已解绑')
      await fetchMembers()
    } else {
      ElMessage.error(res.message || '解绑失败')
    }
  } catch {
    // cancelled
  }
}

onMounted(fetchData)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.member-dialog-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}
</style>
