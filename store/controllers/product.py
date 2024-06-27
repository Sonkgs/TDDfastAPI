from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.exceptions import NotFoundException

from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase
from store.core.exceptions import DatabaseInsertError

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
    return await usecase.create(body=body)


@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()


@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    return await usecase.update(id=id, body=body)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)

async def create(self, body: ProductIn) -> ProductOut:
    try:
        product_model = ProductModel(**body.model_dump())
        await self.collection.insert_one(product_model.model_dump())
        return ProductOut(**product_model.model_dump())
    except pymongo.errors.WriteError as e:
        raise DatabaseInsertError(message=str(e))
    
async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
    product = await self.collection.find_one({"id": id})
    if not product:
        raise NotFoundException(message=f"Product not found with id: {id}")

    result = await self.collection.find_one_and_update(
        filter={"id": id},
        update={"$set": body.model_dump(exclude_none=True, include={"updated_at"})},
        return_document=pymongo.ReturnDocument.AFTER,
    )

    return ProductUpdateOut(**result)