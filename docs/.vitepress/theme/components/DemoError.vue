<template>
  <div class="dle-wrap">
    <div class="dle-cap">误差演示：f(x)=sin x，钉子 0 / 1.5 / 3。上图蓝线是真函数、橙虚线是插值 L₂、红色竖线段是两者差距 R₂(x)；下图红线是真实误差，灰色包络是理论上界 ±ω₃(x)/6</div>
    <canvas ref="cvT" width="960" height="240" class="dle-cv" role="img" aria-label="真函数与插值曲线对比"></canvas>
    <canvas ref="cvB" width="960" height="190" class="dle-cv2" role="img" aria-label="误差与理论包络对比"></canvas>
    <div class="dle-row">
      <button class="dle-btn" @click="toggle">{{ playing ? '⏸ 暂停' : '▶ 播放' }}</button>
      <input type="range" min="0" max="3" step="0.005" v-model.number="xv" class="dle-x">
      <span class="dle-xlab">x={{ xv.toFixed(3) }}</span>
    </div>
    <div class="dle-read" v-html="readout"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const xv = ref(0.75), playing = ref(false), readout = ref('')
const cvT = ref(null), cvB = ref(null)
let raf = null, ct = null, cb = null, W = 960, H1 = 240, H2 = 190

function Lfn(x){
  const l1 = x*(x-3)/((1.5)*(1.5-3))
  const l2 = x*(x-1.5)/((3)*(1.5))
  return Math.sin(1.5)*l1 + Math.sin(3)*l2
}
function om(x){ return x*(x-1.5)*(x-3) }
function Rfn(x){ return Math.sin(x) - Lfn(x) }

function vars(){
  const s = getComputedStyle(document.documentElement)
  const g = (n, f) => s.getPropertyValue(n).trim() || f
  return {
    text: g('--vp-c-text-1', '#1e293b'),
    mut: g('--vp-c-text-2', '#64748b'),
    div: g('--vp-c-divider', '#e2e8f0')
  }
}

function draw(){
  if (!ct || !cb) return
  const v = vars()
  const X0 = 44, X1 = W-16
  const mx = x => X0 + x/3*(X1-X0)
  const myT = val => H1-26 - ((val+0.3)/1.55)*(H1-46)
  const myB = val => H2/2 - (val/0.42)*(H2/2-18)
  const axes = (c, my, H) => {
    c.strokeStyle = v.div; c.lineWidth = 1
    c.beginPath(); c.moveTo(X0, my(0)); c.lineTo(X1, my(0)); c.stroke()
    c.fillStyle = v.mut; c.font = '12px sans-serif'
    for (const t of [0, 1, 2, 3]) c.fillText(String(t), mx(t)-3, my(0)+15)
  }
  const curve = (c, f, my, color, width, dash) => {
    c.strokeStyle = color; c.lineWidth = width; c.setLineDash(dash || [])
    c.beginPath()
    for (let px = X0; px <= X1; px++){
      const x = (px-X0)/(X1-X0)*3
      const py = my(f(x))
      px === X0 ? c.moveTo(px, py) : c.lineTo(px, py)
    }
    c.stroke(); c.setLineDash([])
  }
  ct.clearRect(0, 0, W, H1); cb.clearRect(0, 0, W, H2)
  axes(ct, myT, H1); axes(cb, myB, H2)
  // 包络 ±|ω|/6
  cb.fillStyle = 'rgba(148,163,184,0.18)'
  cb.beginPath(); cb.moveTo(mx(0), myB(0))
  for (let px = X0; px <= X1; px++){ const x = (px-X0)/(X1-X0)*3; cb.lineTo(px, myB(om(x)/6)) }
  for (let px = X1; px >= X0; px--){ const x = (px-X0)/(X1-X0)*3; cb.lineTo(px, myB(-om(x)/6)) }
  cb.closePath(); cb.fill()
  cb.strokeStyle = '#94a3b8'; cb.lineWidth = 1.4; cb.setLineDash([5, 4])
  cb.beginPath()
  for (let px = X0; px <= X1; px++){ const x = (px-X0)/(X1-X0)*3; const py = myB(om(x)/6); px === X0 ? cb.moveTo(px, py) : cb.lineTo(px, py) }
  cb.stroke()
  cb.beginPath()
  for (let px = X0; px <= X1; px++){ const x = (px-X0)/(X1-X0)*3; const py = myB(-om(x)/6); px === X0 ? cb.moveTo(px, py) : cb.lineTo(px, py) }
  cb.stroke(); cb.setLineDash([])
  curve(cb, Rfn, myB, '#dc2626', 2)
  // 上图
  curve(ct, Math.sin, myT, '#3b82f6', 2.2)
  curve(ct, Lfn, myT, '#f97316', 2, [7, 5])
  for (const [nx, ny] of [[0, 0], [1.5, Math.sin(1.5)], [3, Math.sin(3)]]){
    ct.fillStyle = v.text
    ct.beginPath(); ct.arc(mx(nx), myT(ny), 4.5, 0, 7); ct.fill()
  }
  // 探针
  const x = xv.value, pxp = mx(x)
  ct.strokeStyle = 'rgba(220,38,38,0.55)'; ct.lineWidth = 1.6
  ct.beginPath(); ct.moveTo(pxp, myT(Math.sin(x))); ct.lineTo(pxp, myT(Lfn(x))); ct.stroke()
  cb.strokeStyle = 'rgba(220,38,38,0.55)'
  cb.beginPath(); cb.moveTo(pxp, 12); cb.lineTo(pxp, H2-12); cb.stroke()
  cb.fillStyle = '#dc2626'
  cb.beginPath(); cb.arc(pxp, myB(Rfn(x)), 4.5, 0, 7); cb.fill()
  // 读数
  const r = Rfn(x), w = om(x), bnd = Math.abs(w)/6
  readout.value =
    '真实误差 R₂(x)=f−L₂ = <b style="color:#dc2626">' + r.toFixed(4) + '</b>' +
    '　｜　ω₃(x) = <b>' + w.toFixed(4) + '</b>' +
    '　｜　理论上界 |ω₃|/6 = <b>' + bnd.toFixed(4) + '</b>' +
    '<br><span style="color:' + v.mut + '">红线始终没跑出灰色包络 → |R₂(x)| ≤ |ω₃(x)|/6 成立（max|f‴|=1，误差上界=函数弯度×钉子地形因子）</span>'
}

function step(){
  if (!playing.value) return
  xv.value += 0.012
  if (xv.value > 3) xv.value = 0
  draw()
  raf = requestAnimationFrame(step)
}
function toggle(){
  playing.value = !playing.value
  if (playing.value) step()
  else if (raf) cancelAnimationFrame(raf)
}

onMounted(() => {
  ct = cvT.value.getContext('2d')
  cb = cvB.value.getContext('2d')
  draw()
})
onBeforeUnmount(() => { if (raf) cancelAnimationFrame(raf) })
watch(xv, draw)
</script>

<style scoped>
.dle-wrap{ border:1px solid var(--vp-c-divider); border-radius:10px; padding:12px 14px; background:var(--vp-c-bg-soft); margin:14px 0; }
.dle-cap{ font-size:13px; color:var(--vp-c-text-2); margin-bottom:8px; line-height:1.6; }
.dle-cv{ width:100%; height:auto; background:var(--vp-c-bg); border:1px solid var(--vp-c-divider); border-radius:8px; }
.dle-cv2{ width:100%; height:auto; background:var(--vp-c-bg); border:1px solid var(--vp-c-divider); border-radius:8px; margin-top:6px; }
.dle-row{ display:flex; align-items:center; gap:12px; margin-top:10px; }
.dle-btn{ padding:3px 14px; border:1px solid var(--vp-c-divider); background:var(--vp-c-bg); color:var(--vp-c-text-1); border-radius:6px; cursor:pointer; font-size:13px; }
.dle-x{ flex:1; min-width:140px; }
.dle-xlab{ font-size:13px; font-variant-numeric:tabular-nums; color:var(--vp-c-text-1); width:80px; text-align:right; }
.dle-read{ font-size:13px; margin-top:8px; line-height:1.7; background:var(--vp-c-bg); border:1px solid var(--vp-c-divider); border-radius:8px; padding:8px 12px; font-variant-numeric:tabular-nums; color:var(--vp-c-text-1); }
</style>
