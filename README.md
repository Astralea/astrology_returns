# astrology

CLI toolkit for natal charts, solar/lunar returns, transits, profections, firdaria, and more.

Text output designed for copy-paste into language models for interpretation.

## Install

```bash
uv sync
```

## Commands

### Bazi (八字 — Chinese Astrology)

```bash
# Basic chart
uv run astro bazi --date 1990-01-15 --time 08:00 --city "Beijing"

# With full analysis
uv run astro bazi --date 1990-01-15 --time 08:00 --city "Beijing" --relations --dayun --liunian

# Female chart
uv run astro bazi --date 1990-01-15 --time 08:00 --city "Beijing" --gender female
```

**Features:**
- Four pillars (年柱/月柱/日柱/时柱) with solar term-based month pillar
- True solar time correction (use `--no-true-solar` to disable)
- ShiShen (十神) analysis
- Earthly branch relations: 六合, 六冲, 三合, 三会, 刑, 害, 破
- DaYun (大运) calculation with gender-specific direction
- LiuNian (流年) lookup

### Bazi Period (行运)

```bash
# Current period (大运 + 流年 + 流月 + 流日)
uv run astro bazi-period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing"

# Specific year
uv run astro bazi-period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing" --year 2026

# Compact view
uv run astro bazi-period --natal-date 1990-01-15 --natal-time 08:00 --city "Beijing" --compact
```

**Features:**
- Shows current DaYun (大运) period
- LiuNian (流年) with branch relations to natal chart
- LiuYue (流月) and LiuRi (流日) analysis
- Transit relations (刑冲合害) with original chart

### Natal Chart

```bash
uv run astro natal --date 1990-01-15 --time 08:00 --city "Beijing"
uv run astro natal --date 1990-01-15 --time 08:00 --location "39.9,116.4"
uv run astro natal --date 1990-01-15 --time 08:00 --city "Beijing" --house-system whole_sign
```

### Solar Return

```bash
uv run astro sr --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"
```

### Lunar Return

```bash
# Next lunar return after a date
uv run astro lr --natal-date 1990-01-15 --natal-time 08:00 --after 2026-03-11 --city "Shanghai"

# All lunar returns in a year (~13)
uv run astro lr-year --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"
```

### Horary

```bash
# Current moment
uv run astro horary --city "Tokyo"

# Specific time
uv run astro horary --date 2026-03-11 --time 14:30 --city "London"
```

### Annual Profection

```bash
uv run astro profection --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"
```

Shows the activated house (age mod 12), Lord of the Year, and its natal position.

### Firdaria

```bash
uv run astro firdaria --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"

# Full 75-year table
uv run astro firdaria --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing" --full
```

Medieval planetary period system. Auto-detects diurnal/nocturnal birth.

### Transits

```bash
# Jupiter & Saturn transits (default)
uv run astro transit --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing"

# Specific planets
uv run astro transit --natal-date 1990-01-15 --natal-time 08:00 --year 2026 --city "Beijing" --planet Mars --planet Venus
```

### Geocode

```bash
uv run astro geo "New York"
```

## Options

| Option | Description |
|--------|-------------|
| `--location "lat,lon"` | Coordinates directly |
| `--city "name"` | City name (geocoded via OpenStreetMap) |
| `--house-system` | `placidus` (default), `koch`, `whole_sign`, `equal`, `campanus`, `regiomontanus`, `porphyry`, `morinus` |
| `--unicode / --no-unicode` | Use zodiac symbols (♈♉♊) instead of abbreviations (Ari/Tau/Gem) |
| `--modern / --traditional` | Include outer planets in dignities & receptions (default: traditional) |
| `--ut` | Input time is in UT (default: local time, auto-detected from location) |

Global options go before the subcommand:

```bash
uv run astro --unicode --modern sr --natal-date ...
```

## Chart Output

### Western Astrology

Every chart includes:

- **Planets** — position, house placement, retrograde flag (R), dignity/debility markers
- **Essential Dignities Table** — domicile, exaltation, triplicity, term, face rulers
- **Aspects** — major aspects (conjunction, sextile, square, trine, opposition) with orbs, applying/separating
- **Receptions** — mutual receptions (aspect-free) and one-way receptions (require aspect)
- **Moon Void of Course** — detection with degrees remaining in sign

### Bazi (八字) Output

Every bazi chart includes:

- **Four Pillars** — year/month/day/hour pillars (年柱/月柱/日柱/时柱)
- **Day Master** —日主 (Ruling Element of the Day)
- **ShiShen** — 十神 (Ten Gods) for each stem and branch
- **Cang Gan** — 藏干 (Hidden Stems) with their ShiShen
- **Branch Relations** — 六合, 六冲, 三合, 三会, 刑, 害, 破 (when using `--relations`)
- **DaYun** — 大运 (10-year luck periods) with gender-specific direction
- **LiuNian** — 流年 (yearly pillars)

## Notes

- Times default to **local time** (timezone auto-detected from location). Use `--ut` for Universal Time input.
- Uses Moshier ephemeris (built-in, no external files needed).
- Chiron is excluded (requires separate Swiss Ephemeris data files).
