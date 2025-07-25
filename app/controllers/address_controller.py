from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.address import Address
from app.schemas.address_schema import AddressCreate, AddressUpdate

def create_address(db: Session, user_id: int, address: AddressCreate):
    # If this is set as default, unset other default addresses
    if address.is_default:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True
        ).update({"is_default": False})
    
    db_address = Address(user_id=user_id, **address.dict())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

def get_addresses(db: Session, user_id: int):
    return db.query(Address).filter(Address.user_id == user_id).all()

def get_address_by_id(db: Session, address_id: int, user_id: int):
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return address

def update_address(db: Session, address_id: int, user_id: int, address_update: AddressUpdate):
    address = get_address_by_id(db, address_id, user_id)
    
    # If setting as default, unset other default addresses
    if address_update.is_default:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True,
            Address.id != address_id
        ).update({"is_default": False})
    
    update_data = address_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.commit()
    db.refresh(address)
    return address

def delete_address(db: Session, address_id: int, user_id: int):
    address = get_address_by_id(db, address_id, user_id)
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}
