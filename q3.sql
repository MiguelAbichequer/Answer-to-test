CREATE DATABASE stack;
USE stack;
SET GLOBAL local_infile = 1;

-- criar tabelas
CREATE TABLE operadoras_cadastrais (
    registro_ans VARCHAR(20),
    cnpj VARCHAR(14) PRIMARY KEY,
    razao_social VARCHAR(255),
    modalidade VARCHAR(100),
    uf CHAR(2)
);

CREATE TABLE despesas_consolidadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cnpj VARCHAR(14),
    trimestre INT,
    ano INT,
    valor_despesa DECIMAL(18,2),
    FOREIGN KEY (cnpj) REFERENCES operadoras_cadastrais(cnpj)
);

CREATE TABLE despesas_agregadas (
    razao_social VARCHAR(255),
    uf CHAR(2),
    total_despesas DECIMAL(18,2),
    media_despesas DECIMAL(18,2),
    desvio_padrao DECIMAL(18,2),
    PRIMARY KEY (razao_social, uf)
);

CREATE INDEX idx_despesas_cnpj ON despesas_consolidadas(cnpj);
CREATE INDEX idx_despesas_periodo ON despesas_consolidadas(ano, trimestre);
-- importar dados
LOAD DATA LOCAL INFILE 'C:/Users/Usuário/Desktop/GITinf/Answer-to-test/Relatorio_cadop.csv'
INTO TABLE operadoras_cadastrais
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/Users/Usuário/Desktop/GITinf/Answer-to-test/consolidado_despesas.csv'
INTO TABLE despesas_consolidadas
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'C:/Users/Usuário/Desktop/GITinf/Answer-to-test/despesas_agregadas.csv'
INTO TABLE despesas_agregadas
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
