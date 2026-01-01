#!/bin/bash
cd /tmp/kavia/workspace/code-generation/student-management-system-6602-6619/teachers_book_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

