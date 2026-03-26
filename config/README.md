# 📁 PROMETHEUS Trading Platform - Configuration Directory

This directory contains configuration files and templates for the PROMETHEUS Trading Platform v2.0.

## 📋 Configuration Files Overview

### 🔧 Core Configuration
- **`app.yaml`** - Main application configuration
- **`database.yaml`** - Database connection settings
- **`security.yaml`** - Security and authentication settings
- **`logging.yaml`** - Logging configuration

### 🧠 AI & ML Configuration
- **`ai_models.yaml`** - AI model configurations
- **`gpt_oss.yaml`** - GPT-OSS integration settings
- **`thinkmesh.yaml`** - ThinkMesh configuration
- **`quantum.yaml`** - Quantum engine parameters

### 🌐 Deployment Configuration
- **`docker.yaml`** - Docker container settings
- **`kubernetes/`** - Kubernetes deployment manifests
- **`nginx.conf`** - Reverse proxy configuration
- **`systemd/`** - Linux service configurations

### 📊 Trading Configuration
- **`trading.yaml`** - Trading engine parameters
- **`risk_management.yaml`** - Risk management rules
- **`market_data.yaml`** - Market data provider settings
- **`strategies/`** - Default trading strategy configurations

## 🚀 Quick Configuration

### 1. Basic Setup

```bash

# Copy template configurations

cp config/templates/*.yaml config/

# Edit main configuration

nano config/app.yaml

```

### 2. Environment-Specific Configs

```bash

# Development

cp config/environments/development.yaml config/app.yaml

# Production

cp config/environments/production.yaml config/app.yaml

# Testing

cp config/environments/testing.yaml config/app.yaml

```

### 3. Override with Environment Variables

Most configuration values can be overridden with environment variables:

```bash

export PROMETHEUS_DATABASE_URL="postgresql://user:pass@localhost/prometheus"
export PROMETHEUS_AI_OPENAI_API_KEY="your-api-key"
export PROMETHEUS_TRADING_MAX_POSITION_SIZE="50000"

```

## 📝 Configuration Priority

Configuration values are loaded in the following order (highest priority first):

1. **Environment Variables** (PROMETHEUS_*)
2. **Command Line Arguments** (--config-file, etc.)
3. **Local Configuration Files** (config/*.yaml)
4. **Template Configuration Files** (config/templates/*.yaml)
5. **Default Values** (hardcoded in application)

## 🔒 Security Considerations

### Sensitive Data
- Never commit API keys or passwords to version control
- Use environment variables for sensitive configuration
- Ensure configuration files have proper permissions (600)

### Example Secure Setup

```bash

# Set proper permissions

chmod 600 config/*.yaml
chown prometheus:prometheus config/*.yaml

# Use environment variables for secrets

export PROMETHEUS_SECRET_KEY="$(openssl rand -base64 32)"
export PROMETHEUS_DATABASE_PASSWORD="your-secure-password"

```

## 🛠️ Configuration Validation

### Validate Configuration

```bash

# Check configuration syntax

python -m prometheus.config.validator --config config/app.yaml

# Validate all configurations

python -m prometheus.config.validator --all

# Check environment-specific config

python -m prometheus.config.validator --env production

```

### Schema Validation

All configuration files are validated against JSON schemas located in `config/schemas/`.

## 📊 Configuration Examples

### Minimal Configuration

```yaml

# config/app.yaml

app:
  name: "PROMETHEUS Trading Platform"
  version: "2.0.0"
  environment: "production"

database:
  url: "sqlite:///./prometheus_trading.db"

security:
  secret_key: "${PROMETHEUS_SECRET_KEY}"
  jwt_expiration: 3600

ai:
  enabled: true
  openai_api_key: "${OPENAI_API_KEY}"

```

### Production Configuration

```yaml

# config/app.yaml

app:
  name: "PROMETHEUS Trading Platform"
  version: "2.0.0"
  environment: "production"
  debug: false
  workers: 8

database:
  url: "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/prometheus"
  pool_size: 20
  max_overflow: 30

security:
  secret_key: "${PROMETHEUS_SECRET_KEY}"
  jwt_expiration: 3600
  cors_origins:

    - "https://yourdomain.com"
    - "https://app.yourdomain.com"

ai:
  enabled: true
  openai_api_key: "${OPENAI_API_KEY}"
  gpt_oss:
    enabled: true
    model_path: "/opt/models/gpt-oss-20b"
  quantum:
    enabled: true
    qubits: 50

trading:
  max_position_size: 100000
  risk_tolerance: "moderate"
  auto_trading: false

monitoring:
  prometheus_metrics: true
  health_checks: true
  log_level: "INFO"

```

## 🔄 Configuration Management

### Dynamic Configuration Updates

Some configuration changes can be applied without restarting:

```python

# Hot reload configuration

from prometheus.config import ConfigManager
config_manager = ConfigManager()
config_manager.reload()

```

### Configuration Backup

```bash

# Backup current configuration

tar -czf config-backup-$(date +%Y%m%d).tar.gz config/

# Restore configuration

tar -xzf config-backup-20250830.tar.gz

```

## 🧪 Testing Configuration

### Configuration Testing

```bash

# Test configuration loading

python -c "
from prometheus.config import load_config
config = load_config('config/app.yaml')
print('Configuration loaded successfully!')
print(f'App name: {config.app.name}')
print(f'Environment: {config.app.environment}')
"

# Test database connection

python -c "
from prometheus.database import test_connection
if test_connection():
    print('Database connection: OK')
else:
    print('Database connection: FAILED')
"

```

## 📚 Advanced Configuration Topics

### Custom Configuration Sources

Extend configuration loading to support custom sources:

```python

# config/custom_loader.py

from prometheus.config.base import ConfigLoader

class ConsulConfigLoader(ConfigLoader):
    def load(self, key):
        # Load from Consul KV store
        pass

class VaultConfigLoader(ConfigLoader):
    def load(self, key):
        # Load secrets from HashiCorp Vault
        pass

```

### Configuration Encryption

Encrypt sensitive configuration values:

```bash

# Encrypt configuration

python -m prometheus.config.encrypt config/app.yaml config/app.yaml.enc

# Decrypt at runtime

export PROMETHEUS_CONFIG_ENCRYPTION_KEY="your-encryption-key"

```

## 🔧 Troubleshooting

### Common Configuration Issues

**Issue: Configuration file not found**

```bash

# Check file path and permissions

ls -la config/app.yaml

# Ensure file exists and is readable

```

**Issue: Invalid YAML syntax**

```bash

# Validate YAML syntax

python -c "import yaml; yaml.safe_load(open('config/app.yaml'))"

```

**Issue: Environment variable not interpolated**

```bash

# Check environment variable is set

echo $PROMETHEUS_SECRET_KEY

# Ensure proper syntax in YAML: ${VARIABLE_NAME}

```

**Issue: Configuration value not taking effect**

```bash

# Check configuration priority

python -m prometheus.config.debug --show-sources

```

## 📞 Support

For configuration-related questions:

1. Check the [Configuration Guide](../docs/configuration.md)
2. Review the [Environment Variables Reference](../docs/env-reference.md)
3. Submit an issue on GitHub
4. Contact enterprise support for priority assistance

---

**Configuration files in this directory power the entire PROMETHEUS Trading Platform. Handle with care! 🚀**
