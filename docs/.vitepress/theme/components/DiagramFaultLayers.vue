<script setup>
// 故障分层图：把所有遇到的故障按「能不能彻底修掉」分三层。
// 底座是已免疫的（修一次永久生效），中间是偶发复发的（修不掉、只能等它犯），
// 顶层是设计代价（不是 bug，换工具才会消失）。这张图是全文的骨架。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 470"
      role="img"
      aria-label="故障三层图：底层是已彻底修复的故障（路径硬编码、批处理延迟变量、端口 TIME_WAIT、事件监听器堆积、YAML 编码），修一次永久免疫；中间层是偶发复发的故障（Docker 容器 DNS 失效），修不好、只能等它犯，恢复要两分钟；顶层是设计代价（每个环境都要单独配、连不上就只能干等），不是 bug，换掉这套东西才会消失"
    >
      <rect class="panel" x="0" y="0" width="960" height="470" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="469" rx="13.5" />

      <text class="cap" x="34" y="42" font-size="15" letter-spacing="1">修到最后，才发现问题是分层的</text>

      <!-- 顶层：设计代价 -->
      <rect class="b-warm" x="34" y="62" width="892" height="96" rx="12" />
      <text class="t-warm" x="56" y="94" font-size="16" font-weight="600">第三层：设计代价 —— 不是 bug，是这类工具本来的样子</text>
      <text class="t-mut" x="56" y="122" font-size="14">每个环境都要单独配一遍 · 服务连不上就只能干等 · 能力上限锁在别人给的表单里</text>
      <text class="t-warm" x="56" y="145" font-size="13" fill-opacity="0.85">→ 换掉这套东西才会消失</text>

      <!-- 中层：偶发复发 -->
      <rect class="b-hi" x="34" y="172" width="892" height="96" rx="12" />
      <text class="t-hi" x="56" y="204" font-size="16" font-weight="600">第二层：偶发复发 —— 知道怎么修，但如果不用它就不会犯</text>
      <text class="t-mut" x="56" y="232" font-size="14">容器 DNS 解析偶发失效 · 重启后容器 IP 变了但缓存没刷新</text>
      <text class="t-hi" x="56" y="255" font-size="13" fill-opacity="0.85">→ 修一次好一阵，代价是每次复发都要手动重建网络（约 2 分钟）</text>

      <!-- 底层：已彻底修复 -->
      <rect class="b-ok" x="34" y="282" width="892" height="130" rx="12" />
      <text class="t-ok" x="56" y="314" font-size="16" font-weight="600">第一层：已彻底修复 —— 修一次，永久免疫</text>
      <text class="t-mut" x="56" y="342" font-size="14">路径硬编码 · 批处理延迟变量 · 端口 TIME_WAIT · 事件监听器堆积 · 中文编码冲突</text>
      <text class="t-ok" x="56" y="365" font-size="13" fill-opacity="0.85">→ 这些问题不会再出现，但它们是当时耗掉最多时间的部分</text>
      <text class="t-mut" x="56" y="392" font-size="13">剩下的两件事没修：偶发的那层修不掉，设计那层不该由我修</text>

      <text class="note" x="34" y="444" font-size="13">判断一个自建服务要不要留，不看它出了多少问题，看它有几层问题修不掉</text>
    </svg>
  </div>
</template>
