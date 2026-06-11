# Experiments Directory

This directory contains experimental code and research results that are being tested before being integrated into the main production codebase.

## Directory Structure

- `active/` - Currently active experiments being tested
- `archive/` - Archived experiments (successful merged to main, or discontinued)

## Active Experiments

### throughput_test.py
System throughput testing for high-frequency packet ingestion. Tests the system's ability to handle sustained packet loads and measures mitigation latency.

## Workflow

1. New experiments go in `active/`
2. When experiments prove successful, merge to main branch
3. Move successful experiments to `archive/` with documentation
4. Move failed experiments to `archive/` with failure analysis

## Notes

- Experimental code may not have the same level of testing as production code
- Always test thoroughly before merging to main
- Document results and findings in experiment-specific README files
