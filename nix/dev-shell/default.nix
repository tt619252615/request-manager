{ inputs, ... }:

let
  self = inputs.self;
  nixpkgs = inputs.nixpkgs;
in {

  perSystem = { system, pkgs, lib, ... }: {
    _module.args.pkgs = import nixpkgs {
      inherit system;
    };

    devShells.default = pkgs.mkShell {
      name = "request-manager-dev";

      packages = with pkgs; [
        # Python 后端开发环境
        (python3.withPackages (p:
          with p; [
          # Web框架
          fastapi
          uvicorn
          pydantic
          pydantic-settings
          
          # 数据库
          sqlalchemy
          alembic
          psycopg2
          
          # 任务调度
          celery
          redis
          
          # HTTP客户端
          requests
          httpx
          
          # 工具库
          loguru
          python-jose
          passlib
          python-multipart
          pymysql
          # 开发工具
          yapf
          black
          pylint
          pytest
          pytest-asyncio
          ]))
        
        # Python 工具
        pyright
        ruff
        pre-commit
        
        # Node.js 前端开发环境
        nodejs_20
        nodePackages.pnpm
        nodePackages.typescript
        nodePackages.eslint
        nodePackages.prettier
        
        # 数据库服务
        postgresql_15
        redis
        
        # 开发工具
        docker
        docker-compose
        curl
        jq
        
        # 编辑器工具
        git
      ];

      shellHook = ''
        echo "🚀 RequestManager 开发环境已启动"
        echo "📦 Python: $(python --version)"
        echo "📦 Node.js: $(node --version)"
        echo "📦 pnpm: $(pnpm --version)"
        echo ""
        echo "💡 快速开始："
        echo "  - 启动后端开发服务器: cd backend && uvicorn app.main:app --reload"
        echo "  - 启动前端开发服务器: cd frontend && pnpm dev"
        echo "  - 初始化数据库: cd backend && alembic upgrade head"
        echo ""
        
        export PS1="$(echo -e '\uf3e2') {\[$(tput sgr0)\]\[\033[38;5;228m\]\w\[$(tput sgr0)\]\[\033[38;5;15m\]} (RequestManager) \\$ \[$(tput sgr0)\]"  
        export PYTHONPATH="$(pwd):$PYTHONPATH"
        
        # 数据库配置
        export DATABASE_URL="postgresql://localhost:5432/request_manager"
        export REDIS_URL="redis://localhost:6379"
        
        # 开发环境标识
        export NODE_ENV="development"
        export PYTHON_ENV="development"
      '';
    };
  };
}