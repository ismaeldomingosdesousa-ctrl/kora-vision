import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import React from "react";

interface DashboardCardProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  value?: string | number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  children?: React.ReactNode;
}

export default function DashboardCard({
  title,
  description,
  icon,
  value,
  trend,
  children,
}: DashboardCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          {icon && <div className="text-muted-foreground">{icon}</div>}
        </div>
      </CardHeader>
      <CardContent>
        {value !== undefined && (
          <div className="flex items-baseline gap-2 mb-4">
            <span className="text-3xl font-bold text-foreground">{value}</span>
            {trend && (
              <span
                className={`text-sm font-medium ${
                  trend.isPositive ? "text-green-600" : "text-red-600"
                }`}
              >
                {trend.isPositive ? "+" : ""}{trend.value}%
              </span>
            )}
          </div>
        )}
        {children}
      </CardContent>
    </Card>
  );
}
