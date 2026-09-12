<script setup>
// 两种文章结构的对比示意。
// 用组件而不是 img 标签引入，配色就能走 CSS 变量，自动跟随亮/暗主题。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 372"
      role="img"
      aria-label="两种文章结构的对比：叙事式从具体情境、一个困惑、怎么查的、机制是什么、卡住的地方，走到一句结论；教程式从背景、原理、示例走到总结"
    >
      <rect class="panel" x="0" y="0" width="960" height="372" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="371" rx="13.5" />

      <text class="cap" x="34" y="44" font-size="15" letter-spacing="1">同一件事，两种排法</text>

      <!-- 叙事式：蓝色高亮，是推荐走法 -->
      <text class="t-hi" x="34" y="92" font-size="15">叙事式：从现场切进去，读者跟着你走一遍</text>
      <g>
        <rect class="b-hi" x="34" y="106" width="132" height="58" rx="10" />
        <rect class="b-hi" x="186" y="106" width="132" height="58" rx="10" />
        <rect class="b-hi" x="338" y="106" width="132" height="58" rx="10" />
        <rect class="b-hi" x="490" y="106" width="132" height="58" rx="10" />
        <rect class="b-hi" x="642" y="106" width="132" height="58" rx="10" />
        <rect class="b-ok" x="794" y="106" width="132" height="58" rx="10" />
      </g>
      <g class="t-hi" text-anchor="middle" font-size="15">
        <text x="100" y="141">具体情境</text>
        <text x="252" y="141">一个困惑</text>
        <text x="404" y="141">怎么查的</text>
        <text x="556" y="141">机制是什么</text>
        <text x="708" y="141">卡住的地方</text>
      </g>
      <text class="t-ok" x="860" y="141" text-anchor="middle" font-size="15">一句结论</text>

      <defs>
        <marker id="dn-hi" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-hi" d="M0,0 L8,4 L0,8 z" />
        </marker>
        <marker id="dn-mut" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-mut" d="M0,0 L8,4 L0,8 z" />
        </marker>
      </defs>
      <g class="link-hi" stroke-width="1.8" marker-end="url(#dn-hi)">
        <line x1="168" y1="135" x2="182" y2="135" />
        <line x1="320" y1="135" x2="334" y2="135" />
        <line x1="472" y1="135" x2="486" y2="135" />
        <line x1="624" y1="135" x2="638" y2="135" />
        <line x1="776" y1="135" x2="790" y2="135" />
      </g>

      <!-- 教程式：灰色弱化，两条路都成立，但这条记不住是谁写的 -->
      <text class="t-mut" x="34" y="222" font-size="15">教程式：四平八稳，读完记不住是谁写的</text>
      <g>
        <rect class="b-mut" x="111" y="236" width="168" height="58" rx="10" />
        <rect class="b-mut" x="301" y="236" width="168" height="58" rx="10" />
        <rect class="b-mut" x="491" y="236" width="168" height="58" rx="10" />
        <rect class="b-mut" x="681" y="236" width="168" height="58" rx="10" />
      </g>
      <g class="t-mut" text-anchor="middle" font-size="15">
        <text x="195" y="271">背景</text>
        <text x="385" y="271">原理</text>
        <text x="575" y="271">示例</text>
        <text x="765" y="271">总结</text>
      </g>
      <g class="link-mut" stroke-width="1.8" marker-end="url(#dn-mut)">
        <line x1="281" y1="265" x2="297" y2="265" />
        <line x1="471" y1="265" x2="487" y2="265" />
        <line x1="661" y1="265" x2="677" y2="265" />
      </g>

      <text class="note" x="34" y="344" font-size="13">两种都能写完，差别在于读者读完记住的是方法，还是你</text>
    </svg>
  </div>
</template>
