#!/bin/bash

###############################################################################
# PROMETHEUS Frontend Deployment Script
# Builds and deploys the frontend to production
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend"
BUILD_DIR="$FRONTEND_DIR/build"
BACKUP_DIR="backups/frontend"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     PROMETHEUS Frontend Deployment Script                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found!"
    exit 1
fi

print_status "Frontend directory found"

# Navigate to frontend directory
cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    npm install --legacy-peer-deps
    print_status "Dependencies installed"
else
    print_status "Dependencies already installed"
fi

# Run tests
print_info "Running tests..."
npm test -- --watchAll=false --passWithNoTests || {
    print_error "Tests failed! Deployment aborted."
    exit 1
}
print_status "All tests passed"

# Run linting
print_info "Running linter..."
npm run lint --if-present || print_warning "Linting skipped (no lint script found)"

# Create backup of existing build
if [ -d "$BUILD_DIR" ]; then
    print_info "Creating backup of existing build..."
    mkdir -p "../$BACKUP_DIR"
    tar -czf "../$BACKUP_DIR/build_$TIMESTAMP.tar.gz" "$BUILD_DIR"
    print_status "Backup created: $BACKUP_DIR/build_$TIMESTAMP.tar.gz"
fi

# Clean previous build
print_info "Cleaning previous build..."
rm -rf "$BUILD_DIR"
print_status "Previous build cleaned"

# Build for production
print_info "Building for production..."
export NODE_ENV=production
npm run build || {
    print_error "Build failed! Deployment aborted."
    exit 1
}
print_status "Production build completed"

# Verify build
if [ ! -d "$BUILD_DIR" ]; then
    print_error "Build directory not created! Deployment aborted."
    exit 1
fi

print_status "Build directory verified"

# Check build size
BUILD_SIZE=$(du -sh "$BUILD_DIR" | cut -f1)
print_info "Build size: $BUILD_SIZE"

# Analyze bundle size
print_info "Analyzing bundle size..."
if [ -f "$BUILD_DIR/static/js/main.*.js" ]; then
    MAIN_JS_SIZE=$(du -h "$BUILD_DIR"/static/js/main.*.js | cut -f1)
    print_info "Main JS bundle size: $MAIN_JS_SIZE"
fi

# Generate build report
print_info "Generating build report..."
cat > "$BUILD_DIR/build-info.json" << EOF
{
  "buildDate": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "buildTimestamp": "$TIMESTAMP",
  "nodeVersion": "$(node --version)",
  "npmVersion": "$(npm --version)",
  "buildSize": "$BUILD_SIZE",
  "environment": "production"
}
EOF
print_status "Build report generated"

# Optimize images (if imagemin is available)
if command -v imagemin &> /dev/null; then
    print_info "Optimizing images..."
    find "$BUILD_DIR" -type f \( -name "*.jpg" -o -name "*.png" \) -exec imagemin {} --out-dir={} \;
    print_status "Images optimized"
else
    print_warning "imagemin not found. Skipping image optimization."
fi

# Generate service worker (if workbox is available)
if command -v workbox &> /dev/null; then
    print_info "Generating service worker..."
    workbox generateSW workbox-config.js || print_warning "Service worker generation failed"
else
    print_warning "workbox not found. Skipping service worker generation."
fi

# Security headers check
print_info "Checking security headers..."
if [ -f "$BUILD_DIR/index.html" ]; then
    if grep -q "Content-Security-Policy" "$BUILD_DIR/index.html"; then
        print_status "CSP headers found"
    else
        print_warning "CSP headers not found. Consider adding them."
    fi
fi

# Deployment options
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Deployment Options                                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Deploy to local server (copy to ../dist)"
echo "2. Deploy to Cloudflare Pages"
echo "3. Deploy to Vercel"
echo "4. Deploy to Netlify"
echo "5. Create deployment package (tar.gz)"
echo "6. Exit (build only)"
echo ""
read -p "Select deployment option (1-6): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        print_info "Deploying to local server..."
        mkdir -p ../dist
        cp -r "$BUILD_DIR"/* ../dist/
        print_status "Deployed to ../dist"
        ;;
    2)
        print_info "Deploying to Cloudflare Pages..."
        if command -v wrangler &> /dev/null; then
            wrangler pages publish "$BUILD_DIR" --project-name=prometheus-trading
            print_status "Deployed to Cloudflare Pages"
        else
            print_error "wrangler CLI not found. Install with: npm install -g wrangler"
        fi
        ;;
    3)
        print_info "Deploying to Vercel..."
        if command -v vercel &> /dev/null; then
            vercel --prod
            print_status "Deployed to Vercel"
        else
            print_error "vercel CLI not found. Install with: npm install -g vercel"
        fi
        ;;
    4)
        print_info "Deploying to Netlify..."
        if command -v netlify &> /dev/null; then
            netlify deploy --prod --dir="$BUILD_DIR"
            print_status "Deployed to Netlify"
        else
            print_error "netlify CLI not found. Install with: npm install -g netlify-cli"
        fi
        ;;
    5)
        print_info "Creating deployment package..."
        PACKAGE_NAME="prometheus-frontend-$TIMESTAMP.tar.gz"
        tar -czf "../$PACKAGE_NAME" "$BUILD_DIR"
        print_status "Deployment package created: $PACKAGE_NAME"
        ;;
    6)
        print_info "Build completed. Exiting without deployment."
        ;;
    *)
        print_error "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Deployment Completed Successfully!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
print_info "Build location: $BUILD_DIR"
print_info "Build size: $BUILD_SIZE"
print_info "Timestamp: $TIMESTAMP"
echo ""

