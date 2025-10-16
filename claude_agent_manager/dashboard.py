"""
IMPROVEMENT #2: Real-time Progress Dashboard and Monitoring
Live web-based dashboard for monitoring agent activity and pipeline progress
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import threading

try:
    from flask import Flask, render_template, jsonify
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class DashboardServer:
    """
    Real-time monitoring dashboard

    Features:
    - Live agent status
    - Pipeline progress visualization
    - Performance metrics
    - Token usage tracking
    - Error monitoring
    """

    def __init__(self, agent_manager, port: int = 5000):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask required: pip install flask flask-socketio")

        self.agent_manager = agent_manager
        self.port = port

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'sales-pipeline-secret'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        self.metrics = {
            "opportunities_processed": 0,
            "opportunities_qualified": 0,
            "opportunities_closed": 0,
            "total_revenue_pipeline": 0.0,
            "avg_processing_time": 0.0,
            "success_rate": 0.0
        }

        self.activity_log: List[Dict[str, Any]] = []
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            return render_template('dashboard.html')

        @self.app.route('/api/stats')
        def get_stats():
            """Get current statistics"""
            stats = self.agent_manager.get_stats()

            return jsonify({
                "timestamp": datetime.now().isoformat(),
                "agent_stats": stats,
                "pipeline_metrics": self.metrics,
                "activity_log": self.activity_log[-50:]  # Last 50 activities
            })

        @self.app.route('/api/agents')
        def get_agents():
            """Get agent details"""
            stats = self.agent_manager.get_stats()
            return jsonify(stats.get('agent_stats', []))

        @self.app.route('/api/opportunities')
        def get_opportunities():
            """Get pipeline opportunities"""
            # This would integrate with your pipeline manager
            return jsonify({
                "total": self.metrics["opportunities_processed"],
                "qualified": self.metrics["opportunities_qualified"],
                "closed": self.metrics["opportunities_closed"]
            })

    def log_activity(self, activity_type: str, message: str, details: Dict = None):
        """Log activity for display"""
        self.activity_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "message": message,
            "details": details or {}
        })

        # Keep only last 1000 activities
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-1000:]

        # Emit to connected clients
        if FLASK_AVAILABLE:
            self.socketio.emit('activity', {
                "type": activity_type,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

    def update_metrics(self, **kwargs):
        """Update dashboard metrics"""
        self.metrics.update(kwargs)

        # Emit to connected clients
        if FLASK_AVAILABLE:
            self.socketio.emit('metrics_update', self.metrics)

    def start(self):
        """Start dashboard server"""
        def run_server():
            self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=False)

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

        print(f"\n✅ Dashboard running at http://localhost:{self.port}")
        print(f"   Open in your browser to monitor pipeline progress\n")


class ConsoleDashboard:
    """
    Terminal-based dashboard for systems without Flask

    Features:
    - Real-time console updates
    - Progress bars
    - Colored output
    - Activity stream
    """

    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.start_time = datetime.now()

    def print_header(self):
        """Print dashboard header"""
        print("\n" + "="*80)
        print("SALES PIPELINE DASHBOARD")
        print("="*80)

    def print_stats(self):
        """Print current statistics"""
        stats = self.agent_manager.get_stats()
        runtime = (datetime.now() - self.start_time).total_seconds()

        print(f"\n📊 SYSTEM STATUS (Runtime: {runtime:.0f}s)")
        print(f"   Active Agents: {stats['active_agents']}/{stats['total_agents']}")
        print(f"   Queue Size: {stats['queue_size']}")
        print(f"   Tasks Processed: {stats['total_tasks_processed']}")
        print(f"   Tasks Failed: {stats['total_tasks_failed']}")
        print(f"   Success Rate: {self._calculate_success_rate(stats):.1f}%")
        print(f"   Total Tokens: {stats['total_tokens_consumed']:,}")

    def print_agent_status(self):
        """Print agent status table"""
        stats = self.agent_manager.get_stats()

        print(f"\n🤖 AGENT STATUS")
        print("-"*80)
        print(f"{'Agent Name':<25} {'Status':<10} {'Tasks':<8} {'Tokens':<12}")
        print("-"*80)

        for agent in stats.get('agent_stats', []):
            status_emoji = "🟢" if agent['status'] == 'idle' else "🔴"
            print(f"{agent['name']:<25} {status_emoji} {agent['status']:<9} "
                  f"{agent['tasks_completed']:<8} {agent['total_tokens_used']:>11,}")

    def print_pipeline_progress(self, opportunities: List[Dict]):
        """Print pipeline progress"""
        print(f"\n📈 PIPELINE PROGRESS ({len(opportunities)} opportunities)")
        print("-"*80)

        stages = defaultdict(int)
        for opp in opportunities:
            stages[opp.get('stage', 'unknown')] += 1

        for stage, count in stages.items():
            bar = "█" * min(count, 40)
            print(f"{stage:<20} {bar} {count}")

    def _calculate_success_rate(self, stats: Dict) -> float:
        """Calculate success rate"""
        total = stats['total_tasks_processed'] + stats['total_tasks_failed']
        if total == 0:
            return 0.0
        return (stats['total_tasks_processed'] / total) * 100

    def update(self, opportunities: List[Dict] = None):
        """Update console display"""
        # Clear screen (cross-platform)
        print("\033[2J\033[H", end='')

        self.print_header()
        self.print_stats()
        self.print_agent_status()

        if opportunities:
            self.print_pipeline_progress(opportunities)

        print("\n" + "="*80)


# HTML Template for Web Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sales Pipeline Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric {
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        .agent-list {
            list-style: none;
            padding: 0;
        }
        .agent-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
        }
        .status-idle { background: #10b981; }
        .status-busy { background: #f59e0b; }
        .status-error { background: #ef4444; }
        .activity-log {
            max-height: 400px;
            overflow-y: auto;
            font-size: 13px;
        }
        .activity-item {
            padding: 8px;
            border-left: 3px solid #667eea;
            margin-bottom: 10px;
            background: #f9fafb;
        }
        .timestamp {
            color: #999;
            font-size: 11px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Sales Pipeline Dashboard</h1>
            <p>Real-time monitoring of AI agent cluster</p>
        </div>

        <div class="grid">
            <div class="card">
                <div class="metric" id="opportunities-processed">0</div>
                <div class="metric-label">Opportunities Processed</div>
            </div>
            <div class="card">
                <div class="metric" id="qualified-rate">0%</div>
                <div class="metric-label">Qualification Rate</div>
            </div>
            <div class="card">
                <div class="metric" id="active-agents">0</div>
                <div class="metric-label">Active Agents</div>
            </div>
            <div class="card">
                <div class="metric" id="total-tokens">0</div>
                <div class="metric-label">Tokens Consumed</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Agent Status</h3>
                <ul class="agent-list" id="agent-list"></ul>
            </div>
            <div class="card">
                <h3>Activity Log</h3>
                <div class="activity-log" id="activity-log"></div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();

        // Update metrics
        socket.on('metrics_update', (data) => {
            document.getElementById('opportunities-processed').textContent = data.opportunities_processed;
            document.getElementById('qualified-rate').textContent =
                ((data.opportunities_qualified / data.opportunities_processed) * 100).toFixed(1) + '%';
        });

        // Update activity log
        socket.on('activity', (data) => {
            const log = document.getElementById('activity-log');
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <strong>${data.type}</strong>: ${data.message}
                <div class="timestamp">${new Date(data.timestamp).toLocaleTimeString()}</div>
            `;
            log.insertBefore(item, log.firstChild);

            // Keep only last 50 items
            while (log.children.length > 50) {
                log.removeChild(log.lastChild);
            }
        });

        // Fetch initial stats
        async function updateStats() {
            const response = await fetch('/api/stats');
            const data = await response.json();

            // Update metrics
            document.getElementById('opportunities-processed').textContent =
                data.pipeline_metrics.opportunities_processed;
            document.getElementById('active-agents').textContent =
                data.agent_stats.active_agents;
            document.getElementById('total-tokens').textContent =
                data.agent_stats.total_tokens_consumed.toLocaleString();

            // Update agent list
            const agentList = document.getElementById('agent-list');
            agentList.innerHTML = data.agent_stats.agent_stats.map(agent => `
                <li class="agent-item">
                    <span>
                        <span class="status-dot status-${agent.status}"></span>
                        ${agent.name}
                    </span>
                    <span>${agent.tasks_completed} tasks</span>
                </li>
            `).join('');
        }

        // Update every 2 seconds
        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
"""

# Save HTML template
def create_dashboard_template():
    """Create dashboard HTML template file"""
    import os
    template_dir = "templates"
    os.makedirs(template_dir, exist_ok=True)

    with open(os.path.join(template_dir, "dashboard.html"), "w") as f:
        f.write(DASHBOARD_HTML)
