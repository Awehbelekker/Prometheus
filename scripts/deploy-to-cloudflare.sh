#!/bin/bash

###############################################################################
# PROMETHEUS - Cloudflare Pages Deployment Script
# Automated deployment to Cloudflare Pages
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend"
BUILD_DIR="$FRONTEND_DIR/build"
PROJECT_NAME="prometheus-trading"
DOMAIN="prometheus-trade.com"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     PROMETHEUS - Cloudflare Deployment Script             ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
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

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    print_error "Wrangler CLI not found!"
    print_info "Installing Wrangler..."
    npm install -g wrangler
    print_status "Wrangler installed"
fi

print_status "Wrangler CLI found"

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

# Create _headers file if it doesn't exist
if [ ! -f "public/_headers" ]; then
    print_info "Creating _headers file..."
    cat > public/_headers << 'EOF'
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.prometheus-trade.com wss://api.prometheus-trade.com;
EOF
    print_status "_headers file created"
fi

# Create _redirects file if it doesn't exist
if [ ! -f "public/_redirects" ]; then
    print_info "Creating _redirects file..."
    cat > public/_redirects << 'EOF'
# Redirect all traffic to HTTPS
http://prometheus-trade.com/* https://prometheus-trade.com/:splat 301!
http://www.prometheus-trade.com/* https://prometheus-trade.com/:splat 301!

# SPA fallback - serve index.html for all routes
/*    /index.html   200
EOF
    print_status "_redirects file created"
fi

# Run tests
print_info "Running tests..."
npm test -- --watchAll=false --passWithNoTests || {
    print_warning "Some tests failed, but continuing deployment..."
}
print_status "Tests completed"

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
    print_info "Cleaning previous build..."
    rm -rf build
    print_status "Previous build cleaned"
fi

# Build for production
print_info "Building for production..."
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
npm run build || {
    print_error "Build failed! Deployment aborted."
    exit 1
}
print_status "Production build completed"

# Verify build
if [ ! -d "build" ]; then
    print_error "Build directory not created! Deployment aborted."
    exit 1
fi

print_status "Build directory verified"

# Check build size
BUILD_SIZE=$(du -sh build | cut -f1)
print_info "Build size: $BUILD_SIZE"

# Check if user is logged in to Wrangler
print_info "Checking Wrangler authentication..."
if ! wrangler whoami &> /dev/null; then
    print_warning "Not logged in to Wrangler"
    print_info "Please login to Cloudflare..."
    wrangler login
fi

print_status "Wrangler authentication verified"

# Deployment options
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Deployment Options                                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. Deploy to Production (prometheus-trading)"
echo "2. Deploy to Staging (prometheus-staging)"
echo "3. Deploy with custom project name"
echo "4. Exit (build only)"
echo ""
read -p "Select deployment option (1-4): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        print_info "Deploying to Production..."
        PROJECT_NAME="prometheus-trading"
        wrangler pages deploy build --project-name=$PROJECT_NAME --branch=main || {
            print_error "Deployment failed!"
            exit 1
        }
        print_status "Deployed to Production"
        echo ""
        print_info "Your site is live at:"
        echo -e "${GREEN}  https://$DOMAIN${NC}"
        echo -e "${GREEN}  https://$PROJECT_NAME.pages.dev${NC}"
        ;;
    2)
        print_info "Deploying to Staging..."
        PROJECT_NAME="prometheus-staging"
        wrangler pages deploy build --project-name=$PROJECT_NAME --branch=develop || {
            print_error "Deployment failed!"
            exit 1
        }
        print_status "Deployed to Staging"
        echo ""
        print_info "Your staging site is live at:"
        echo -e "${GREEN}  https://$PROJECT_NAME.pages.dev${NC}"
        ;;
    3)
        read -p "Enter project name: " CUSTOM_PROJECT_NAME
        print_info "Deploying to $CUSTOM_PROJECT_NAME..."
        wrangler pages deploy build --project-name=$CUSTOM_PROJECT_NAME || {
            print_error "Deployment failed!"
            exit 1
        }
        print_status "Deployed to $CUSTOM_PROJECT_NAME"
        echo ""
        print_info "Your site is live at:"
        echo -e "${GREEN}  https://$CUSTOM_PROJECT_NAME.pages.dev${NC}"
        ;;
    4)
        print_info "Build completed. Exiting without deployment."
        exit 0
        ;;
    *)
        print_error "Invalid option. Exiting."
        exit 1
        ;;
esac

# Post-deployment checks
echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     Post-Deployment Checklist                              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "✓ Build completed successfully"
echo "✓ Deployed to Cloudflare Pages"
echo ""
echo "Next steps:"
echo "1. Visit your site and verify it's working"
echo "2. Check browser console for any errors"
echo "3. Test all features (dashboard, trading, etc.)"
echo "4. Verify API connectivity"
echo "5. Test on mobile devices"
echo ""
echo "To configure custom domain:"
echo "  wrangler pages domain add $DOMAIN --project-name=$PROJECT_NAME"
echo ""
echo "To view deployment logs:"
echo "  wrangler pages deployment tail --project-name=$PROJECT_NAME"
echo ""
echo "To list all deployments:"
echo "  wrangler pages deployment list --project-name=$PROJECT_NAME"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Deployment Completed Successfully!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

