# Auto-Branching for New Features

## Feature Request

Automatically create a new git branch whenever a new feature folder is created in `inputs-to-outputs/`.

## Motivation

When starting work on a new feature in the TDD workflow:
1. A new folder is created in `inputs-to-outputs/feature-name/`
2. This indicates the start of a new feature development
3. Currently, developers must manually create a feature branch
4. Automating this would enforce good git practices and reduce friction

## Proposed Implementation

### Option 1: File System Watcher (Recommended)
```python
import watchdog
from git import Repo

class FeatureBranchWatcher:
    def on_created(self, event):
        if event.is_directory and event.src_path.startswith("inputs-to-outputs/"):
            feature_name = Path(event.src_path).name
            if not feature_name.startswith("example-"):
                create_feature_branch(feature_name)
    
    def create_feature_branch(self, feature_name):
        repo = Repo(".")
        # Create branch from main
        new_branch = repo.create_head(f"feature/{feature_name}", "main")
        new_branch.checkout()
        print(f"Created and checked out branch: feature/{feature_name}")
```

### Option 2: Git Hook
```bash
#!/bin/bash
# .git/hooks/post-commit
# Check if new folder added to inputs-to-outputs/
if git diff --name-only HEAD~1 | grep -q "^inputs-to-outputs/.*/$"; then
    feature=$(git diff --name-only HEAD~1 | grep "^inputs-to-outputs/" | head -1 | cut -d'/' -f2)
    git checkout -b "feature/$feature"
fi
```

### Option 3: CLI Command Enhancement
```bash
# Enhanced ai-rails command
ai-rails new-feature email-validator
# This would:
# 1. Create inputs-to-outputs/email-validator/
# 2. Create git branch feature/email-validator
# 3. Switch to the new branch
```

## Benefits

1. **Enforces Git Flow**: Each feature gets its own branch automatically
2. **Reduces Errors**: No forgetting to create branches
3. **Better History**: Clear correlation between folders and branches
4. **Easier Merging**: Each feature can be reviewed/merged independently

## Considerations

### Potential Issues:
1. **Accidental Folders**: What if someone creates a test folder?
   - Solution: Ignore folders starting with "test-" or "example-"

2. **Branch Conflicts**: What if branch already exists?
   - Solution: Append timestamp or prompt user

3. **Uncommitted Changes**: What if working directory is dirty?
   - Solution: Stash changes or warn user

4. **Main Branch Protection**: What if main is protected?
   - Solution: Create from main but don't push until ready

### Configuration Options:
```yaml
# .ai-rails/config.yaml
auto_branching:
  enabled: true
  branch_prefix: "feature/"
  ignore_patterns:
    - "example-*"
    - "test-*"
    - "tmp-*"
  source_branch: "main"
  auto_push: false
```

## Implementation Priority

**Medium** - This is a nice-to-have feature that improves workflow but isn't critical for MVP.

## Success Criteria

- [ ] New feature folders trigger branch creation
- [ ] Example folders are ignored
- [ ] Handles edge cases gracefully
- [ ] Can be disabled via configuration
- [ ] Clear user feedback when branches are created

## Related Features

- Could integrate with #6 (Enhanced n8n Integration)
- Could trigger webhook when new feature starts
- Could auto-create PR draft when branch is pushed