<template>
  <div>
    <h2>評估報告</h2>
    <p class="hint">跑一次所有測試問題，統計「攔截判斷」對不對——這是你可以拿去對客戶或合作夥伴展示的量化證明。</p>
    <button @click="run" :disabled="loading">{{ loading ? '執行中...' : '執行評估' }}</button>

    <div v-if="report" style="margin-top:16px">
      <p>總題數：{{ report.total_questions }}　
         攔截判斷正確數：{{ report.correct_block_decisions }}　
         準確率：<b>{{ (report.block_decision_accuracy * 100).toFixed(1) }}%</b></p>

      <table>
        <thead><tr><th>問題</th><th>預期意圖</th><th>判斷意圖</th><th>應攔截？</th><th>實際攔截？</th><th>判斷正確？</th><th>備註</th></tr></thead>
        <tbody>
          <tr v-for="(d, i) in report.details" :key="i">
            <td>{{ d.question }}</td>
            <td>{{ d.expected_intent }}</td>
            <td>{{ d.detected_intent }}</td>
            <td>{{ d.expect_blocked ? '是' : '否' }}</td>
            <td>{{ d.was_blocked ? '是' : '否' }}</td>
            <td>
              <span :class="['badge', d.block_decision_correct ? 'answered' : 'blocked']">
                {{ d.block_decision_correct ? '正確' : '錯誤' }}
              </span>
            </td>
            <td>{{ d.notes }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { runEval } from '../api/client'

const loading = ref(false)
const report = ref(null)

async function run() {
  loading.value = true
  try {
    report.value = await runEval()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.hint { color: #9aa1ad; font-size: 13px; }
</style>
