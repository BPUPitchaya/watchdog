# VERSION MANAGEMENT AND RELEASE PROCESS

This document describes the version management and release process for WATCHDOG.

## Version Numbering

WATCHDOG uses semantic versioning (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Current Version
- **Version**: 2.0.0
- **Status**: Stable

## Version Update Locations

When updating the version number, update these files:

1. **setup_mac.py** (lines 27-28)
   ```python
   'CFBundleVersion': '2.0',
   'CFBundleShortVersionString': '2.0',
   ```

2. **README.md** (version reference in project description)

3. **This file** (update Current Version section)

4. **CHANGELOG.md** (add new version entry)

## Release Process

### Pre-Release Checklist

#### Code Quality
- [ ] All automated tests pass (`python3 tests/test_core.py`)
- [ ] Code review completed for all changes
- [ ] No critical bugs remaining
- [ ] Documentation updated

#### Build Verification
- [ ] macOS .app builds successfully
- [ ] Windows .exe builds successfully (on Windows machine)
- [ ] Linux package builds successfully
- [ ] All builds tested on target platforms

#### Testing
- [ ] Cross-platform testing completed
- [ ] Performance testing under load
- [ ] Security review completed
- [ ] User acceptance testing

#### Documentation
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] USER_GUIDE.md updated
- [ ] BUILD_AND_TEST.md updated
- [ ] Release notes prepared

### Release Steps

#### 1. Create Release Branch
```bash
git checkout -b release/v2.0.0
```

#### 2. Update Version Numbers
Update version in all locations listed above.

#### 3. Update CHANGELOG
Add new version entry to CHANGELOG.md with:
- Version number
- Release date
- New features
- Bug fixes
- Breaking changes
- Known issues

#### 4. Build Release Artifacts

**macOS:**
```bash
python3 setup_mac.py py2app
# Result: dist/WATCHDOG AI Dashboard.app
```

**Windows:**
```cmd
pyinstaller build_windows.py
# Result: dist/WATCHDOG/WATCHDOG.exe
```

**Linux:**
```bash
python3 setup.py install
# Result: Installed package
```

#### 5. Test Release Artifacts
- [ ] Test macOS .app on clean macOS installation
- [ ] Test Windows .exe on clean Windows installation
- [ ] Test Linux package on clean Linux installation
- [ ] Verify onboarding wizard works
- [ ] Verify network monitoring works
- [ ] Verify ML detection works
- [ ] Verify firewall blocking works

#### 6. Create Git Tag
```bash
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

#### 7. Merge to Main
```bash
git checkout main
git merge release/v2.0.0
git push origin main
```

#### 8. Create Release
- Create GitHub release with tag v2.0.0
- Attach build artifacts:
  - WATCHDOG AI Dashboard.app (macOS)
  - WATCHDOG.exe (Windows)
  - Source distribution (Linux)
- Include release notes from CHANGELOG

#### 9. Announce Release
- Update project website
- Send notification to users
- Post on relevant platforms

## Post-Release Tasks

### Cleanup
- [ ] Delete release branch
- [ ] Archive old release artifacts
- [ ] Update version to next development version

### Monitoring
- [ ] Monitor for bug reports
- [ ] Track user feedback
- [ ] Collect performance metrics
- [ ] Document any issues found

## Hotfix Process

For critical bugs that need immediate release:

1. Create hotfix branch: `git checkout -b hotfix/v2.0.1`
2. Fix the bug
3. Update version to PATCH version (e.g., 2.0.1)
4. Update CHANGELOG
5. Build and test
6. Create tag: `git tag -a v2.0.1`
7. Merge to main and release branch
8. Create release

## Development Workflow

### Feature Development
1. Create feature branch: `git checkout -b feature/new-feature`
2. Develop and test
3. Create pull request to main
4. Code review
5. Merge to main

### Bug Fixes
1. Create bugfix branch: `git checkout -b bugfix/issue-description`
2. Fix and test
3. Create pull request to main
4. Code review
5. Merge to main

## CHANGELOG Format

```markdown
## [2.0.0] - 2024-06-08

### Added
- New feature 1
- New feature 2

### Changed
- Updated component X
- Improved performance of Y

### Fixed
- Fixed bug in component Z
- Resolved issue with feature A

### Breaking Changes
- API change that requires user action

### Known Issues
- Issue 1: Description
- Issue 2: Description
```

## Release Notes Template

```markdown
# WATCHDOG v2.0.0 Release Notes

## Overview
Brief description of the release

## New Features
- Feature 1: Description
- Feature 2: Description

## Improvements
- Improvement 1: Description
- Improvement 2: Description

## Bug Fixes
- Bug fix 1: Description
- Bug fix 2: Description

## Compatibility
- macOS: Version X and later
- Windows: Version Y and later
- Linux: Distribution Z and later

## Upgrade Instructions
Steps for users to upgrade

## Known Issues
List of known issues

## Download Links
- macOS: [Link]
- Windows: [Link]
- Linux: [Link]
```

## Version History

### v2.0.0 (Current)
- Simplified onboarding wizard for non-technical users
- Fixed onboarding wizard exit logic
- Added cross-platform build support
- Added automated tests
- Created comprehensive documentation

### v1.0.0
- Initial release
- Basic network monitoring
- ML threat detection
- Firewall integration
- PyQt6 UI

## Security Considerations

### Release Security
- Sign all release artifacts
- Verify checksums
- Use secure distribution channels
- Document any security changes

### Vulnerability Disclosure
- Report security issues privately
- Coordinate fix timeline
- Release security updates promptly
- Document security fixes in release notes

## Rollback Plan

If a critical issue is discovered post-release:

1. **Immediate Actions**
   - Announce issue to users
   - Provide workaround if available
   - Stop distribution of affected version

2. **Rollback Steps**
   - Revert to previous stable version
   - Update download links
   - Notify users to downgrade

3. **Post-Rollback**
   - Fix the issue
   - Test thoroughly
   - Release new version

## Performance Benchmarks

Track performance metrics for each release:

- Startup time
- Memory usage
- CPU usage
- Packet capture rate
- ML prediction latency
- UI responsiveness

Document these in release notes to show improvements.

## Support and Maintenance

### Support Period
- Major versions: 12 months support
- Minor versions: 6 months support
- Patch versions: Until next minor version

### End of Life
- Announce EOL 3 months in advance
- Provide migration guide
- Archive old versions
- Update documentation

## Contact

For release-related questions:
- Maintainer: [Your Name]
- Email: [your.email@example.com]
- GitHub Issues: [repository-url]/issues
