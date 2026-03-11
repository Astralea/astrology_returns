# astrology

CLI toolkit for natal charts, solar/lunar returns, transits, profections, firdaria, and more.

Text output designed for copy-paste into language models for interpretation.

## Install

```bash
uv sync
```

## Commands

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

Every chart includes:

- **Planets** — position, house placement, retrograde flag (R), dignity/debility markers
- **Essential Dignities Table** — domicile, exaltation, triplicity, term, face rulers
- **Aspects** — major aspects (conjunction, sextile, square, trine, opposition) with orbs, applying/separating
- **Receptions** — mutual receptions (aspect-free) and one-way receptions (require aspect)
- **Moon Void of Course** — detection with degrees remaining in sign

## Notes

- Times default to **local time** (timezone auto-detected from location). Use `--ut` for Universal Time input.
- Uses Moshier ephemeris (built-in, no external files needed).
- Chiron is excluded (requires separate Swiss Ephemeris data files).
