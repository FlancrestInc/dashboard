# Dashboard Layout Configuration Design

## Goal

Add display-size-aware layout configuration to the household dashboard, including landscape and portrait presets, a visual custom layout builder, tabbed settings, and configurable photo display modes.

## Current State

The app is a small FastAPI dashboard with server-rendered templates. Settings are stored as a JSON document in SQLite through `SettingsStore`, normalized in `app/settings.py`, rendered by `app/templates/display.html`, and updated from the single-page form in `app/templates/admin.html`. The current display has a coarse `layout_preset` value with CSS differences for `classic`, `focus`, and `camera`.

## Proposed Architecture

Introduce a structured `layout` settings object while preserving backward compatibility with the existing top-level `layout_preset`. The layout object stores display dimensions, orientation, preset, and custom percentage-based block rectangles. Preset geometry is defined in Python so the display and admin preview can use the same layout model.

The display template renders enabled dashboard blocks as individually positioned regions. Preset mode uses built-in geometry; custom mode uses saved geometry validated against allowed block IDs and bounded percentages. This keeps fullscreen display behavior deterministic for the 1920 x 1080 target while scaling to common landscape and portrait displays.

## Layout Model

`layout` contains:

- `mode`: `preset` or `custom`
- `preset`: `classic`, `focus`, `camera`, `portrait`, `photo-frame`, or `dense`
- `display_size`: common size key such as `1920x1080`, `1080x1920`, `2560x1440`, `3840x2160`, `1280x800`, or `custom`
- `width`: normalized integer display width
- `height`: normalized integer display height
- `orientation`: `landscape` or `portrait`
- `custom_blocks`: mapping of block IDs to percentage rectangles with `x`, `y`, `w`, and `h`

Supported block IDs are `clock`, `weather`, `calendar`, `frigate`, and `photos`.

## Presets

Initial presets:

- `classic`: clock/weather header with agenda and camera below.
- `focus`: larger agenda area with secondary camera/weather.
- `camera`: camera-first layout.
- `portrait`: stacked portrait layout for rotated 1080p displays.
- `photo-frame`: reserves a prominent photo block alongside core information.
- `dense`: compact information-rich layout for smaller displays.

## Admin UI

The admin page becomes tabbed to keep settings manageable:

- `Board`: title and save actions.
- `Layout`: display size, orientation, preset selection, and visual custom builder.
- `Photos`: rotation and display behavior.
- `Data Sources`: weather, calendar, and Frigate configuration.
- `Blocks`: visibility toggles.

The layout builder is a scaled preview canvas. Users can drag blocks and resize them in custom mode. The builder saves hidden form inputs containing percentage rectangles. Preset selection can seed custom mode.

## Photos

Photo settings expand from basic background rotation to configurable presentation:

- `display_mode`: `background`, `frame`, or `both`
- `rotation_seconds`
- `background_fit`: `cover` or `contain`
- `background_overlay`: 0 to 90 percent
- `frame_fit`: `cover` or `contain`
- `show_captions`: boolean

When `display_mode` includes `frame`, the `photos` block renders as a normal dashboard block. When it includes `background`, the background layer continues rotating photos behind content.

## Error Handling

Invalid settings fall back to safe defaults. Custom block values are clamped so blocks stay on the canvas and keep minimum usable dimensions. Unknown block IDs are ignored. Legacy settings that only contain `layout_preset` continue to load.

## Testing

Add unit tests for layout defaulting, form parsing, invalid fallback, custom geometry clamping, and photo option parsing. Existing tests should continue to pass.
