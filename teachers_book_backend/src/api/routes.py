from fastapi import APIRouter, HTTPException
from typing import List
from .models import (
    Student, StudentCreate, StudentUpdate,
    CustomField, CustomFieldCreate, CustomFieldUpdate,
    StudentCustomFieldValue, StudentCustomFieldValueCreate, StudentCustomFieldValueUpdate
)
from .database import get_db

router = APIRouter()

# --- Students CRUD ---
# PUBLIC_INTERFACE
@router.get("/students", response_model=List[Student], tags=["students"])
def list_students():
    """Returns all students, each with their custom fields and values."""
    with get_db() as cur:
        cur.execute("SELECT id, full_name FROM students ORDER BY id;")
        students = [{"id": sid, "full_name": name} for sid, name in cur.fetchall()]
        # Load custom fields for each
        cur.execute("SELECT id, name FROM custom_fields;")
        cf_names = {cid: cname for cid, cname in cur.fetchall()}
        cur.execute("SELECT student_id, custom_field_id, value FROM student_custom_field_values;")
        value_results = cur.fetchall()
        stu_field_map = {}
        for student_id, field_id, value in value_results:
            stu_field_map.setdefault(student_id, {})[cf_names.get(field_id, str(field_id))] = value
        for stu in students:
            stu["custom_fields"] = stu_field_map.get(stu["id"], {})
        return students

# PUBLIC_INTERFACE
@router.get("/students/{student_id}", response_model=Student, tags=["students"])
def get_student(student_id: int):
    """Get a single student by ID."""
    with get_db() as cur:
        cur.execute("SELECT id, full_name FROM students WHERE id=%s;", (student_id,))
        s = cur.fetchone()
        if not s:
            raise HTTPException(status_code=404, detail="Student not found")
        cur.execute("SELECT id, name FROM custom_fields;")
        cf_names = {cid: cname for cid, cname in cur.fetchall()}
        cur.execute("SELECT custom_field_id, value FROM student_custom_field_values WHERE student_id=%s;", (student_id,))
        custom_fields = {cf_names.get(field_id, str(field_id)): value for field_id, value in cur.fetchall()}
        return {"id": s[0], "full_name": s[1], "custom_fields": custom_fields}

# PUBLIC_INTERFACE
@router.post("/students", response_model=Student, status_code=201, tags=["students"])
def create_student(student: StudentCreate):
    """Create new student."""
    with get_db() as cur:
        cur.execute("INSERT INTO students (full_name) VALUES (%s) RETURNING id;", (student.full_name,))
        student_id = cur.fetchone()[0]
        return {"id": student_id, "full_name": student.full_name, "custom_fields": {}}

# PUBLIC_INTERFACE
@router.put("/students/{student_id}", response_model=Student, tags=["students"])
def update_student(student_id: int, student: StudentUpdate):
    """Update an existing student."""
    with get_db() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s;", (student_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        if student.full_name:
            cur.execute("UPDATE students SET full_name=%s WHERE id=%s;", (student.full_name, student_id))
        cur.execute("SELECT full_name FROM students WHERE id=%s;", (student_id,))
        full_name = cur.fetchone()[0]
        # Fetch custom fields
        cur.execute("SELECT id, name FROM custom_fields;")
        cf_names = {cid: cname for cid, cname in cur.fetchall()}
        cur.execute("SELECT custom_field_id, value FROM student_custom_field_values WHERE student_id=%s;", (student_id,))
        custom_fields = {cf_names.get(field_id, str(field_id)): value for field_id, value in cur.fetchall()}
        return {"id": student_id, "full_name": full_name, "custom_fields": custom_fields}

# PUBLIC_INTERFACE
@router.delete("/students/{student_id}", status_code=204, tags=["students"])
def delete_student(student_id: int):
    """Delete a student and their custom field values."""
    with get_db() as cur:
        cur.execute("SELECT id FROM students WHERE id=%s;", (student_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cur.execute("DELETE FROM student_custom_field_values WHERE student_id=%s;", (student_id,))
        cur.execute("DELETE FROM students WHERE id=%s;", (student_id,))
    return None

# --- Custom Fields CRUD ---
# PUBLIC_INTERFACE
@router.get("/custom_fields", response_model=List[CustomField], tags=["custom_fields"])
def list_custom_fields():
    """List all custom fields."""
    with get_db() as cur:
        cur.execute("SELECT id, name, field_type FROM custom_fields ORDER BY id;")
        return [{"id": cid, "name": name, "field_type": ftype} for cid, name, ftype in cur.fetchall()]

# PUBLIC_INTERFACE
@router.get("/custom_fields/{field_id}", response_model=CustomField, tags=["custom_fields"])
def get_custom_field(field_id: int):
    """Get details for a specific custom field."""
    with get_db() as cur:
        cur.execute("SELECT id, name, field_type FROM custom_fields WHERE id=%s;", (field_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Custom field not found")
        return {"id": row[0], "name": row[1], "field_type": row[2]}

# PUBLIC_INTERFACE
@router.post("/custom_fields", response_model=CustomField, status_code=201, tags=["custom_fields"])
def create_custom_field(custom_field: CustomFieldCreate):
    """Create a new custom field."""
    with get_db() as cur:
        cur.execute(
            "INSERT INTO custom_fields (name, field_type) VALUES (%s, %s) RETURNING id;",
            (custom_field.name, custom_field.field_type)
        )
        cf_id = cur.fetchone()[0]
        return {"id": cf_id, "name": custom_field.name, "field_type": custom_field.field_type}

# PUBLIC_INTERFACE
@router.put("/custom_fields/{field_id}", response_model=CustomField, tags=["custom_fields"])
def update_custom_field(field_id: int, custom_field: CustomFieldUpdate):
    """Update an existing custom field."""
    with get_db() as cur:
        cur.execute("SELECT id, name, field_type FROM custom_fields WHERE id=%s;", (field_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Custom field not found")
        update_fields = []
        update_values = []
        if custom_field.name:
            update_fields.append("name=%s")
            update_values.append(custom_field.name)
        if custom_field.field_type:
            update_fields.append("field_type=%s")
            update_values.append(custom_field.field_type)
        if update_fields:
            update_values.append(field_id)
            cur.execute(f"UPDATE custom_fields SET {', '.join(update_fields)} WHERE id=%s;", tuple(update_values))
        # Return latest
        cur.execute("SELECT id, name, field_type FROM custom_fields WHERE id=%s;", (field_id,))
        row = cur.fetchone()
        return {"id": row[0], "name": row[1], "field_type": row[2]}

# PUBLIC_INTERFACE
@router.delete("/custom_fields/{field_id}", status_code=204, tags=["custom_fields"])
def delete_custom_field(field_id: int):
    """Delete a custom field and all its values."""
    with get_db() as cur:
        cur.execute("DELETE FROM student_custom_field_values WHERE custom_field_id=%s;", (field_id,))
        cur.execute("DELETE FROM custom_fields WHERE id=%s;", (field_id,))
    return None

# --- Assign/Update Custom Field Value for Student ---
# PUBLIC_INTERFACE
@router.post("/students/{student_id}/custom_field_values", response_model=StudentCustomFieldValue, status_code=201, tags=["student_field_values"])
def assign_custom_field_value(student_id: int, payload: StudentCustomFieldValueCreate):
    """Assign a value to a custom field for a specific student."""
    with get_db() as cur:
        # Check student and field exist
        cur.execute("SELECT id FROM students WHERE id=%s;", (student_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cur.execute("SELECT id FROM custom_fields WHERE id=%s;", (payload.custom_field_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Custom field not found")
        # Insert or update value
        cur.execute(
            "SELECT id FROM student_custom_field_values WHERE student_id=%s AND custom_field_id=%s;",
            (student_id, payload.custom_field_id)
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE student_custom_field_values SET value=%s WHERE id=%s RETURNING id;",
                (payload.value, row[0])
            )
            new_id = row[0]
        else:
            cur.execute(
                "INSERT INTO student_custom_field_values (student_id, custom_field_id, value) VALUES (%s, %s, %s) RETURNING id;",
                (student_id, payload.custom_field_id, payload.value)
            )
            new_id = cur.fetchone()[0]
        return {"id": new_id, "student_id": student_id, "custom_field_id": payload.custom_field_id, "value": payload.value}

# PUBLIC_INTERFACE
@router.put("/students/{student_id}/custom_field_values/{field_id}", response_model=StudentCustomFieldValue, tags=["student_field_values"])
def update_custom_field_value(student_id: int, field_id: int, payload: StudentCustomFieldValueUpdate):
    """Update value for a specific custom field for a student."""
    with get_db() as cur:
        cur.execute(
            "UPDATE student_custom_field_values SET value=%s WHERE student_id=%s AND custom_field_id=%s RETURNING id;",
            (payload.value, student_id, field_id)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Custom field value not found")
        return {"id": row[0], "student_id": student_id, "custom_field_id": field_id, "value": payload.value}
