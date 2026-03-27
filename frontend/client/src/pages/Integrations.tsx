import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Calendar,
  Zap,
  BarChart3,
  MessageCircle,
  Plus,
  Trash2,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

interface Integration {
  id: string;
  name: string;
  type: string;
  status: "connected" | "disconnected" | "error";
  lastSync?: string;
  icon: React.ReactNode;
}

const availableIntegrations = [
  {
    type: "google_calendar",
    name: "Google Calendar",
    description: "Sincronize seus eventos de calendário",
    icon: <Calendar className="w-8 h-8" />,
  },
  {
    type: "jira",
    name: "Jira",
    description: "Acompanhe suas issues e tarefas",
    icon: <Zap className="w-8 h-8" />,
  },
  {
    type: "datadog",
    name: "Datadog",
    description: "Monitore suas métricas",
    icon: <BarChart3 className="w-8 h-8" />,
  },
  {
    type: "dynatrace",
    name: "Dynatrace",
    description: "APM e análise de performance",
    icon: <BarChart3 className="w-8 h-8" />,
  },
  {
    type: "whatsapp",
    name: "WhatsApp",
    description: "Receba notificações via WhatsApp",
    icon: <MessageCircle className="w-8 h-8" />,
  },
];

export default function Integrations() {
  const [connectedIntegrations, setConnectedIntegrations] = useState<
    Integration[]
  >([
    {
      id: "1",
      name: "Meu Calendário",
      type: "google_calendar",
      status: "connected",
      lastSync: "Há 2 minutos",
      icon: <Calendar className="w-6 h-6" />,
    },
    {
      id: "2",
      name: "Projeto A",
      type: "jira",
      status: "connected",
      lastSync: "Há 5 minutos",
      icon: <Zap className="w-6 h-6" />,
    },
  ]);

  const handleRemoveIntegration = (id: string) => {
    setConnectedIntegrations(
      connectedIntegrations.filter((i) => i.id !== id)
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "text-green-600";
      case "error":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle className="w-5 h-5" />;
      case "error":
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Integrações</h1>
          <p className="text-muted-foreground mt-1">
            Conecte seus serviços favoritos
          </p>
        </div>

        {/* Connected Integrations */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-foreground">
            Integrações Conectadas
          </h2>

          {connectedIntegrations.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-muted-foreground">
                  Nenhuma integração conectada ainda
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {connectedIntegrations.map((integration) => (
                <Card key={integration.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="text-muted-foreground">
                          {integration.icon}
                        </div>
                        <div>
                          <p className="font-medium text-foreground">
                            {integration.name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            Sincronizado {integration.lastSync}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div
                          className={`flex items-center gap-1 ${getStatusColor(
                            integration.status
                          )}`}
                        >
                          {getStatusIcon(integration.status)}
                          <span className="text-sm capitalize">
                            {integration.status === "connected"
                              ? "Conectado"
                              : "Desconectado"}
                          </span>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            handleRemoveIntegration(integration.id)
                          }
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Available Integrations */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-foreground">
            Serviços Disponíveis
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableIntegrations.map((service) => {
              const isConnected = connectedIntegrations.some(
                (i) => i.type === service.type
              );

              return (
                <Card
                  key={service.type}
                  className="hover:shadow-lg transition-shadow"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="text-muted-foreground">
                        {service.icon}
                      </div>
                      {isConnected && (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                    </div>
                    <CardTitle className="text-lg mt-2">
                      {service.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground mb-4">
                      {service.description}
                    </p>
                    <Button
                      className="w-full"
                      variant={isConnected ? "outline" : "default"}
                      disabled={isConnected}
                    >
                      {isConnected ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Conectado
                        </>
                      ) : (
                        <>
                          <Plus className="w-4 h-4 mr-2" />
                          Conectar
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
