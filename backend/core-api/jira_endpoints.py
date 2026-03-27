"""
Endpoints da API para Jira
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.jira_integration import JiraCloudIntegration

router = APIRouter(prefix="/api/v1/jira", tags=["jira"])


class JiraConfig(BaseModel):
    """Configuração do Jira"""
    email: str
    api_token: str
    site_url: str
    project_key: str


class JiraTestRequest(BaseModel):
    """Request para testar conexão"""
    email: str
    api_token: str
    site_url: str


@router.post("/test-connection")
async def test_jira_connection(request: JiraTestRequest):
    """
    Testa conexão com Jira
    
    Exemplo:
    {
        "email": "ismael.sousa@paytrack.com.br",
        "api_token": "ATATT3xFfGF0zUHXGcU-4lMrVGLrmdsYx_kL0yO7A9twhBHzre7boMuL_V8KDxKQa_IqD5Zp61RDVvI4HzcvKIwvrMN1kq80JGdKmZmKxYfpPcGFJIYizoYp2lqbbsua51mgukxu4dLyfEaSW9axQJNF-3XInuTTYWRhYNdxFMCacn5IUBwTfEQ=00B87E60",
        "site_url": "paytrack"
    }
    """
    try:
        jira = JiraCloudIntegration(
            email=request.email,
            api_token=request.api_token,
            site_url=request.site_url
        )
        
        result = jira.test_connection()
        
        if result.get('success'):
            return {
                "success": True,
                "message": result.get('message'),
                "user": result.get('user')
            }
        else:
            raise HTTPException(status_code=401, detail=result.get('message'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard")
async def get_jira_dashboard(config: JiraConfig):
    """
    Retorna dados do dashboard Jira
    
    Exemplo:
    {
        "email": "ismael.sousa@paytrack.com.br",
        "api_token": "ATATT3xFfGF0zUHXGcU-4lMrVGLrmdsYx_kL0yO7A9twhBHzre7boMuL_V8KDxKQa_IqD5Zp61RDVvI4HzcvKIwvrMN1kq80JGdKmZmKxYfpPcGFJIYizoYp2lqbbsua51mgukxu4dLyfEaSW9axQJNF-3XInuTTYWRhYNdxFMCacn5IUBwTfEQ=00B87E60",
        "site_url": "paytrack",
        "project_key": "CLOUDOPS"
    }
    """
    try:
        jira = JiraCloudIntegration(
            email=config.email,
            api_token=config.api_token,
            site_url=config.site_url
        )
        
        data = jira.get_dashboard_data(config.project_key)
        
        if data.get('success'):
            return data
        else:
            raise HTTPException(status_code=500, detail=data.get('message'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/issues")
async def get_jira_issues(config: JiraConfig, issue_type: Optional[str] = None):
    """
    Retorna issues de um projeto
    
    Exemplo:
    {
        "email": "ismael.sousa@paytrack.com.br",
        "api_token": "ATATT3xFfGF0zUHXGcU-4lMrVGLrmdsYx_kL0yO7A9twhBHzre7boMuL_V8KDxKQa_IqD5Zp61RDVvI4HzcvKIwvrMN1kq80JGdKmZmKxYfpPcGFJIYizoYp2lqbbsua51mgukxu4dLyfEaSW9axQJNF-3XInuTTYWRhYNdxFMCacn5IUBwTfEQ=00B87E60",
        "site_url": "paytrack",
        "project_key": "CLOUDOPS"
    }
    """
    try:
        jira = JiraCloudIntegration(
            email=config.email,
            api_token=config.api_token,
            site_url=config.site_url
        )
        
        data = jira.get_issues(config.project_key, issue_type)
        
        if data.get('success'):
            return data
        else:
            raise HTTPException(status_code=500, detail=data.get('message'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics")
async def get_jira_metrics(config: JiraConfig):
    """
    Retorna métricas do projeto
    
    Exemplo:
    {
        "email": "ismael.sousa@paytrack.com.br",
        "api_token": "ATATT3xFfGF0zUHXGcU-4lMrVGLrmdsYx_kL0yO7A9twhBHzre7boMuL_V8KDxKQa_IqD5Zp61RDVvI4HzcvKIwvrMN1kq80JGdKmZmKxYfpPcGFJIYizoYp2lqbbsua51mgukxu4dLyfEaSW9axQJNF-3XInuTTYWRhYNdxFMCacn5IUBwTfEQ=00B87E60",
        "site_url": "paytrack",
        "project_key": "CLOUDOPS"
    }
    """
    try:
        jira = JiraCloudIntegration(
            email=config.email,
            api_token=config.api_token,
            site_url=config.site_url
        )
        
        data = jira.get_metrics(config.project_key)
        
        if data.get('success'):
            return data
        else:
            raise HTTPException(status_code=500, detail=data.get('message'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sla-at-risk")
async def get_jira_sla_at_risk(config: JiraConfig):
    """
    Retorna issues em risco de SLA
    
    Exemplo:
    {
        "email": "ismael.sousa@paytrack.com.br",
        "api_token": "ATATT3xFfGF0zUHXGcU-4lMrVGLrmdsYx_kL0yO7A9twhBHzre7boMuL_V8KDxKQa_IqD5Zp61RDVvI4HzcvKIwvrMN1kq80JGdKmZmKxYfpPcGFJIYizoYp2lqbbsua51mgukxu4dLyfEaSW9axQJNF-3XInuTTYWRhYNdxFMCacn5IUBwTfEQ=00B87E60",
        "site_url": "paytrack",
        "project_key": "CLOUDOPS"
    }
    """
    try:
        jira = JiraCloudIntegration(
            email=config.email,
            api_token=config.api_token,
            site_url=config.site_url
        )
        
        data = jira.get_sla_at_risk(config.project_key)
        
        return {
            "success": True,
            "sla_at_risk": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
