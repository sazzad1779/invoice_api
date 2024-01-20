from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)
    hashed_password = Column(String)


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    product_service_type = Column(String, index=True)
    description = Column(String)
    unit_price = Column(Float)
    quantity = Column(Integer)
    discount = Column(Float)
    vat_percentage = Column(Float)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    invoice = relationship("Invoice", backref="invoice_items")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_date = Column(String)
    customer_id = Column(String, index=True)
    due_date = Column(String)
    gross_discount = Column(Float)
    gross_total = Column(Float)
    terms_and_conditions = Column(String)