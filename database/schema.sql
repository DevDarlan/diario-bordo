-- Tabela para armazenar as viagens
CREATE TABLE IF NOT EXISTS viagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,                -- Formato DD/MM/YYYY
    hora_saida TEXT NOT NULL,          -- Formato HH:MM
    km_inicial INTEGER NOT NULL,
    destino TEXT NOT NULL,
    hora_chegada TEXT,                 -- Formato HH:MM (pode ser NULL)
    km_final INTEGER,                  -- Pode ser NULL
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gatilho para atualizar o timestamp quando a viagem for modificada
CREATE TRIGGER IF NOT EXISTS atualiza_timestamp
AFTER UPDATE ON viagens
FOR EACH ROW
BEGIN
    UPDATE viagens SET atualizado_em = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;