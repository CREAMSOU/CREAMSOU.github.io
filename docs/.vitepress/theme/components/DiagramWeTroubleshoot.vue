<script setup>
// 两条排查路的对比：先猜"缺运行库"走死，再去读崩溃日志找到真因。
// 用组件而不是 img 引入，配色走 CSS 变量，自动跟随亮/暗主题。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 372"
      role="img"
      aria-label="两条排查路的对比：第一条猜缺 WebView2，下载安装包、静默安装走死；第二条去读 Windows 事件日志，发现崩溃模块是 libcef.dll，用禁用 GPU 验证后写进配置修好"
    >
      <rect class="panel" x="0" y="0" width="960" height="372" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="371" rx="13.5" />

      <text class="cap" x="34" y="44" font-size="15" letter-spacing="1">同一台机器，两条排查路</text>

      <defs>
        <marker id="wt-warm" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-mut" d="M0,0 L8,4 L0,8 z" />
        </marker>
        <marker id="wt-hi" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-hi" d="M0,0 L8,4 L0,8 z" />
        </marker>
      </defs>

      <!-- 第一条路：错，越走越死 -->
      <text class="t-warm" x="34" y="88" font-size="15">第一条：我以为缺运行库 —— 错</text>
      <g>
        <rect class="b-warm" x="34" y="102" width="208" height="58" rx="10" />
        <rect class="b-warm" x="262" y="102" width="208" height="58" rx="10" />
        <rect class="b-warm" x="490" y="102" width="208" height="58" rx="10" />
        <rect class="b-dash" x="718" y="102" width="208" height="58" rx="10" />
      </g>
      <g class="t-warm" text-anchor="middle" font-size="14">
        <text x="138" y="137">打不开，先猜原因</text>
        <text x="366" y="137">认定缺 WebView2</text>
        <text x="594" y="137">下载 · 静默安装</text>
      </g>
      <text class="t-mut" x="822" y="137" text-anchor="middle" font-size="14">装完说早就装了</text>

      <g class="link-mut" stroke-width="1.8" marker-end="url(#wt-warm)">
        <line x1="246" y1="131" x2="258" y2="131" />
        <line x1="474" y1="131" x2="486" y2="131" />
        <line x1="702" y1="131" x2="714" y2="131" />
      </g>

      <!-- 第二条路：对，直指根因 -->
      <text class="t-hi" x="34" y="214" font-size="15">第二条：去读崩溃日志 —— 对</text>
      <g>
        <rect class="b-hi" x="34" y="228" width="208" height="58" rx="10" />
        <rect class="b-hi" x="262" y="228" width="208" height="58" rx="10" />
        <rect class="b-hi" x="490" y="228" width="208" height="58" rx="10" />
        <rect class="b-ok" x="718" y="228" width="208" height="58" rx="10" />
      </g>
      <g class="t-hi" text-anchor="middle" font-size="14">
        <text x="138" y="263">翻事件日志</text>
        <text x="366" y="263">模块 libcef.dll</text>
        <text x="594" y="263">--disable-gpu 验证</text>
      </g>
      <text class="t-ok" x="822" y="263" text-anchor="middle" font-size="14">写进配置，修好</text>

      <g class="link-hi" stroke-width="1.8" marker-end="url(#wt-hi)">
        <line x1="246" y1="257" x2="258" y2="257" />
        <line x1="474" y1="257" x2="486" y2="257" />
        <line x1="702" y1="257" x2="714" y2="257" />
      </g>

      <text class="note" x="34" y="344" font-size="13">猜「缺运行库」有一条完整的因果链，所以最容易一头扎进去；模块名才是第一手证据</text>
    </svg>
  </div>
</template>
