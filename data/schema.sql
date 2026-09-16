-- =============================================================
-- NaitPrais - Base de datos del cliente Tabaiba Stays
-- Motor: SQLite (las fechas se guardan como texto AAAA-MM-DD)
-- =============================================================

PRAGMA foreign_keys = ON;

-- Municipios donde trabaja la gestora
CREATE TABLE municipios (
    id_municipio  INTEGER PRIMARY KEY,
    nombre        TEXT NOT NULL,
    isla          TEXT NOT NULL,
    codigo_ine    TEXT NOT NULL UNIQUE      -- para cruzar con los datos del ISTAC
);

-- Viviendas que gestiona la empresa
CREATE TABLE viviendas (
    id_vivienda   INTEGER PRIMARY KEY,
    id_municipio  INTEGER NOT NULL REFERENCES municipios(id_municipio),
    num_registro  TEXT NOT NULL UNIQUE,     -- número del Registro General Turístico
    tipo          TEXT NOT NULL,            -- apartamento, casa o villa
    plazas        INTEGER NOT NULL,
    dormitorios   INTEGER NOT NULL,
    piscina       INTEGER NOT NULL,         -- 1 = sí, 0 = no
    vista_mar     INTEGER NOT NULL,         -- 1 = sí, 0 = no
    activa        INTEGER NOT NULL          -- 1 = se gestiona actualmente
);

-- Reservas de los huéspedes
CREATE TABLE reservas (
    id_reserva     INTEGER PRIMARY KEY,
    id_vivienda    INTEGER NOT NULL REFERENCES viviendas(id_vivienda),
    fecha_reserva  TEXT NOT NULL,
    fecha_entrada  TEXT NOT NULL,
    fecha_salida   TEXT NOT NULL,
    noches         INTEGER NOT NULL,
    num_huespedes  INTEGER NOT NULL,
    precio_noche   REAL NOT NULL,
    canal          TEXT NOT NULL,           -- Airbnb, Booking, Vrbo o Web
    pais_huesped   TEXT,
    puntuacion     INTEGER,                 -- de 1 a 5; vacío si no dejó reseña
    estado         TEXT NOT NULL            -- confirmada o cancelada
);

-- Precio publicado cada día para cada vivienda, se vendiera la noche o no
CREATE TABLE calendario_precios (
    id_vivienda   INTEGER NOT NULL REFERENCES viviendas(id_vivienda),
    fecha         TEXT NOT NULL,
    precio_noche  REAL NOT NULL,
    ocupada       INTEGER NOT NULL,         -- 1 = ocupada, 0 = libre
    PRIMARY KEY (id_vivienda, fecha)
);

-- Datos oficiales del ISTAC por municipio y mes
CREATE TABLE mercado_istac (
    id_municipio           INTEGER NOT NULL REFERENCES municipios(id_municipio),
    periodo                TEXT NOT NULL,   -- AAAA-MM
    viviendas_disponibles  INTEGER,
    viviendas_reservadas   INTEGER,         -- viviendas con al menos una reserva en el mes
    plazas                 INTEGER,
    tasa_vivienda_reservada REAL,           -- % de viviendas disponibles que tuvieron reserva
    estancia_media         REAL,            -- en noches
    ingresos               REAL,            -- en euros
    PRIMARY KEY (id_municipio, periodo)
);
