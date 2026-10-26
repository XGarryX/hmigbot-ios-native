# 启播链路 3 路兜底完整代码（复盘 v1 复盘）

> 锚点：SKILL.md §2

---

## 完整 PlayerCore.loadAndStart 代码

```typescript
import { media } from '@kit.MediaKit';
import { router } from '@kit.ArkUI';

interface PlayerRouteParams {
  sectionId: string;
  sectionType: string;
  courseId: string;
  videoUrl?: string;
  name?: string;
  coverImage?: string;
  dura?: number;
  consume?: number;
}

class VideoPlayerCore {
  private avPlayer: media.AVPlayer | null = null;
  private surfaceId: string | null = null;
  private isInitialized: boolean = false;
  private pendingUrl: string | null = null;

  /**
   * 启播 3 路策略：
   * 1) Fast path: 调用方透传 videoUrl
   * 2) Fallback A: detail-multi（结构化更完整，对齐 Android 列表页字段）
   * 3) Fallback B: detail-single（已知部分子项返空字符串，最后兜底）
   */
  async loadAndStart(params: PlayerRouteParams): Promise<void> {
    let url: string | undefined;

    // Path 1: Fast path
    if (params.videoUrl !== undefined && params.videoUrl.length > 0) {
      url = params.videoUrl;
    }

    // Path 2: detail-multi
    if (!url) {
      try {
        const raw = await ApiService.get<object>('/detail/multi', { courseId: params.courseId });
        const detail = DetailMulti.fromJson(raw);
        url = detail.sections.find(s => s.id === params.sectionId)?.shortVideo;
      } catch (e) {
        console.warn('[Player] detail-multi failed', (e as Error).message);
      }
    }

    // Path 3: detail-single（最后兜底）
    if (!url) {
      try {
        const raw = await ApiService.get<object>('/detail/single', { sectionId: params.sectionId });
        const detail = DetailSingle.fromJson(raw);
        url = detail.shortVideo;
      } catch (e) {
        console.warn('[Player] detail-single failed', (e as Error).message);
      }
    }

    if (!url) {
      this.showPlayerError('视频地址不可用');
      return;
    }

    await this.prepareWithUrl(url);
  }

  private async prepareWithUrl(url: string): Promise<void> {
    if (!this.avPlayer) {
      this.avPlayer = await media.createAVPlayer();
      this.bindStateListener();
    }
    this.pendingUrl = url;
    this.avPlayer.url = url;  // → Initialized
  }

  setSurface(id: string): void {
    this.surfaceId = id;
    this.tryAttachAndPrepare();
  }

  private bindStateListener(): void {
    this.avPlayer!.on('stateChange', (state, _reason) => {
      if (state === 'initialized') {
        this.isInitialized = true;
        this.tryAttachAndPrepare();
      }
      // ... 其它状态
    });
  }

  private tryAttachAndPrepare(): void {
    if (this.surfaceId && this.isInitialized && this.avPlayer) {
      this.avPlayer.surfaceId = this.surfaceId;
      this.avPlayer.prepare();  // 双向等待都满足才 prepare
    }
  }
}
```

---

## 调用方透传示例

```typescript
// ListDetailPage（列表）
private jumpToPlayer(s: SectionItem): void {
  const params: PlayerRouteParams = {
    sectionId: s.id,
    sectionType: s.sectionType,
    courseId: this.effectiveCourseId,
    videoUrl: s.shortVideo,                    // ← 列表已有，必传
    name: s.name,
    coverImage: s.coverImage,
    dura: parseFloat(s.dura || '0'),
    consume: parseFloat(s.consume || '0'),
  };
  router.pushUrl({ url: 'pages/VideoPlayerPage', params });
}
```

---

## 为什么这样设计

| 决策 | 理由 |
|---|---|
| 调用方透传 | 列表已经有 `shortVideo`，再调 detail-single 是冗余 ~700ms 延迟 |
| 优先 detail-multi | 比 detail-single 字段更全；很多 detail-single 返空但 detail-multi 是有效的 |
| detail-single 作最后兜底 | 总比直接报错强 |
| 三路用 try/catch 链 | 任何一路失败不阻塞下一路；错误降级到"视频不可用"而不是 "API 网络错" |

---

## 复盘 v1 实战发现

某实战项目视频播放页多次启播失败的复盘：

1. 初版只走 detail-single → 部分子项"无法播放"（数据缺失）
2. 改为只走 detail-multi → 启播延迟 ~700ms（多一次串行 API）
3. 终版三路兜底 → 启播延迟接近 0（fast path 命中），数据缺失也能兜底

详见各项目自有的 `migration-decisions` 启播相关条目。
