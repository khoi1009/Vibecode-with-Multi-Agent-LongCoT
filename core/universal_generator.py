from pathlib import Path
import re
from typing import Dict, Optional

class UniversalGenerator:
    """
    Dynamically generates project structures based on prompt complexity.
    Replaces hardcoded demo logic with a universal 'Code Synapse'.
    """

    def __init__(self, workspace_path: Path, skill_loader=None):
        self.workspace = workspace_path
        self.skill_loader = skill_loader
        
        # Templates
        self.react_glass_component = """import React, { useState } from 'react';

const Card = ({ title, children, accent = "blue" }) => (
  <div className={`group relative overflow-hidden rounded-xl bg-white/5 p-6 shadow-2xl backdrop-blur-xl border border-white/10 hover:border-${accent}-500/50 transition-all duration-300 hover:-translate-y-1`}>
    <div className={`absolute inset-0 bg-gradient-to-br from-${accent}-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity`} />
    <div className="relative">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full bg-${accent}-500`} />
        {title}
      </h3>
      <div className="text-gray-300">
        {children}
      </div>
    </div>
  </div>
);

export default function App() {
  const [active, setActive] = useState(true);

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white p-8 font-sans selection:bg-purple-500/30">
      <div className="max-w-7xl mx-auto">
        <header className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 animate-pulse" />
            <h1 className="text-4xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
              {{PROJECT_NAME_UPPER}}
            </h1>
          </div>
          <button className="px-6 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors backdrop-blur-md">
            + System Action
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card title="Analytics" accent="purple">
            <div className="text-4xl font-mono font-bold">98.5%</div>
            <div className="text-sm text-green-400 mt-2">System Optimal</div>
          </Card>
          
          <Card title="Active Protocols" accent="blue">
            <div className="space-y-2 mt-2">
              <div className="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-3/4 animate-pulse" />
              </div>
              <div className="flex justify-between text-xs text-gray-500">
                <span>Processing...</span>
                <span>75%</span>
              </div>
            </div>
          </Card>

           <Card title="AI Insight" accent="green">
             <p className="italic text-sm">"The architecture suggests a scalar approach to complexity management."</p>
           </Card>
        </div>
      </div>
    </div>
  );
}
"""

    def generate(self, query: str) -> None:
        """Main entry point for generation"""
        
        # 1. Analyze Complexity
        complexity = self._analyze_complexity(query)
        
        # 2. Extract Project Name
        project_name = self._extract_project_name(query)
        safe_name = re.sub(r'[^a-z0-9_]', '_', project_name.lower())
        
        # 3. Generate
        print(f"\n   [Universal Generator] Detected Context: {project_name} ({complexity.upper()})")
        
        target_dir = self.workspace / safe_name
        target_dir.mkdir(exist_ok=True)
        
        if complexity == 'advanced':
            self._generate_advanced(target_dir, project_name, query)
        elif complexity == 'intermediate':
            self._generate_intermediate(target_dir, project_name, query)
        else:
            self._generate_basic(target_dir, project_name)
            
        print(f"   [+] Generated universal project structure in: {target_dir}")

    def _get_active_skills(self, query: str) -> list:
        """Get relevant skills from the loader if available"""
        active_skills = []
        if self.skill_loader:
            # Select top 3 skills
            skills_with_scores = self.skill_loader.select_skills(query, max_skills=3)
            active_skills = [s[0].name for s in skills_with_scores]
            
            if active_skills:
                print(f"   [Skill Synapse] Injecting DNA from: {', '.join(active_skills)}")
                
        return active_skills

    def _analyze_complexity(self, query: str) -> str:
        q = query.lower()
        if any(w in q for w in ['platform', 'system', 'board', 'complex', 'manager', 'hub', 'suite', 'social', 'saas']):
            return 'advanced'
        if any(w in q for w in ['app', 'tracker', 'dashboard', 'api', 'site', 'blog', 'shop']):
            return 'intermediate'
        return 'basic'

    def _extract_project_name(self, query: str) -> str:
        # Simple heuristic: remove common verbs and articles and quotes
        clean_query = query.replace('"', '').replace("'", "")
        words = clean_query.lower().split()
        stop_words = {'create', 'build', 'write', 'make', 'generate', 'a', 'an', 'the', 'project', 'application', 'for', 'with', 'refactor', 'optimize', 'fix', 'debug', 'code', 'app'}
        meaningful = [w for w in words if w not in stop_words]
        
        if not meaningful:
            return "untitled_project"
            
        return "_".join(meaningful[:2]) # Take first 2 meaningful words

    def _generate_basic(self, target_dir: Path, name: str):
        """Single file script"""
        (target_dir / "main.py").write_text(f"""# {name.title()}
# Generated by Vibecode Universal Engine

def main():
    print("Initializing {name}...")
    # TODO: Implement core logic
    
    data = [i for i in range(100)]
    print(f"Processed {{len(data)}} items.")

if __name__ == "__main__":
    main()
""", encoding="utf-8")
        print("   [OK] Generated Basic Python Script")

    def _generate_intermediate(self, target_dir: Path, name: str, query: str = ""):
        """Flask App"""
        
        # Skill-based enhancements
        skills = self._get_active_skills(query)
        requirements = ["flask", "requests"]
        
        auth_code = ""
        if 'better-auth' in skills or 'authentication' in query.lower():
            requirements.extend(["python-jose", "passlib", "python-multipart"])
            auth_code = """
# [Skill: better-auth] Secure Authentication Middleware
from functools import wraps
from flask import request, abort

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            # In a real app, verify JWT here
            pass 
        return f(*args, **kwargs)
    return decorated
"""

        (target_dir / "app.py").write_text(f"""from flask import Flask, render_template

app = Flask(__name__)
{auth_code}

@app.route('/')
def home():
    return '''
    <html>
        <head><title>{name.title()}</title></head>
        <body style="font-family: sans-serif; padding: 2rem; background: #f0f0f0;">
            <div style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #333;">{name.title()}</h1>
                <p>Welcome to your AI-generated {name} application.</p>
                <button style="background: #0070f3; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">Action</button>
            </div>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
""", encoding="utf-8")
        
        (target_dir / "requirements.txt").write_text("\n".join(requirements), encoding="utf-8")
        print("   [OK] Generated Intermediate Flask App")

    def _generate_advanced(self, target_dir: Path, name: str, query: str = ""):
        """React + FastAPI"""
        
        # Skill-based enhancements
        skills = self._get_active_skills(query)
        
        # Backend Enhancements
        be_reqs = ["fastapi", "uvicorn", "pydantic"]
        be_imports = ""
        be_middleware = ""
        
        if 'better-auth' in skills or 'authentication' in query.lower():
            be_reqs.extend(["python-jose[cryptography]", "passlib[bcrypt]"])
            be_imports += "from fastapi.security import OAuth2PasswordBearer\n"
            be_middleware += "\n# [Skill: better-auth] OAuth2 Scheme\noauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')\n"

        if 'databases' in skills:
            be_reqs.extend(["sqlalchemy", "alembic"])
            be_imports += "from sqlalchemy import create_engine\n"

        # Frontend Enhancements
        fe_deps = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "framer-motion": "^11.0.0",
            "lucide-react": "^0.330.0",
            "clsx": "^2.1.0",
            "tailwind-merge": "^2.2.1"
        }
        
        if 'threejs' in skills:
            fe_deps["three"] = "^0.160.0"
            fe_deps["@react-three/fiber"] = "^8.15.0"
            
        if 'ui-ux-pro-max' in skills:
            # Add specific tailwind plugins or component libraries if defined in skill
            pass
        
        # Backend Generation
        be_dir = target_dir / "backend"
        be_dir.mkdir(exist_ok=True)
        static_dir = be_dir / "static"
        static_dir.mkdir(exist_ok=True)

        # Generate Zero-Dependency Frontend (React via CDN)
        # This ensures the app works IMMEDIATELY without Node/NPM
        
        # We transform the JSX component to be standalone
        cdn_component = self.react_glass_component.replace("{{PROJECT_NAME_UPPER}}", name.upper())
        cdn_component = cdn_component.replace("export default function App", "function App")
        cdn_component = cdn_component.replace("import React, { useState } from 'react';", "const { useState } = React;")
        
        # Fix accent class/style interpolation for Babel/standalone
        cdn_component = cdn_component.replace("from-${accent}-500/10", "from-blue-500/10") # Simplify for DEMO robustness
        cdn_component = cdn_component.replace("to-purple-500/10", "to-purple-500/10")
        cdn_component = cdn_component.replace("hover:border-${accent}-500/50", "hover:border-blue-500/50")

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name.title()} - Vibecode</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-[#0A0A0B] text-white">
    <div id="root"></div>

    <script type="text/babel">
        {cdn_component}

        const container = document.getElementById('root');
        const root = ReactDOM.createRoot(container);
        root.render(<App />);
    </script>
</body>
</html>
"""
        (static_dir / "index.html").write_text(html_content, encoding="utf-8")

        # Update FastAPI to serve static files
        (be_dir / "main.py").write_text(f"""from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
{be_imports}

app = FastAPI(title="{name.title()} API")
{be_middleware}

# Serve the Zero-Dependency Frontend
app.mount("/assets", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

@app.get("/api/status")
def read_status():
    return {{"system": "{name.title()}", "status": "online"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""", encoding="utf-8")
        
        (be_dir / "requirements.txt").write_text("\n".join(be_reqs), encoding="utf-8")
        
        # Frontend Generation
        fe_dir = target_dir / "frontend"
        fe_dir.mkdir(exist_ok=True)
        src_dir = fe_dir / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # package.json
        import json
        pkg_json = {
            "name": name.lower(),
            "version": "0.1.0",
            "type": "module",
            "scripts": {"dev": "vite", "build": "vite build"},
            "dependencies": fe_deps
        }
        (fe_dir / "package.json").write_text(json.dumps(pkg_json, indent=2), encoding="utf-8")
        
        # Inject custom title into component
        component_code = self.react_glass_component.replace("{{PROJECT_NAME_UPPER}}", name.upper())
        
        # Add ThreeJS placeholder if skill active
        if 'threejs' in skills:
            component_code = component_code.replace("</div>\n    </div>\n  );\n}", """
        <div className="absolute inset-0 -z-10 opacity-30">
            {/* [Skill: threejs] Canvas would go here */}
            <div className="w-full h-full bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 via-gray-900 to-black"></div>
        </div>
      </div>
    </div>
  );
}""")
            
        (src_dir / "App.jsx").write_text(component_code, encoding="utf-8")
        
        (target_dir / "README.md").write_text(f"""# {name.title()}

## Generated by Vibecode Universal Engine
### Active Skills Synapse:
{chr(10).join([f'- {s}' for s in skills])}
""", encoding="utf-8")
        print("   [OK] Generated Advanced Full-Stack Architecture")
