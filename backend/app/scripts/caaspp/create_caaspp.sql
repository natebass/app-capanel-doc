CREATE TABLE caaspp_aggregate_scores ( 
    -- 1. IDENTIFIERS & DEMOGRAPHICS (Shared)
    county_code VARCHAR(2) NULL,
    district_code VARCHAR(5) NOT NULL,
    district_name VARCHAR(255) NULL,
    school_code VARCHAR(255) NULL,
    school_name VARCHAR(255) NULL,
    type_id VARCHAR(255) NULL,
    filler VARCHAR(50) NULL,
    test_year INT NOT NULL,  -- Partition Key
    test_type VARCHAR(10) NOT NULL,
    test_id VARCHAR(10) NOT NULL,
    student_group_id VARCHAR(10) NOT NULL,
    grade VARCHAR(5) NOT NULL,
    
    -- 2. PARTICIPATION & BASE SCORES (Shared)
    total_students_enrolled VARCHAR(50) NOT NULL,
    total_students_tested VARCHAR(50) NOT NULL,
    total_students_tested_with_scores VARCHAR(50) NULL,
    mean_scale_score VARCHAR(50) NULL,
    
    -- 3. CAA PERFORMANCE LEVELS (Shared)
    percentage_level_3 VARCHAR(50) NULL,
    count_level_3 VARCHAR(50) NULL,
    percentage_level_2 VARCHAR(50) NULL,
    count_level_2 VARCHAR(50) NULL,
    percentage_level_1 VARCHAR(50) NULL,
    count_level_1 VARCHAR(50) NULL,
    overall_total VARCHAR(50) NULL,
    
    -- 4. SMARTER BALANCED PERFORMANCE LEVELS (Shared)
    percentage_standard_exceeded VARCHAR(50) NULL,
    count_standard_exceeded VARCHAR(50) NULL,
    percentage_standard_met VARCHAR(50) NULL,
    count_standard_met VARCHAR(50) NULL,
    percentage_standard_met_and_above VARCHAR(50) NULL,
    count_standard_met_and_above VARCHAR(50) NULL,
    percentage_standard_nearly_met VARCHAR(50) NULL,
    count_standard_nearly_met VARCHAR(50) NULL,
    percentage_standard_not_met VARCHAR(50) NULL,
    count_standard_not_met VARCHAR(50) NULL,
    
    -- 5. CAST (SCIENCE) DOMAINS (Shared)
    life_sci_percent_below_standard VARCHAR(50) NULL,
    life_sci_count_below_standard VARCHAR(50) NULL,
    life_sci_percent_near_standard VARCHAR(50) NULL,
    life_sci_count_near_standard VARCHAR(50) NULL,
    life_sci_percent_above_standard VARCHAR(50) NULL,
    life_sci_count_above_standard VARCHAR(50) NULL,
    life_sci_total VARCHAR(50) NULL,
    
    physical_sci_percent_below_standard VARCHAR(50) NULL,
    physical_sci_count_below_standard VARCHAR(50) NULL,
    physical_sci_percent_near_standard VARCHAR(50) NULL,
    physical_sci_count_near_standard VARCHAR(50) NULL,
    physical_sci_percent_above_standard VARCHAR(50) NULL,
    physical_sci_count_above_standard VARCHAR(50) NULL,
    physical_sci_total VARCHAR(50) NULL,
    
    earth_sci_percent_below_standard VARCHAR(50) NULL,
    earth_sci_count_below_standard VARCHAR(50) NULL,
    earth_sci_percent_near_standard VARCHAR(50) NULL,
    earth_sci_count_near_standard VARCHAR(50) NULL,
    earth_sci_percent_above_standard VARCHAR(50) NULL,
    earth_sci_count_above_standard VARCHAR(50) NULL,
    earth_sci_total VARCHAR(50) NULL,
    
    -- ==========================================
    -- 6. RETIRED COLUMNS (2024 ONLY)
    -- ==========================================
    percent_range_3 VARCHAR(50) NULL,
    count_range_3 VARCHAR(50) NULL,
    percent_range_2 VARCHAR(50) NULL,
    count_range_2 VARCHAR(50) NULL,
    percent_range_1 VARCHAR(50) NULL,
    count_range_1 VARCHAR(50) NULL,

    -- ==========================================
    -- 7. NEW COLUMNS (2025 ONLY - ELPAC/ALTERNATE)
    -- ==========================================
    overall_mean_scale_score VARCHAR(50) NULL,
    overall_percent_level_3 VARCHAR(50) NULL,
    overall_percent_level_2 VARCHAR(50) NULL,
    overall_percent_level_1 VARCHAR(50) NULL,
    
    listening_domain_percent_level_1 VARCHAR(50) NULL,
    listening_domain_count_level_1 VARCHAR(50) NULL,
    listening_domain_percent_level_2 VARCHAR(50) NULL,
    listening_domain_count_level_2 VARCHAR(50) NULL,
    listening_domain_percent_level_3 VARCHAR(50) NULL,
    listening_domain_count_level_3 VARCHAR(50) NULL,
    listening_domain_total VARCHAR(50) NULL,
    
    writing_domain_percent_level_1 VARCHAR(50) NULL,
    writing_domain_count_level_1 VARCHAR(50) NULL,
    writing_domain_percent_level_2 VARCHAR(50) NULL,
    writing_domain_count_level_2 VARCHAR(50) NULL,
    writing_domain_percent_level_3 VARCHAR(50) NULL,
    writing_domain_count_level_3 VARCHAR(50) NULL,
    writing_domain_total VARCHAR(50) NULL,
    
    reading_domain_percent_level_1 VARCHAR(50) NULL,
    reading_domain_count_level_1 VARCHAR(50) NULL,
    reading_domain_percent_level_2 VARCHAR(50) NULL,
    reading_domain_count_level_2 VARCHAR(50) NULL,
    reading_domain_percent_level_3 VARCHAR(50) NULL,
    reading_domain_count_level_3 VARCHAR(50) NULL,
    reading_domain_total VARCHAR(50) NULL,
    
    speaking_domain_percent_level_1 VARCHAR(50) NULL,
    speaking_domain_count_level_1 VARCHAR(50) NULL,
    speaking_domain_percent_level_2 VARCHAR(50) NULL,
    speaking_domain_count_level_2 VARCHAR(50) NULL,
    speaking_domain_percent_level_3 VARCHAR(50) NULL,
    speaking_domain_count_level_3 VARCHAR(50) NULL,
    speaking_domain_total VARCHAR(50) NULL,
    
    composite_1_mean_scale_score VARCHAR(50) NULL,
    composite_1_percent_level_1 VARCHAR(50) NULL,
    composite_1_count_level_1 VARCHAR(50) NULL,
    composite_1_percent_level_2 VARCHAR(50) NULL,
    composite_1_count_level_2 VARCHAR(50) NULL,
    composite_1_percent_level_3 VARCHAR(50) NULL,
    composite_1_count_level_3 VARCHAR(50) NULL,
    composite_1_total VARCHAR(50) NULL,
    
    composite_2_mean_scale_score VARCHAR(50) NULL,
    composite_2_percent_level_1 VARCHAR(50) NULL,
    composite_2_count_level_1 VARCHAR(50) NULL,
    composite_2_percent_level_2 VARCHAR(50) NULL,
    composite_2_count_level_2 VARCHAR(50) NULL,
    composite_2_percent_level_3 VARCHAR(50) NULL,
    composite_2_count_level_3 VARCHAR(50) NULL,
    composite_2_total VARCHAR(50) NULL,

    -- ==========================================
    -- 8. SMARTER BALANCED AREAS 1-4 (Shared)
    -- ==========================================
    area_1_percentage_above_standard VARCHAR(50) NULL,
    area_1_count_above_standard VARCHAR(50) NULL,
    area_1_percentage_near_standard VARCHAR(50) NULL,
    area_1_count_near_standard VARCHAR(50) NULL,
    area_1_percentage_below_standard VARCHAR(50) NULL,
    area_1_count_below_standard VARCHAR(50) NULL,
    area_1_total VARCHAR(50) NULL,
    
    area_2_percentage_above_standard VARCHAR(50) NULL,
    area_2_count_above_standard VARCHAR(50) NULL,
    area_2_percentage_near_standard VARCHAR(50) NULL,
    area_2_count_near_standard VARCHAR(50) NULL,
    area_2_percentage_below_standard VARCHAR(50) NULL,
    area_2_count_below_standard VARCHAR(50) NULL,
    area_2_total VARCHAR(50) NULL,
    
    area_3_percentage_above_standard VARCHAR(50) NULL,
    area_3_count_above_standard VARCHAR(50) NULL,
    area_3_percentage_near_standard VARCHAR(50) NULL,
    area_3_count_near_standard VARCHAR(50) NULL,
    area_3_percentage_below_standard VARCHAR(50) NULL,
    area_3_count_below_standard VARCHAR(50) NULL,
    area_3_total VARCHAR(50) NULL,
    
    area_4_percentage_above_standard VARCHAR(50) NULL,
    area_4_count_above_standard VARCHAR(50) NULL,
    area_4_percentage_near_standard VARCHAR(50) NULL,
    area_4_count_near_standard VARCHAR(50) NULL,
    area_4_percentage_below_standard VARCHAR(50) NULL,
    area_4_count_below_standard VARCHAR(50) NULL,
    area_4_total VARCHAR(50) NULL,
    
    -- 9. COMPOSITE AREAS (Shared)
    composite_area_1_percentage_above_standard VARCHAR(50) NULL,
    composite_area_1_count_above_standard VARCHAR(50) NULL,
    composite_area_1_percentage_near_standard VARCHAR(50) NULL,
    composite_area_1_count_near_standard VARCHAR(50) NULL,
    composite_area_1_percentage_below_standard VARCHAR(50) NULL,
    composite_area_1_count_below_standard VARCHAR(50) NULL,
    composite_area_1_total VARCHAR(50) NULL,
    
    composite_area_2_percentage_above_standard VARCHAR(50) NULL,
    composite_area_2_count_above_standard VARCHAR(50) NULL,
    composite_area_2_percentage_near_standard VARCHAR(50) NULL,
    composite_area_2_count_near_standard VARCHAR(50) NULL,
    composite_area_2_percentage_below_standard VARCHAR(50) NULL,
    composite_area_2_count_below_standard VARCHAR(50) NULL,
    composite_area_2_total VARCHAR(50) NULL 

) PARTITION BY LIST (test_year);

-- Create the specific partitions
CREATE TABLE caaspp_aggregate_scores_2024 PARTITION OF caaspp_aggregate_scores FOR VALUES IN (2024);
CREATE TABLE caaspp_aggregate_scores_2025 PARTITION OF caaspp_aggregate_scores FOR VALUES IN (2025);
