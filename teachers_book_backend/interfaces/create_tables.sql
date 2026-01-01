-- Table for main students (id, full_name)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL
);

-- Table for custom fields definition (id, name, field_type)
CREATE TABLE IF NOT EXISTS custom_fields (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    field_type TEXT NOT NULL
);

-- Table for storing the field value per student (id, student_id, custom_field_id, value)
CREATE TABLE IF NOT EXISTS student_custom_field_values (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    custom_field_id INTEGER NOT NULL REFERENCES custom_fields(id) ON DELETE CASCADE,
    value TEXT
);

-- Add a unique constraint so a student + custom_field combo is unique
ALTER TABLE student_custom_field_values ADD CONSTRAINT IF NOT EXISTS unique_student_custom_field UNIQUE (student_id, custom_field_id);
