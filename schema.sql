-- avrkrcloud_app — live calls + history (written by cloudagi AGI)
CREATE TABLE IF NOT EXISTS live_calls (
  callid VARCHAR(32) NOT NULL PRIMARY KEY,
  tenantid VARCHAR(80) NOT NULL,
  agent_number VARCHAR(40) NULL,
  user_number VARCHAR(40) NULL,
  caller_id VARCHAR(128) NULL,
  direction VARCHAR(16) NOT NULL DEFAULT 'outbound',
  status VARCHAR(32) NOT NULL DEFAULT 'initiated',
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  linkedid VARCHAR(64) NULL,
  channel VARCHAR(128) NULL,
  INDEX idx_live_calls_tenant (tenantid),
  INDEX idx_live_calls_started (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS call_history (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  callid VARCHAR(32) NOT NULL,
  tenantid VARCHAR(80) NOT NULL,
  agent_number VARCHAR(40) NULL,
  user_number VARCHAR(40) NULL,
  caller_id VARCHAR(128) NULL,
  direction VARCHAR(16) NOT NULL DEFAULT 'outbound',
  status VARCHAR(32) NOT NULL DEFAULT 'completed',
  started_at DATETIME NOT NULL,
  ended_at DATETIME NOT NULL,
  duration_seconds INT UNSIGNED NULL,
  hangup_cause VARCHAR(64) NULL,
  INDEX idx_call_history_tenant_ended (tenantid, ended_at),
  INDEX idx_call_history_callid (callid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
