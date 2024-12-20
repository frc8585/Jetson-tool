// src/app/settings/page.tsx
"use client";

import { useState } from "react";
import { Form, Button, Alert, Row, Col } from "react-bootstrap";
import { updateRobotSettings } from "@/lib/api";
import AuthGuard from "../../components/AuthGuard";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    maxSpeed: 0,
    pidValues: { p: 0, i: 0, d: 0 },
    autonomousMode: false,
  });
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setMessage("未授權，請重新登入");
        return;
      }

      await updateRobotSettings(settings, token);
      setMessage("設置成功更新");
    } catch {
      setMessage("更新失敗");
    }
  };

  return (
    <AuthGuard>
      <div className="container mt-4">
        <h1>機器人參數設置</h1>
        {message && <Alert variant="info">{message}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group>
            <Form.Label>最大速度</Form.Label>
            <Form.Control
              type="number"
              value={settings.maxSpeed}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  maxSpeed: Number(e.target.value),
                })
              }
            />
          </Form.Group>
          <Form.Group className="mt-3">
            <Form.Label>PID 控制值</Form.Label>
            <Row>
              <Col>
                <Form.Control
                  type="number"
                  placeholder="P值"
                  value={settings.pidValues.p}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      pidValues: {
                        ...settings.pidValues,
                        p: Number(e.target.value),
                      },
                    })
                  }
                />
              </Col>
              <Col>
                <Form.Control
                  type="number"
                  placeholder="I值"
                  value={settings.pidValues.i}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      pidValues: {
                        ...settings.pidValues,
                        i: Number(e.target.value),
                      },
                    })
                  }
                />
              </Col>
              <Col>
                <Form.Control
                  type="number"
                  placeholder="D值"
                  value={settings.pidValues.d}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      pidValues: {
                        ...settings.pidValues,
                        d: Number(e.target.value),
                      },
                    })
                  }
                />
              </Col>
            </Row>
          </Form.Group>
          <Form.Group className="mt-3">
            <Form.Check
              type="switch"
              label="自動模式"
              checked={settings.autonomousMode}
              onChange={() =>
                setSettings({
                  ...settings,
                  autonomousMode: !settings.autonomousMode,
                })
              }
            />
          </Form.Group>
          <Button variant="primary" type="submit" className="mt-3">
            保存設置
          </Button>
        </Form>
      </div>
    </AuthGuard>
  );
}
