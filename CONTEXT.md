# CONTEXT.md — hsutools

## Project State

**Version**: 1.2.1  
**Status**: Active development  
**Last analyzed**: 2026-08-21

## What We Learned

### Strengths
1. **Clean architecture** — clear separation between CLI layer (`cli.py`) and business logic (`core/`)
2. **Complete i18n** — bilingual support (en/zh) with env var fallback
3. **User-friendly CLI** — preview and confirmation before destructive operations
4. **Automated release** — tag-based PyPI publishing with GitHub Actions

### Areas for Improvement
1. **Test coverage is low** — only 6 tests, core functions like `s2tw`, `topdf`, `resize` lack unit tests
2. **`test_demo/` directory** — residual manual testing files, should be cleaned up
3. **`s2tw` extensions param** — CLI defines it but doesn't expose it (cli.py:554 hardcodes `None`)
4. **Error handling** — some core functions have thin error handling

## Decisions Made

- [ ] Created `AGENTS.md` for AI agent guidance
- [ ] Created `CONTEXT.md` for project state tracking

## Open Questions

1. Should `test_demo/` be removed or added to `.gitignore`?
2. Should `s2tw` extensions be exposed as a CLI option?
3. What's the testing strategy — more CLI integration tests or unit tests per module?

## Next Steps (if requested)

- Add unit tests for `s2tw.py`, `image_resize.py`, `create_path.py`
- Clean up `test_demo/` directory
- Expose `s2tw` extensions parameter in CLI
- Add `--dry-run` mode for batch operations
