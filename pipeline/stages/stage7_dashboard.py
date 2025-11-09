"""
Stage 7: Dashboard & Alerts
Prepare data for dashboard and generate alerts
"""

import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.append('..')
from config import DB_CONFIG

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, smtp_server=None, smtp_port=None, sender_email=None, sender_password=None):
        self.smtp_server = smtp_server or 'smtp.gmail.com'
        self.smtp_port = smtp_port or 587
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.alerts = []
    
    def generate_alerts(self, decisions_df):
        """
        Generate alerts based on priority levels
        
        Args:
            decisions_df: Decisions dataframe
        
        Returns:
            list: List of alerts
        """
        alerts = []
        
        # CRITICAL alerts
        critical_equipment = decisions_df[decisions_df['priority_level'] == 'CRITICAL']
        for _, row in critical_equipment.iterrows():
            alert = {
                'level': 'CRITICAL',
                'equipment_id': row['equipment_id'],
                'message': f"URGENT: {row['equipment_id']} requires immediate maintenance. Failure probability: {row['failure_probability']*100:.0f}%, RUL: {row['rul_days']} days",
                'timestamp': datetime.now(),
                'action': 'EMAIL_SMS'
            }
            alerts.append(alert)
        
        # HIGH alerts
        high_equipment = decisions_df[decisions_df['priority_level'] == 'HIGH']
        for _, row in high_equipment.iterrows():
            alert = {
                'level': 'HIGH',
                'equipment_id': row['equipment_id'],
                'message': f"HIGH PRIORITY: {row['equipment_id']} maintenance recommended within 7 days. Failure probability: {row['failure_probability']*100:.0f}%",
                'timestamp': datetime.now(),
                'action': 'DASHBOARD'
            }
            alerts.append(alert)
        
        self.alerts = alerts
        return alerts
    
    def send_email_alert(self, recipient_email, subject, body):
        """
        Send email alert
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body
        
        Returns:
            bool: Success status
        """
        if not self.sender_email or not self.sender_password:
            print("[WARN] Email credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            print(f"[OK] Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False
    
    def print_alerts(self):
        """Print alerts to console"""
        if not self.alerts:
            print("[INFO] No alerts")
            return
        
        print(f"\n[ALERTS] {len(self.alerts)} alerts generated:")
        for alert in self.alerts:
            print(f"  [{alert['level']}] {alert['message']}")

def prepare_dashboard_data(decisions_df):
    """
    Prepare data for dashboard visualization
    
    Args:
        decisions_df: Decisions dataframe
    
    Returns:
        dict: Dashboard data
    """
    dashboard_data = {
        'overview': {
            'total_equipment': len(decisions_df),
            'critical_count': len(decisions_df[decisions_df['priority_level'] == 'CRITICAL']),
            'high_count': len(decisions_df[decisions_df['priority_level'] == 'HIGH']),
            'medium_count': len(decisions_df[decisions_df['priority_level'] == 'MEDIUM']),
            'low_count': len(decisions_df[decisions_df['priority_level'] == 'LOW']),
            'normal_count': len(decisions_df[decisions_df['priority_level'] == 'NORMAL']),
            'fleet_health': (1 - decisions_df['failure_probability'].mean()) * 100,
            'avg_risk_score': decisions_df['risk_score'].mean()
        },
        'priority_list': decisions_df[decisions_df['priority_level'].isin(['CRITICAL', 'HIGH'])].sort_values(
            'risk_score', ascending=False
        )[['equipment_id', 'equipment_type', 'priority_level', 'risk_score', 'rul_days', 'recommendation_text']].head(20),
        'sensor_trends': {
            'avg_failure_probability': decisions_df['failure_probability'].mean(),
            'avg_rul_days': decisions_df['rul_days'].mean(),
            'avg_anomaly_score': decisions_df['anomaly_score'].mean(),
            'avg_confidence_score': decisions_df['confidence_score'].mean()
        },
        'health_scores': decisions_df[['equipment_id', 'equipment_type', 'risk_score']].sort_values(
            'risk_score', ascending=True
        ).head(20),
        'cost_analysis': {
            'total_maintenance_cost': decisions_df['estimated_maintenance_cost'].sum(),
            'total_failure_cost': decisions_df['estimated_failure_cost'].sum(),
            'total_net_benefit': decisions_df['net_benefit'].sum(),
            'avg_roi': decisions_df['roi'].mean()
        }
    }
    
    return dashboard_data

def generate_html_dashboard(dashboard_data):
    """
    Generate HTML dashboard
    
    Args:
        dashboard_data: Dashboard data dictionary
    
    Returns:
        str: HTML content
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Predictive Maintenance Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .metric {{ background-color: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ font-size: 12px; color: #7f8c8d; }}
            .critical {{ color: #e74c3c; }}
            .high {{ color: #f39c12; }}
            .medium {{ color: #f1c40f; }}
            .low {{ color: #27ae60; }}
            .table {{ width: 100%; border-collapse: collapse; background-color: white; margin: 20px 0; }}
            .table th {{ background-color: #34495e; color: white; padding: 10px; text-align: left; }}
            .table td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
            .table tr:hover {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Predictive Maintenance Dashboard</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <h2>Fleet Overview</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                <div class="metric">
                    <div class="metric-label">Total Equipment</div>
                    <div class="metric-value">{dashboard_data['overview']['total_equipment']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Critical</div>
                    <div class="metric-value critical">{dashboard_data['overview']['critical_count']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Fleet Health</div>
                    <div class="metric-value">{dashboard_data['overview']['fleet_health']:.1f}%</div>
                </div>
            </div>
            
            <h2>Priority Distribution</h2>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;">
                <div class="metric">
                    <div class="metric-label">Critical</div>
                    <div class="metric-value critical">{dashboard_data['overview']['critical_count']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">High</div>
                    <div class="metric-value high">{dashboard_data['overview']['high_count']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Medium</div>
                    <div class="metric-value medium">{dashboard_data['overview']['medium_count']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Low</div>
                    <div class="metric-value low">{dashboard_data['overview']['low_count']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Normal</div>
                    <div class="metric-value">{dashboard_data['overview']['normal_count']}</div>
                </div>
            </div>
            
            <h2>Cost Analysis</h2>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                <div class="metric">
                    <div class="metric-label">Maintenance Cost</div>
                    <div class="metric-value">${dashboard_data['cost_analysis']['total_maintenance_cost']:.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Failure Cost</div>
                    <div class="metric-value">${dashboard_data['cost_analysis']['total_failure_cost']:.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Net Benefit</div>
                    <div class="metric-value">${dashboard_data['cost_analysis']['total_net_benefit']:.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Avg ROI</div>
                    <div class="metric-value">{dashboard_data['cost_analysis']['avg_roi']:.1f}%</div>
                </div>
            </div>
            
            <h2>Top Priority Equipment</h2>
            <table class="table">
                <tr>
                    <th>Equipment ID</th>
                    <th>Type</th>
                    <th>Priority</th>
                    <th>Risk Score</th>
                    <th>RUL (days)</th>
                </tr>
    """
    
    for _, row in dashboard_data['priority_list'].iterrows():
        priority_class = row['priority_level'].lower()
        html += f"""
                <tr>
                    <td>{row['equipment_id']}</td>
                    <td>{row['equipment_type']}</td>
                    <td class="{priority_class}">{row['priority_level']}</td>
                    <td>{row['risk_score']:.1f}</td>
                    <td>{row['rul_days']}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

def run_stage7(decisions_data):
    """Execute Stage 7: Dashboard & Alerts"""
    print("\n" + "="*60)
    print("STAGE 7: DASHBOARD & ALERTS")
    print("="*60)
    
    try:
        decisions_df = decisions_data['decisions']
        
        # Step 1: Generate alerts
        print("\n[STEP 1] Generating alerts...")
        alert_manager = AlertManager()
        alerts = alert_manager.generate_alerts(decisions_df)
        alert_manager.print_alerts()
        
        # Step 2: Prepare dashboard data
        print("\n[STEP 2] Preparing dashboard data...")
        dashboard_data = prepare_dashboard_data(decisions_df)
        print(f"   Dashboard data prepared")
        
        # Step 3: Generate HTML dashboard
        print("[STEP 3] Generating HTML dashboard...")
        html_content = generate_html_dashboard(dashboard_data)
        
        # Save HTML to file
        dashboard_file = 'dashboard.html'
        with open(dashboard_file, 'w') as f:
            f.write(html_content)
        print(f"   [OK] Dashboard saved to {dashboard_file}")
        
        # Summary
        print(f"\n[COMPLETE] Stage 7 Complete!")
        print(f"   Alerts generated: {len(alerts)}")
        print(f"   Critical alerts: {len([a for a in alerts if a['level'] == 'CRITICAL'])}")
        print(f"   High alerts: {len([a for a in alerts if a['level'] == 'HIGH'])}")
        print(f"   Dashboard file: {dashboard_file}")
        
        return {
            'success': True,
            'alerts': alerts,
            'dashboard_data': dashboard_data,
            'dashboard_file': dashboard_file
        }
        
    except Exception as e:
        print(f"[ERROR] Stage 7 failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    from stage4_risk_scoring import run_stage4
    from stage3_ensemble_prediction import run_stage3
    from stage2_enhanced_features import run_stage2
    from stage1_data_ingestion import run_stage1
    
    data = run_stage1()
    features_data = run_stage2(data)
    predictions_data = run_stage3(features_data)
    decisions_data = run_stage4(predictions_data)
    
    result = run_stage7(decisions_data)
    print(f"\nDashboard result: {result['success']}")
