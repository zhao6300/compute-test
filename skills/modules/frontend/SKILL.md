# Frontend/UI skill

## Use

Apply this skill to any user-facing page, route, interaction, or component.

## Required definition

Before implementation, record the route, state list, data contract, permissions, and success behavior:

```markdown
| Route / component | Purpose | Data | States | permission |
| --- | --- | --- | --- | --- |
```

Do not invent layout before knowing what state the user must act on.

## Required states

1. Default.
2. Loading.
3. Empty.
4. Error, including recoverable action.
5. Permission denied.
6. Long action in progress, with cancel or clear feedback where appropriate.
7. Offline / degraded mode when relevant.

## Quality rules

1. One primary action per core screen.
2. Avoid labels the target user cannot understand.
3. Every interactive control is reachable by keyboard and has a visible focus state.
4. Icon-only actions need `aria-label`.
5. Keep color, text, and control contrast accessible.
6. Do not use progressive enhancement as an excuse for unusable slow paths.
7. Lazy-load only above a measured benefit.
8. Avoid client state that can contradict the server.
9. Preserve the user's position and decision after an error or refresh.
10. Do not hide destructive risk behind affirmative labels like "Continue".

## Verification

Before launch, capture evidence for:

1. The smallest keyboard walkthrough.
2. A mobile screen at the narrowest supported viewport.
3. Screen-reader or semantic-tree behavior for the core action.
4. Contrast for key text, controls, and focus states.
5. Network failure handling and retry behavior.
6. Largest Contentful Paint, Interaction to Next Paint, and Cumulative Layout Shift where the tooling supports it.

Do not claim ready from the code alone.
