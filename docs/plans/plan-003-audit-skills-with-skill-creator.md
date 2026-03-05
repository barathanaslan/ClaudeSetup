# Plan 003: Audit Existing Skills Against Skill-Creator Standards

## Objective
Use Anthropic's skill-creator guidelines to audit our 5 custom skills and identify improvements. The skill-creator SKILL.md defines best practices for skill writing — check if our skills follow them.

## Context
- Skill-creator reference: /Users/barathanaslan/Projects/ClaudeSetup/skills/skill-creator/SKILL.md
- Our skills to audit (read each SKILL.md):
  - /Users/barathanaslan/Projects/ClaudeSetup/skills/workflow/SKILL.md
  - /Users/barathanaslan/Projects/ClaudeSetup/skills/project-docs/SKILL.md
  - /Users/barathanaslan/Projects/ClaudeSetup/skills/gemini-api/SKILL.md
  - /Users/barathanaslan/Projects/ClaudeSetup/skills/ml-training/SKILL.md
  - /Users/barathanaslan/Projects/ClaudeSetup/skills/apple-ml/SKILL.md

## Steps

1. Read the skill-creator SKILL.md fully — extract the key quality criteria:
   - Frontmatter requirements (name, description — especially description quality)
   - SKILL.md structure best practices
   - Progressive disclosure (3-level loading system)
   - "Principle of Lack of Surprise"
   - Writing patterns and style guidelines
   - Line count limits (under 500 lines)
   - Description optimization (trigger conditions)

2. For EACH of our 5 skills, evaluate:
   - **Description quality**: Is it "pushy" enough about when to trigger? Does it list concrete trigger phrases/patterns?
   - **Line count**: Is it under 500 lines? If over, what can move to references/?
   - **Progressive disclosure**: Are there things that should be in references/ instead of the main SKILL.md?
   - **Writing style**: Is it concise? Does it explain "why" behind instructions? Does it avoid vague language?
   - **Test cases**: Could we define test scenarios for each skill?
   - **Completeness**: Any gaps or missing patterns?

3. Produce a structured report with:
   - Per-skill scorecard (pass/needs-improvement for each criterion)
   - Specific improvement recommendations with priority
   - Any skills that need restructuring

## Acceptance Criteria
- [ ] All 5 skills evaluated against skill-creator criteria
- [ ] Specific, actionable recommendations for each skill
- [ ] Priority ranking of improvements

## Constraints
- This is a READ-ONLY audit — do NOT modify any skill files
- Be specific: cite line numbers and exact issues, not vague suggestions
- Focus on things that would actually improve triggering and quality
