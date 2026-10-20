<script setup>
// 三轮排查的对照：缺运行库（死路）→ 判给显卡（假修复，复发）→ 权限（真因）。
// 用组件而不是 img 引入，配色走 CSS 变量，自动跟随亮/暗主题。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 466"
      role="img"
      aria-label="三轮排查对比：第一轮猜缺 WebView2 走死；第二轮读事件日志发现 libcef 崩溃，用禁用 GPU 临时压住，三天后复发；第三轮发现程序自身日志停止写入，实测配置目录不可写，根因是权限，补一条权限后修复"
    >
      <rect class="panel" x="0" y="0" width="960" height="466" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="465" rx="13.5" />

      <text class="cap" x="34" y="42" font-size="15" letter-spacing="1">同一台机器，三轮排查</text>

      <defs>
        <marker id="wt-warm" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-mut" d="M0,0 L8,4 L0,8 z" />
        </marker>
        <marker id="wt-hi" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path class="arrow-hi" d="M0,0 L8,4 L0,8 z" />
        </marker>
      </defs>

      <!-- 第一轮：错，越走越死 -->
      <text class="t-warm" x="34" y="76" font-size="15">第一轮：以为缺运行库 —— 不是</text>
      <g>
        <rect class="b-warm" x="34" y="88" width="208" height="58" rx="10" />
        <rect class="b-warm" x="262" y="88" width="208" height="58" rx="10" />
        <rect class="b-warm" x="490" y="88" width="208" height="58" rx="10" />
        <rect class="b-dash" x="718" y="88" width="208" height="58" rx="10" />
      </g>
      <g class="t-warm" text-anchor="middle" font-size="14">
        <text x="138" y="123">打不开，先猜原因</text>
        <text x="366" y="123">认定缺 WebView2</text>
        <text x="594" y="123">下载 · 静默安装</text>
      </g>
      <text class="t-mut" x="822" y="123" text-anchor="middle" font-size="14">装完说早就装了</text>

      <g class="link-mut" stroke-width="1.8" marker-end="url(#wt-warm)">
        <line x1="246" y1="117" x2="258" y2="117" />
        <line x1="474" y1="117" x2="486" y2="117" />
        <line x1="702" y1="117" x2="714" y2="117" />
      </g>

      <!-- 第二轮：证据对了一半，结论错 -->
      <text class="t-warm" x="34" y="200" font-size="15">第二轮：查到 libcef 崩，判给显卡 —— 只对了一半</text>
      <g>
        <rect class="b-hi" x="34" y="212" width="208" height="58" rx="10" />
        <rect class="b-hi" x="262" y="212" width="208" height="58" rx="10" />
        <rect class="b-warm" x="490" y="212" width="208" height="58" rx="10" />
        <rect class="b-dash" x="718" y="212" width="208" height="58" rx="10" />
      </g>
      <g text-anchor="middle" font-size="14">
        <text class="t-hi" x="138" y="247">翻事件日志</text>
        <text class="t-hi" x="366" y="247">模块 libcef.dll</text>
        <text class="t-warm" x="594" y="247">关掉 GPU 加速</text>
      </g>
      <text class="t-mut" x="822" y="247" text-anchor="middle" font-size="14">三天后原样复发</text>

      <g class="link-hi" stroke-width="1.8" marker-end="url(#wt-hi)">
        <line x1="246" y1="241" x2="258" y2="241" />
        <line x1="474" y1="241" x2="486" y2="241" />
      </g>
      <g class="link-mut" stroke-width="1.8" marker-end="url(#wt-warm)">
        <line x1="702" y1="241" x2="714" y2="241" />
      </g>

      <!-- 第三轮：对，直指根因 -->
      <text class="t-hi" x="34" y="324" font-size="15">第三轮：程序自己的日志停了 —— 是权限</text>
      <g>
        <rect class="b-hi" x="34" y="336" width="208" height="58" rx="10" />
        <rect class="b-hi" x="262" y="336" width="208" height="58" rx="10" />
        <rect class="b-hi" x="490" y="336" width="208" height="58" rx="10" />
        <rect class="b-ok" x="718" y="336" width="208" height="58" rx="10" />
      </g>
      <g class="t-hi" text-anchor="middle" font-size="14">
        <text x="138" y="371">日志一个字没写</text>
        <text x="366" y="371">实测目录写不进</text>
        <text x="594" y="371">CEF 建不了锁文件</text>
      </g>
      <text class="t-ok" x="822" y="371" text-anchor="middle" font-size="14">补一条权限，修好</text>

      <g class="link-hi" stroke-width="1.8" marker-end="url(#wt-hi)">
        <line x1="246" y1="365" x2="258" y2="365" />
        <line x1="474" y1="365" x2="486" y2="365" />
        <line x1="702" y1="365" x2="714" y2="365" />
      </g>

      <text class="note" x="34" y="432" font-size="13">前两轮都只解释了一部分现象；能同时解释「UI 秒退 + 壁纸正常 + 日志不写」的，只有权限这一条</text>
    </svg>
  </div>
</template>
