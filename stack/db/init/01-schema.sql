-- Schema for the observability demo mesh. For laptop simplicity every domain
-- shares one database (meshdb); a production data mesh would isolate each
-- domain's store. The observability story is identical either way — each service
-- still issues its own auto-traced Postgres spans under the request's trace.

-- order domain ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id     TEXT PRIMARY KEY,
    customer_id  TEXT NOT NULL,
    sku          TEXT NOT NULL,
    quantity     INT  NOT NULL,
    amount_cents BIGINT NOT NULL,
    status       TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- inventory domain -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS stock (
    sku      TEXT PRIMARY KEY,
    on_hand  INT  NOT NULL
);
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id TEXT PRIMARY KEY,
    order_id       TEXT NOT NULL,
    sku            TEXT NOT NULL,
    quantity       INT  NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- seed a few SKUs so a fresh stack can place an order immediately
INSERT INTO stock (sku, on_hand) VALUES
    ('WIDGET-001', 1000),
    ('GADGET-002', 500),
    ('GIZMO-003',  50)
ON CONFLICT (sku) DO NOTHING;

-- payment domain -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS authorizations (
    authorization_id TEXT PRIMARY KEY,
    order_id         TEXT UNIQUE NOT NULL,
    customer_id      TEXT NOT NULL,
    amount_cents     BIGINT NOT NULL,
    authorized       BOOLEAN NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- shipping domain ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    order_id    TEXT NOT NULL,
    sku         TEXT NOT NULL,
    quantity    INT  NOT NULL,
    status      TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- review domain --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    sku       TEXT NOT NULL,
    rating    INT  NOT NULL,
    body      TEXT NOT NULL
);
INSERT INTO reviews (review_id, sku, rating, body) VALUES
    ('r1', 'WIDGET-001', 5, 'Excellent widget, ships fast.'),
    ('r2', 'WIDGET-001', 4, 'Solid, would buy again.'),
    ('r3', 'GADGET-002', 3, 'Does the job.')
ON CONFLICT (review_id) DO NOTHING;
