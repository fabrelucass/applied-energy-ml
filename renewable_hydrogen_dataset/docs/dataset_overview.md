# Overview — renewable_hydrogen_dataset.csv

## Schema
| Column | Dtype | Missing | Non-null |
|---|---|---:|---:|
| p_id2 | int64 | 0 | 2535 |
| start_year | int64 | 0 | 2535 |
| season_days_injured | int64 | 0 | 2535 |
| total_days_injured | int64 | 0 | 2535 |
| season_minutes_played | int64 | 0 | 2535 |
| season_games_played | int64 | 0 | 2535 |
| season_matches_in_squad | int64 | 0 | 2535 |
| total_minutes_played | int64 | 0 | 2535 |
| total_games_played | int64 | 0 | 2535 |
| dob | object | 0 | 2535 |
| height_cm | int64 | 0 | 2535 |
| weight_kg | int64 | 0 | 2535 |
| nationality | object | 0 | 2535 |
| work_rate | object | 0 | 2535 |
| pace | int64 | 0 | 2535 |
| physic | int64 | 0 | 2535 |
| fifa_rating | int64 | 0 | 2535 |
| position | object | 0 | 2535 |
| age | int64 | 0 | 2535 |
| bmi | float64 | 0 | 2535 |
| work_rate_numeric | int64 | 0 | 2535 |
| position_numeric | int64 | 0 | 2535 |
| significant_injury_prev_season | int64 | 0 | 2535 |
| cumulative_days_injured | int64 | 0 | 2535 |
| season_days_injured_prev_season | int64 | 0 | 2535 |
| target | int64 | 0 | 2535 |

## Numeric Stats
| Column | Mean | Std | Min | P25 | P50 | P75 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| p_id2 | 1268.000 | 731.936 | 1.000 | 634.500 | 1268.000 | 1901.500 | 2535.000 |
| start_year | 2012.173 | 7.179 | 2000.000 | 2006.000 | 2012.000 | 2018.000 | 2024.000 |
| season_days_injured | 49.181 | 28.959 | 0.000 | 24.000 | 50.000 | 74.000 | 99.000 |
| total_days_injured | 251.058 | 144.830 | 0.000 | 129.000 | 250.000 | 377.000 | 499.000 |
| season_minutes_played | 1505.323 | 869.420 | 1.000 | 745.500 | 1528.000 | 2251.500 | 2999.000 |
| season_games_played | 18.423 | 10.877 | 0.000 | 9.000 | 19.000 | 27.000 | 37.000 |
| season_matches_in_squad | 24.478 | 14.374 | 0.000 | 12.000 | 25.000 | 36.000 | 49.000 |
| total_minutes_played | 24393.633 | 14369.940 | 17.000 | 11853.000 | 24079.000 | 36486.500 | 49999.000 |
| total_games_played | 253.692 | 145.219 | 0.000 | 129.000 | 254.000 | 383.000 | 499.000 |
| height_cm | 174.122 | 14.361 | 150.000 | 162.000 | 174.000 | 186.000 | 199.000 |
| weight_kg | 74.265 | 14.521 | 50.000 | 62.000 | 74.000 | 87.000 | 99.000 |
| pace | 64.911 | 19.912 | 30.000 | 48.000 | 66.000 | 82.000 | 98.000 |
| physic | 63.335 | 19.916 | 30.000 | 46.000 | 63.000 | 80.000 | 98.000 |
| fifa_rating | 74.387 | 14.080 | 50.000 | 62.000 | 75.000 | 86.000 | 98.000 |
| age | 28.555 | 6.384 | 18.000 | 23.000 | 29.000 | 34.000 | 39.000 |
| bmi | 24.277 | 3.353 | 18.501 | 21.371 | 24.317 | 27.196 | 29.996 |
| work_rate_numeric | 2.008 | 0.820 | 1.000 | 1.000 | 2.000 | 3.000 | 3.000 |
| position_numeric | 2.485 | 1.121 | 1.000 | 1.000 | 2.000 | 3.000 | 4.000 |
| significant_injury_prev_season | 0.500 | 0.500 | 0.000 | 0.000 | 1.000 | 1.000 | 1.000 |
| cumulative_days_injured | 496.383 | 285.370 | 0.000 | 254.500 | 500.000 | 732.000 | 999.000 |
| season_days_injured_prev_season | 48.484 | 28.310 | 0.000 | 24.000 | 47.000 | 73.000 | 99.000 |
| target | 0.498 | 0.500 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |

## Categorical Top Values
| Column | Top values (count) |
|---|---|
| dob | 1970-01-01:1; 1970-01-02:1; 1970-01-03:1; 1970-01-04:1; 1970-01-05:1; 1970-01-06:1; 1970-01-07:1; 1970-01-08:1; 1970-01-09:1; 1970-01-10:1 |
| nationality | Hyderabad:529; Mumbai:525; Delhi:500; Chennai:495; Bangalore:486 |
| work_rate | Low:868; High:836; Medium:831 |
| position | Defender:653; Forward:629; Midfielder:629; Goalkeeper:624 |

## Histograms
- rh_hist_p_id2.png
- rh_hist_start_year.png
- rh_hist_season_days_injured.png
- rh_hist_total_days_injured.png
- rh_hist_season_minutes_played.png
- rh_hist_season_games_played.png
- rh_hist_season_matches_in_squad.png
- rh_hist_total_minutes_played.png
- rh_hist_total_games_played.png
- rh_hist_height_cm.png
- rh_hist_weight_kg.png
- rh_hist_pace.png

## Correlation
- rh_corr_heatmap.png
