# SFCC Pipeline Concepts

## Pipeline Nodes

### Start Node
- Entry point for a pipeline
- Can be public (callable from URL) or private

### Call Node
- Calls another pipeline and **returns** to the current pipeline
- Like a subroutine — control comes back after the called pipeline finishes

### Jump Node
- Calls another pipeline and does **NOT return**
- Like a redirect — execution continues in the called pipeline only

**Common exam question: "What is the difference between a jump node and a call node?"**
- Call node: returns to calling pipeline after execution
- Jump node: does NOT return to calling pipeline
- Correct answer: "Workflow does not return to the calling pipeline" (describes jump node behavior)

## Pipeline vs Controller (SFRA)

Modern SFCC uses controllers instead of pipelines:
- Controllers are JavaScript files in `cartridges/`
- More flexible and testable than pipelines
- Pipeline concepts still apply to understanding legacy code

## Pipeline Dictionary

- Shared data context within a pipeline
- Available to ISML templates
- Lost in remote includes (independent dictionary)

## Key Differences: Call vs Jump

| Feature | Call Node | Jump Node |
|---|---|---|
| Returns to caller | Yes | No |
| Execution flow | Subroutine-like | Redirect-like |
| Pipeline dictionary | Shared | Independent |

## Remote Includes in Pipelines

When using `<isinclude url="...">`:
- Triggers a new HTTP request
- Pipeline dictionary is NOT shared
- Independent caching policy
- Maximum depth: 16 levels
