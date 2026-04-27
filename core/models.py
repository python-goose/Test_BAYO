from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base

class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Связь: один аффилиат может прислать много лидов
    leads = relationship("Lead", back_populates="affiliate")

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    # Связь: на один оффер может быть много лидов
    leads = relationship("Lead", back_populates="offer")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    
    # Внешние ключи (связи с другими таблицами)
    affiliate_id = Column(Integer, ForeignKey("affiliates.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    
    # Время создания (нужно для дедупликации 10 мин)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Обратные связи
    affiliate = relationship("Affiliate", back_populates="leads")
    offer = relationship("Offer", back_populates="leads")