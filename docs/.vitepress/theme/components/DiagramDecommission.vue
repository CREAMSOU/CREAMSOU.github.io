<script setup>
// 卸载自建服务的两条路：想当然的短路径 vs 实际需要走的路。
// 用组件而不是 img 标签引入，配色就能走 CSS 变量，自动跟随亮/暗主题。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 330"
      role="img"
      aria-label="卸载自建服务的两条路径对比：想当然的做法是删目录、删镜像、收工三步；实际要做的是先审计资产，分清哪些能重建哪些不能，把不能重建的归档，验证归档完整后才动手删"
    >
      <rect class="panel" x="0" y="0" width="960" height="330" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="329" rx="13.5" />

      <text class="cap" x="34" y="44" font-size="15" letter-spacing="1">卸载一个自建服务，两条路</text>

      <!-- 想当然的路：灰色，看着短，代价是丢东西 -->
      <text class="t-mut" x="34" y="88" font-size="15">我一开始以为：删掉就完了</text>
      <g>
        <rect class="b-mut" x="34" y="100" width="202" height="54" rx="10" />
        <rect class="b-mut" x="264" y="100" width="202" height="54" rx="10" />
        <rect class="b-mut" x="494" y="100" width="202" height="54" rx="10" />
      </g>
      <g class="t-mut" text-anchor="middle" font-size="15">
        <text x="135" y="133">删目录</text>
        <text x="365" y="133">删镜像</text>
        <text x="595" y="133">收工</text>
      </g>
      <defs>
        <marker id="dc-mut" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-mut" d="M0,0 L8,4 L0,8 z" />
        </marker>
        <marker id="dc-hi" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-hi" d="M0,0 L8,4 L0,8 z" />
        </marker>
      </defs>
      <g class="link-mut" stroke-width="1.8" marker-end="url(#dc-mut)">
        <line x1="236" y1="127" x2="260" y2="127" />
        <line x1="466" y1="127" x2="490" y2="127" />
      </g>

      <!-- 实际走的：蓝色主路径，最后一步落在绿色 -->
      <text class="t-hi" x="34" y="200" font-size="15">实际要走的：先分清哪些东西丢了就回不来</text>
      <g>
        <rect class="b-hi" x="34" y="212" width="202" height="54" rx="10" />
        <rect class="b-hi" x="264" y="212" width="202" height="54" rx="10" />
        <rect class="b-hi" x="494" y="212" width="202" height="54" rx="10" />
        <rect class="b-ok" x="724" y="212" width="202" height="54" rx="10" />
      </g>
      <g text-anchor="middle" font-size="15">
        <text class="t-hi" x="135" y="245">审计全部资产</text>
        <text class="t-hi" x="365" y="245">分清能重建 / 不能重建</text>
        <text class="t-hi" x="595" y="245">归档不能重建的</text>
        <text class="t-ok" x="825" y="245">验证后动手删</text>
      </g>
      <g class="link-hi" stroke-width="1.8" marker-end="url(#dc-hi)">
        <line x1="236" y1="239" x2="260" y2="239" />
        <line x1="466" y1="239" x2="490" y2="239" />
        <line x1="696" y1="239" x2="720" y2="239" />
      </g>

      <text class="note" x="34" y="304" font-size="13">删不是难点，判断什么能重建才是</text>
    </svg>
  </div>
</template>
