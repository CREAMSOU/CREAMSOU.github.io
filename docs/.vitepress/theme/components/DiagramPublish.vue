<script setup>
// 发布链路示意：正常走 git push，失败自动改走 Git API。
// 同样是组件，配色跟随亮/暗主题。
</script>

<template>
  <div class="dgm-wrap">
  <svg
    class="dgm"
    viewBox="0 0 960 392"
    role="img"
    aria-label="发布链路：本地编辑器提交后正常走 git push 到 GitHub 仓库，由 GitHub Actions 自动构建并发布到 GitHub Pages；push 失败时改走 Git API 提交这条备用通路"
  >
    <rect class="panel" x="0" y="0" width="960" height="392" rx="14" />
    <rect class="panel-line" x="0.5" y="0.5" width="959" height="391" rx="13.5" />

    <text class="cap" x="34" y="46" font-size="15" letter-spacing="1">一次发布，两条走法</text>

    <!-- 主链路 -->
    <g>
      <rect class="b-hi" x="34" y="104" width="130" height="84" rx="10" />
      <rect class="b-mut" x="186" y="104" width="130" height="84" rx="10" />
      <rect class="b-mut" x="338" y="104" width="130" height="84" rx="10" />
      <rect class="b-mut" x="490" y="104" width="130" height="84" rx="10" />
      <rect class="b-warm" x="642" y="104" width="130" height="84" rx="10" />
      <rect class="b-ok" x="794" y="104" width="130" height="84" rx="10" />
    </g>

    <g text-anchor="middle" font-size="15.5">
      <text class="t-hi" x="99" y="140">本地编辑器</text>
      <text class="t-sub" x="99" y="164" font-size="13">改文章、存文件</text>

      <text class="t-mut" x="251" y="140">提交</text>
      <text class="t-sub" x="251" y="164" font-size="13">git commit</text>

      <text class="t-mut" x="403" y="140">推送</text>
      <text class="t-sub" x="403" y="164" font-size="13">git push</text>

      <text class="t-mut" x="555" y="140">GitHub 仓库</text>
      <text class="t-sub" x="555" y="164" font-size="13">代码放这儿</text>

      <text class="t-warm" x="707" y="140">自动构建</text>
      <text class="t-sub" x="707" y="164" font-size="13">GitHub Actions</text>

      <text class="t-ok" x="859" y="140">线上页面</text>
      <text class="t-sub" x="859" y="164" font-size="13">GitHub Pages</text>
    </g>

    <defs>
      <marker id="dp-main" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
        <path class="arrow-mut" d="M0,0 L9,4.5 L0,9 z" />
      </marker>
      <marker id="dp-alt" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
        <path class="arrow-dim" d="M0,0 L9,4.5 L0,9 z" />
      </marker>
    </defs>
    <g class="link-mut" stroke-width="1.8" marker-end="url(#dp-main)">
      <line x1="166" y1="146" x2="182" y2="146" />
      <line x1="318" y1="146" x2="334" y2="146" />
      <line x1="470" y1="146" x2="486" y2="146" />
      <line x1="622" y1="146" x2="638" y2="146" />
      <line x1="774" y1="146" x2="790" y2="146" />
    </g>

    <!-- 备用通路：push 失败时走这条 -->
    <rect class="b-dash" x="278" y="256" width="250" height="76" rx="10" />
    <text class="t-alt" x="403" y="288" text-anchor="middle" font-size="15">推送失败就走这条</text>
    <text class="t-sub" x="403" y="312" text-anchor="middle" font-size="13">直接用 Git API 建提交，更稳</text>

    <path class="link-dim" d="M403 192 L403 252" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#dp-alt)" fill="none" />
    <path class="link-dim" d="M524 294 C 568 294, 566 244, 558 200" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#dp-alt)" fill="none" />

    <text class="note" x="34" y="368" font-size="13">实线＝正常路径　　虚线＝出问题时的备用路径</text>
  </svg>
  </div>
</template>
