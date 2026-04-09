<template>
  <div class="rbac-page">
    <el-card v-loading="loading">
      <template #header>
        <span>角色与权限</span>
      </template>

      <el-empty v-if="!loading && roles.length === 0" description="暂无角色数据" />

      <div v-else class="role-list">
        <el-card v-for="role in roles" :key="role.id || role.code" class="role-card" shadow="hover">
          <template #header>
            <div class="role-card-header">
              <span class="role-name">{{ role.name }}</span>
              <el-tag size="small">{{ role.code }}</el-tag>
            </div>
          </template>
          <div class="role-desc">{{ role.description || '暂无描述' }}</div>

          <div class="permission-section">
            <div class="section-title">权限列表</div>
            <div class="permission-grid" v-if="role.permissions && role.permissions.length > 0">
              <el-tag
                v-for="perm in role.permissions"
                :key="perm.code || perm"
                size="small"
                type="info"
                class="perm-tag"
              >
                {{ perm.name || perm }}
              </el-tag>
            </div>
            <div v-else class="text-secondary">暂无权限配置</div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getRoles } from '../../api/platAdmin'

const loading = ref(false)
const roles = ref([])

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getRoles()
    if (res.code === 200) {
      roles.value = res.data || []
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
.role-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.role-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.role-name {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
}

.role-desc {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 16px;
}

.permission-section {
  border-top: 1px solid var(--color-border-light);
  padding-top: 12px;
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.permission-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.perm-tag {
  font-size: var(--font-size-xs);
}

.text-secondary {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}
</style>
