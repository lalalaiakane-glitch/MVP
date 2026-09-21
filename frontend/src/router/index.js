import { createRouter, createWebHistory } from 'vue-router'
import ContentManagerView from '../views/ContentManagerView.vue'
import ChatTestView from '../views/ChatTestView.vue'
import EvalReportView from '../views/EvalReportView.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/content', component: ContentManagerView },
  { path: '/chat', component: ChatTestView },
  { path: '/eval', component: EvalReportView }
]

export default createRouter({ history: createWebHistory(), routes })
