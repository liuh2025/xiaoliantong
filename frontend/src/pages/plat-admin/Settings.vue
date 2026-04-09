<template>
  <div class="settings-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
          <el-button v-if="!editing" type="primary" @click="startEdit">编辑</el-button>
          <div v-else class="edit-actions">
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="!loading && settings.length === 0" description="暂无系统设置" />

      <el-descriptions v-else :column="1" border>
        <el-descriptions-item
          v-for="item in displaySettings"
          :key="item.key"
          :label="item.label || item.key"
        >
          <template v-if="editing">
            <el-input v-if="typeof item.value === 'string'" v-model="form[item.key]" />
            <el-input-number
              v-else-if="typeof item.value === 'number'"
              v-model="form[item.key]"
              :min="0"
            />
            <el-switch v-else-if="typeof item.value === 'boolean'" v-model="form[item.key]" />
          </template>
          <template v-else>
            <span v-if="typeof item.value === 'boolean'">
              <el-tag :type="item.value ? 'success' : 'info'" size="small">
                {{ item.value ? '是' : '否' }}
              </el-tag>
            </span>
            <span v-else>{{ item.value }}</span>
          </template>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSettings, updateSettings } from '../../api/platAdmin'

const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const rawSettings = ref({})
const form = ref({})

const displaySettings = computed(() => {
  return Object.entries(rawSettings.value).map(([key, value]) => ({
    key,
    value,
    label: key,
  }))
})

async function fetchData() {
  loading.value = true
  try {
    const { data: res } = await getSettings()
    if (res.code === 200) {
      rawSettings.value = res.data || {}
    }
  } catch {
    ElMessage.error('加载设置失败')
  } finally {
    loading.value = false
  }
}

function startEdit() {
  editing.value = true
  form.value = { ...rawSettings.value }
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    const { data: res } = await updateSettings(form.value)
    if (res.code === 200) {
      ElMessage.success('保存成功')
      editing.value = false
      await fetchData()
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.edit-actions {
  display: flex;
  gap: 8px;
}
</style>
