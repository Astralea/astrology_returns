# astrology-returns

CLI tool for calculating Natal charts (本命盘), Solar Returns (日返), Lunar Returns (月返), and Horary charts.

Text output designed for easy copy-paste into chart software (e.g. 宫神星).

## Install

```bash
uv sync
```

## Commands

### Natal Chart (本命盘)

```bash
# By city name
uv run astro natal --date 1990-01-15 --time 08:00 --city "Beijing"

# By coordinates
uv run astro natal --date 1990-01-15 --time 08:00 --location "39.9,116.4"

# With whole sign houses
uv run astro natal --date 1990-01-15 --time 08:00 --city "Beijing" --house-system whole_sign
```

### Solar Return (日返)

```bash
# By coordinates
uv run astro sr --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --location "39.9,116.4"

# By city name
uv run astro sr --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"
```

### Lunar Return (月返)

```bash
# Next lunar return after a date
uv run astro lr --natal-date 1990-01-15 --natal-time 08:00 --after 2026-03-11 --city "Shanghai"

# All lunar returns in a year (~13)
uv run astro lr-year --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"
```

### Horary (卜卦盘)

```bash
# Current moment
uv run astro horary --city "Tokyo"

# Specific time
uv run astro horary --date 2026-03-11 --time 14:30 --city "London"
```

### Geocode (查经纬度)

```bash
uv run astro geo "New York"
```

## Options

| Option | Description |
|--------|-------------|
| `--location "lat,lon"` | Coordinates directly |
| `--city "name"` | City name (geocoded via OpenStreetMap) |
| `--house-system` | `placidus` (default), `koch`, `whole_sign`, `equal`, `campanus`, `regiomontanus`, `porphyry`, `morinus` |
| `--unicode / --no-unicode` | Use ♈♉♊ symbols instead of Ari/Tau/Gem |

Unicode symbols go before the subcommand:

```bash
uv run astro --unicode sr --natal-date ...
```

## Output

Every chart includes:

- **Planets** with position, retrograde flag (R), and dignity/debility markers (Dom, Exl, Det, Fall, Trm, Fac)
- **Essential Dignities Table** — domicile, exaltation, term, face rulers for each planet's sign
- **Aspects** — all major aspects (☌ ⚹ □ △ ☍) with orbs, sorted by tightness, marked applying (a) or separating (s)
- **Receptions (互容/接纳)** — mutual receptions (domicile, exaltation, mixed) and one-way receptions

## Notes

- All times are in **UT** (Universal Time). Convert from your local timezone before use.
- Uses Moshier ephemeris (built-in, no external files needed).
- Chiron is excluded (requires separate Swiss Ephemeris data files).
