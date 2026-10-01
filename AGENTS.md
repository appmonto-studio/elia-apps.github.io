# Development workflow: iteration vs stabilization

This project is often developed interactively, especially for UX/UI work.

Unless the user explicitly asks to finalize, stabilize, verify, or prepare a change for release, treat requested UI/UX changes as ITERATION MODE.

## ITERATION MODE

During iterative UX/UI work:

- Focus on implementing the requested change quickly and cleanly.
- Do not add or rewrite UI tests, screenshot tests, golden tests, or emulator/instrumentation tests after every small change.
- Do not launch an emulator or run connected/instrumented Android tests unless they are necessary to diagnose a problem.
- Do not run the full test suite after every incremental edit.
- Avoid repeatedly updating tests that merely mirror temporary UI copy, spacing, layout, or navigation structure while those details are still being explored.
- Preserve existing tests unless a production-code change requires a minimal adjustment to keep the project buildable.
- Use lightweight verification when useful, such as compilation, targeted static checks, or a small relevant unit test.
- If a lightweight check already passed and no subsequent change affects that area, do not rerun it without a reason.
- At the end of the task, report any tests that were intentionally deferred.

The priority in this mode is fast iteration and obtaining a reviewable implementation for the user to inspect.

## STABILIZATION MODE

Enter stabilization mode only when the user explicitly indicates that the current UX/feature block is accepted or asks to finalize/test it.

In stabilization mode:

1. Review the accumulated implementation as a whole.
2. Remove temporary/debug-only UI or code that is no longer needed.
3. Update or add meaningful tests for the final behavior.
4. Prefer testing stable behavior and navigation contracts rather than implementation details.
5. Run the narrowest relevant tests first.
6. Run emulator/instrumentation/screenshot tests where they provide meaningful coverage.
7. Run broader project checks once the targeted tests are green.
8. Fix regressions caused by the accumulated changes and rerun only the affected checks as needed.

Do not perform repeated full-suite or emulator runs unless failures or subsequent changes justify them.

If the user explicitly requests a specific test or verification step, that request overrides these defaults.
