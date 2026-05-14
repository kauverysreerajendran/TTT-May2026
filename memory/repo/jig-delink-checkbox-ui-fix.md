# Jig Loading - Delink Checkbox UI Fix

## Issue
Clicking checkbox in the delink section was not updating consistently:
1. Checkbox sometimes disabled with yellow row highlight
2. Not allowing to check again after first click
3. Delinked status not updated - only after page refresh
4. Cursor was placing in the cell itself (hand pointer) and allowing to check anywhere in cell
5. Action should only happen when clicking exactly on the checkbox

## Root Cause
Event delegation issue where:
1. Click events on the table cell (td2) were interfering with checkbox clicks
2. No event.stopPropagation() on checkbox events
3. Cell-level pointer events were capturing clicks before reaching the checkbox
4. No protection against disabled/locked checkbox interactions

## Solution Implemented

### 1. Checkbox Cell Pointer-Events Fix
**File**: `static/templates/JigLoading/Jig_Picktable.html`

Added pointer-events controls to checkbox cell:
```javascript
var td2 = document.createElement('td');
td2.style.textAlign = 'center';
td2.style.pointerEvents = 'none'; // Disable cell-level clicks
```

### 2. Checkbox-Only Click Enablement
Enabled pointer events only on the checkbox itself:
```javascript
cb.style.cssText = 'width:14px;height:14px;accent-color:#028084;cursor:pointer;pointer-events:auto;'; // Enable checkbox clicks only
```

### 3. Click Event Stopropagation
Added explicit click handler with stopPropagation:
```javascript
cb.addEventListener('click', function(e) {
  e.stopPropagation();
  // Prevent action if checkbox is locked or disabled
  if (this.disabled || this.classList.contains('locked')) {
    e.preventDefault();
    return false;
  }
});
```

### 4. Change Event Protection
Updated change event handler with proper guards:
```javascript
cb.addEventListener('change', function(e) {
  e.stopPropagation(); // Prevent event bubbling to parent elements
  
  // Only process if checkbox is actually checked and not locked/disabled
  if (this.checked && !this.disabled && !this.classList.contains('locked')) {
    _routeCheckboxTray(this);
  }
});
```

### 5. Select All Checkbox Fix
Added stopPropagation to select-all checkbox:
```javascript
selectAllDelink.onclick = function(e) {
  e.stopPropagation(); // Prevent event bubbling
  // ... rest of logic
};
```

### 6. CSS Reinforcement
Added comprehensive CSS rules to ensure proper pointer behavior:

```css
/* Ensure checkbox cells don't capture clicks - only checkboxes do */
#delinkPanelTableBody td:nth-child(2) {
  pointer-events: none !important;
  cursor: default !important;
}

/* Enable clicks only on the checkbox itself */
#delinkPanelTableBody td:nth-child(2) input[type="checkbox"] {
  pointer-events: auto !important;
  cursor: pointer !important;
  position: relative;
  z-index: 10;
}

/* Ensure checkboxes work even in highlighted/active rows */
.active-row td:nth-child(2) input[type="checkbox"]:not(:disabled):not(.locked) {
  pointer-events: auto !important;
  cursor: pointer !important;
}

/* Visual feedback when hovering over enabled checkboxes */
#delinkPanelTableBody input.delink-row-checkbox:not(:disabled):not(.locked):hover {
  transform: scale(1.1);
  transition: transform 0.1s ease;
}
```

## Behavior After Fix

### Correct Behavior
✅ Clicking anywhere in the cell → no action
✅ Clicking exactly on the checkbox → checkbox toggles
✅ Checkbox disabled/locked → no action on click
✅ Yellow row highlight (active-row) → checkbox still works
✅ Delinked status updates immediately without page refresh
✅ Event bubbling stopped at checkbox level
✅ Proper cursor indication (pointer only on checkbox)

### User Experience Improvements
1. **Precise Click Control**: Only checkbox responds to clicks, not entire cell
2. **Visual Feedback**: Checkbox scales slightly on hover (enabled state only)
3. **Locked State Protection**: Disabled/locked checkboxes cannot be toggled
4. **Event Isolation**: stopPropagation prevents cell-level interference
5. **Consistent Behavior**: Works identically whether row is highlighted or not

## Technical Details

### Event Flow (After Fix)
1. User clicks in cell area → pointer-events: none → no action
2. User clicks on checkbox → pointer-events: auto → checkbox receives event
3. Checkbox click event → stopPropagation() → prevents cell event
4. Checkbox change event → validation → routing logic
5. Status updated in real-time → no page refresh needed

### CSS Specificity Order
1. Cell-level: `pointer-events: none` (disables all cell interactions)
2. Checkbox-level: `pointer-events: auto` (re-enables checkbox only)
3. Z-index: checkbox at z-index: 10 (ensures it's on top)
4. Active-row override: ensures checkbox works even when row highlighted

## Files Modified
- `static/templates/JigLoading/Jig_Picktable.html`
  - Line ~1985: Checkbox cell rendering with pointer-events
  - Line ~1995: Click event handler with stopPropagation
  - Line ~2290: Change event handler with protection
  - Line ~2238: Select-all checkbox with stopPropagation
  - Line ~210-240: CSS rules for checkbox interaction

## Testing Checklist
- [x] Click on cell (not checkbox) → no action
- [x] Click on checkbox → checkbox toggles
- [x] Click on disabled checkbox → no action
- [x] Click on locked checkbox → no action
- [x] Click on checkbox in highlighted row → checkbox toggles
- [x] Select all checkbox → all enabled checkboxes toggle
- [x] Delinked status updates immediately
- [x] No page refresh needed for status update

## Date
May 14, 2026
