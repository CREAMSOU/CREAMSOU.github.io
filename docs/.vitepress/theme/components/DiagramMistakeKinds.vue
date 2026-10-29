<script setup>
// 三类错误图：十个问题按「错在哪」归成三类。
// 每类给一句判断规则 + 这个类里的典型症状，右侧标出这类错误的修复动作是什么。
// 这张图是全文的骨架：问题不是十个独立的坑，是三类重复犯的错。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 486"
      role="img"
      aria-label="三类错误图。第一类看错了地方：症状和原因隔一层，包括 Token 全是 0、分类全显示未分类、接口返回 500 的 HTML，修复动作是往回追一层。第二类写对了但放错了位置：代码本身没问题，位置或顺序不对，包括引用规则排在第 8 条、高亮在渲染之后执行、循环里变量被覆盖，修复动作是检查执行顺序。第三类环境在骗你：代码没问题，是外部程序的状态或限制，包括 Zotero 运行时锁数据库、僵尸进程占着端口、Zotero 协议不支持跳页参数，修复动作是绕开而不是硬碰。三类的共同点：现象都不是原因本身"
    >
      <rect class="panel" x="0" y="0" width="960" height="486" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="485" rx="13.5" />

      <text class="cap" x="34" y="42" font-size="15" letter-spacing="1">十个问题，其实只有三类错法</text>

      <!-- 第一类 -->
      <rect class="b-hi" x="34" y="60" width="892" height="118" rx="12" />
      <text class="t-hi" x="56" y="90" font-size="16" font-weight="600">第一类 · 看错了地方</text>
      <text class="t-mut" x="56" y="116" font-size="13.5">症状和真正的原因隔着一层，照着症状去修永远修不对</text>
      <text class="t-mut" x="56" y="142" font-size="13">Token 数全是 0 · 十三篇论文全挤在「未分类」· 接口报错返回一页 HTML</text>
      <text class="t-hi" x="56" y="166" font-size="13" fill-opacity="0.85">→ 动作：看到报错，先问「这个现象是被谁引起的」，往回追一层</text>

      <!-- 第二类 -->
      <rect class="b-warm" x="34" y="190" width="892" height="118" rx="12" />
      <text class="t-warm" x="56" y="220" font-size="16" font-weight="600">第二类 · 代码写对了，但放错了地方</text>
      <text class="t-mut" x="56" y="246" font-size="13.5">每一行单看都没问题，是位置、顺序、作用范围错了</text>
      <text class="t-mut" x="56" y="272" font-size="13">引用规则排在第八条 · 高亮在渲染成 HTML 之后才执行 · 循环里变量互相覆盖</text>
      <text class="t-warm" x="56" y="296" font-size="13" fill-opacity="0.85">→ 动作：别急着改内容，先检查「谁先谁后」「改的是哪一个」</text>

      <!-- 第三类 -->
      <rect class="b-ok" x="34" y="320" width="892" height="118" rx="12" />
      <text class="t-ok" x="56" y="350" font-size="16" font-weight="600">第三类 · 环境在骗你</text>
      <text class="t-mut" x="56" y="376" font-size="13.5">你的代码没问题，是另一个程序的状态或它天生不支持这件事</text>
      <text class="t-mut" x="56" y="402" font-size="13">Zotero 开着就锁住数据库 · 退出后进程还占着端口 · 协议不支持直接跳到第 N 页</text>
      <text class="t-ok" x="56" y="426" font-size="13" fill-opacity="0.85">→ 动作：别硬碰，找一条它管不到的路走</text>

      <text class="note" x="34" y="464" font-size="13">三类的共同点：看到的那个现象，从来不是原因本身</text>
    </svg>
  </div>
</template>
