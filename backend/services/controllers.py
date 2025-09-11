from fastapi import HTTPException, status
from typing import List, Dict, Any
from backend.database.connector import DatabaseConnector
from backend.services.models import ServiceCreateModel, ServiceUpdateModel

db = DatabaseConnector()

def get_all_services(has_insurances: bool = False) -> List[Dict[str, Any]]:
    try:
        services = db.call_procedure("sp_get_all_services", ())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stored procedure error: {e}"
        )

    if has_insurances:
        for s in services:
            if s.get("price") is not None:
                s["price"] = s["price"] / 2 
    return services


def get_service_by_id(service_id: int) -> Dict[str, Any]:
    try:
        result = db.call_procedure("sp_get_service_by_id", (service_id,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored procedure error: {e}")

    if not result:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return result[0]


def get_my_services_by_user(user_id: int) -> List[Dict[str, Any]]:
    try:
        return db.call_procedure("sp_get_my_services_by_user", (user_id,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored procedure error: {e}")


def create_service(data: ServiceCreateModel) -> Dict[str, Any]:
    try:
        result = db.call_procedure(
            "sp_create_service",
            (data.name, data.description, data.price)
        )
        return result[0] if result else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored procedure error: {e}")


def update_service(data: ServiceUpdateModel) -> Dict[str, Any]:
    try:
        result = db.call_procedure(
            "sp_update_service",
            (data.id, data.name, data.description, data.price)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored procedure error: {e}")


def delete_service(service_id: int) -> None:
    try:
        db.call_procedure("sp_delete_service", (service_id,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stored procedure error: {e}")
