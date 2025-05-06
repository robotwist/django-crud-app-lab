# Fonts for Artifact Archive

This directory is intended for font files used in the Artifact Archive application.

## Font Stack

The application uses the following fonts for its analog appearance:

1. **Barry** (Primary display font)
   - Used for the "Artifact Archive" lettering
   - Google Fonts replacement: DM Serif Display

2. **Kabel Black** (Heading font)
   - Used for titles and buttons
   - Google Fonts replacement: Roboto Mono

3. **Friz Quadrata** (Body font)
   - Used for form labels and content
   - Google Fonts replacement: Crimson Pro

## Implementation

Instead of requiring actual font files, we use Google Fonts as replacements to ensure consistency across all platforms:

```css
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600&family=DM+Serif+Display&family=Roboto+Mono:wght@700&display=swap');
```

## Custom Font Installation

If you want to use the actual specified fonts:

1. Place the font files in this directory (.woff and .woff2 formats)
2. Uncomment the @font-face declarations in `analog_form.css`
3. Update the CSS variables to use the actual font names 