import { ref } from 'vue'
import request from '../api/request'

export function useDict() {
  const industries = ref([])
  const subIndustries = ref([])
  const categories = ref([])
  const provinces = ref([])
  const regions = ref([])
  const loading = ref(false)

  async function fetchIndustries(parentId = 0) {
    loading.value = true
    try {
      const { data } = await request.get('/ent/dict/industry', { params: { parent_id: parentId } })
      if (data.code === 200) {
        if (parentId === 0) {
          industries.value = data.data || []
        } else {
          subIndustries.value = data.data || []
        }
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    loading.value = true
    try {
      const { data } = await request.get('/ent/dict/category')
      if (data.code === 200) {
        categories.value = data.data || []
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchRegions(parentId = 0) {
    loading.value = true
    try {
      const { data } = await request.get('/ent/dict/region', { params: { parent_id: parentId } })
      if (data.code === 200) {
        if (parentId === 0) {
          provinces.value = data.data || []
        } else {
          regions.value = data.data || []
        }
      }
    } finally {
      loading.value = false
    }
  }

  return {
    industries, subIndustries, categories, provinces, regions,
    loading, fetchIndustries, fetchCategories, fetchRegions,
  }
}
