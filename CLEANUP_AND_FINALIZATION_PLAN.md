# Prometheus Cleanup and Finalization Plan

## Problem Analysis

### Current State
- **Two Workspaces**: 
  - `PROMETHEUS-Trading-Platform` (Primary - has official HRM)
  - `PROMETHEUS-Enterprise-Package-COMPLETE` (Enterprise features)
- **41 Launch Files** in Trading Platform (many duplicates/archived)
- **5 Launch Files** in Enterprise Package
- **17 .env Files** scattered across both workspaces
- **Import Path Conflicts**: `core.xxx` vs `backend.core.xxx`

### Key Differences

| Aspect | Trading Platform | Enterprise Package |
|--------|------------------|-------------------|
| Import Path | `from core.xxx` | `from backend.core.xxx` |
| HRM | Official HRM repo exists | Lightweight hierarchical_reasoning |
| Launcher Size | 71KB (1,595 lines) | 272KB (5,087 lines) |
| Structure | Direct `core/` | `backend/core/` |
| Official HRM | ✅ Present | ❌ Not present |

## Cleanup Strategy

### Phase 1: Identify Primary System ✅

**Decision**: Use `PROMETHEUS-Trading-Platform` as primary

- Has official HRM repository
- Cleaner structure
- More recent updates
- Direct import paths

### Phase 2: Consolidate Launch Files

**Action**: Create single unified launcher

1. Keep Trading Platform launcher as base
2. Integrate unique Enterprise features
3. Archive/remove duplicate launchers
4. Create `LAUNCH_PROMETHEUS.py` as single entry point

### Phase 3: Consolidate .env Files

**Action**: Single source of truth

1. Use `.env` in Trading Platform root as primary
2. Merge all configurations from other .env files
3. Remove duplicate .env files
4. Create `.env.example` template

### Phase 4: Integrate Enterprise Features

**Action**: Copy unique features to Trading Platform

1. Identify unique Enterprise features
2. Copy to Trading Platform with updated import paths
3. Test integration
4. Remove Enterprise Package dependency

### Phase 5: Finalize System

**Action**: Complete integration

1. Verify all systems work
2. Update documentation
3. Test full system
4. Create final unified launcher

## Implementation Plan

### Step 1: Analyze Enterprise Features
- Compare both workspaces
- Identify unique Enterprise features
- List features to integrate

### Step 2: Create Unified Launcher
- Base on Trading Platform launcher
- Add Enterprise features
- Support both import paths during transition
- Test compatibility

### Step 3: Consolidate .env
- Read all .env files
- Merge configurations
- Create single `.env`
- Remove duplicates

### Step 4: Update Import Paths
- Standardize on `core.xxx` (Trading Platform style)
- Update Enterprise features to use Trading Platform paths
- Test all imports

### Step 5: Clean Up
- Archive old launchers
- Remove duplicate files
- Organize structure
- Update documentation

## Files to Consolidate

### Launch Files (Keep 1, Archive Rest)
- **Primary**: `launch_ultimate_prometheus_LIVE_TRADING.py` (Trading Platform)
- **Archive**: All other launch files
- **Create**: `LAUNCH_PROMETHEUS.py` (unified entry point)

### .env Files (Consolidate to 1)
- **Primary**: `.env` (Trading Platform root)
- **Merge**: All other .env files
- **Create**: `.env.example` (template)
- **Remove**: All duplicate .env files

### Core Modules
- **Keep**: Trading Platform `core/` structure
- **Integrate**: Unique Enterprise features
- **Update**: Import paths to `core.xxx`

## Success Criteria

1. ✅ Single unified launcher works
2. ✅ Single .env file with all configs
3. ✅ All systems integrated
4. ✅ No import path conflicts
5. ✅ Official HRM integrated
6. ✅ Full system functional

## Next Steps

1. Analyze Enterprise features
2. Create unified launcher
3. Consolidate .env files
4. Test integration
5. Finalize system

