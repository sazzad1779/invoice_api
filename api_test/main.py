# user.py
from fastapi import FastAPI,APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import *
from schemas import *
from database import *
from fastapi import Path

Base.metadata.create_all(bind=engine) # Base from database declarative_base()

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

 # Password Hashing
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



@app.post("/users/store")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validate the incoming data using Pydantic
    if not user.name or not user.email or not user.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid input data")

    # Check if the username is already taken
    existing_user_username = db.query(User).filter(User.name == user.name).first()
    if existing_user_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Check if the email is already taken
    existing_user_email = db.query(User).filter(User.email == user.email).first()
    if existing_user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # All checks passed, create the user
    hashed_password = get_password_hash(user.password)
    db_user = User(**user.dict(), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"Authentication Status": "Successful", "User Details": db_user}

# API endpoint to create a new invoice
# Custom function to convert SQLAlchemy model to response model
def convert_to_response_model(db_invoice: Invoice) -> InvoiceCreate:
    return InvoiceCreate(
        id=db_invoice.id,
        invoice_date=db_invoice.invoice_date,
        customer_id=db_invoice.customer_id,
        due_date=db_invoice.due_date,
        gross_discount=db_invoice.gross_discount,
        gross_total=db_invoice.gross_total,
        terms_and_conditions=db_invoice.terms_and_conditions,
        invoiceItems=[
            InvoiceItemCreate(
                product_service_type=item.product_service_type,
                description=item.description,
                unit_price=item.unit_price,
                quantity=item.quantity,
                discount=item.discount,
                vat_percentage=item.vat_percentage,
            )
            for item in db_invoice.invoice_items
        ],
    )


# FastAPI route with validation and error handling
@app.post("/invoice/store", response_model=InvoiceCreate)
async def create_invoice(invoice_create: InvoiceCreate, db=Depends(get_db)):

    # Custom validation to check if the invoice_date is unique
    if db.query(Invoice).filter(Invoice.invoice_date == invoice_create.invoice_date).first():
        raise HTTPException(status_code=400, detail="Invoice with the same date already exists")


    db_invoice = Invoice(
        invoice_date=invoice_create.invoice_date,
        customer_id=invoice_create.customer_id,
        due_date=invoice_create.due_date,
        gross_discount=invoice_create.gross_discount,
        gross_total=invoice_create.gross_total,
        terms_and_conditions=invoice_create.terms_and_conditions,
    )
    for item in invoice_create.invoiceItems:
        # Perform additional validation as needed
        if item.unit_price < 0 or item.quantity < 0:
            raise HTTPException(status_code=400, detail="Unit price and quantity must be non-negative")

        db_item = InvoiceItem(
            product_service_type=item.product_service_type,
            description=item.description,
            unit_price=item.unit_price,
            quantity=item.quantity,
            discount=item.discount,
            vat_percentage=item.vat_percentage,
        )
        db_invoice.invoice_items.append(db_item)

    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return convert_to_response_model(db_invoice)


# FastAPI route to get a list of invoices
@app.get("/invoices/", response_model=List[InvoiceCreate])
async def get_invoice_list(db=Depends(get_db)):
    invoices = db.query(Invoice).all()
    return [convert_to_response_model(invoice) for invoice in invoices]

# FastAPI route to get invoice details
@app.get("/invoices/{invoice_id}", response_model=InvoiceCreate)
async def get_invoice_details(
    invoice_id: int = Path(..., title="The ID of the invoice to retrieve", ge=1),
    db=Depends(get_db),
):
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return convert_to_response_model(db_invoice)




