from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import CurrentUser
from app.core.security import verify_password, hash_password, create_access_token, DGI_ROLES
from app.schemas.auth import LoginResponse, UserInfo, ChangePasswordRequest

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT u.id, u.email, u.password_hash, u.is_active, u.division_id,
                   u.failed_login_attempts, u.locked_until,
                   c.code as role_code, c.label as role_label,
                   p.names as nombre, p.paternal_surname as apellido_paterno
            FROM core."user" u
            JOIN ref.category c ON u.system_role_id = c.id
            JOIN core.person p ON u.person_id = p.id
            WHERE u.email = :email AND u.deleted_at IS NULL
        """),
        {"email": form.username},
    )
    user = result.mappings().first()

    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario desactivado")

    token = create_access_token({"sub": str(user["id"]), "role": user["role_code"]})

    population = "dgi" if user["role_code"] in DGI_ROLES else "operativa"

    return LoginResponse(
        access_token=token,
        user=UserInfo(
            id=user["id"],
            email=user["email"],
            nombre=user["nombre"],
            apellido_paterno=user["apellido_paterno"],
            role_code=user["role_code"],
            role_label=user["role_label"],
            division_id=user["division_id"],
            population=population,
        ),
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Change the current user's password. Requires current password verification."""
    result = await db.execute(
        text('SELECT password_hash FROM core."user" WHERE id = :id AND deleted_at IS NULL'),
        {"id": str(user["id"])},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if not verify_password(body.current_password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña actual incorrecta")

    new_hash = hash_password(body.new_password)
    await db.execute(
        text('UPDATE core."user" SET password_hash = :hash, updated_at = NOW() WHERE id = :id'),
        {"hash": new_hash, "id": str(user["id"])},
    )
    await db.commit()
    return {"message": "Contraseña actualizada exitosamente"}
