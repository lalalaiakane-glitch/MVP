<template>
  <div>
    <h2>內容管理（證據分級內容）</h2>
    <p class="hint">這裡填的是「真正的護城河」——請把範例內容換成真的品牌內容並標好證據等級。</p>

    <div class="form-grid">
      <label><span>產品編號</span><input v-model="form.product_id" placeholder="P-SERUM-01" /></label>
      <label><span>證據等級</span>
        <select v-model="form.evidence_tier">
          <option value="A">A - 臨床/研究等級</option>
          <option value="B">B - 官方仿單/成分事實</option>
          <option value="C">C - 使用者回饋/軼事</option>
          <option value="D">D - 未經查證</option>
        </select>
      </label>
      <label><span>內容類型</span>
        <select v-model="form.claim_type">
          <option value="efficacy_claim">療效聲明</option>
          <option value="ingredient_fact">成分事實</option>
          <option value="anecdotal">使用者軼事</option>
          <option value="usage_instruction">使用方式</option>
        </select>
      </label>
      <label><span>來源引用</span><input v-model="form.source_citation" placeholder="例如：OO期刊2025 / 產品仿單" /></label>
    </div>
    <label><span>內容本文</span><textarea v-model="form.text" rows="2"></textarea></label>
    <button @click="submit" :disabled="!form.product_id || !form.text" style="margin-top:8px">
      {{ editingId ? '更新這條內容' : '新增內容' }}
    </button>
    <button v-if="editingId" @click="cancelEdit" style="margin-left:8px; background:#333">取消編輯</button>

    <table>
      <thead><tr><th>等級</th><th>產品</th><th>內容</th><th>來源</th><th></th></tr></thead>
      <tbody>
        <tr v-for="c in list" :key="c.id">
          <td :class="'tier-' + c.evidence_tier">{{ c.evidence_tier }}</td>
          <td>{{ c.product_id }}</td>
          <td>{{ c.text }}</td>
          <td>{{ c.source_citation || '—' }}</td>
          <td>
            <button @click="edit(c)" style="background:#333">編輯</button>
            <button @click="remove(c.id)" style="background:#7a2222; margin-left:4px">刪除</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { listContent, createContent, updateContent, deleteContent } from '../api/client'

const list = ref([])
const editingId = ref(null)
const form = reactive({
  brand_id: 'demo-brand',
  product_id: '',
  text: '',
  evidence_tier: 'A',
  claim_type: 'ingredient_fact',
  source_citation: ''
})

async function load() {
  list.value = await listContent()
}

async function submit() {
  if (editingId.value) {
    await updateContent(editingId.value, { ...form })
  } else {
    await createContent({ ...form })
  }
  cancelEdit()
  await load()
}

function edit(c) {
  editingId.value = c.id
  Object.assign(form, c)
}

function cancelEdit() {
  editingId.value = null
  Object.assign(form, { brand_id: 'demo-brand', product_id: '', text: '', evidence_tier: 'A', claim_type: 'ingredient_fact', source_citation: '' })
}

async function remove(id) {
  await deleteContent(id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.hint { color: #9aa1ad; font-size: 13px; }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px; }
label span { display: block; font-size: 13px; color: #9aa1ad; margin-bottom: 4px; }
</style>
