CREATE TABLE "academic_indicators" (
    -- IDENTIFIERS
    "county_code" character varying(2),
    "district_code" character varying(5) NOT NULL,
    "school_code" character varying(7),
    "record_type_id" character varying(2),
    "charter_number" character varying(4),
    "test_year" character varying(4) NOT NULL,
    "test_type" character varying(2) NOT NULL,
    "test_id" character varying(2) NOT NULL,
    "student_group_id" character varying(3) NOT NULL,
    "grade" character varying(2) NOT NULL,

    -- PARTICIPATION
    "students_enrolled" character varying(10) NOT NULL,
    "students_tested" character varying(10) NOT NULL,
    "students_tested_with_scores" character varying(10),

    -- OVERALL SCORES (Mapped to generic levels)
    "overall_mean_scale_score" character varying(10),
    "overall_total" character varying(10),
    "overall_level_1_pct" character varying(10),
    "overall_level_1_count" character varying(10),
    "overall_level_2_pct" character varying(10),
    "overall_level_2_count" character varying(10),
    "overall_level_3_pct" character varying(10),
    "overall_level_3_count" character varying(10),
    "overall_level_4_pct" character varying(10),
    "overall_level_4_count" character varying(10),
    "overall_met_and_above_pct" character varying(10),
    "overall_met_and_above_count" character varying(10),

    -- DOMAIN DATA (Using JSONB for nested, test-specific areas)
    "domain_data" JSONB
);

-- Specialized GIN Index for ultra-fast JSONB querying
CREATE INDEX "idx_acad_ind_domain_data" ON "academic_indicators" USING GIN ("domain_data");

-- B-Tree Indexes for common filtering and joins
CREATE INDEX "idx_acad_ind_location" ON "academic_indicators" ("county_code", "district_code", "school_code");
CREATE INDEX "idx_acad_ind_test" ON "academic_indicators" ("test_year", "test_id");
CREATE INDEX "idx_acad_ind_demographics" ON "academic_indicators" ("student_group_id", "grade");