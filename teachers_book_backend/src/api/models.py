from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
class StudentBase(BaseModel):
    full_name: str = Field(..., description="Full name of the student")

# PUBLIC_INTERFACE
class StudentCreate(StudentBase):
    pass

# PUBLIC_INTERFACE
class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name of the student")

# PUBLIC_INTERFACE
class Student(StudentBase):
    id: int
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class CustomFieldBase(BaseModel):
    name: str = Field(..., description="Name of the custom field (e.g., 'marks')")
    field_type: str = Field(..., description="Type of the field, e.g., 'text', 'number', 'date'")

# PUBLIC_INTERFACE
class CustomFieldCreate(CustomFieldBase):
    pass

# PUBLIC_INTERFACE
class CustomFieldUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the custom field")
    field_type: Optional[str] = Field(None, description="Type of the field")

# PUBLIC_INTERFACE
class CustomField(CustomFieldBase):
    id: int

    class Config:
        orm_mode = True

# PUBLIC_INTERFACE
class StudentCustomFieldValueBase(BaseModel):
    student_id: int
    custom_field_id: int
    value: Any

# PUBLIC_INTERFACE
class StudentCustomFieldValueCreate(StudentCustomFieldValueBase):
    pass

# PUBLIC_INTERFACE
class StudentCustomFieldValueUpdate(BaseModel):
    value: Any

# PUBLIC_INTERFACE
class StudentCustomFieldValue(StudentCustomFieldValueBase):
    id: int

    class Config:
        orm_mode = True
