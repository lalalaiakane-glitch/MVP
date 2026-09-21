<template>
  <div>
    <h2>問答測試（攤開完整過程）</h2>
    <p class="hint">這頁的重點不是「回答好不好」，是讓你看到系統每一步是怎麼判斷的——這就是跟純 prompt 最大的差別。</p>

    <label>
      <span>產品編號（對應範例資料 P-SERUM-01）</span>
      <input v-model="productId" placeholder="P-SERUM-01" />
    </label>
    <label style="margin-top:8px">
      <span>問題</span>
      <textarea v-model="question" rows="2" placeholder="試試：這罐精華液可以治療我的痘疤嗎？"></textarea>
    </label>
    <button :disabled="loading || !question" @click="ask" style="margin-top:8px">
      {{ loading ? '處理中...' : '送出問題' }}
    </button>

    <div v-if="result" class="trace">
      <h3>Step 1-2：意圖判斷 + 決策表查詢</h3>
      <p>意圖：<b>{{ result.detected_intent }}</b>（{{ result.rule_description }}）</p>
      <p>本次要求的最低證據等級：<b :class="'tier-' + result.min_evidence_tier_required">{{ result.min_evidence_tier_required }}</b></p>

      <h3>Step 3：檢索到的內容</h3>
      <p v-if="result.retrieved_chunks.length === 0" class="empty">沒有檢索到符合最低證據等級的內容</p>
      <table v-else>
        <thead><tr><th>證據等級</th><th>內容</th><th>來源</th><th>相似度</th></tr></thead>
        <tbody>
          <tr v-for="c in result.retrieved_chunks" :key="c.id">
            <td :class="'tier-' + c.evidence_tier">{{ c.evidence_tier }}</td>
            <td>{{ c.text }}</td>
            <td>{{ c.source_citation || '—' }}</td>
            <td>{{ c.score.toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>

      <h3 v-if="result.prompt_used">Step 4：實際送給模型的 Prompt</h3>
      <pre v-if="result.prompt_used" class="prompt-box">{{ result.prompt_used }}</pre>

      <h3>Step 5-6：模型回答 + 事後驗證</h3>
      <p v-if="result.raw_response"><b>模型原始回答：</b>{{ result.raw_response }}</p>
      <p v-if="result.validation_passed !== null">
        驗證結果：
        <span :class="['badge', result.validation_passed ? 'answered' : 'blocked']">
          {{ result.validation_passed ? '通過' : '未通過，已攔截' }}
        </span>
      </p>
      <ul v-if="result.validation_reasons.length">
        <li v-for="(r, i) in result.validation_reasons" :key="i">{{ r }}</li>
      </ul>

      <h3>最終回給使用者的內容</h3>
      <p class="final-response">
        <span :class="['badge', result.fallback_triggered || result.validation_passed === false ? 'blocked' : 'answered']">
          {{ result.fallback_triggered || result.validation_passed === false ? '攔截／轉真人' : 'AI 直接回答' }}
        </span>
        {{ result.final_response }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { askQuestion } from '../api/client'

const question = ref('')
const productId = ref('P-SERUM-01')
const loading = ref(false)
const result = ref(null)

async function ask() {
  loading.value = true
  try {
    result.value = await askQuestion(question.value, productId.value || undefined)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
label { display: block; margin-bottom: 4px; }
label span { display: block; font-size: 13px; color: #9aa1ad; margin-bottom: 4px; }
.hint { color: #9aa1ad; font-size: 13px; }
.trace { margin-top: 24px; border-top: 1px solid #262a33; padding-top: 16px; }
.trace h3 { font-size: 14px; color: #9db4ff; margin: 16px 0 4px; }
.prompt-box { background: #14161c; border: 1px solid #262a33; border-radius: 6px; padding: 10px; white-space: pre-wrap; font-size: 12px; }
.final-response { background: #14161c; border-radius: 6px; padding: 12px; }
.empty { color: #9aa1ad; }
</style>
