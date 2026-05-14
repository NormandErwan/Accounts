# CLAUDE.md

## Project

CLI tool that enriches French bank CSV exports with Firefly III categories and destination account names, producing an import-ready CSV.

## Toolchain

- **dotnet** — build, test, run (`dotnet build`, `dotnet test`, `dotnet run`)
- **CSharpier** — formatter (`dotnet csharpier check .` / `dotnet csharpier format .`)
- **Roslyn analyzers** — linter (via `dotnet build -warnaserror`)

Run all checks before committing:

```bash
dotnet build -warnaserror && dotnet csharpier check . && dotnet test
```

## Conventions

- All **code** is in English: variable names, method names, class names, comments.
- All **display strings** are in French: category names, CLI messages.
- Firefly III field names: `source_name` (bank account), `destination_name` (payee for withdrawals), `type` (`withdrawal` / `deposit` / `transfer`).
- No personal data in the repository — fixtures use invented names; real CSVs are passed as base64 CI secrets.
