// src/components/SettingsForm.tsx
import React, { useState } from "react";
import { Form, Button, Card, Row, Col, Alert } from "react-bootstrap";

interface RobotSettings {
  maxSpeed: number;
  autonomousMode: boolean;
  pidValues: {
    p: number;
    i: number;
    d: number;
  };
  safetyThreshold: number;
  driveMode: "tank" | "arcade" | "mecanum";
}

interface SettingsFormProps {
  initialSettings: RobotSettings;
  onSettingsUpdate?: (settings: RobotSettings) => void;
}

const SettingsForm: React.FC<SettingsFormProps> = ({
  initialSettings,
  onSettingsUpdate,
}) => {
  const [settings, setSettings] = useState<RobotSettings>(initialSettings);
  const [message, setMessage] = useState<{ text: string; variant: string }>({
    text: "",
    variant: "info",
  });

  const handleSettingChange = <K extends keyof RobotSettings>(
    key: K,
    value: RobotSettings[K]
  ) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handlePIDChange = (
    key: keyof RobotSettings["pidValues"],
    value: number
  ) => {
    setSettings((prev) => ({
      ...prev,
      pidValues: {
        ...prev.pidValues,
        [key]: value,
      },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setMessage({
          text: "未授權，請重新登入",
          variant: "danger",
        });
        return;
      }

      setMessage({
        text: "設置成功更新",
        variant: "success",
      });

      if (onSettingsUpdate) {
        onSettingsUpdate(settings);
      }
    } catch (error) {
      console.error("Error updating settings:", error);
      setMessage({
        text: "更新失敗，請檢查網路連線",
        variant: "danger",
      });
    }
  };

  return (
    <Card>
      <Card.Header>
        <h4>機器人參數設置</h4>
      </Card.Header>
      <Card.Body>
        {message.text && (
          <Alert variant={message.variant as "success" | "danger" | "info"}>
            {message.text}
          </Alert>
        )}
        <Form onSubmit={handleSubmit}>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>最大行進速度</Form.Label>
                <Form.Control
                  type="number"
                  value={settings.maxSpeed}
                  onChange={(e) =>
                    handleSettingChange("maxSpeed", Number(e.target.value))
                  }
                  min={0}
                  max={100}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>安全臨界值</Form.Label>
                <Form.Control
                  type="number"
                  value={settings.safetyThreshold}
                  onChange={(e) =>
                    handleSettingChange(
                      "safetyThreshold",
                      Number(e.target.value)
                    )
                  }
                  min={0}
                  max={100}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>P 值</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  value={settings.pidValues.p}
                  onChange={(e) => handlePIDChange("p", Number(e.target.value))}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>I 值</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  value={settings.pidValues.i}
                  onChange={(e) => handlePIDChange("i", Number(e.target.value))}
                />
              </Form.Group>
            </Col>
            <Col md={4}>
              <Form.Group className="mb-3">
                <Form.Label>D 值</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  value={settings.pidValues.d}
                  onChange={(e) => handlePIDChange("d", Number(e.target.value))}
                />
              </Form.Group>
            </Col>
          </Row>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>驅動模式</Form.Label>
                <Form.Select
                  value={settings.driveMode}
                  onChange={(e) =>
                    handleSettingChange(
                      "driveMode",
                      e.target.value as "tank" | "arcade" | "mecanum"
                    )
                  }
                >
                  <option value="tank">坦克模式</option>
                  <option value="arcade">街機模式</option>
                  <option value="mecanum">全向輪模式</option>
                </Form.Select>
              </Form.Group>
            </Col>
            <Col md={6} className="d-flex align-items-end">
              <Form.Check
                type="switch"
                id="autonomousMode"
                label="自主模式"
                checked={settings.autonomousMode}
                onChange={() =>
                  handleSettingChange(
                    "autonomousMode",
                    !settings.autonomousMode
                  )
                }
              />
            </Col>
          </Row>

          <Button variant="primary" type="submit" className="w-100 mt-3">
            保存設置
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default SettingsForm;
