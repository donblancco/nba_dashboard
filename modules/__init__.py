# pages パッケージの初期化ファイル

# 各ページモジュールをインポート
try:
    from . import team_overview
    from . import scoring_analysis
    from . import advanced_analytics
    from . import team_comparison
    from . import correlation_analysis
    from . import data_explorer
    from . import salary_efficiency
except ImportError as e:
    # インポートエラーの場合、個別にインポートを試行
    print(f"Warning: Some page modules could not be imported: {e}")
    
    # 個別インポート
    try:
        from . import team_overview
    except ImportError:
        team_overview = None
    
    try:
        from . import scoring_analysis
    except ImportError:
        scoring_analysis = None
    
    try:
        from . import advanced_analytics
    except ImportError:
        advanced_analytics = None
    
    try:
        from . import team_comparison
    except ImportError:
        team_comparison = None
    
    try:
        from . import correlation_analysis
    except ImportError:
        correlation_analysis = None
    
    try:
        from . import data_explorer
    except ImportError:
        data_explorer = None
    
    try:
        from . import salary_efficiency
    except ImportError:
        salary_efficiency = None

__all__ = [
    'team_overview',
    'scoring_analysis', 
    'advanced_analytics',
    'team_comparison',
    'correlation_analysis',
    'data_explorer',
    'salary_efficiency'
]