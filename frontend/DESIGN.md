# Design System: UMKM Geospatial & Product Intelligence Suite

## 1. Visual Theme & Atmosphere
A high-density, cockpit-precise intelligence console for mapping Indonesian micro, small, and medium enterprises (UMKM) and tracking marketplace product data. The atmosphere is utilitarian, disciplined, and dark-neutral — reminiscent of a geospatial command terminal.

- **Density:** Cockpit Dense (8/10) — compact data cells, rich map canvas, tight analytical metrics.
- **Variance:** Offset Asymmetric (6/10) — 60/40 map-to-catalog split view, asymmetric stat cards.
- **Motion:** Fluid Spring (6/10) — `stiffness: 120, damping: 18`, smooth leaflet pan transitions, staggered list mounts.

---

## 2. Color Palette & Roles
- **Canvas Base** (`#09090B`) — Primary viewport background, zinc-950 depth
- **Surface Elevation 1** (`#121215`) — Sidebar, filter bar, and map HUD overlays
- **Surface Elevation 2** (`#18181B`) — Active cards, hover surfaces, modal backdrops
- **Charcoal Border** (`#27272A`) — 1px crisp structural dividing lines
- **Primary Text** (`#F4F4F5`) — High-contrast zinc-100 typography
- **Muted Steel** (`#71717A`) — Secondary labels, timestamps, coordinate readouts
- **Emerald Accent** (`#10B981`) — Single high-contrast signal accent for verified badges, live statuses, and primary CTAs
- **Amber Signal** (`#F59E0B`) — Marketplace pricing alerts & ratings

*Rule: Maximum 1 primary accent. The AI purple/neon glow aesthetic is strictly banned.*

---

## 3. Typography Rules
- **Display & Titles:** `Plus Jakarta Sans` / `Geist` (font-weight: 600, track-tight, -0.02em)
- **Body:** `Plus Jakarta Sans` / `Geist` (font-weight: 400, leading 1.5, max 65ch)
- **Mono:** `JetBrains Mono` / `Geist Mono` (for all prices, coordinates, lat/long, stock numbers, and scrape job IDs)
- **Banned:** `Inter`, generic serif fonts, and emoji characters anywhere in the interface.

---

## 4. Component Stylings
- **Map Viewport:** Dark themed OpenStreetMap / CartoDB Dark Matter tiles, custom SVG ring markers with pulsing halos for active locations.
- **Buttons:** Flat slate fill with 1px border. Tactile `transform: translateY(1px)` on `:active`. Zero neon glow.
- **Cards:** Crisp 10px rounded corners, subtle `1px solid #27272A` borders, elevated background `#121215`.
- **Inputs & Search:** Top label, integrated filter tags, `#18181B` background with `#10B981` subtle focus ring.
- **Drawer / Detail View:** Slide-over inspection pane with tabbed product table, store coordinates, and WhatsApp direct trigger.
- **Loaders:** Skeletal pulse shimmers matching exact card geometries.

---

## 5. Layout Principles
- Two-column responsive desktop layout (Interactive Map pane on left/top, UMKM & Product bento feed on right).
- Full height `min-h-[100dvh]`.
- Clean single column collapse below 1024px.
- Zero horizontal overflowing elements.

---

## 6. Anti-Patterns (Banned)
- NO emojis in headers, tabs, or buttons (use clean monochromatic SVG icons instead).
- NO Inter font.
- NO pure black (`#000000`) or saturated purple neon gradients.
- NO generic placeholder texts ("John Doe", "Acme").
- NO circular indeterminate spinner loaders.
