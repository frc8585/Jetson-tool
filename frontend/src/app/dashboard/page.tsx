// src/app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import { Card, Row, Col, Spinner } from "react-bootstrap";
import { fetchRobotStatus } from "@/lib/api";
import AuthGuard from "../../components/AuthGuard";

export default function DashboardPage() {
  interface RobotStatus {
    batteryVoltage: number;
    temperature: number;
    systemStatus: string;
  }

  const [status, setStatus] = useState<RobotStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStatus() {
      try {
        const robotStatus = await fetchRobotStatus();
        setStatus(robotStatus);
      } catch {
        // 處理錯誤
      } finally {
        setLoading(false);
      }
    }

    loadStatus();
    const interval = setInterval(loadStatus, 5000); // 每5秒更新一次
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <Spinner animation="border" />;
  }

  return (
    <AuthGuard>
      <div className="container mt-4">
        <h1>機器人即時狀態</h1>
        <Row>
          <Col md={4}>
            <Card>
              <Card.Header>電池電量</Card.Header>
              <Card.Body>{status?.batteryVoltage} V</Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card>
              <Card.Header>溫度</Card.Header>
              <Card.Body>{status?.temperature}°C</Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card>
              <Card.Header>系統狀態</Card.Header>
              <Card.Body>{status?.systemStatus}</Card.Body>
            </Card>
          </Col>
        </Row>
      </div>
    </AuthGuard>
  );
}
