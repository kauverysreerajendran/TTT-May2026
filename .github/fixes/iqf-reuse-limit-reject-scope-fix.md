# IQF Reuse Limit Scope Fix — Reject Section Blocked by Accept Validation

**Date**: May 4, 2026  
**Module**: IQF Audit → Tray Allocation  
**Issue Type**: Frontend Validation Scope Leak  
**Severity**: High (blocks normal workflow)

---

## 01 — Problem Statement

### Issue
After completing **Accept section** tray scanning (4 reusable trays used), when user taps **existing trays in Reject section**, system incorrectly throws:

```
❌ Exceeded reusable tray limit (4). Scan a new tray for remaining accept slots.
```

### User Flow (Broken)
```
1. Accept section: Scan 4 trays (reusable limit = 4)
   ✅ JB-A00031 → 4
   ✅ JB-A00032 → 12
   ✅ JB-A00033 → 12
   ✅ JB-A00034 → 12
   Total Accepted = 40

2. Cursor moves to Reject section
3. User taps existing tray in "Existing Trays - Tap to Use"
   ❌ ERROR: "Exceeded reusable tray limit (4)"
   
4. Expected: Tray should auto-fill Reject slot (no limit check)
```

---

## 02 — Root Cause

**File**: `Iqf_PickTable.html`  
**Function**: `window._iqfTapToFillTray` (starting line ~3827)  

### Problem Code (Before Fix)
```javascript
window._iqfTapToFillTray = function(card){
  var trayId = card.getAttribute('data-tray-id');
  var qty = parseInt(card.getAttribute('data-qty')) || 0;
  var isTopTray = card.getAttribute('data-is-top-tray') === 'true';
  var trayCapacity = parseInt(card.getAttribute('data-tray-capacity')) || 0;
  
  // ❌ PROBLEM: Reuse limit checked FIRST (before determining target section)
  var _tapMaxReuse = window._maxReuseLimit || 0;
  if(_tapMaxReuse > 0){
    var _tapUsedCount = document.querySelectorAll('.iqf-existing-tray-card.iqf-tray-used').length;
    if(_tapUsedCount >= _tapMaxReuse){
      // ❌ Blocks ALL taps (including Reject) when Accept limit reached
      _reuseErrEl.innerHTML = '... Exceeded reusable tray limit ...';
      return; // ← Early exit prevents Reject tray selection
    }
  }

  // Check if already used
  if(card.classList.contains('iqf-tray-used')){ ... }
  
  // Find target slot (Accept OR Reject)
  var allInputs = document.querySelectorAll('#iqf-accepted-tray-slots-body .tray-scan-input');
  var targetInput = null;
  
  for(var i = 0; i < allInputs.length; i++){
    if(!allInputs[i].value.trim()){ targetInput = allInputs[i]; break; }
  }
  
  if(!targetInput){
    // Redirect to Reject slot when Accept full
    var _rejInputs = document.querySelectorAll('#iqf-reject-tbody .rej-scan-input');
    // ❌ Never reaches here due to early return above
  }
}
```

### Logic Flaw
```
Current Flow (Wrong):
┌─────────────────────────────────────────┐
│ 1. Check reuse limit (max 4)           │ ❌ Applied globally
│    If exceeded → STOP (return)          │
├─────────────────────────────────────────┤
│ 2. Check if tray already used           │
├─────────────────────────────────────────┤
│ 3. Find target slot:                    │
│    • Accept slots first                 │ ← Never evaluated when limit hit
│    • Fallback to Reject if Accept full  │
├─────────────────────────────────────────┤
│ 4. Fill the slot                        │
└─────────────────────────────────────────┘

Problem: Step 1 blocks Reject before Step 3 determines target section.
```

---

## 03 — Solution

### Architecture Principle
**Accept reusable limit (max 4 trays) applies ONLY to Accept section.**  
**Reject section has NO reusable limit restriction.**

### Correct Flow
```
Fixed Flow (Correct):
┌─────────────────────────────────────────┐
│ 1. Check if tray already used           │
├─────────────────────────────────────────┤
│ 2. Find target slot:                    │
│    • Accept slots first                 │
│    • Fallback to Reject if Accept full  │
├─────────────────────────────────────────┤
│ 3. IF target is Accept slot:            │ ✅ Scoped validation
│      → Check reuse limit                │
│      → If exceeded, show error & stop   │
│                                         │
│    IF target is Reject slot:            │ ✅ No limit check
│      → Skip reuse limit check           │
│      → Allow any existing tray          │
├─────────────────────────────────────────┤
│ 4. Fill the slot                        │
└─────────────────────────────────────────┘
```

---

## 04 — Code Fix

**File**: `static/templates/IQF/Iqf_PickTable.html`  
**Function**: `window._iqfTapToFillTray`  
**Lines**: ~3827-3890

### Changes Made

#### BEFORE (Wrong)
```javascript
window._iqfTapToFillTray = function(card){
  // ... extract tray data ...
  
  // ❌ Check reuse limit BEFORE determining target section
  var _tapMaxReuse = window._maxReuseLimit || 0;
  if(_tapMaxReuse > 0){
    var _tapUsedCount = document.querySelectorAll('.iqf-existing-tray-card.iqf-tray-used').length;
    if(_tapUsedCount >= _tapMaxReuse){
      _reuseErrEl.innerHTML = '... Exceeded reusable tray limit ...';
      return; // ← Blocks Reject too
    }
  }

  // Check if already used
  if(card.classList.contains('iqf-tray-used')){ return; }
  
  // Find target slot (Accept first, Reject fallback)
  var allInputs = document.querySelectorAll('#iqf-accepted-tray-slots-body .tray-scan-input');
  var targetInput = null;
  for(var i = 0; i < allInputs.length; i++){
    if(!allInputs[i].value.trim()){ targetInput = allInputs[i]; break; }
  }
  
  if(!targetInput){
    // Redirect to Reject
    var _rejInputs = document.querySelectorAll('#iqf-reject-tbody .rej-scan-input');
    // ... fill reject input ...
  }
  
  // Fill Accept slot
  // ...
}
```

#### AFTER (Fixed)
```javascript
window._iqfTapToFillTray = function(card){
  // ... extract tray data ...

  // ✅ Step 1: Check if already used
  if(card.classList.contains('iqf-tray-used')){ return; }
  
  // ✅ Step 2: Find target slot (Accept first, Reject fallback)
  var allInputs = document.querySelectorAll('#iqf-accepted-tray-slots-body .tray-scan-input');
  var targetInput = null;
  for(var i = 0; i < allInputs.length; i++){
    if(!allInputs[i].value.trim()){ targetInput = allInputs[i]; break; }
  }
  
  if(!targetInput){
    // ✅ Accept full → redirect to Reject (NO REUSE LIMIT CHECK)
    var _rejInputs = document.querySelectorAll('#iqf-reject-tbody .rej-scan-input');
    var _targetRejInput = null;
    for(var _ri = 0; _ri < _rejInputs.length; _ri++){
      if(!_rejInputs[_ri].value.trim() && !_rejInputs[_ri].classList.contains('rej-scan-valid')){
        _targetRejInput = _rejInputs[_ri]; break;
      }
    }
    if(_targetRejInput){
      _targetRejInput.value = trayId.toUpperCase();
      _targetRejInput.dispatchEvent(new Event('input', { bubbles: true }));
      return; // ✅ Filled Reject slot, done
    }
    // All reject slots also full
    Swal.fire({ icon: 'info', title: 'All Slots Filled', ... });
    return;
  }
  
  // ✅ Step 3: ONLY for Accept slot → check reuse limit
  var _tapMaxReuse = window._maxReuseLimit || 0;
  if(_tapMaxReuse > 0){
    var _tapUsedCount = document.querySelectorAll('.iqf-existing-tray-card.iqf-tray-used').length;
    if(_tapUsedCount >= _tapMaxReuse){
      // ✅ Show error ONLY when filling Accept slot
      var _reuseErrEl = document.getElementById('iqf-reuse-error');
      if(_reuseErrEl){
        _reuseErrEl.innerHTML = '... Exceeded reusable tray limit ...';
        _reuseErrEl.style.display = 'block';
        setTimeout(function(){ _reuseErrEl.style.display = 'none'; }, 3000);
      }
      return; // ✅ Block Accept, but Reject already handled above
    }
  }
  
  // ✅ Step 4: Fill Accept slot (reuse limit OK)
  targetInput.value = trayId.toUpperCase();
  // ... rest of accept slot fill logic ...
}
```

---

## 05 — Validation Flow Chart

### Before Fix (Broken)
```
User taps existing tray
       ↓
Check reuse limit (4/4 used)
       ↓
   [BLOCKED] ❌ (even for Reject)
       ↓
   Error shown
```

### After Fix (Correct)
```
User taps existing tray
       ↓
Check if already used?
  │   No
  ↓
Find target slot
  ├─ Accept slot empty?
  │     Yes → Check reuse limit
  │             ├─ OK → Fill Accept slot ✅
  │             └─ Exceeded → Show error ❌
  │
  └─ Accept full?
        Yes → Find Reject slot
                ├─ Empty → Fill Reject slot ✅ (no limit check)
                └─ Full → Show "all slots filled" ℹ️
```

---

## 06 — Edge Cases Tested

### Scenario 1: Normal Flow (Accept → Reject)
```
1. Accept: 4 trays scanned (limit reached)
2. Tap existing tray → ✅ Auto-fills Reject slot
3. No error shown
```

### Scenario 2: Accept Limit Not Reached
```
1. Accept: 2 trays scanned (limit = 4)
2. Tap existing tray → ✅ Auto-fills Accept slot
3. Reuse badge: "Reusable: 3/4"
```

### Scenario 3: Accept Limit Reached + New Tray Needed
```
1. Accept: 4 trays scanned (all reusable slots used)
2. Accept: 2 more empty slots (need new trays)
3. Tap existing tray → ❌ Error: "Exceeded reusable limit, scan new tray"
4. Scan new tray → ✅ Fills remaining Accept slots
```

### Scenario 4: Partial Accept
```
1. Accept: 40 qty allocated to 4 trays
2. Reject: 10 qty needs 1 tray
3. Tap existing tray after Accept complete → ✅ Fills Reject slot
```

### Scenario 5: Full Reject
```
1. Accept: 0 qty (full rejection)
2. Reject: All qty in reject section
3. Tap existing tray → ✅ Fills Reject slot (no Accept validation applied)
```

---

## 07 — Regression Prevention

### Rules Enforced
```
✅ Accept Section:
   - Reusable tray limit = max(0, total_tray_count - trays_needed)
   - Backend calculates limit based on capacity
   - Frontend enforces limit only when filling Accept slots
   
✅ Reject Section:
   - No reusable limit check
   - Any existing tray can be selected
   - Validation: no duplicates with Accept, no duplicates within Reject
   
✅ Delink Section:
   - Auto-allocates leftover trays AFTER Accept + Reject complete
   - Not affected by reusable limit
```

### What Did NOT Change
```
❌ Backend logic (views.py)
❌ Reusable limit calculation
❌ Accept section limit enforcement (still max 4 when calculated)
❌ Reject tray allocation rules
❌ Delink logic
❌ Existing tray card rendering
```

---

## 08 — Testing Checklist

### Manual Test Steps
1. ✅ Open IQF Audit modal for lot with 50 qty (40 Accept, 10 Reject)
2. ✅ Scan 4 Accept trays (reusable limit reached)
3. ✅ Verify reusable badge shows "Reusable: 4/4"
4. ✅ Tap existing tray → Should fill Reject slot (not blocked)
5. ✅ Verify no error about exceeded limit
6. ✅ Complete Accept with new trays if needed
7. ✅ Complete Reject scanning
8. ✅ Verify Delink section auto-allocates remaining trays
9. ✅ Submit lot → Verify backend processes correctly

### Automation Test Cases (Future)
```javascript
test('IQF_TapToFill_RejectAfterAcceptFull', () => {
  // 1. Fill all Accept slots (reuse limit reached)
  fillAcceptSlots({ reuseCount: 4 });
  
  // 2. Tap existing tray
  const existingCard = getExistingTrayCard('JB-A00035');
  tapToFillTray(existingCard);
  
  // 3. Verify no error, Reject slot filled
  expect(getReuseError()).not.toBeVisible();
  expect(getRejectSlot(1).value).toBe('JB-A00035');
});
```

---

## 09 — Impact Assessment

### Components Changed
- ✅ `Iqf_PickTable.html` — `_iqfTapToFillTray` function (validation scope fix)

### Components NOT Changed
- ❌ Backend APIs (`views.py`, `services.py`)
- ❌ Accept slot rendering logic
- ❌ Reject slot rendering logic
- ❌ Delink computation logic
- ❌ Reusable limit calculation

### Risk Level
**Low** — Isolated frontend validation scope fix, no backend changes.

---

## 10 — Conclusion

### Fix Summary
**Moved reusable tray limit validation from global scope to Accept-only scope.**

### Before
```
✅ Reuse limit checked for ALL taps
❌ Blocked Reject tray selection after Accept limit reached
```

### After
```
✅ Reuse limit checked ONLY when filling Accept slots
✅ Reject section bypasses reuse limit check
✅ Maintains Accept limit enforcement (max 4 reusable)
✅ User can freely tap existing trays for Reject after Accept complete
```

### Validation Principle
```
Frontend displays. Backend decides.
Accept has reusable limit. Reject does not.
Validation scope must match business rule scope.
```

---

**Status**: ✅ Fixed  
**Verified By**: Senior Frontend + Backend Developer  
**Approval**: Pending QA Testing
