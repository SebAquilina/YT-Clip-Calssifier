# The automatic candle maker nobody's talking about (yet)

- **Video:** [ivWkG-wDrn4](https://www.youtube.com/watch?v=ivWkG-wDrn4)
- **Duration:** 3:29  (209s)
- **Source:** storyboard  |  **Windows:** 26  |  **Segments:** 10

## Action segments (merged)

| # | Time | Duration | Action | Phase | Step | Conf |
|--:|------|---------:|--------|-------|:----:|-----:|
| 1 | 0:00–0:48 | 48s | `transition` | aux |  | 0.42 |
| 2 | 0:48–1:04 | 16s | `reveal_result` | finish | ✓ | 0.40 |
| 3 | 1:04–1:12 | 8s | `transition` | aux |  | 0.40 |
| 4 | 1:12–1:20 | 8s | `pour_wax` | assemble | ✓ | 0.40 |
| 5 | 1:20–1:28 | 8s | `melt_wax` | process | ✓ | 0.40 |
| 6 | 1:28–1:53 | 24s | `reveal_result` | finish | ✓ | 0.40 |
| 7 | 1:53–2:01 | 8s | `melt_wax` | process | ✓ | 0.40 |
| 8 | 2:01–2:09 | 8s | `pour_wax` | assemble | ✓ | 0.40 |
| 9 | 2:09–2:41 | 32s | `reveal_result` | finish | ✓ | 0.40 |
| 10 | 2:41–3:29 | 48s | `transition` | aux |  | 0.42 |

## Per-window detail

| Window | Time | Action | Conf | Notes |
|-------:|------|--------|-----:|-------|
| W0 | 0:00–0:08 | `transition` | 0.50 |  |
| W1 | 0:08–0:16 | `transition` *(smoothed)* | 0.40 | despiked to match neighbours |
| W2 | 0:16–0:24 | `transition` | 0.40 |  |
| W3 | 0:24–0:32 | `transition` | 0.40 |  |
| W4 | 0:32–0:40 | `transition` | 0.40 |  |
| W5 | 0:40–0:48 | `transition` | 0.40 |  |
| W6 | 0:48–0:56 | `reveal_result` | 0.40 |  |
| W7 | 0:56–1:04 | `reveal_result` | 0.40 |  |
| W8 | 1:04–1:12 | `transition` | 0.40 |  |
| W9 | 1:12–1:20 | `pour_wax` | 0.40 | backward step vs canonical order (reveal_result->pour_wax) |
| W10 | 1:20–1:28 | `melt_wax` | 0.40 | backward step vs canonical order (reveal_result->melt_wax) |
| W11 | 1:28–1:36 | `reveal_result` | 0.40 |  |
| W12 | 1:36–1:44 | `reveal_result` *(smoothed)* | 0.40 | despiked to match neighbours |
| W13 | 1:44–1:53 | `reveal_result` | 0.40 |  |
| W14 | 1:53–2:01 | `melt_wax` | 0.40 | backward step vs canonical order (reveal_result->melt_wax) |
| W15 | 2:01–2:09 | `pour_wax` | 0.40 | backward step vs canonical order (reveal_result->pour_wax) |
| W16 | 2:09–2:17 | `reveal_result` | 0.40 |  |
| W17 | 2:17–2:25 | `reveal_result` | 0.40 |  |
| W18 | 2:25–2:33 | `reveal_result` *(smoothed)* | 0.40 | despiked to match neighbours |
| W19 | 2:33–2:41 | `reveal_result` | 0.40 |  |
| W20 | 2:41–2:49 | `transition` | 0.40 |  |
| W21 | 2:49–2:57 | `transition` | 0.40 |  |
| W22 | 2:57–3:05 | `transition` *(smoothed)* | 0.40 | despiked to match neighbours |
| W23 | 3:05–3:13 | `transition` | 0.40 |  |
| W24 | 3:13–3:21 | `transition` | 0.40 |  |
| W25 | 3:21–3:29 | `transition` | 0.50 |  |
