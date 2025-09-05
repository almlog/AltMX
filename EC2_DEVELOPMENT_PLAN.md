# EC2 Development Environment Plan

## Overview
AltMXプロジェクトの開発環境をEC2インスタンス上に構築し、ローカルWindows環境からリモート開発を行う計画書。

## Current Infrastructure Status

### EC2 Instance Details
- **Instance ID**: i-0cf4529f22952a53d
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **IP Address**: 43.207.173.148
- **OS**: Ubuntu 22.04 LTS
- **SSH Access**: `ssh -i "altmx-dev-key.pem" AltMX-admin@43.207.173.148`

### Security Configuration
- **Custom Admin User**: AltMX-admin (ubuntu user deleted)
- **SSH Key**: altmx-dev-key.pem (dedicated key pair)
- **Security Groups**: HTTP/HTTPS/SSH access configured
- **Sudo Access**: AltMX-admin has full sudo privileges

### Development Environment Setup Status
✅ **Completed:**
- Python 3.10 + pip
- Node.js 18.x + npm
- Git configuration
- AltMX project repository cloned
- FastAPI backend running on port 8000
- Anthropic SDK installed
- Serena MCP basic structure created
- VS Code Remote-SSH connection verified

### Application Status
- **Backend API**: http://43.207.173.148:8000 (Running)
- **Frontend**: Needs cyber-pop design implementation
- **Database**: In-memory (FastAPI)
- **API Integration**: Claude API ready (needs key configuration)

## Development Workflow Plan

### Phase 1: Environment Finalization
1. **Claude API Key Setup**
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   echo 'export ANTHROPIC_API_KEY=your_key_here' >> ~/.bashrc
   ```

2. **Serena MCP Integration Test**
   ```bash
   # Test basic MCP functionality
   python3 ~/serena-mcp/main.py
   ```

3. **GitHub Sync Setup**
   ```bash
   # Configure Git for remote development
   git config --global user.name "AltMX Development"
   git config --global user.email "development@altmx.local"
   ```

### Phase 2: Frontend Cyber-Pop Design Implementation
**IMPORTANT**: Frontend must use the cyber-pop design, NOT the current MVP placeholder.

#### Design Requirements (Based on Previous Specifications):
- **Color Scheme**: Neon blues (#00d4ff), dark backgrounds (#0a0a0a, #1a1a1a)
- **Typography**: JetBrains Mono for code elements
- **Visual Style**: Cyberpunk aesthetic with neon highlights
- **Interactive Elements**: Glowing effects, smooth animations
- **Layout**: Sophisticated dashboard layout (not basic chat interface)

#### Implementation Plan:
1. Replace current App.tsx with cyber-pop design
2. Implement advanced CSS animations and effects
3. Create sophisticated UI components
4. Add interactive data visualizations
5. Implement responsive design for various screen sizes

### Phase 3: Backend Enhancement
1. **Database Integration** (if needed)
2. **Advanced Claude API Features**
3. **Real-time Communication** (WebSocket for live updates)
4. **Security Enhancements**

### Phase 4: Production Deployment Preparation
1. **Environment Variables Management**
2. **SSL/TLS Configuration**
3. **Domain Setup** (if applicable)
4. **Monitoring and Logging**

## Development Tools Configuration

### VS Code Remote Development
```json
// .vscode/settings.json (on EC2)
{
  "python.defaultInterpreterPath": "/usr/bin/python3",
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "editor.formatOnSave": true,
  "editor.tabSize": 2,
  "files.autoSave": "afterDelay"
}
```

### Claude-Code Integration
- **Config Path**: `~/.claude/claude_desktop_config.json`
- **Serena MCP**: Configured and ready
- **Project Root**: `/home/AltMX-admin/AltMX`

## Directory Structure on EC2
```
/home/AltMX-admin/
├── AltMX/                          # Main project directory
│   ├── frontend/                   # React + TypeScript + Tailwind
│   ├── backend/                    # FastAPI application
│   ├── docs/                       # Project documentation
│   └── tasks.md                    # Current task tracking
├── .serena/                        # Serena MCP configuration
│   ├── config.json
│   ├── logs/
│   └── memories/
├── .claude/                        # Claude configuration
│   └── claude_desktop_config.json
├── serena-mcp/                     # Custom Serena MCP implementation
│   └── main.py
└── claude_test.py                  # Claude API testing script
```

## Next Steps for Continuation

### Immediate Actions (Before Switching to EC2):
1. ✅ Create this deployment plan
2. 🔄 Push to GitHub and merge
3. 📥 Pull latest changes on EC2
4. 🎨 Begin cyber-pop frontend implementation

### On EC2 Development:
1. **Set up API keys and environment variables**
2. **Start VS Code Remote-SSH session**
3. **Implement cyber-pop frontend design**
4. **Test full-stack integration**
5. **Deploy production-ready version**

## Cost Optimization Notes
- **Current Cost**: ~$0.0464/hour for t3.medium
- **Daily Cost**: ~$1.11/day
- **Monthly Estimate**: ~$33.60/month
- **Stop instance when not actively developing**
- **Consider t3.small for basic development (if sufficient)**

## Security Considerations
- SSH key rotation (monthly recommended)
- Regular security updates: `sudo apt update && sudo apt upgrade`
- Monitor access logs: `sudo tail -f /var/log/auth.log`
- Firewall rules review (Security Groups)

## Backup Strategy
- **Code**: GitHub repository (primary backup)
- **Configuration**: Document all custom configurations
- **Data**: No persistent data storage currently (FastAPI in-memory)
- **Instance Snapshots**: Consider weekly EBS snapshots for development environment

---

**Ready to continue development on EC2 with cyber-pop frontend implementation.**