# Jig Cycle Count Display Fix

## Issue
After unloading a jig and reusing it, the cycle count was not incrementing correctly:
- First unload: showed Cycle 1 ✓
- Second unload: showed Cycle 1 ✗ (should show Cycle 2)

## Root Cause
The `get_next_jig_cycle()` function in `Jig_Loading/views.py` was calculating cycle count based on JigCompleted records instead of reading the `cycle_count` field from the Jig model.

**Old Logic (WRONG):**
```python
submitted_count = JigCompleted.objects.filter(
    jig_id=jig_id,
    lot_id=lot_id,
    draft_status='submitted'
).count()
next_cycle = submitted_count + 1
```

This calculated cycles PER (jig_id, lot_id) pair, not per jig globally.

## Solution Implemented
Updated `get_next_jig_cycle()` to read cycle_count directly from the Jig model (SSOT):

```python
# ✅ Read cycle_count directly from Jig model (SSOT)
# cycle_count is incremented automatically during unloading
# Display cycle_count + 1 to show "next cycle" for new loading
current_cycle_count = jig_obj.cycle_count if jig_obj.cycle_count is not None else 0
next_cycle = current_cycle_count + 1
```

## Cycle Count Architecture

### Database Field (SSOT)
- **Jig.cycle_count** (Integer, default=0)
- Represents number of COMPLETED loading-unloading cycles
- Incremented atomically during unloading using `F('cycle_count') + 1`

### Unloading Logic (Auto-Increment)

**Zone 1** (`Jig_Unloading/views.py` - SubmitAllUnloadZ1View):
```python
Jig.objects.filter(jig_qr_id=jig_qr_id).update(
    is_loaded=False,
    occupied_flag=False,
    cycle_count=F('cycle_count') + 1,  # Atomic increment
    ...
)
```

**Zone 2** (`JigUnloading_Zone2/views.py` - JU_Zone_save_jig_unload_tray_ids):
```python
released_jigs.update(
    is_loaded=False,
    occupied_flag=False,
    cycle_count=F('cycle_count') + 1  # Atomic increment
)
```

### Loading Logic (Display Only)
- Loading does NOT modify cycle_count
- Reads cycle_count and displays as "next cycle number"
- Calculation: `next_cycle = current_cycle_count + 1`

### Display Logic

**Backend (Jig_Loading/views.py - JigValidateAPI):**
```python
current_cycle_count = jig_obj.cycle_count or 0
next_cycle = current_cycle_count + 1  # +1 for display
return {'cycle_count': next_cycle}
```

**Frontend (Jig_Picktable.html line 7153):**
```javascript
cycleEl.textContent = d.cycle_count || 1;
```

## Cycle Count Flow Example

### First Load-Unload Cycle
1. **New Jig**: cycle_count = 0
2. **Load Jig**: Backend sends next_cycle = 0 + 1 = 1 → Displays "Cycle 1" ✓
3. **Unload Jig**: cycle_count becomes 1 (via F() + 1)

### Second Load-Unload Cycle
1. **Jig State**: cycle_count = 1
2. **Load Jig**: Backend sends next_cycle = 1 + 1 = 2 → Displays "Cycle 2" ✓
3. **Unload Jig**: cycle_count becomes 2

### Third Load-Unload Cycle
1. **Jig State**: cycle_count = 2
2. **Load Jig**: Backend sends next_cycle = 2 + 1 = 3 → Displays "Cycle 3" ✓
3. **Unload Jig**: cycle_count becomes 3

## Key Principles

### Single Source of Truth (SSOT)
- **Jig.cycle_count** is the ONLY authoritative source for cycle tracking
- Do NOT calculate cycles from JigCompleted, JigLoadingRecord, or any other table
- All cycle count displays must read from Jig.cycle_count

### Atomic Operations
- Use F() expressions for thread-safe increments
- Prevents race conditions in concurrent unloading operations

### Display Convention
- Database stores **completed cycles** (0, 1, 2, ...)
- UI displays **next cycle number** (1, 2, 3, ...)
- Formula: displayed_cycle = db_cycle_count + 1

### Global Tracking
- Cycle count is per Jig ID (global)
- Not per (jig_id, lot_id) pair
- Tracks total reuse count across all lots

## Files Modified
- **Jig_Loading/views.py** (line ~2287-2303)
  - Updated `get_next_jig_cycle()` function
  - Now reads from `jig_obj.cycle_count` instead of counting JigCompleted records

## Files Previously Modified (Already Correct)
- **Jig_Loading/models.py** - Added cycle_count field
- **Jig_Unloading/views.py** - Auto-increment on Zone 1 unload
- **JigUnloading_Zone2/views.py** - Auto-increment on Zone 2 unload
- **Jig_Picktable.html** - Frontend display logic

## Testing Checklist
- [x] New jig shows "Cycle 1" on first load
- [ ] After first unload, same jig shows "Cycle 2" on reload
- [ ] After second unload, same jig shows "Cycle 3" on reload
- [ ] Cycle count persists across different lots
- [ ] Concurrent unloads don't corrupt cycle_count
- [ ] Null/0 cycle_count defaults to "Cycle 1" display

## Date
May 14, 2026
