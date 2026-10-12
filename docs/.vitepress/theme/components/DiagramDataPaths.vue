<script setup>
// 双数据路径对比图：同一个 compose 项目，两条取数路径给出两个结论。
// 左边路径 A 走 docker compose config（一直正确，成了对照组），
// 右边路径 B 走内置扫描器，两个解析 bug 都只坏这一边。
// 这张图是全文的骨架：bug 不是靠读代码找到的，是靠两条路径互相矛盾找到的。
</script>

<template>
  <div class="dgm-wrap">
    <svg
      class="dgm"
      viewBox="0 0 960 500"
      role="img"
      aria-label="双数据路径对比图。同一个 compose 文件分出两条取数路径：路径 A 走 docker compose config，得出 18 个挂载、5 个不可重建、915.2 MB，一直正确，成了对照组，代价是需要装 docker 命令行。路径 B 走内置扫描器，得出 16 个挂载、3 个不可重建、413.9 MB，比 A 少了 501.3 MB。造成差异的两个解析 bug 都只坏路径 B 这一边：COMPOSE_PROFILES 没做变量插值，导致两个服务被误判为未启用；YAML 锚点没解析，导致环境变量文件引用从 36 个掉到 10 个。结论：让两条路径互相核对，本身才是发现 bug 的机制"
    >
      <rect class="panel" x="0" y="0" width="960" height="500" rx="14" />
      <rect class="panel-line" x="0.5" y="0.5" width="959" height="499" rx="13.5" />

      <text class="cap" x="34" y="44" font-size="15" letter-spacing="1">同一个项目，两条取数路径，两个结论</text>

      <!-- 输入 -->
      <rect class="b-mut" x="340" y="62" width="280" height="54" rx="10" />
      <text class="t-mut" x="480" y="95" text-anchor="middle" font-size="15">compose 文件（一个自建服务栈）</text>

      <!-- 分叉 -->
      <defs>
        <marker id="dpath-arw" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">
          <path class="arrow-mut" d="M0,0 L9,4.5 L0,9 z" />
        </marker>
      </defs>
      <g class="link-mut" stroke-width="1.8" marker-end="url(#dpath-arw)" fill="none">
        <path d="M480 116 V136 H250 V168" />
        <path d="M480 116 V136 H710 V168" />
      </g>

      <!-- 路径 A -->
      <text class="t-ok" x="250" y="190" text-anchor="middle" font-size="15">路径 A · docker compose config</text>
      <rect class="b-ok" x="90" y="206" width="320" height="96" rx="10" />
      <text class="t-ok" x="250" y="234" text-anchor="middle" font-size="15.5" font-weight="600">18 个挂载 · 5 个不可重建</text>
      <text class="t-mut" x="250" y="260" text-anchor="middle" font-size="14">915.2 MB</text>
      <text class="t-ok" x="250" y="284" text-anchor="middle" font-size="13" fill-opacity="0.85">一直是对的 —— 它成了对照组</text>

      <rect class="b-mut" x="90" y="318" width="320" height="136" rx="10" />
      <text class="t-mut" x="110" y="346" font-size="13.5" font-weight="600">为什么 A 一直是对的</text>
      <text class="t-sub" x="110" y="374" font-size="13">docker 自己解析了 YAML 锚点，</text>
      <text class="t-sub" x="110" y="394" font-size="13">也自己做了 profile 过滤，</text>
      <text class="t-sub" x="110" y="414" font-size="13">工具只管读它的结果。</text>
      <text class="t-alt" x="110" y="440" font-size="13">代价：得装 docker 命令行</text>

      <!-- 路径 B -->
      <text class="t-warm" x="710" y="190" text-anchor="middle" font-size="15">路径 B · 内置扫描器</text>
      <rect class="b-warm" x="550" y="206" width="320" height="96" rx="10" />
      <text class="t-warm" x="710" y="234" text-anchor="middle" font-size="15.5" font-weight="600">16 个挂载 · 3 个不可重建</text>
      <text class="t-mut" x="710" y="260" text-anchor="middle" font-size="14">413.9 MB</text>
      <text class="t-warm" x="710" y="284" text-anchor="middle" font-size="13" fill-opacity="0.85">比 A 少了 501.3 MB</text>

      <rect class="b-dash" x="550" y="318" width="320" height="136" rx="10" />
      <text class="t-warm" x="570" y="346" font-size="13.5" font-weight="600">两个解析 bug，都只坏这一边</text>
      <text class="t-mut" x="570" y="374" font-size="13">COMPOSE_PROFILES 没做插值</text>
      <text class="t-mut" x="570" y="394" font-size="13">　→ 两个服务被判「未启用」</text>
      <text class="t-mut" x="570" y="420" font-size="13">YAML 锚点没解析</text>
      <text class="t-mut" x="570" y="440" font-size="13">　→ env_file 引用从 36 掉到 10</text>

      <text class="note" x="34" y="480" font-size="13">让两条路径互相核对 —— 这本身才是发现 bug 的机制</text>
    </svg>
  </div>
</template>
