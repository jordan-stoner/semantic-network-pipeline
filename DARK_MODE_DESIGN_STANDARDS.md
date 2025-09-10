# MLX Project Dark Mode Design Standards

## CSS Design Methodology

### Investigation Process (CRITICAL - Follow This Order)
1. **Check Parent CSS**: Always investigate parent containers and inherited styles first
2. **Identify Framework Conflicts**: Look for Bootstrap or other framework classes that may override custom styles
3. **Use Browser DevTools**: Inspect computed styles to understand what's actually being applied
4. **Test CSS Loading**: Add obvious test rules (red background) to verify CSS is actually loading
5. **Check Specificity**: Ensure your selectors have higher specificity than conflicting rules

### CSS Modification Hierarchy
1. **Categorical Styles**: Define styles by category (`.btn`, `.btn-text`) rather than specific IDs
2. **Override Framework Classes**: Target specific framework classes (`.me-1`, `.me-2`) when necessary
3. **Avoid Inline Styles**: Modify CSS classes instead of adding inline styles
4. **Use Specificity Properly**: Increase specificity with compound selectors (`.btn i.me-1`) rather than `!important` when possible
5. **Context-Specific Rules**: When general rules fail, target specific contexts (`.edit-options .btn`)

### Code Organization
- **No Duplicate Rules**: Don't insert new lines when modifying existing categorical styles
- **Logical Grouping**: Keep related styles together (all button styles in one section)
- **Clear Comments**: Document the purpose of overrides and special cases
- **Consistent Naming**: Use descriptive class names that indicate purpose

### Example Approach
```css
/* Wrong: Specific ID targeting */
#editBtnDynamic { margin: 10px; }

/* Right: Categorical with framework override */
.btn i.me-1 { margin-right: 10px !important; }
```

## MLX Chat Specific CSS Issues

### Message Bubble Inheritance Problem
**Issue**: Buttons inside `.message-bubble` containers inherit different CSS context that can override global button styles.

**Solution**: Move problematic UI elements outside message bubbles when possible:
```javascript
// Wrong: Inside message bubble
optionsDiv.className = 'message-bubble assistant-message';

// Right: Outside message bubble  
optionsDiv.className = 'text-center my-3';
```

### Bootstrap Framework Conflicts
**Issue**: `custom-framework.css` loads after `magma-theme.css` and has `!important` rules that override our styles.

**Common Conflicts**:
- `.me-1 { margin-right: 0.25rem !important; }` - Overrides icon spacing
- `.me-2 { margin-right: 0.5rem !important; }` - Overrides icon spacing

**Solution**: Use higher specificity selectors:
```css
/* Higher specificity to override framework */
.btn i.bi.me-1, button i.bi.me-1 {
    margin-right: 10px !important;
}
```

### Dynamic Content CSS Application
**Issue**: Dynamically created elements may not inherit CSS properly or may be created after CSS loads.

**Troubleshooting**:
1. Check if CSS rules apply to static elements first
2. Use browser DevTools to verify dynamic elements have correct classes
3. Consider if timing issues prevent CSS application

### CSS Cache Issues
**Issue**: Browser caching can prevent CSS changes from appearing.

**Solutions**:
1. Update cache-busting parameter: `?v=X` in CSS link
2. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
3. Test in incognito/private window
4. Check if CSS file is actually being served with updated content

## Core Design Philosophy
**ALL interfaces in the MLX project use dark mode with dark backgrounds**

## Color Hierarchy (from magma-theme.css)
- **Primary Background**: `--obsidian-black` (#0a0a0a) - Body/page background
- **Secondary Background**: `--deep-charcoal` (#1a1a1a) - Main containers
- **Tertiary Background**: `--volcanic-ash` (#2a2a2a) - Content areas, cards
- **Text Color**: `--smoke-white` (#f5f5f5) - Primary text
- **Secondary Text**: `--ash-gray` (#4a4a4a) - Muted text

## Magma Accent Colors
- **Primary Accent**: `--molten-orange` (#ff6b35)
- **Secondary Accent**: `--ember-red` (#ff4500) 
- **Tertiary Accent**: `--lava-yellow` (#ffaa44)
- **Supporting**: `--warm-amber` (#ff8c42)
- **Subtle**: `--copper-glow` (#d2691e)

## Design Consistency Rules
1. **Never use light backgrounds** - all components must use dark theme
2. **Reference CSS variables** - always use `var(--color-name)` not hex codes
3. **Maintain hierarchy** - obsidian → charcoal → volcanic ash progression
4. **Magma accents only** - use magma colors for highlights and interactions
5. **Smoke white text** - primary text should always be readable on dark backgrounds
6. **Bootstrap Icons only** - use Bootstrap Icons instead of emoji or other icon sets
7. **NO EMOJI EVER** - Emoji are prohibited in all interfaces, use Bootstrap Icons instead
8. **NO DUPLICATE FILES** - Never create versioned files (file_v2.py, file_enhanced.py) - overwrite originals

## Version Control Standards
- **Single source files**: One canonical version of each file
- **Overwrite, don't duplicate**: Update existing files instead of creating new versions
- **No appended names**: Never use suffixes like `_enhanced`, `_v2`, `_new`, `_final`
- **Clean project structure**: Remove all duplicate/versioned files before commits
- **Future GitHub integration**: Proper version control will handle history

## Training Data Standards
- **Dual approach**: Support both vocabulary and style training data extraction
- **MLX compatibility**: All training data uses `{"text": "content"}` format
- **File naming**: `vocabulary_training.jsonl` and `style_training.jsonl`
- **Token limits**: Vocabulary contexts ≤6 tokens, style chunks ≤1500 characters
- **Quality controls**: Minimum lengths, POS-aware allocation, sentence boundaries
- **User choice**: Allow selection of vocabulary, style, or both training types

## Icon Standards
- **Use Bootstrap Icons CDN**: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css`
- **Automatic spacing**: All `.bi` icons have 10px right margin via CSS
- **No manual spacing needed**: CSS handles consistent icon spacing globally
- **Common icons used in project**:
  - Charts/Analytics: `bi-bar-chart-fill`, `bi-graph-up`, `bi-pie-chart-fill`
  - Interaction: `bi-cursor-fill`, `bi-hand-index`, `bi-mouse`
  - Data: `bi-file-text`, `bi-collection`, `bi-grid`
  - Actions: `bi-play-fill`, `bi-stop-fill`, `bi-refresh`
- **NO EMOJI**: Emoji are strictly forbidden - always use Bootstrap Icons

## Component Standards
- **Containers**: `--deep-charcoal` background with rounded corners
- **Content Areas**: `--volcanic-ash` background for distinction
- **Interactive Elements**: Magma colors with hover effects
- **Text**: `--smoke-white` for primary, `--ash-gray` for secondary
- **Shadows**: Dark shadows with higher opacity for depth

## Applications
- **MLX Chat Interface**: Full dark mode implementation
- **Word Cloud Visualizations**: Dark containers with magma-colored words
- **All Future Components**: Must follow these dark mode standards

This ensures visual consistency across the entire MLX project ecosystem.
