from sqlalchemy import Integer, String, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .portfolio import Asset

class Tag(Base):
    """
    标签模型。
    表示可用于资产分类、筛选的标签，支持与资产多对多关联。
    """
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # 标签ID
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 标签名称
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        secondary="asset_tags",
        back_populates="tags"
    )  # 关联资产多对多关系

class AssetTag(Base):
    """
    资产-标签关联表。
    实现资产与标签的多对多关系。
    """
    __tablename__ = "asset_tags"
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), primary_key=True)  # 资产ID
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)  # 标签ID 