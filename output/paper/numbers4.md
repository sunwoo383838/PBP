# numbers4
## Qwen3.5-27B
  first: n=262 direct 28.2 routing 37.4 ingress 59.2 full_load 54.6 | Δ +30.9 [+24.0, +38.2] | stale direct 8 routing 7 ingress 5 full_load 10
  revisit, unchanged: n=127 direct 49.6 routing 48.8 ingress 52.0 full_load 59.1 | Δ +2.4 [-3.9, +9.4] | stale direct 1 routing 1 ingress 0 full_load 0
  revisit, changed: n=38 direct 10.5 routing 10.5 ingress 18.4 full_load 15.8 | Δ +7.9 [+0.0, +18.4] | stale direct 8 routing 5 ingress 0 full_load 5
  revisit share by window: {'1-5': 0.42657342657342656, '6-10': 0.36619718309859156, '11-15': 0.36619718309859156}
  H H0: n=40 direct 22.5 routing 27.5 ingress 67.5 full_load 52.5 | Δ +45.0 [+22.5, +65.0]
  H H1: n=102 direct 7.8 routing 26.5 ingress 54.9 full_load 41.2 | Δ +47.1 [+36.3, +56.9]
  H H2: n=120 direct 2.5 routing 10.0 ingress 25.8 full_load 27.5 | Δ +23.3 [+15.0, +31.7]
  H none: n=165 direct 73.3 routing 69.1 ingress 69.1 full_load 77.6 | Δ -4.2 [-10.3, +1.8]
  R R0: n=56 direct 50.0 routing 69.6 ingress 89.3 full_load 55.4 | Δ +39.3 [+25.0, +51.8]
  R R1: n=179 direct 40.2 routing 43.6 ingress 57.0 full_load 68.7 | Δ +16.8 [+8.9, +25.1]
  R R2: n=115 direct 33.0 routing 40.9 ingress 56.5 full_load 53.9 | Δ +23.5 [+13.9, +33.9]
  R R3: n=77 direct 3.9 routing 0.0 ingress 14.3 full_load 10.4 | Δ +10.4 [+2.6, +18.2]
  in_evidence: H0 needs 48 in_evidence 10% search-loss 19%; H1 needs 161 in_evidence 19% search-loss 4%; H2 needs 244 in_evidence 9% search-loss 13%
  load: direct top1 61% hhi 0.50; routing top1 40% hhi 0.32; ingress top1 35% hhi 0.27 | latency: direct 3.3/9.7; routing 9.6/21.5; ingress 15.9/44.9; full_load 3.7/8.0
  departed-holder tasks: {'n': 51, 'acc': {'direct': 0.0196078431372549, 'routing': 0.0196078431372549, 'ingress': 0.43137254901960786, 'full_load': 0.35294117647058826}} | owner_exception: {'n': 65, 'referred': 15, 'acc_referred': 0.5333333333333333, 'acc_not_referred': 0.28, 'acc_direct': 0.24615384615384617}
## DeepSeek-V4-Flash
  first: n=262 direct 30.5 routing 43.5 ingress 56.9 full_load 71.8 | Δ +26.3 [+20.2, +33.2] | stale direct 7 routing 4 ingress 4 full_load 5
  revisit, unchanged: n=127 direct 50.4 routing 57.5 ingress 53.5 full_load 56.7 | Δ +3.1 [-3.9, +10.2] | stale direct 1 routing 0 ingress 1 full_load 0
  revisit, changed: n=38 direct 10.5 routing 13.2 ingress 21.1 full_load 18.4 | Δ +10.5 [+0.0, +23.7] | stale direct 8 routing 3 ingress 0 full_load 11
  revisit share by window: {'1-5': 0.42657342657342656, '6-10': 0.36619718309859156, '11-15': 0.36619718309859156}
  H H0: n=40 direct 22.5 routing 50.0 ingress 62.5 full_load 75.0 | Δ +40.0 [+22.5, +57.5]
  H H1: n=102 direct 11.8 routing 25.5 ingress 46.1 full_load 57.8 | Δ +34.3 [+24.5, +45.1]
  H H2: n=120 direct 4.2 routing 16.7 ingress 27.5 full_load 49.2 | Δ +23.3 [+14.2, +32.5]
  H none: n=165 direct 73.9 routing 76.4 ingress 72.7 full_load 72.1 | Δ -1.2 [-6.7, +4.8]
  R R0: n=56 direct 57.1 routing 89.3 ingress 94.6 full_load 75.0 | Δ +37.5 [+25.0, +50.0]
  R R1: n=179 direct 41.9 routing 46.4 ingress 55.9 full_load 72.6 | Δ +14.0 [+7.3, +21.2]
  R R2: n=115 direct 30.4 routing 47.0 ingress 56.5 full_load 67.8 | Δ +26.1 [+15.7, +36.5]
  R R3: n=77 direct 7.8 routing 6.5 ingress 9.1 full_load 22.1 | Δ +1.3 [-5.2, +7.8]
  in_evidence: H0 needs 48 in_evidence 10% search-loss 6%; H1 needs 161 in_evidence 10% search-loss 6%; H2 needs 244 in_evidence 11% search-loss 9%
  load: direct top1 53% hhi 0.44; routing top1 35% hhi 0.26; ingress top1 31% hhi 0.23 | latency: direct 5.7/16.5; routing 14.7/40.7; ingress 17.7/47.4; full_load 4.3/11.3
  departed-holder tasks: {'n': 51, 'acc': {'direct': 0.0196078431372549, 'routing': 0.0196078431372549, 'ingress': 0.27450980392156865, 'full_load': 0.49019607843137253}} | owner_exception: {'n': 65, 'referred': 16, 'acc_referred': 0.375, 'acc_not_referred': 0.2653061224489796, 'acc_direct': 0.23076923076923078}
## Qwen3.5-9B
  first: n=262 direct 13.4 routing 19.5 ingress 24.0 full_load 31.7 | Δ +10.7 [+5.7, +16.0] | stale direct 8 routing 6 ingress 4 full_load 10
  revisit, unchanged: n=127 direct 33.9 routing 35.4 ingress 31.5 full_load 58.3 | Δ -2.4 [-9.4, +4.7] | stale direct 0 routing 2 ingress 0 full_load 1
  revisit, changed: n=38 direct 5.3 routing 2.6 ingress 10.5 full_load 18.4 | Δ +5.3 [+0.0, +13.2] | stale direct 5 routing 3 ingress 0 full_load 3
  revisit share by window: {'1-5': 0.42657342657342656, '6-10': 0.36619718309859156, '11-15': 0.36619718309859156}
  H H0: n=40 direct 7.5 routing 7.5 ingress 25.0 full_load 25.0 | Δ +17.5 [+2.5, +35.0]
  H H1: n=102 direct 3.9 routing 4.9 ingress 12.7 full_load 20.6 | Δ +8.8 [+2.9, +14.7]
  H H2: n=120 direct 0.8 routing 4.2 ingress 4.2 full_load 10.8 | Δ +3.3 [+0.0, +7.5]
  H none: n=165 direct 43.6 routing 50.9 ingress 47.9 full_load 72.7 | Δ +4.2 [-3.6, +12.1]
  R R0: n=56 direct 39.3 routing 48.2 ingress 69.6 full_load 51.8 | Δ +30.4 [+17.9, +42.9]
  R R1: n=179 direct 20.7 routing 25.7 ingress 23.5 full_load 47.5 | Δ +2.8 [-3.9, +9.5]
  R R2: n=115 direct 16.5 routing 19.1 ingress 20.9 full_load 40.0 | Δ +4.3 [-1.7, +10.4]
  R R3: n=77 direct 2.6 routing 2.6 ingress 2.6 full_load 5.2 | Δ +0.0 [-5.2, +5.2]
  in_evidence: H0 needs 48 in_evidence 27% search-loss 2%; H1 needs 161 in_evidence 34% search-loss 8%; H2 needs 244 in_evidence 12% search-loss 12%
  load: direct top1 37% hhi 0.27; routing top1 37% hhi 0.27; ingress top1 33% hhi 0.23 | latency: direct 8.3/31.1; routing 14.5/58.9; ingress 17.1/53.3; full_load 5.3/15.7
  departed-holder tasks: {'n': 51, 'acc': {'direct': 0.0196078431372549, 'routing': 0.058823529411764705, 'ingress': 0.058823529411764705, 'full_load': 0.09803921568627451}} | owner_exception: {'n': 65, 'referred': 7, 'acc_referred': 0.42857142857142855, 'acc_not_referred': 0.15517241379310345, 'acc_direct': 0.16923076923076924}