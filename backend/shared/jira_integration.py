"""
Integração Real com Jira Service Manager Cloud
Conecta à API Jira Cloud usando email e API Token
"""

import requests
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class JiraCloudIntegration:
    """Integração real com Jira Cloud"""
    
    def __init__(self, email: str, api_token: str, site_url: str):
        """
        Inicializa integração com Jira Cloud
        
        Args:
            email: Email da conta Jira
            api_token: API Token gerado no Jira
            site_url: URL do site (ex: paytrack para paytrack.atlassian.net)
        """
        self.email = email
        self.api_token = api_token
        self.site_url = site_url
        self.base_url = f"https://{site_url}.atlassian.net/rest/api/3"
        
        # Criar header de autenticação (Basic Auth)
        credentials = f"{email}:{api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict:
        """Testa conexão com Jira"""
        try:
            response = requests.get(
                f"{self.base_url}/myself",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": f"Conectado como {user_data.get('displayName')}",
                    "user": user_data.get('emailAddress')
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }
    
    def get_issues(self, project_key: str, issue_type: Optional[str] = None) -> Dict:
        """
        Busca issues de um projeto
        
        Args:
            project_key: Chave do projeto (ex: CLOUDOPS)
            issue_type: Tipo de issue (Request, Incident, etc)
        
        Returns:
            Dict com issues encontradas
        """
        try:
            # Montar JQL
            jql = f"project = {project_key}"
            if issue_type:
                jql += f" AND type = {issue_type}"
            
            params = {
                "jql": jql,
                "maxResults": 100,
                "fields": [
                    "key",
                    "summary",
                    "status",
                    "priority",
                    "created",
                    "updated",
                    "duedate",
                    "assignee",
                    "customfield_10037"  # SLA
                ]
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = []
                
                for issue in data.get('issues', []):
                    fields = issue.get('fields', {})
                    issues.append({
                        "key": issue.get('key'),
                        "summary": fields.get('summary'),
                        "status": fields.get('status', {}).get('name'),
                        "priority": fields.get('priority', {}).get('name'),
                        "created": fields.get('created'),
                        "updated": fields.get('updated'),
                        "duedate": fields.get('duedate'),
                        "assignee": fields.get('assignee', {}).get('displayName'),
                        "type": fields.get('issuetype', {}).get('name')
                    })
                
                return {
                    "success": True,
                    "total": data.get('total', 0),
                    "issues": issues
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro: {response.status_code}",
                    "issues": []
                }
        except Exception as e:
            logger.error(f"Erro ao buscar issues: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "issues": []
            }
    
    def get_metrics(self, project_key: str) -> Dict:
        """
        Calcula métricas do projeto
        
        Args:
            project_key: Chave do projeto
        
        Returns:
            Dict com métricas
        """
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # Volume diário
            jql_daily = f"project = {project_key} AND created >= {today}"
            response_daily = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={"jql": jql_daily, "maxResults": 0},
                timeout=10
            )
            daily_count = response_daily.json().get('total', 0) if response_daily.status_code == 200 else 0
            
            # Volume semanal
            jql_weekly = f"project = {project_key} AND created >= {week_ago}"
            response_weekly = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={"jql": jql_weekly, "maxResults": 0},
                timeout=10
            )
            weekly_count = response_weekly.json().get('total', 0) if response_weekly.status_code == 200 else 0
            
            # Volume mensal
            jql_monthly = f"project = {project_key} AND created >= {month_ago}"
            response_monthly = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={"jql": jql_monthly, "maxResults": 0},
                timeout=10
            )
            monthly_count = response_monthly.json().get('total', 0) if response_monthly.status_code == 200 else 0
            
            return {
                "success": True,
                "daily": daily_count,
                "weekly": weekly_count,
                "monthly": monthly_count
            }
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {str(e)}")
            return {
                "success": False,
                "daily": 0,
                "weekly": 0,
                "monthly": 0
            }
    
    def get_sla_at_risk(self, project_key: str) -> List[Dict]:
        """
        Busca issues em risco de SLA
        
        Args:
            project_key: Chave do projeto
        
        Returns:
            Lista de issues em risco
        """
        try:
            # Buscar issues com status que indica risco
            jql = f"project = {project_key} AND status != Done AND status != Closed"
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params={
                    "jql": jql,
                    "maxResults": 50,
                    "fields": ["key", "summary", "duedate", "priority"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                at_risk = []
                now = datetime.now()
                
                for issue in response.json().get('issues', []):
                    fields = issue.get('fields', {})
                    duedate = fields.get('duedate')
                    
                    if duedate:
                        due = datetime.strptime(duedate, "%Y-%m-%d")
                        hours_until_due = (due - now).total_seconds() / 3600
                        
                        # Se vence em menos de 24 horas, está em risco
                        if 0 < hours_until_due < 24:
                            at_risk.append({
                                "key": issue.get('key'),
                                "summary": fields.get('summary'),
                                "duedate": duedate,
                                "hours_until_due": round(hours_until_due, 1),
                                "priority": fields.get('priority', {}).get('name')
                            })
                
                return at_risk
            else:
                return []
        except Exception as e:
            logger.error(f"Erro ao buscar issues em risco: {str(e)}")
            return []
    
    def get_dashboard_data(self, project_key: str) -> Dict:
        """
        Retorna todos os dados necessários para o dashboard
        
        Args:
            project_key: Chave do projeto
        
        Returns:
            Dict com todos os dados
        """
        try:
            # Buscar requests
            requests_data = self.get_issues(project_key, "Service Request")
            requests_count = requests_data.get('total', 0) if requests_data.get('success') else 0
            
            # Buscar incidentes
            incidents_data = self.get_issues(project_key, "Incident")
            incidents_count = incidents_data.get('total', 0) if incidents_data.get('success') else 0
            
            # Buscar métricas
            metrics = self.get_metrics(project_key)
            
            # Buscar issues em risco
            at_risk = self.get_sla_at_risk(project_key)
            
            return {
                "success": True,
                "project": project_key,
                "issues": {
                    "total_requests": requests_count,
                    "total_incidents": incidents_count,
                    "total": requests_count + incidents_count
                },
                "metrics": {
                    "daily": metrics.get('daily', 0),
                    "weekly": metrics.get('weekly', 0),
                    "monthly": metrics.get('monthly', 0)
                },
                "sla_at_risk": at_risk,
                "sla_at_risk_count": len(at_risk),
                "recent_issues": (requests_data.get('issues', []) + incidents_data.get('issues', []))[:5]
            }
        except Exception as e:
            logger.error(f"Erro ao buscar dados do dashboard: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
