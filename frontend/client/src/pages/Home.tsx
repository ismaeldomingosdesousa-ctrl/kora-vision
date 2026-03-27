import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { ArrowRight, Zap, BarChart3, Gauge } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      {/* Navigation */}
      <nav className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container flex items-center justify-between h-16">
          <div className="text-2xl font-bold text-foreground">Kora Vision</div>
          <div className="flex gap-4">
            <Link href="/dashboard">
              <Button variant="ghost">Dashboard</Button>
            </Link>
            <Link href="/dashboard">
              <Button>Entrar</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container py-20 md:py-32">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground leading-tight">
            Seu Centro de Operações Inteligente
          </h1>
          <p className="text-xl text-muted-foreground">
            Unifique todos os seus serviços em um único dashboard. Sincronize
            calendários, tarefas, métricas e muito mais.
          </p>
          <div className="flex gap-4 justify-center pt-4">
            <Link href="/dashboard">
              <Button size="lg" className="gap-2">
                Começar Agora
                <ArrowRight size={20} />
              </Button>
            </Link>
            <Button size="lg" variant="outline">
              Saiba Mais
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container py-20">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Recursos Poderosos
          </h2>
          <p className="text-lg text-muted-foreground">
            Tudo que você precisa para gerenciar suas operações
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              icon: <Zap className="w-12 h-12 text-sidebar-primary" />,
              title: "Integrações Rápidas",
              description:
                "Conecte Google Calendar, Jira, Datadog, Dynatrace e WhatsApp em segundos",
            },
            {
              icon: <BarChart3 className="w-12 h-12 text-sidebar-primary" />,
              title: "Dashboards Personalizados",
              description:
                "Crie dashboards com widgets customizados para suas necessidades",
            },
            {
              icon: <Gauge className="w-12 h-12 text-sidebar-primary" />,
              title: "Real-time Updates",
              description:
                "Receba atualizações em tempo real de todos os seus serviços",
            },
          ].map((feature, i) => (
            <div
              key={i}
              className="bg-card border border-border rounded-lg p-8 hover:shadow-lg transition-shadow"
            >
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Integrations Section */}
      <section className="container py-20">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-foreground mb-4">
            Serviços Suportados
          </h2>
          <p className="text-lg text-muted-foreground">
            Integre com seus ferramentas favoritas
          </p>
        </div>

        <div className="grid md:grid-cols-5 gap-4">
          {[
            "Google Calendar",
            "Jira",
            "Datadog",
            "Dynatrace",
            "WhatsApp",
          ].map((service, i) => (
            <div
              key={i}
              className="bg-card border border-border rounded-lg p-6 text-center hover:shadow-lg transition-shadow"
            >
              <p className="font-medium text-foreground">{service}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="container py-20">
        <div className="bg-sidebar-primary text-sidebar-primary-foreground rounded-lg p-12 text-center space-y-6">
          <h2 className="text-4xl font-bold">
            Pronto para começar?
          </h2>
          <p className="text-lg opacity-90">
            Junte-se a milhares de usuários que já estão otimizando suas operações
          </p>
          <Link href="/dashboard">
            <Button
              size="lg"
              className="bg-sidebar-primary-foreground text-sidebar-primary hover:bg-sidebar-primary-foreground/90"
            >
              Acessar Dashboard
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-background mt-20">
        <div className="container py-8">
          <div className="text-center text-muted-foreground">
            <p>&copy; 2026 Kora Vision. Todos os direitos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
