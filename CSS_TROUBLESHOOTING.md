# MLX Chat CSS Troubleshooting Guide

## Quick Diagnostic Checklist

### 1. CSS Not Loading
**Symptoms**: No visual changes despite CSS modifications
**Diagnosis**:
```css
/* Add test rule to verify CSS loading */
.btn { background: red !important; }
```
**Solutions**:
- Update cache-busting parameter: `?v=X` in HTML template
- Restart Flask server: `pkill -f "web_chat.py" && python web_chat.py &`
- Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)

### 2. CSS Loading But Not Applying
**Symptoms**: CSS file shows updated rules but elements unchanged
**Diagnosis**: Check browser DevTools computed styles
**Common Causes**:
- Framework override (custom-framework.css has `!important` rules)
- Insufficient specificity
- Wrong selector targeting

### 3. Dynamic Elements Not Styled
**Symptoms**: Static elements styled correctly, dynamic elements unchanged
**Root Cause**: Elements created by JavaScript after CSS loads
**Solution**: Target parent containers or use higher specificity

## MLX Chat Specific Issues

### Message Bubble CSS Inheritance
**Problem**: Buttons inside `.message-bubble` containers don't follow global button styles
**File**: `templates/chat.html` - `showEditOptions()` function
**Solution**: Move UI elements outside message bubbles
```javascript
// Wrong
optionsDiv.className = 'message-bubble assistant-message';

// Right  
optionsDiv.className = 'text-center my-3';
```

### Bootstrap Framework Conflicts
**File**: `static/css/custom-framework.css`
**Problem Classes**:
- `.me-1 { margin-right: 0.25rem !important; }`
- `.me-2 { margin-right: 0.5rem !important; }`

**Override Strategy**:
```css
/* Higher specificity wins */
.btn i.bi.me-1, button i.bi.me-1 {
    margin-right: 10px !important;
}
```

### Icon Spacing Issues
**Common Pattern**: `<i class="bi bi-icon me-1"></i>Text` with no space
**Problem**: Bootstrap `me-1` class overridden by framework
**Solutions**:
1. **CSS Override**: Target with higher specificity
2. **HTML Fix**: Add space in template: `<i class="bi bi-icon"></i> Text`
3. **Move Outside Bubble**: Change container context

### CSS Load Order
**Current Order** (in `templates/chat.html`):
1. Bootstrap Icons CSS
2. `custom-framework.css` (has `!important` rules)
3. `magma-theme.css` (our custom styles)

**Implication**: Our styles load last but framework uses `!important`
**Solution**: Use higher specificity rather than more `!important` rules

## Debugging Workflow

### Step 1: Verify CSS Loading
```css
/* Add to magma-theme.css */
body { border: 5px solid red !important; }
```
If no red border appears, CSS isn't loading.

### Step 2: Test Element Targeting
```css
/* Target specific problematic element */
#editBtnDynamic { background: yellow !important; }
```
If element doesn't turn yellow, selector is wrong.

### Step 3: Check Framework Conflicts
Search `custom-framework.css` for conflicting classes:
```bash
grep -n "me-1\|me-2" static/css/custom-framework.css
```

### Step 4: Inspect Computed Styles
1. Right-click element → Inspect
2. Check "Computed" tab in DevTools
3. Look for overridden styles (crossed out)

## File Locations

### CSS Files
- **Main Styles**: `static/css/magma-theme.css`
- **Framework**: `static/css/custom-framework.css` (loads first, has `!important`)
- **Template**: `templates/chat.html` (contains CSS links and cache-busting)

### Dynamic Content Creation
- **Edit/Regenerate Buttons**: `templates/chat.html` - `showEditOptions()` function
- **Continue Button**: `templates/chat.html` - `addContinueButton()` function

### Server Management
- **Start**: `python web_chat.py &`
- **Stop**: `pkill -f "web_chat.py"`
- **Check**: `ps aux | grep "web_chat.py"`

## Common Solutions

### Button Icon Spacing
```css
/* Universal fix for Bootstrap icon spacing */
.btn i.bi.me-1, button i.bi.me-1 {
    margin-right: 10px !important;
}
```

### Dynamic Button Styling
```css
/* Target specific dynamic buttons */
#editBtnDynamic i, #regenerateBtnDynamic i {
    margin-right: 10px !important;
}
```

### Message Bubble Context Issues
Move problematic elements outside bubbles:
```javascript
// Change container class
optionsDiv.className = 'text-center my-3'; // Instead of 'message-bubble'
```

## Prevention Guidelines

1. **Test Static Elements First**: Verify CSS works on non-dynamic content
2. **Use Browser DevTools**: Always inspect computed styles
3. **Check Framework Files**: Look for conflicting `!important` rules
4. **Restart Server**: After template changes, restart Flask server
5. **Update Cache-Busting**: Increment `?v=X` parameter after CSS changes
6. **Document Context Issues**: Note when elements need specific container contexts
