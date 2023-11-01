CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_points_place ON points (place);

CREATE INDEX idx_lines_highway ON lines (highway);
CREATE INDEX idx_lines_waterway ON lines (waterway);
CREATE INDEX idx_lines_other ON lines USING GIST(other_tags gist_trgm_ops);

CREATE INDEX idx_multipolygons_natural ON multipolygons ("natural");
CREATE INDEX idx_multipolygons_landuse ON multipolygons (landuse, aeroway);
CREATE INDEX idx_multipolygons_leisure ON multipolygons (leisure);
CREATE INDEX idx_multipolygons_other ON multipolygons USING GIST(other_tags gist_trgm_ops);
