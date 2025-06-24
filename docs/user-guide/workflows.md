# AI Rails TDD - Portable System Guide

## Installation

```bash
cd /path/to/ai-rails-tdd
./install.sh
```

This installs the `ai-rails` command globally.

## Using AI Rails in Any Project

### 1. Initialize in Your Project

```bash
cd /path/to/your/project
ai-rails init
```

This creates:
```
your-project/
├── .ai-rails/                    # Added to .gitignore automatically
│   ├── planning/
│   │   └── current.md           # Current planning doc (auto-populated)
│   ├── tests/
│   │   ├── generated.py         # AI generated tests
│   │   └── approved.py          # Human approved tests
│   ├── implementation/
│   │   ├── generated.py         # AI generated code
│   │   └── approved.py          # Human approved code
│   ├── results/
│   │   ├── test-run.json        # Test execution results
│   │   └── coverage.json        # Coverage report
│   ├── history/                 # Archive of past features
│   └── config.json              # Project configuration
└── planning-doc-template.md     # Template for your planning doc
```

### 2. Write Your Planning Document

Edit `planning-doc-template.md` with your feature details, then save as:
`planning-doc-[feature-name].md`

### 3. Start AI Rails Services

From anywhere:
```bash
ai-rails-start
```

This starts:
- Approval server on http://localhost:8000
- Test runner on http://localhost:8001

### 4. Import Workflow in n8n

1. Open n8n at your configured URL
2. Create new workflow
3. Import the workflow from: `ai-rails-tdd/workflows/ai-rails-portable.json`
4. Save the workflow

### 5. Run the TDD Process

1. In the workflow, edit "Project Configuration" node:
   - Paste your planning document content
   - Set `project_path` to your project's absolute path
2. Execute the workflow

### 6. The TDD Flow

```
Planning Doc → Generate Tests → Human Approval → Generate Code → Run Tests
     ↓              ↓                 ↓                ↓             ↓
  .ai-rails/    .ai-rails/       Web UI at       .ai-rails/    .ai-rails/
  planning/     tests/           localhost:8000   implementation/ results/
  current.md    generated.py                      generated.py   test-run.json
```

### 7. Check Status

```bash
ai-rails status
```

Shows:
- Current planning document
- Generated/approved tests
- Generated/approved implementation  
- Test results
- Historical features

### 8. Using the Output

After tests pass:
1. Review files in `.ai-rails/`
2. Copy approved implementation to your actual project structure
3. Archive the feature:

```bash
ai-rails archive --name "user-authentication"
```

## File Locations

All AI Rails files are in `.ai-rails/` which is:
- Automatically added to `.gitignore`
- Never pushed to public repos
- Consistent across all projects

## Commands Reference

- `ai-rails init` - Initialize in current project
- `ai-rails status` - Check current feature status
- `ai-rails archive --name [name]` - Archive completed feature
- `ai-rails-start` - Start services from anywhere

## Workflow Features

The portable workflow:
1. Reads/writes to standardized `.ai-rails/` locations
2. Passes data between nodes (not files)
3. Only writes approved content to disk
4. Runs actual tests with pytest
5. Shows real coverage metrics

## Tips

1. **Multiple Features**: Use `ai-rails archive` between features to keep workspace clean
2. **Review History**: Check `.ai-rails/history/` for past implementations
3. **Custom Templates**: Modify `planning-doc-template.md` for your needs
4. **Python/JS**: The system auto-detects language from your planning doc

## Troubleshooting

If services don't start:
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :8001

# Start manually from AI Rails directory
cd /path/to/ai-rails-tdd
./scripts/start-services.sh
```

If n8n can't write files:
- Ensure `project_path` in workflow is absolute path
- Check permissions on project directory