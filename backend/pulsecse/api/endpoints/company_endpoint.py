"""
Company Endpoint

This module handles company-related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from sqlalchemy.orm import Session
from typing import List

from backend.pulsecse import crud, models, schemas
from backend.pulsecse.database import get_db

router = APIRouter()


@router.get("/companies/", response_model=List[schemas.Company])
def read_companies(db: Session = Depends(get_db)):
    """
    Read all companies.

    Args:
    db (Session): Database session.

    Returns:
    List[Company]: List of companies.
    """
    companies = crud.get_companies(db)
    return companies


@router.get("/companies/{company_id}", response_model=schemas.Company)
def read_company(company_id: int, db: Session = Depends(get_db)):
    """
    Read a company by ID.

    Args:
    company_id (int): Company ID.
    db (Session): Database session.

    Returns:
    Company: Company object.
    """
    company = crud.get_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/companies/", response_model=schemas.Company)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company.

    Args:
    company (CompanyCreate): Company data.
    db (Session): Database session.

    Returns:
    Company: Created company object.
    """
    return crud.create_company(db, company)


@router.put("/companies/{company_id}", response_model=schemas.Company)
def update_company(company_id: int, company: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    """
    Update a company.

    Args:
    company_id (int): Company ID.
    company (CompanyUpdate): Updated company data.
    db (Session): Database session.

    Returns:
    Company: Updated company object.
    """
    db_company = crud.get_company(db, company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return crud.update_company(db, db_company, company)


@router.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """
    Delete a company.

    Args:
    company_id (int): Company ID.
    db (Session): Database session.

    Returns:
    JSONResponse: Success message.
    """
    company = crud.get_company(db, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    crud.delete_company(db, company)
    return JSONResponse(content={"message": "Company deleted successfully"}, status_code=200)