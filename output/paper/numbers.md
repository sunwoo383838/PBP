# numbers (auto)

## Qwen3.5-27B base n=427: direct 33.0, routing 38.4, ingress 53.4, full_load 52.5
  route +5.4 [+1.6, +9.1] p=0.0067 ({'a_only': 45, 'b_only': 22, 'p': 0.006741447363103126}); sel +15.0 [+10.3, +19.9] p=1.9e-09; total +20.4 [+15.0, +25.3] p=2.4e-14 ({'a_only': 112, 'b_only': 25, 'p': 2.403640054084458e-14}); vs full +0.9 [-4.4, +6.3]
  A n=180: direct 71.7, routing 68.3, ingress 69.4, full_load 78.3 | route -3.3 [-9.4, +2.8] | sel +1.1 [-5.0, +6.7] | total -2.2 [-8.3, +3.9]
  B n=85: direct 11.8, routing 32.9, ingress 55.3, full_load 40.0 | route +21.2 [+10.6, +31.8] | sel +22.4 [+9.4, +35.3] | total +43.5 [+30.6, +56.5]
  C n=96: direct 1.0, routing 11.5, ingress 32.3, full_load 28.1 | route +10.4 [+4.2, +17.7] | sel +20.8 [+12.5, +30.2] | total +31.2 [+21.9, +40.6]
  D n=66: direct 1.5, routing 3.0, ingress 37.9, full_load 33.3 | route +1.5 [-3.0, +7.6] | sel +34.8 [+22.7, +47.0] | total +36.4 [+25.8, +48.5]
  days 1-5 n=143: direct 36.4, routing 42.0, ingress 60.1, full_load 55.9 | total +23.8 [+14.7, +33.6]
  days 6-10 n=142: direct 31.0, routing 38.7, ingress 52.1, full_load 51.4 | total +21.1 [+12.0, +30.3]
  days 11-15 n=142: direct 31.7, routing 34.5, ingress 47.9, full_load 50.0 | total +16.2 [+9.2, +23.9]
  cost: direct calls 20.9 tok 250k usd 0.082 exh 0.0% noans 0.7%; routing calls 35.9 tok 410k usd 0.147 exh 0.0% noans 0.2%; ingress calls 50.4 tok 605k usd 0.224 exh 0.0% noans 0.0%; full_load calls 6.6 tok 192k usd 0.061 exh 0.0% noans 0.2%
  reach: direct A=73.3 B=47.0 C=62.9 D=71.6 all=65.7; routing A=68.6 B=76.1 C=70.3 D=80.5 all=72.4; ingress A=73.4 B=79.1 C=77.3 D=78.8 all=76.4
  additions effect: A: with n=156 ing 70.5 dir 71.8 / without n=24 ing 62.5 dir 70.8; B: with n=77 ing 54.5 dir 13.0 / without n=8 ing 62.5 dir 0.0; C: with n=90 ing 33.3 dir 1.1 / without n=6 ing 16.7 dir 0.0; D: with n=66 ing 37.9 dir 1.5 / without n=0 ing nan dir nan; all: with n=389 ing 53.2 dir 31.9 / without n=38 ing 55.3 dir 44.7
## DeepSeek-V4-Flash base n=427: direct 34.7, routing 45.0, ingress 52.7, full_load 62.5
  route +10.3 [+6.6, +13.8] p=6.2e-08 ({'a_only': 56, 'b_only': 12, 'p': 6.209495737562187e-08}); sel +7.7 [+3.3, +11.9] p=0.00081; total +18.0 [+13.3, +23.0] p=4.4e-13 ({'a_only': 98, 'b_only': 21, 'p': 4.4033126351506443e-13}); vs full -9.8 [-15.0, -4.9]
  A n=180: direct 72.8, routing 75.6, ingress 72.8, full_load 73.3 | route +2.8 [-2.2, +7.8] | sel -2.8 [-8.9, +2.8] | total +0.0 [-6.1, +5.6]
  B n=85: direct 14.1, routing 44.7, ingress 50.6, full_load 60.0 | route +30.6 [+20.0, +41.2] | sel +5.9 [-4.7, +16.5] | total +36.5 [+24.7, +48.2]
  C n=96: direct 4.2, routing 17.7, ingress 35.4, full_load 56.2 | route +13.5 [+6.2, +21.9] | sel +17.7 [+7.3, +28.1] | total +31.2 [+20.8, +41.7]
  D n=66: direct 1.5, routing 1.5, ingress 25.8, full_load 45.5 | route +0.0 [+0.0, +0.0] | sel +24.2 [+15.2, +34.8] | total +24.2 [+13.6, +34.8]
  days 1-5 n=143: direct 39.2, routing 47.6, ingress 59.4, full_load 60.1 | total +20.3 [+11.9, +28.7]
  days 6-10 n=142: direct 33.8, routing 43.0, ingress 49.3, full_load 66.9 | total +15.5 [+7.7, +23.9]
  days 11-15 n=142: direct 31.0, routing 44.4, ingress 49.3, full_load 60.6 | total +18.3 [+10.6, +26.8]
  cost: direct calls 42.4 tok 594k usd 0.055 exh 0.9% noans 0.0%; routing calls 67.2 tok 839k usd 0.068 exh 1.4% noans 0.0%; ingress calls 82.7 tok 1022k usd 0.088 exh 1.9% noans 0.9%; full_load calls 7.6 tok 313k usd 0.029 exh 0.2% noans 0.0%
  reach: direct A=78.7 B=61.3 C=70.3 D=78.4 all=73.4; routing A=87.8 B=85.2 C=87.5 D=91.1 all=87.9; ingress A=87.2 B=84.8 C=88.4 D=89.4 all=87.5
  additions effect: A: with n=164 ing 70.1 dir 70.1 / without n=16 ing 100.0 dir 100.0; B: with n=80 ing 50.0 dir 15.0 / without n=5 ing 60.0 dir 0.0; C: with n=96 ing 35.4 dir 4.2 / without n=0 ing nan dir nan; D: with n=66 ing 25.8 dir 1.5 / without n=0 ing nan dir nan; all: with n=406 ing 50.7 dir 32.5 / without n=21 ing 90.5 dir 76.2
## Qwen3.5-9B base n=427: direct 18.7, routing 22.7, ingress 25.1, full_load 38.4
  route +4.0 [+0.5, +7.5] p=0.033 ({'a_only': 37, 'b_only': 20, 'p': 0.033143967787505446}); sel +2.3 [-1.6, +6.3] p=0.27; total +6.3 [+2.3, +10.1] p=0.0021 ({'a_only': 50, 'b_only': 23, 'p': 0.002118172746400632}); vs full -13.3 [-17.8, -8.7]
  A n=180: direct 40.0, routing 46.7, ingress 46.7, full_load 71.1 | route +6.7 [-0.6, +13.9] | sel +0.0 [-6.7, +6.7] | total +6.7 [-0.6, +14.4]
  B n=85: direct 5.9, routing 4.7, ingress 18.8, full_load 23.5 | route -1.2 [-5.9, +3.5] | sel +14.1 [+4.7, +23.5] | total +12.9 [+4.7, +22.4]
  C n=96: direct 2.1, routing 6.2, ingress 4.2, full_load 11.5 | route +4.2 [+0.0, +9.4] | sel -2.1 [-7.3, +3.1] | total +2.1 [-3.1, +7.3]
  D n=66: direct 1.5, routing 4.5, ingress 4.5, full_load 7.6 | route +3.0 [-3.0, +9.1] | sel +0.0 [-6.1, +6.1] | total +3.0 [+0.0, +7.6]
  days 1-5 n=143: direct 23.8, routing 23.1, ingress 26.6, full_load 42.0 | total +2.8 [-4.2, +9.8]
  days 6-10 n=142: direct 14.8, routing 23.2, ingress 23.9, full_load 38.7 | total +9.2 [+3.5, +15.5]
  days 11-15 n=142: direct 17.6, routing 21.8, ingress 24.6, full_load 34.5 | total +7.0 [+0.0, +14.1]
  cost: direct calls 41.3 tok 729k usd 0.066 exh 10.1% noans 0.2%; routing calls 45.7 tok 518k usd 0.044 exh 2.1% noans 0.2%; ingress calls 55.6 tok 619k usd 0.055 exh 0.9% noans 0.9%; full_load calls 7.6 tok 221k usd 0.022 exh 1.2% noans 0.5%
  reach: direct A=41.3 B=37.0 C=41.4 D=49.6 all=42.0; routing A=61.2 B=61.7 C=65.2 D=69.9 all=63.9; ingress A=56.8 B=59.1 C=64.3 D=67.8 all=61.1
  additions effect: A: with n=158 ing 51.3 dir 41.1 / without n=22 ing 13.6 dir 31.8; B: with n=76 ing 21.1 dir 5.3 / without n=9 ing 0.0 dir 11.1; C: with n=96 ing 4.2 dir 2.1 / without n=0 ing nan dir nan; D: with n=64 ing 1.6 dir 1.6 / without n=2 ing 100.0 dir 0.0; all: with n=394 ing 25.9 dir 18.3 / without n=33 ing 15.2 dir 24.2

## scale shared templates (11): ['alloc', 'budget', 'capacity', 'conflict', 'diag', 'lookup', 'plan', 'precedence', 'purchase', 'temporal', 'whatif']
  R1 G=5: all n=141 total +17.7 [+9.9, +25.5] | shared n=118 direct 34.7, routing 36.4, ingress 47.5, full_load 49.2 total +12.7 [+5.1, +21.2] route +1.7 [-5.1, +9.3] sel +11.0 [+3.4, +18.6]
  D3 G=6: all n=167 total +26.9 [+18.6, +35.3] | shared n=167 direct 34.7, routing 44.3, ingress 61.7, full_load 48.5 total +26.9 [+18.6, +35.3] route +9.6 [+3.6, +16.8] sel +17.4 [+10.8, +24.6]
  base G=10: all n=285 total +22.5 [+15.8, +28.8] | shared n=235 direct 38.3, routing 42.6, ingress 54.9, full_load 54.0 total +16.6 [+9.4, +23.8] route +4.3 [-0.4, +9.4] sel +12.3 [+5.5, +18.7]
  R3 G=15: all n=427 total +19.7 [+15.0, +24.6] | shared n=350 direct 33.4, routing 40.9, ingress 50.3, full_load 50.3 total +16.9 [+11.4, +22.0] route +7.4 [+3.1, +12.0] sel +9.4 [+4.6, +14.3]
  spans 2 n=274: direct 31.8, routing 45.6, ingress 58.8, full_load 65.3 total +27.0 [+21.2, +32.8] route +13.9 [+9.1, +18.6] sel +13.1 [+7.3, +18.2]
  spans 3 n=390: direct 36.2, routing 43.1, ingress 62.6, full_load 49.5 total +26.4 [+21.0, +31.8] route +6.9 [+2.6, +11.0] sel +19.5 [+14.9, +24.1]
  spans 4 n=323: direct 33.1, routing 35.9, ingress 48.6, full_load 50.5 total +15.5 [+9.9, +21.7] route +2.8 [-1.9, +7.4] sel +12.7 [+6.8, +18.3]
  spans 5+ n=175: direct 16.6, routing 18.9, ingress 24.6, full_load 30.9 total +8.0 [+2.3, +14.3] route +2.3 [-3.4, +7.4] sel +5.7 [+0.6, +11.4]
  pooled n=1162: A n=483 direct 67.9 routing 65.8 ingress 67.3 full_load 74.7 route -2.1 [-5.6, +1.7] sel +1.4 [-2.1, +5.2]; B n=238 direct 11.3 routing 36.1 ingress 58.8 full_load 42.9 route +24.8 [+18.1, +31.1] sel +22.7 [+15.1, +29.8]; C n=272 direct 1.8 routing 9.2 ingress 30.9 full_load 27.6 route +7.4 [+4.0, +11.0] sel +21.7 [+16.5, +27.2]; D n=169 direct 2.4 routing 7.7 ingress 33.1 full_load 30.2 route +5.3 [+1.8, +9.5] sel +25.4 [+18.3, +32.5]; c_ops n=270 direct 1.5 routing 8.1 ingress 29.6 full_load 24.1 route +6.7 [+3.7, +10.0] sel +21.5 [+15.9, +27.4]

## variants n=285
  direct: acc 33.7 A 71.1 B 15.5 C 1.6 D 0.0 cops 1.5 calls 20.8 tok 229k usd 0.077 | vs ingress -22.5 [-29.1, -16.1] p=1.6e-10 | reach 66.2
  routing: acc 40.4 A 68.6 B 34.5 C 17.5 D 2.3 cops 15.4 calls 35.4 tok 380k usd 0.146 | vs direct +6.7 [+2.1, +11.2] | vs ingress -15.8 [-22.1, -9.8] p=1e-06 | reach 71.4
  ingress: acc 56.1 A 69.4 B 51.7 C 39.7 D 48.8 cops 36.9 calls 49.4 tok 576k usd 0.227 | vs direct +22.5 [+16.1, +28.8] | reach 76.5
  full_load: acc 53.7 A 77.7 B 43.1 C 28.6 D 37.2 cops 24.6 calls 6.8 tok 200k usd 0.063 | vs direct +20.0 [+14.4, +26.0] | vs ingress -2.5 [-9.5, +4.6] p=0.54 | reach nan
  direct_relay: acc 33.7 A 71.1 B 13.8 C 3.2 D 0.0 cops 3.1 calls 37.8 tok 420k usd 0.121 | vs direct +0.0 [-3.5, +3.5] | vs ingress -22.5 [-29.1, -15.8] p=1e-10 | reach 64.3
  retrieve: acc 47.0 A 66.9 B 48.3 C 25.4 D 20.9 cops 21.5 calls 28.3 tok 328k usd 0.115 | vs direct +13.3 [+7.7, +18.9] | vs ingress -9.1 [-15.4, -3.5] p=0.0038 | reach 70.6
  sidecar: acc 55.8 A 76.0 B 39.7 C 42.9 D 39.5 cops 40.0 calls 26.4 tok 284k usd 0.108 | vs direct +22.1 [+16.5, +27.7] | vs ingress -0.4 [-6.3, +5.3] p=1 | reach 64.8

## gateway
  qwen3.5-27b/routing: n 1524, members_selected 2.252, referral_rate 0.041, out_of_scope_rate 0.005, additions 0.000, conflicts 0.000, proposals 0.000, dropped 0.000, requery_rate 0.000, any_addition_rate 0.000
  qwen3.5-27b/ingress: n 1463, members_selected 2.275, referral_rate 0.027, out_of_scope_rate 0.006, additions 1.569, conflicts 0.614, proposals 0.634, dropped 0.062, requery_rate 0.368, any_addition_rate 0.619
  deepseek-v4-flash/routing: n 2504, members_selected 2.474, referral_rate 0.025, out_of_scope_rate 0.005, additions 0.000, conflicts 0.000, proposals 0.000, dropped 0.000, requery_rate 0.000, any_addition_rate 0.000
  deepseek-v4-flash/ingress: n 1813, members_selected 2.591, referral_rate 0.022, out_of_scope_rate 0.007, additions 3.293, conflicts 0.716, proposals 0.490, dropped 0.101, requery_rate 0.627, any_addition_rate 0.681
  qwen3.5-9b/routing: n 1767, members_selected 2.303, referral_rate 0.026, out_of_scope_rate 0.014, additions 0.000, conflicts 0.000, proposals 0.000, dropped 0.000, requery_rate 0.000, any_addition_rate 0.000
  qwen3.5-9b/ingress: n 1377, members_selected 2.188, referral_rate 0.017, out_of_scope_rate 0.010, additions 4.466, conflicts 0.290, proposals 0.583, dropped 0.055, requery_rate 0.500, any_addition_rate 0.876

## templates (27B pooled)
  alloc n=74: direct 2.7 routing 1.4 ingress 6.8 full_load 1.4 total +4.1 [-1.4, +9.5]
  budget n=89: direct 12.4 routing 20.2 ingress 43.8 full_load 39.3 total +31.5 [+21.3, +41.6]
  capacity n=98: direct 7.1 routing 10.2 ingress 48.0 full_load 51.0 total +40.8 [+30.6, +51.0]
  conflict n=82: direct 48.8 routing 69.5 ingress 76.8 full_load 97.6 total +28.0 [+17.1, +40.2]
  contract_gate n=82: direct 4.9 routing 28.0 ingress 73.2 full_load 68.3 total +68.3 [+57.3, +78.0]
  diag n=98: direct 43.9 routing 43.9 ingress 49.0 full_load 61.2 total +5.1 [-5.1, +15.3]
  lookup n=147: direct 56.5 routing 80.3 ingress 93.9 full_load 59.9 total +37.4 [+29.3, +45.6]
  plan n=126: direct 57.1 routing 54.8 ingress 54.0 full_load 57.1 total -3.2 [-12.7, +5.6]
  precedence n=58: direct 63.8 routing 58.6 ingress 58.6 full_load 79.3 total -5.2 [-17.2, +6.9]
  purchase n=105: direct 12.4 routing 13.3 ingress 33.3 full_load 15.2 total +21.0 [+11.4, +30.5]
  renewal n=14: direct 71.4 routing 71.4 ingress 78.6 full_load 85.7 total +7.1 [+0.0, +21.4]
  sourcing n=40: direct 2.5 routing 5.0 ingress 7.5 full_load 35.0 total +5.0 [+0.0, +12.5]
  temporal n=56: direct 39.3 routing 41.1 ingress 42.9 full_load 50.0 total +3.6 [-3.6, +10.7]
  vendor n=37: direct 2.7 routing 2.7 ingress 18.9 full_load 13.5 total +16.2 [+2.7, +29.7]
  whatif n=56: direct 32.1 routing 33.9 ingress 41.1 full_load 46.4 total +8.9 [-3.6, +21.4]

## ops: {'n_runs': 81, 'total_cost_usd': 1130.32, 'total_llm_calls': 407762, 'restarts': 233, 'n_scored_rows': 8919}