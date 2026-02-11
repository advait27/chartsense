#!/bin/bash

# ChartSense Netlify Deployment Pre-Flight Check
# Run this before deploying to Netlify to verify configuration

echo "🚀 ChartSense Netlify Pre-Flight Check"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

# Function to print failure
failure() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "📋 Configuration Files:"
echo "----------------------"

# Check netlify.toml
if [ -f "netlify.toml" ]; then
    success "netlify.toml exists"
else
    failure "netlify.toml not found"
fi

# Check netlify functions
if [ -d "netlify/functions" ]; then
    success "netlify/functions directory exists"
    
    if [ -f "netlify/functions/analyze.py" ]; then
        success "  analyze.py function exists"
    else
        failure "  analyze.py function missing"
    fi
    
    if [ -f "netlify/functions/chat.py" ]; then
        success "  chat.py function exists"
    else
        failure "  chat.py function missing"
    fi
    
    if [ -f "netlify/functions/requirements.txt" ]; then
        success "  requirements.txt exists"
    else
        failure "  requirements.txt missing"
    fi
    
    if [ -f "netlify/functions/runtime.txt" ]; then
        success "  runtime.txt exists"
    else
        failure "  runtime.txt missing"
    fi
else
    failure "netlify/functions directory not found"
fi

echo ""
echo "🔒 Security:"
echo "------------"

# Check .gitignore
if [ -f ".gitignore" ]; then
    success ".gitignore exists"
    
    if grep -q "^\.env$" .gitignore; then
        success "  .env is in .gitignore"
    else
        failure "  .env not in .gitignore!"
    fi
else
    failure ".gitignore not found"
fi

# Check if .env is tracked
if git ls-files --error-unmatch .env 2>/dev/null; then
    failure ".env is tracked by git! Remove it with: git rm --cached .env"
else
    success ".env is not tracked by git"
fi

# Check if .env.example exists
if [ -f ".env.example" ]; then
    success ".env.example exists (good for documentation)"
else
    warning ".env.example not found (optional but recommended)"
fi

echo ""
echo "⚛️  Frontend:"
echo "-------------"

if [ -d "frontend-react" ]; then
    success "frontend-react directory exists"
    
    if [ -f "frontend-react/package.json" ]; then
        success "  package.json exists"
        
        # Check for required dependencies
        if grep -q '"react"' frontend-react/package.json; then
            success "  React dependency found"
        else
            failure "  React dependency missing"
        fi
    else
        failure "  package.json missing"
    fi
    
    # Check if build directory exists (should be gitignored)
    if [ -d "frontend-react/build" ]; then
        warning "  build/ directory exists (should be generated on Netlify)"
    fi
else
    failure "frontend-react directory not found"
fi

echo ""
echo "🐍 Backend:"
echo "-----------"

if [ -d "backend" ]; then
    success "backend directory exists"
    
    if [ -f "backend/config.py" ]; then
        success "  config.py exists"
    else
        failure "  config.py missing"
    fi
    
    if [ -d "backend/core" ]; then
        success "  core/ module exists"
    else
        failure "  core/ module missing"
    fi
    
    if [ -d "backend/services" ]; then
        success "  services/ module exists"
    else
        failure "  services/ module missing"
    fi
else
    failure "backend directory not found"
fi

echo ""
echo "📦 Dependencies:"
echo "----------------"

if [ -f "requirements.txt" ]; then
    success "Root requirements.txt exists"
fi

if [ -f "netlify/functions/requirements.txt" ]; then
    success "Netlify functions requirements.txt exists"
    
    # Check for key dependencies
    if grep -q "httpx" netlify/functions/requirements.txt; then
        success "  httpx dependency found"
    else
        warning "  httpx dependency not found"
    fi
    
    if grep -q "Pillow" netlify/functions/requirements.txt; then
        success "  Pillow dependency found"
    else
        warning "  Pillow dependency not found"
    fi
fi

echo ""
echo "🌿 Git Status:"
echo "--------------"

if git rev-parse --git-dir > /dev/null 2>&1; then
    success "Git repository initialized"
    
    # Check if there are uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        success "Working tree is clean"
    else
        warning "You have uncommitted changes"
        echo "    Run: git add . && git commit -m 'Ready for deployment'"
    fi
    
    # Check if connected to remote
    if git remote get-url origin > /dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        success "Remote origin configured: $REMOTE_URL"
        
        # Check if local is ahead of remote
        if git rev-parse @{u} > /dev/null 2>&1; then
            LOCAL=$(git rev-parse @)
            REMOTE=$(git rev-parse @{u})
            
            if [ "$LOCAL" = "$REMOTE" ]; then
                success "Local branch is up to date with remote"
            else
                warning "Local branch differs from remote"
                echo "    Run: git push origin main"
            fi
        else
            warning "No upstream branch configured"
            echo "    Run: git push -u origin main"
        fi
    else
        failure "No remote origin configured"
        echo "    Add remote: git remote add origin <your-repo-url>"
    fi
else
    failure "Not a git repository"
fi

echo ""
echo "📄 Documentation:"
echo "-----------------"

if [ -f "README.md" ]; then
    success "README.md exists"
fi

if [ -f "DEPLOYMENT.md" ]; then
    success "DEPLOYMENT.md exists"
fi

if [ -f "NETLIFY_DEPLOY_CHECKLIST.md" ]; then
    success "NETLIFY_DEPLOY_CHECKLIST.md exists"
fi

echo ""
echo "======================================"
echo -e "${GREEN}Checks Passed: $CHECKS_PASSED${NC}"
if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}Checks Failed: $CHECKS_FAILED${NC}"
else
    echo -e "${GREEN}Checks Failed: $CHECKS_FAILED${NC}"
fi
echo "======================================"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All critical checks passed!${NC}"
    echo ""
    echo "✅ Your project is ready for Netlify deployment!"
    echo ""
    echo "Next steps:"
    echo "  1. Push to GitHub: git push origin main"
    echo "  2. Go to https://app.netlify.com"
    echo "  3. Import your repository"
    echo "  4. Add HF_API_KEY in environment variables"
    echo "  5. Deploy!"
    echo ""
    echo "📖 See NETLIFY_DEPLOY_CHECKLIST.md for detailed instructions"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    exit 1
fi
