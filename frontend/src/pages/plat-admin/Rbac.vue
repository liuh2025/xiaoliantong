<template>
  <div class="rbac-page">
    <el-card v-loading="loading">
      <template #header>
        <span>账号与角色权限</span>
      </template>

      <el-empty v-if="!loading && roles.length === 0" description="暂无角色数据" />

      <div v-else class="rbac-layout">
        <!-- Left: Role list -->
        <div class="role-sidebar">
          <div
            v-for="role in roles"
            :key="role.id"
            class="role-item"
            :class="{ active: selectedRoleId === role.id }"
            @click="selectRole(role.id)"
          >
            <div class="role-item-name">{{ role.name }}</div>
            <el-tag size="small" type="info">{{ role.code }}</el-tag>
          </div>
        </div>

        <!-- Right: Permission matrix -->
        <div class="permission-panel">
          <div v-if="!selectedRole" class="empty-hint">请选择左侧角色查看权限配置</div>
          <template v-else>
            <div class="panel-header">
              <div>
                <span class="panel-title">{{ selectedRole.name }}</span>
                <span class="panel-desc">{{ selectedRole.description }}</span>
              </div>
              <el-button type="primary" size="small" :loading="saving" @click="savePermissions">保存配置</el-button>
            </div>

            <el-table :data="permissionModules" border size="small" class="perm-table">
              <el-table-column prop="label" label="功能模块" width="140" />
              <el-table-column label="权限" min-width="200">
                <template #default="{ row }">
                  <el-checkbox
                    :model-value="currentPermissions.includes(row.key)"
                    @change="(val) => togglePermission(row.key, val)"
                  >
                    启用
                  </el-checkbox>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRoles, getRoleDetail, updateRolePermissions } from '../../api/platAdmin'

const loading = ref(false)
const saving = ref(false)
const roles = ref([])
const selectedRoleId = ref(null)
const currentPermissions = ref([])

const permissionModules = [
  { key: 'dashboard', label: '数据大盘' },
  { key: 'audit', label: '企业审核' },
  { key: 'tenant', label: '企业租户' },
  { key: 'content', label: '内容管理' },
  { key: 'master_data', label: '基础数据' },
  { key: 'role', label: '角色权限' },
  { key: 'settings', label: '系统设置' },
  { key: 'enterprise', label: '企业信息' },
  { key: 'opportunity', label: '商机管理' },
  { key: 'feed', label: '校友圈' },
  { key: 'member', label: '成员管理' },
  { key: 'public', label: '公开浏览' },
]

const selectedRole = computed(() => {
  return roles.value.find((r) => r.id === selectedRoleId.value) || null
})

function togglePermission(key, enabled) {
  if (enabled) {
    if (!currentPermissions.value.includes(key)) {
      currentPermissions.value.push(key)
    }
  } else {
    currentPermissions.value = currentPermissions.value.filter((k) => k !== key)
  }
}

async function selectRole(id) {
  selectedRoleId.value = id
  try {
    const { data: res } = await getRoleDetail(id)
    if (res.code === 200) {
      currentPermissions.value = res.data.permissions || []
    }
  } catch {
    currentPermissions.value = []
  }
}

async function savePermissions() {
  if (!selectedRoleId.value) return
  saving.value = true
  try {
    const { data: res } = await updateRolePermissions(selectedRoleId.value, {
      permissions: currentPermissions.value,
    })
    if (res.code === 200) {
      ElMessage.success('权限配置已保存')
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getRoles()
    if (res.code === 200) {
      roles.value = res.data.items || res.data || []
      if (roles.value.length > 0) {
        await selectRole(roles.value[0].id)
      }
    }
  } catch {
    ElMessage.error('加载角色数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.rbac-layout {
  display: flex;
  gap: 24px;
  min-height: 400px;
}

.role-sidebar {
  width: 220px;
  flex-shrink: 0;
  border-right: 1px solid var(--color-border-light);
  padding-right: 16px;
}

.role-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}

.role-item:hover {
  background: var(--color-bg);
}

.role-item.active {
  background: rgba(30, 136, 229, 0.08);
  border: 1px solid var(--color-primary);
}

.role-item-name {
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.permission-panel {
  flex: 1;
}

.empty-hint {
  text-align: center;
  color: var(--color-text-secondary);
  padding: 60px 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
  margin-right: 8px;
}

.panel-desc {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.perm-table {
  max-width: 400px;
}
</style>
