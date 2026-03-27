import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import DashboardCard from "@/components/DashboardCard";
import { Calendar, Zap, AlertCircle, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Dashboard {
  id: string;
  name: string;
  widgets: number;
  lastUpdated: string;
}

export default function Dashboard() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalDashboards: 0,
    activeIntegrations: 0,
    lastSync: "Nunca",
    uptime: "99.9%",
  });

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setDashboards([
        {
          id: "1",
          name: "Visão Geral",
          widgets: 5,
          lastUpdated: "Há 2 minutos",
        },
        {
          id: "2",
          name: "Monitoramento",
          widgets: 8,
          lastUpdated: "Há 5 minutos",
        },
        {
          id: "3",
          name: "Tarefas",
          widgets: 3,
          lastUpdated: "Há 1 hora",
        },
      ]);

      setStats({
        totalDashboards: 3,
        activeIntegrations: 2,
        lastSync: "Há 2 minutos",
        uptime: "99.9%",
      });

      setLoading(false);
    }, 1000);
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Bem-vindo ao Kora Vision
            </p>
          </div>
          <Button className="bg-sidebar-primary text-sidebar-primary-foreground hover:bg-sidebar-primary/90">
            + Novo Dashboard
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <DashboardCard
            title="Dashboards"
            value={stats.totalDashboards}
            icon={<Activity size={24} />}
            trend={{ value: 0, isPositive: true }}
          />
          <DashboardCard
            title="Integrações Ativas"
            value={stats.activeIntegrations}
            icon={<Zap size={24} />}
            trend={{ value: 100, isPositive: true }}
          />
          <DashboardCard
            title="Última Sincronização"
            description={stats.lastSync}
            icon={<Calendar size={24} />}
          />
          <DashboardCard
            title="Disponibilidade"
            value={stats.uptime}
            icon={<AlertCircle size={24} />}
            trend={{ value: 0.1, isPositive: true }}
          />
        </div>

        {/* Dashboards List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-foreground">Meus Dashboards</h2>

          {loading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-20 bg-muted rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboards.map((dashboard) => (
                <Card
                  key={dashboard.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                >
                  <CardHeader>
                    <CardTitle className="text-lg">{dashboard.name}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">
                        {dashboard.widgets} widgets
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Atualizado {dashboard.lastUpdated}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  action: "Sincronização concluída",
                  source: "Google Calendar",
                  time: "Há 2 minutos",
                },
                {
                  action: "Widget adicionado",
                  source: "Jira Board",
                  time: "Há 15 minutos",
                },
                {
                  action: "Dashboard criado",
                  source: "Visão Geral",
                  time: "Há 1 hora",
                },
              ].map((activity, i) => (
                <div
                  key={i}
                  className="flex justify-between items-center py-2 border-b border-border last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {activity.action}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.source}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
