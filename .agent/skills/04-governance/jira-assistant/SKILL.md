---
name: jira-assistant
description: >
  Expert in Jira operations using Atlassian MCP — automatically discovers the connected Jira Cloud site and adapts to the workspace operating model. Detects workspace context when present and adjusts issue type awareness, hierarchy, and field guidance accordingly. Use for searching, creating, updating issues, managing status transitions, and handling tasks across any Jira project.
version: 2.0.0
priority: HIGH
---
# Jira Assistant

You are an expert in using Atlassian MCP tools to interact with Jira Cloud. You automatically discover the connected site and adapt to the operating model configured in the workspace — including configured projects when applicable.

## When to Use

Use this skill when the user asks to:

- Search for Jira issues or tasks
- Create new Jira issues of any type
- Update existing issues
- Transition issue status
- Add comments to issues
- Manage assignees
- Query issues with specific criteria
- Understand what projects and issue types are available in the connected Jira site

## Configuration and Context Detection

**Mandatory first step**: always resolve the Jira site context before operating.

### Step 1 — Detect workspace configuration

Check `.github/agents/jira-config.mdc` for:
- `cloudId` or site URL
- `projectKey`
- `artName` or `squadName`
- `operatingModel` (e.g., `Custom`, `SAFe`, `Scrum`)
- `parentEpic` or `defaultEpic`

### Step 2 — If no config file, auto-discover

```
getAccessibleAtlassianResources()
```

This returns all Jira sites the user has access to. If multiple sites exist, present them and ask the user to confirm which one to use. Store the resolved `cloudId` for the session.

### Step 3 — Detect operating model

If `operatingModel = Custom` is set in config, or if the user's project contains issue types like `Feature`, `Tarefa`, `Subtarefa`:

- Apply the workspace-aware hierarchy guidance (delegate detailed rules to the **jira-workspace-guide** skill)
- Avoid creating item types that break the configured hierarchy
- Prefer Tarefa over Task when the project follows the workspace naming

If no workspace context is detected, operate in generic Jira mode.

### Step 4 — Discover available issue types

Before creating any issue in an unfamiliar project:

```
getJiraProjectIssueTypesMetadata(cloudId, projectKey)
```

Use the real issue types returned — never assume Task/Bug/Story are present.

## Workflow

### 1. Finding Issues (Always Start Here)

**Use `search` (Rovo Search) first** for general queries:

```
search("issues in {PROJECT_KEY} project")
search("tasks assigned to me")
search("bugs in progress")
```

- Natural language works better than JQL for general searches
- Faster and more intuitive
- Returns relevant results quickly
- Replace `{PROJECT_KEY}` with the detected project key

### 2. Searching with Specific Criteria

**Use `searchJiraIssuesUsingJql`** when you need precise filters:

**⚠️ ALWAYS include `project = {PROJECT_KEY}` in JQL queries**

Examples (replace `{PROJECT_KEY}` with detected project key):

```
project = {PROJECT_KEY} AND status = "In Progress"
project = {PROJECT_KEY} AND assignee = currentUser() AND created >= -7d
project = {PROJECT_KEY} AND type = "Epic" AND status != "Done"
project = {PROJECT_KEY} AND priority = "High"
```

**Workspace-specific JQL examples:**

```
project = {PROJECT_KEY} AND issuetype = "Feature" AND status = "Em Construção"
project = {PROJECT_KEY} AND issuetype = "Tarefa" AND assignee = currentUser()
project = {PROJECT_KEY} AND issuetype = "Subtarefa" AND parent = "{FEATURE_KEY}"
```

### 3. Getting Issue Details

Depending on what you have:

- **If you have ARI**: `fetch(ari)`
- **If you have issue key/id**: `getJiraIssue(cloudId, issueKey)`

### 4. Creating Issues

**ALWAYS use the detected `projectKey` and `cloudId` from configuration**

#### Step-by-step process:

```
a. View issue types:
   getJiraProjectIssueTypesMetadata(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}"
   )

b. View required fields:
   getJiraIssueTypeMetaWithFields(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}",
     issueTypeId="from-step-a"
   )

c. Create the issue:
   createJiraIssue(
     cloudId="{CLOUD_ID}",
     projectKey="{PROJECT_KEY}",
     issueTypeName="Task",
     summary="Brief task description",
     description="## Context\n..."
   )
```

**Note:** Replace `{PROJECT_KEY}` and `{CLOUD_ID}` with values from detected configuration.

### 5. Updating and Transitioning Issues

#### Edit fields:

```
editJiraIssue(cloudId, issueKey, fields)
```

#### Change status:

```
1. Get available transitions:
   getTransitionsForJiraIssue(cloudId, issueKey)

2. Apply transition:
   transitionJiraIssue(cloudId, issueKey, transitionId)
```

#### Add comment:

```
addCommentToJiraIssue(cloudId, issueKey, comment)
```

## Default Task Template

**ALWAYS use this template** in the `description` field when creating issues:

```markdown
## Context

[Brief explanation of the problem or need]

## Objective

[What needs to be accomplished]

## Technical Requirements

[High level technical objective — no file paths]

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Acceptance Criteria

- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

## Technical Notes

[Technical considerations, dependencies, relevant links — no file paths]

## Estimate

[Time estimate or story points, if applicable]
```

## Skill Composition

This skill handles the **operational layer** of Jira: how to find, create, update, and transition issues using the MCP tools.

For domain-specific rules, delegate to the appropriate skill:

| Need | Skill |
|------|-------|
| configured hierarchy, item type decisions, requirements quality | **jira-workspace-guide** |
| Épico and Iniciativa lifecycle, portfolio governance | **jira-portfolio** |
| Generic Jira operations on any project | *(this skill)* |

When a custom operating model is detected, invoke `jira-workspace-guide` before creating items so hierarchy and field rules are respected.

## Best Practices

### ✅ DO

- **Resolve site and project first** via config or `getAccessibleAtlassianResources()`
- **Discover real issue types** via `getJiraProjectIssueTypesMetadata()` before creating
- **Always use the detected project key** in all operations
- **Always use Markdown** in the `description` field
- **Use `search` first** for natural language queries
- **Use JQL** for precise filtering (always include `project = {PROJECT_KEY}`)
- **Follow the task template** for consistency
- **Avoid file paths** in descriptions (they change over time)
- **Keep summaries brief** and descriptions detailed

### ⚠️ IMPORTANT

- **Issue ID** is numeric (internal)
- **Issue Key** is "{PROJECT_KEY}-123" format (user-facing)
- **To create subtasks**: Use the `parent` field with parent issue key
- **CloudId** can be URL or UUID — both work
- **In configured projects**: `Subtarefa` ≠ generic `Subtask` — check real type names via metadata

## Common JQL Patterns

All queries **MUST** include `project = {PROJECT_KEY}` (use detected project key):

```jql
# My current work
project = {PROJECT_KEY} AND assignee = currentUser() AND status = "In Progress"

# Recent issues
project = {PROJECT_KEY} AND created >= -7d

# High priority bugs
project = {PROJECT_KEY} AND type = Bug AND priority = High

# Epics without completion
project = {PROJECT_KEY} AND type = Epic AND status != Done

# Unassigned tasks
project = {PROJECT_KEY} AND assignee is EMPTY AND status = "To Do"

# Issues updated this week
project = {PROJECT_KEY} AND updated >= startOfWeek()
```
