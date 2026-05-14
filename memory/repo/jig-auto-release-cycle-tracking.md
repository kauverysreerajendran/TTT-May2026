# Jig ID Auto-Release and Cycle Tracking

## Overview
Implemented automatic Jig ID release functionality that frees jigs after unloading and tracks usage cycles.

## Problem Statement
Previously, when a Jig ID was loaded in the Jig Loading module and then unloaded via Submit All button (Zone 1 or Zone 2), the jig was not automatically marked as free and available for the next usage cycle.

## Solution Implemented

### 1. Database Schema Changes
**File**: `Jig_Loading/models.py`

Added two new fields to the `Jig` model:
- `occupied_flag` (BooleanField, default=False) - Indicates if jig is currently occupied/in-use
- `cycle_count` (IntegerField, default=0) - Tracks number of completed loading-unloading cycles

### 2. Migration Created
**Migration**: `Jig_Loading/migrations/0013_add_jig_occupied_flag_and_cycle_count.py`
- Successfully applied to database
- Adds both new fields with proper defaults

### 3. Jig Loading Updates
**File**: `Jig_Loading/views.py`

When jig is loaded (submit action):
```python
jig_obj.is_loaded = True
jig_obj.occupied_flag = True  # NEW: Mark as occupied
```

When jig is drafted:
```python
Jig.objects.filter(jig_qr_id=jig_id).update(
    drafted=True,
    occupied_flag=True,  # NEW: Mark as occupied even in draft state
    ...
)
```

### 4. Zone 1 Unloading Auto-Release
**File**: `Jig_Unloading/views.py` - `SubmitAllUnloadZ1View`

When Submit All is clicked in Zone 1:
```python
from django.db.models import F
Jig.objects.filter(jig_qr_id=jig_qr_id).update(
    is_loaded=False,
    occupied_flag=False,        # NEW: Mark as free
    current_user=None,
    locked_at=None,
    drafted=False,
    batch_id=None,
    lot_id=None,
    cycle_count=F('cycle_count') + 1,  # NEW: Increment cycle count
)
```

Also handles merged jigs (when Add Model creates multiple jigs):
```python
Jig.objects.filter(jig_qr_id=m_jig_qr).update(
    is_loaded=False, 
    occupied_flag=False,                    # NEW: Mark as free
    cycle_count=F('cycle_count') + 1,       # NEW: Increment cycle count
    ...
)
```

### 5. Zone 2 Unloading Auto-Release
**File**: `JigUnloading_Zone2/views.py` - `JU_Zone_save_jig_unload_tray_ids`

When trays are saved/submitted in Zone 2:
```python
from django.db.models import F
released_jigs.update(
    is_loaded=False,
    occupied_flag=False,                # NEW: Mark as free
    cycle_count=F('cycle_count') + 1    # NEW: Increment cycle count
)
```

Enhanced logging:
```python
for jig in released_jigs:
    jig.refresh_from_db()  # Get updated cycle_count
    print(f"Jig ID {jig.id} - QR: '{jig.jig_qr_id}' is now available for reuse (Cycle: {jig.cycle_count})")
```

## Business Logic Flow

### Loading Phase (Jig Loading Module)
1. User scans/selects Jig ID
2. User loads trays and submits OR saves as draft
3. System sets: `is_loaded=True`, `occupied_flag=True`
4. Jig is now marked as occupied and in-use

### Unloading Phase (Zone 1 or Zone 2)
1. User completes unloading via Submit All button
2. System automatically:
   - Sets `is_loaded=False`
   - Sets `occupied_flag=False` (marks jig as FREE)
   - Increments `cycle_count` by 1
   - Clears `current_user`, `locked_at`, `drafted`, `batch_id`, `lot_id`
3. Jig is now available for next usage in sequence/order
4. Cycle count provides usage tracking/history

## Key Benefits

1. **Automatic Release**: No manual intervention needed to free jigs after unloading
2. **Cycle Tracking**: Each unload automatically increments cycle count for maintenance planning
3. **Cross-Zone Support**: Works identically in both Zone 1 (IPS) and Zone 2 (Dull/SemiBright/Bright)
4. **Data Consistency**: Uses Django's F() expression to prevent race conditions in cycle count increment
5. **Audit Trail**: Cycle count provides historical usage data for each jig

## Technical Notes

- Uses Django's `F('cycle_count') + 1` for atomic increment (prevents race conditions)
- Handles both single-jig and multi-jig (merged) scenarios
- Logging added to track jig release operations for debugging
- Maintains backward compatibility with existing jig tracking
- occupied_flag provides redundant safety check alongside is_loaded

## Testing Checklist

- [ ] Load jig in Jig Loading module - verify occupied_flag=True
- [ ] Submit from Zone 1 - verify occupied_flag=False, cycle_count incremented
- [ ] Submit from Zone 2 - verify occupied_flag=False, cycle_count incremented
- [ ] Save as draft - verify occupied_flag=True
- [ ] Multi-model merged jigs - verify all jigs released properly
- [ ] Check cycle_count increments correctly over multiple cycles
- [ ] Verify jig shows as available in pick table after unload

## Related Files Modified

1. `Jig_Loading/models.py` - Added occupied_flag and cycle_count fields
2. `Jig_Loading/views.py` - Set occupied_flag=True on load/draft
3. `Jig_Unloading/views.py` - Auto-release logic for Zone 1
4. `JigUnloading_Zone2/views.py` - Auto-release logic for Zone 2
5. `Jig_Loading/migrations/0013_add_jig_occupied_flag_and_cycle_count.py` - Database migration

## Date
May 14, 2026
