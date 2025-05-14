from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# File path (make sure the file is in this location)
EXCEL_PATH = "Data/capbudg.xls"

@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}


# Utility: Load Excel Sheets
def load_excel_sheets():
    if not os.path.exists(EXCEL_PATH):
        raise HTTPException(status_code=500, detail=f"Excel file not found at {EXCEL_PATH}")
    try:
        return pd.read_excel(EXCEL_PATH, sheet_name=None, engine='xlrd')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Excel file: {str(e)}")


# ✅ 1. List Table Names
@app.get("/list_tables")
def list_tables():
    sheets = load_excel_sheets()
    return {"tables": list(sheets.keys())}


# ✅ 2. Get Table Details
@app.get("/get_table_details")
def get_table_details(table_name: str = Query(..., description="Name of the table")):
    sheets = load_excel_sheets()
    if table_name not in sheets:
        raise HTTPException(status_code=404, detail="Table not found")

    df = sheets[table_name]
    row_names = df.iloc[:, 0].dropna().astype(str).tolist()
    return {
        "table_name": table_name,
        "row_names": row_names
    }


# ✅ 3. Sum Row Values
@app.get("/row_sum")
def row_sum(
    table_name: str = Query(..., description="Name of the table"),
    row_name: str = Query(..., description="Name of the row to sum")
):
    sheets = load_excel_sheets()
    if table_name not in sheets:
        raise HTTPException(status_code=404, detail="Table not found")

    df = sheets[table_name]
    matched_rows = df[df.iloc[:, 0].astype(str).str.strip() == row_name.strip()]
    
    if matched_rows.empty:
        raise HTTPException(status_code=404, detail="Row not found")

    row_values = matched_rows.iloc[0, 1:]
    numeric_values = pd.to_numeric(row_values, errors='coerce')
    numeric_sum = numeric_values.sum()

    return {
        "table_name": table_name,
        "row_name": row_name,
        "sum": numeric_sum,
        "values": numeric_values.dropna().tolist()
    }


# 🔍 Debug: Check if Excel file is found
@app.get("/debug_file")
def debug_file():
    return {
        "exists": os.path.exists(EXCEL_PATH),
        "path": os.path.abspath(EXCEL_PATH)
    }


# 🔍 Debug: Try reading the Excel file
@app.get("/debug_excel")
def debug_excel():
    try:
        sheets = load_excel_sheets()
        return {"sheet_names": list(sheets.keys())}
    except Exception as e:
        return {"error": str(e)}
