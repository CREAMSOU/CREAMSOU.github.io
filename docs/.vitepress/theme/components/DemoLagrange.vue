<template>
  <div class="dlg-wrap">
    <div class="dlg-cap">拉格朗日插值演示：三颗钉子 (0,y₀)(1,y₁)(2,y₂)，虚线是三个开关 l₀/l₁/l₂，绿粗线是合成结果 L₂</div>
    <canvas ref="cv" width="960" height="380" class="dlg-cv" role="img" aria-label="拉格朗日插值交互演示"></canvas>
    <div class="dlg-row">
      <label class="dlg-lab">y₀<input type="range" min="-2" max="5" step="0.5" v-model.number="y0"></label>
      <label class="dlg-lab">y₁<input type="range" min="-2" max="5" step="0.5" v-model.number="y1"></label>
      <label class="dlg-lab">y₂<input type="range" min="-2" max="5" step="0.5" v-model.number="y2"></label>
      <button class="dlg-btn" @click="toggle">{{ playing ? '⏸ 暂停' : '▶ 播放' }}</button>
      <input type="range" min="0" max="3" step="0.005" v-model.number="xv" class="dlg-x">
      <span class="dlg-xlab">x={{ xv.toFixed(3) }}</span>
    </div>
    <div class="dlg-read" v-html="readout"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const y0 = ref(1), y1 = ref(3), y2 = ref(2), xv = ref(0.75)
const playing = ref(false), readout = ref('')
const cv = ref(null)
let raf = null, ctx = null, W = 960, H = 380

function l0(x){ return (x-1)*(x-2)/2 }
function l1(x){ return x*(x-2)/(-1) }
function l2(x){ return x*(x-1)/2 }
function Lfn(x){ const a=y0.value,b=y1.value,c=y2.value; return a*l0(x)+b*l1(x)+c*l2(x) }

function vars(){
  const s = getComputedStyle(document.documentElement)
  const g = (n, f) => s.getPropertyValue(n).trim() || f
  return {
    text: g('--vp-c-text-1', '#1e293b'),
    mut: g('--vp-c-text-2', '#64748b'),
    div: g('--vp-c-divider', '#e2e8f0'),
    soft: g('--vp-c-bg-soft', '#f8f9fb')
  }
}

function draw(){
  if (!ctx) return
  const v = vars()
  ctx.clearRect(0, 0, W, H)
  // 动态纵轴范围
  let lo = 1e9, hi = -1e9
  for (let i = 0; i <= 240; i++){
    const x = i/240*3
    for (const f of [l0, l1, l2, Lfn]){
      const val = f(x)
      if (val < lo) lo = val
      if (val > hi) hi = val
    }
  }
  lo -= 0.8; hi += 0.8
  const X0 = 44, X1 = W-16, top = 18, bot = H-30
  const mx = x => X0 + x/3*(X1-X0)
  const my = val => bot - (val-lo)/(hi-lo)*(bot-top)
  // 坐标轴
  ctx.strokeStyle = v.div; ctx.lineWidth = 1
  ctx.beginPath(); ctx.moveTo(X0, my(0)); ctx.lineTo(X1, my(0)); ctx.stroke()
  ctx.fillStyle = v.mut; ctx.font = '12px sans-serif'
  for (let t = 0; t <= 3; t++){
    ctx.fillText(String(t), mx(t)-3, my(0)+15)
  }
  // 三个开关（细虚线）
  const sw = [[l0, '#0ea5e9'], [l1, '#f59e0b'], [l2, '#a855f7']]
  for (const [f, c] of sw){
    ctx.strokeStyle = c; ctx.lineWidth = 1.3; ctx.setLineDash([5, 4])
    ctx.beginPath()
    for (let px = X0; px <= X1; px++){
      const x = (px-X0)/(X1-X0)*3
      const py = my(f(x))
      px === X0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py)
    }
    ctx.stroke(); ctx.setLineDash([])
  }
  // 合成曲线（粗实线）
  ctx.strokeStyle = '#16a34a'; ctx.lineWidth = 2.6
  ctx.beginPath()
  for (let px = X0; px <= X1; px++){
    const x = (px-X0)/(X1-X0)*3
    const py = my(Lfn(x))
    px === X0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py)
  }
  ctx.stroke()
  // 钉子
  const ys = [y0.value, y1.value, y2.value]
  for (let i = 0; i < 3; i++){
    ctx.fillStyle = v.text
    ctx.beginPath(); ctx.arc(mx(i), my(ys[i]), 4.5, 0, 7); ctx.fill()
  }
  // 手指
  const x = xv.value, pxp = mx(x)
  ctx.strokeStyle = 'rgba(239,68,68,0.55)'; ctx.lineWidth = 1.5
  ctx.beginPath(); ctx.moveTo(pxp, top); ctx.lineTo(pxp, bot); ctx.stroke()
  ctx.fillStyle = '#16a34a'
  ctx.beginPath(); ctx.arc(pxp, my(Lfn(x)), 5, 0, 7); ctx.fill()
  // 读数
  const ls = [l0(x), l1(x), l2(x)]
  let near = ''
  for (let i = 0; i < 3; i++){
    if (Math.abs(x-i) < 0.02) near = i === 0 ? '踩到 x₀：l₀=1 满格，其余断电' : i === 1 ? '踩到 x₁：l₁=1 满格，其余断电' : '踩到 x₂：l₂=1 满格，其余断电'
  }
  readout.value =
    '开关读数 l₀=<b>' + ls[0].toFixed(3) + '</b>　l₁=<b>' + ls[1].toFixed(3) + '</b>　l₂=<b>' + ls[2].toFixed(3) + '</b>' +
    '　→　L₂(x)=Σyᵢlᵢ=<b style="color:#16a34a">' + Lfn(x).toFixed(3) + '</b>' +
    (near ? '<br><span style="color:' + v.mut + '">' + near + '</span>' : '<br><span style="color:' + v.mut + '">半路读数：各开关输出 0~1 之间的过渡值，曲线是它们的加权和</span>')
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
  ctx = cv.value.getContext('2d')
  draw()
})
onBeforeUnmount(() => { if (raf) cancelAnimationFrame(raf) })
watch([y0, y1, y2, xv], draw)
</script>

<style scoped>
.dlg-wrap{ border:1px solid var(--vp-c-divider); border-radius:10px; padding:12px 14px; background:var(--vp-c-bg-soft); margin:14px 0; }
.dlg-cap{ font-size:13px; color:var(--vp-c-text-2); margin-bottom:8px; }
.dlg-cv{ width:100%; height:auto; background:var(--vp-c-bg); border:1px solid var(--vp-c-divider); border-radius:8px; }
.dlg-row{ display:flex; align-items:center; gap:12px; margin-top:10px; flex-wrap:wrap; }
.dlg-lab{ font-size:13px; color:var(--vp-c-text-1); display:flex; align-items:center; gap:4px; }
.dlg-lab input{ width:90px; }
.dlg-btn{ padding:3px 14px; border:1px solid var(--vp-c-divider); background:var(--vp-c-bg); color:var(--vp-c-text-1); border-radius:6px; cursor:pointer; font-size:13px; }
.dlg-x{ flex:1; min-width:140px; }
.dlg-xlab{ font-size:13px; font-variant-numeric:tabular-nums; color:var(--vp-c-text-1); width:80px; text-align:right; }
.dlg-read{ font-size:13px; margin-top:8px; line-height:1.7; background:var(--vp-c-bg); border:1px solid var(--vp-c-divider); border-radius:8px; padding:8px 12px; font-variant-numeric:tabular-nums; color:var(--vp-c-text-1); }
</style>
