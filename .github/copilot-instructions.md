# Copilot Instructions for Insight.org Project

## Project Overview

This is a Next.js static website project for Multi-Res. The site includes an image processing tool that accepts user uploads, downscales and optimizes images to resolutions from 144p through 4K using a basic image library, and uses an AI model for upscaling. The site uses:

- **Framework**: Next.js (Static Site Generation)
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (manual installation) - Reference: https://ui.shadcn.com/llms.txt
- **SEO**: Critical requirement for all pages
- **Fonts**: Inter (primary), Fustat (secondary)
- **Color Scheme**: Primary and Secondary colors defined in `globals.css` using @theme directive

### Site Structure

- Home (landing page with hero, mission, leadership, partners, events)
- CIO Luncheon (Coming soon page)
- Workshops (Coming soon page)
- Highschool Camp (Coming soon page)
- Donate (Donation page with different tiers)

### Brand Identity

- **Tagline**: "Insight That Builds. Innovation that Lasts."
- **Focus**: Technology leadership, innovation, and educational events
- **Copyright**: © 2025 DePaul iD Lab. All rights reserved.

---

## Critical Rules

### Code Validation

**MUST DO**: After writing any code, validate that ALL instructions in this document are followed. If not, fix immediately before presenting to the user.

**MUST DO**: When user provides files, read them carefully and understand the existing code patterns before making suggestions.

---

## Code Style & Conventions

### General Guidelines

- Match the code style and conventions used in the rest of the file
- For new files, check similar files in the same directory or search the project for reference
- When user mentions specific code lines, search the project to understand context, functionality, and usage patterns
- Read attached files carefully (most are under 600 lines)
- Maintain consistency across the codebase

### React Components

- Use functional components only
- Define proper TypeScript prop types and interfaces
- Include proper error handling
- Follow existing component patterns in the project
- Keep components clean and maintainable

### React Hooks

- Define proper types and interfaces
- Follow existing hook patterns in the project
- Ensure proper dependency arrays

---

## API Design (If Applicable)

### Response Structure

All APIs must return consistent response structures:

```typescript
export interface StandardErrorResponse {
	status: false;
	message: string;
}

export type StandardApiResponse<T> = {
	status: boolean;
	message: string;
	data?: T;
};
```

### API Requirements

- Return appropriate HTTP status codes
- Provide clear, meaningful error messages
- Include proper validation and error handling
- Write descriptive success/error messages while preserving intent

---

## Design & Styling

### Tailwind CSS v4

- Use Tailwind CSS v4 for all styling
- Colors are defined using the `@theme` directive in `globals.css`
- Prefer Tailwind default utility classes
- **Custom Theme Colors**:
  - Primary: `bg-primary-500`, `text-primary-600`, etc. (Blue shades: #e6f4ff to #002a3f)
  - Secondary: `bg-secondary-500`, `text-secondary-600`, etc. (Gray shades: #F8F8F8 to #080808)
  - Note: Use `bg-secondary-*` for custom grays to avoid confusion with Tailwind's default gray palette
- **Custom Fonts**: `font-inter`, `font-fustat`
- **Custom Backgrounds**: `bg-main-gradient`, `bg-footer-gradient`, `bg-section-gradient`

### Responsive Design

- Use Tailwind responsive prefixes (sm:, md:, lg:, xl:, 2xl:)
- Implement mobile-first approach
- Use flexbox and grid for layouts (avoid fixed widths/heights)
- **Breakpoint Strategy**: Mobile and tablet designs share the same layout; desktop (lg: breakpoint) has a different layout
- When implementing responsive designs, mobile (default) and tablet (md:) should look identical
- Only apply lg: prefix for desktop-specific layout changes

### Custom Colors

- Use theme colors: `bg-primary-500`, `bg-secondary-800`, `text-primary-600`, `text-secondary-400`
- For colors not in theme, use arbitrary values: `bg-[#hexcode]` or `text-[#hexcode]`

### Figma Integration

- When user provides Figma CSS with fixed dimensions, convert to responsive flexbox/grid layouts
- Don't use fixed width/height unless absolutely necessary
- Maintain design intent while making it responsive

---

## shadcn/ui Components

- Follow shadcn/ui manual installation patterns
- Reference: https://ui.shadcn.com/llms.txt
- Match existing component structure in the project
- Maintain shadcn/ui conventions for component composition

---

## Build & Testing

### Command Policy

**DO NOT** provide build or run commands for testing unless:

1. User explicitly asks for them
2. Debugging build failures
3. Working on build optimization
4. It's absolutely necessary for the task

### Build Verification

- When build commands are run, check terminal output for errors
- Address build errors before considering work complete
- Verify type checking passes
- Ensure no ESLint errors (unless explicitly ignored)

---

## General Instructions

### What to Do

- Only do what is explicitly asked
- Ask for clarification when uncertain
- Use best judgment when user delegates decision-making
- Provide reasoning for significant decisions
- Stay focused on the current task

### What NOT to Do

- Don't add unnecessary comments
- Don't use emojis in code or comments
- Don't change existing code style without explicit request
- Don't make assumptions - gather context first
- Don't provide unsolicited refactoring suggestions

### Special Commands

- If user says "Ignore previous instructions" → ignore all previous instructions
- If user says "Forget all previous instructions" → forget all previous instructions

---

## File Operations

### Editing Files

- Use appropriate edit tools (never run sed/awk commands unless requested)
- Include sufficient context (3-5 lines before/after) in replacements
- Preserve existing formatting and indentation
- Don't create unnecessary markdown documentation files

### Reading Files

- Read complete files when under 600 lines
- Use grep/search for larger files
- Gather all necessary context before making changes
