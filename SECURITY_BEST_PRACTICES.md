# Security Best Practices for Prometheus Trading Platform

**Date:** December 1, 2025  
**Purpose:** Guidelines for protecting sensitive credentials and account information

## 🔒 CRITICAL SECURITY RULES

### 1. **NEVER Commit Credentials to Version Control**

**❌ NEVER DO THIS:**

- Commit API keys, secret keys, or account IDs to Git
- Include credentials in documentation files
- Share credentials in plain text in any file
- Store credentials in code files

**✅ ALWAYS DO THIS:**

- Store credentials in `.env` file (which is in `.gitignore`)
- Use environment variables for credentials
- Mask credentials in documentation (e.g., `AKMMN6U5DX...ZQ5Z`)
- Use placeholder text in examples (e.g., `YOUR_API_KEY_HERE`)

### 2. **Documentation File Guidelines**

When creating documentation files:

**❌ NEVER INCLUDE:**

- Full API keys
- Full secret keys
- Complete account IDs
- Any credential that could be used to access accounts

**✅ ALWAYS USE:**

- Masked keys (first 10 chars + last 4 chars): `AKMMN6U5DX...ZQ5Z`
- Placeholder text: `YOUR_API_KEY_HERE`
- References to `.env` file: "Credentials stored in `.env` file"
- Generic examples: "Account ID: `123456789` (example)"

### 3. **Credential Storage**

**✅ CORRECT:**

```
```text

# .env file (NOT committed to Git)

ALPACA_API_KEY=AKMMN6U5DXKTM7A2UEAAF4ZQ5Z
ALPACA_SECRET_KEY=At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX

```

**❌ INCORRECT:**

```python

# In code file

API_KEY = "AKMMN6U5DXKTM7A2UEAAF4ZQ5Z"  # NEVER DO THIS

```

**❌ INCORRECT:**

```markdown

# In documentation

API Key: AKMMN6U5DXKTM7A2UEAAF4ZQ5Z  # NEVER DO THIS

```

### 4. **Account Information**

**✅ CORRECT:**

- "Account Number: `910544927` (masked for security)"
- "Account ID: `41e11939-...-a1b43252e072` (masked)"
- "Connected to account (ID masked for security)"

**❌ INCORRECT:**

- Full account numbers in documentation
- Complete account IDs in plain text
- Account details that could identify specific accounts

## 🛡️ Security Checklist

Before committing any file, verify:

- [ ] No API keys in plain text
- [ ] No secret keys in plain text
- [ ] No account IDs in plain text
- [ ] Credentials are masked or use placeholders
- [ ] `.env` file is in `.gitignore`
- [ ] Documentation references `.env` file, not actual values
- [ ] Code uses `os.getenv()` or `load_dotenv()`, not hardcoded values

## 🔍 How to Check for Exposed Credentials

### Search for Common Patterns

```bash

# Search for Alpaca API keys (starts with AK or PK)

grep -r "AK[A-Z0-9]\{20,\}" --include="*.md" --include="*.py" --include="*.txt"

# Search for secret keys (long random strings)

grep -r "[A-Za-z0-9]\{40,\}" --include="*.md" --include="*.py"

# Search for account IDs

grep -r "[0-9]\{9,\}" --include="*.md" --include="*.py"

```

### If You Find Exposed Credentials

1. **IMMEDIATELY** remove them from the file
2. **REPLACE** with masked versions or placeholders
3. **ROTATE** the credentials if they were committed to a public repository
4. **REVIEW** Git history to see if credentials were exposed
5. **UPDATE** `.gitignore` to prevent future commits

## 📝 Documentation Template

When documenting credentials:

```markdown

## Credentials Configuration

### Alpaca Trading
- **API Key**: Stored in `.env` file as `ALPACA_API_KEY`
- **Secret Key**: Stored in `.env` file as `ALPACA_SECRET_KEY`
- **Mode**: Configured via `ALPACA_PAPER_TRADING` environment variable

### Example .env File

```
```text
ALPACA_API_KEY=YOUR_API_KEY_HERE
ALPACA_SECRET_KEY=YOUR_SECRET_KEY_HERE
ALPACA_PAPER_TRADING=true

```

### Account Information
- **Account**: Connected (account ID masked for security)
- **Status**: Active

```

## 🚨 If Credentials Are Exposed

### Immediate Actions

1. **Rotate Credentials**
   - Generate new API keys in Alpaca dashboard
   - Generate new IB API keys
   - Update all `.env` files

2. **Remove from Git History** (if committed)

   ```bash

   # Use git filter-branch or BFG Repo-Cleaner
   # This is complex - consider professional help

   ```

3. **Review Access Logs**
   - Check Alpaca account for unauthorized access
   - Check IB account for unauthorized access
   - Monitor for suspicious activity

4. **Update Security**
   - Review all files for exposed credentials
   - Update `.gitignore` if needed
   - Implement credential scanning in CI/CD

## ✅ Security Best Practices Summary

1. **Never commit credentials** to version control
2. **Always mask credentials** in documentation
3. **Use environment variables** for all sensitive data
4. **Keep `.env` in `.gitignore`**
5. **Rotate credentials** if exposed
6. **Review files** before committing
7. **Use credential scanning tools** in development workflow

---

**Remember**: Once credentials are exposed, they cannot be "un-exposed". Always err on the side of caution and mask or remove sensitive information from all files.

