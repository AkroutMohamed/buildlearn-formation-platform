from fastapi import APIRouter, Body, Depends
from uuid import UUID
from app.dependencies.admin import get_admin_service
from app.dependencies.admin_course import get_admin_course_service
from app.dependencies.admin_product import get_admin_product_service
from app.dependencies.product_instructor import get_product_instructor_service
from app.middleware.auth_middleware import get_current_user
from app.middleware.role_middleware import require_role
from app.schemas.common import AdminDashboardResponse, MessageResponse
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.schemas.user import InstructorCreate, InstructorResponse, InstructorStatusUpdate, UserResponse
from app.services.admin_service import AdminService
from app.services.admin_course_service import AdminCourseService
from app.services.admin_product_service import AdminProductService
from app.services.product_instructor_service import ProductInstructorService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse)
def admin_dashboard(
    current_user = Depends(get_current_user)
):
    require_role(["admin"])(current_user)

    return {
        "message": "Welcome Admin"
    }


@router.get("/instructor-requests", response_model=list[InstructorResponse])
def list_instructor_requests(
    current_user = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    require_role(["admin"])(current_user)
    return service.list_pending_instructors()


@router.post("/instructor-requests/{user_id}/approve", response_model=InstructorResponse)
def approve_instructor_request(
    user_id,
    current_user = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    require_role(["admin"])(current_user)
    return service.approve_instructor(user_id)


@router.post("/instructor-requests/{user_id}/reject", response_model=InstructorResponse)
def reject_instructor_request(
    user_id,
    current_user = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    require_role(["admin"])(current_user)
    return service.reject_instructor(user_id)


@router.get("/instructors", response_model=list[InstructorResponse])
def list_instructors(
    current_user = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    require_role(["admin"])(current_user)
    return service.list_instructors()


@router.post("/instructors", response_model=InstructorResponse)
def create_instructor(
    instructor: InstructorCreate,
    current_user = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
):
    require_role(["admin"])(current_user)
    return service.create_instructor(
        instructor.first_name,
        instructor.last_name,
        instructor.email,
        instructor.password,
    )


# Product / Course management
@router.get("/courses", response_model=list[CourseResponse])
def list_admin_courses(
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.list_courses()


@router.post("/courses", response_model=CourseResponse)
def create_admin_course(
    course: CourseCreate,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.create_course(course, current_user.id)


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_admin_course(
    course_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.get_course(course_id)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_admin_course(
    course_id,
    course: CourseUpdate,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.update_course(course_id, course)


@router.delete("/courses/{course_id}", response_model=MessageResponse)
def delete_admin_course(
    course_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    service.delete_course(course_id)
    return {"message": "Course deleted successfully"}


@router.patch("/courses/{course_id}/publish", response_model=CourseResponse)
def publish_admin_course(
    course_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.publish_course(course_id)


@router.patch("/courses/{course_id}/unpublish", response_model=CourseResponse)
def unpublish_admin_course(
    course_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.unpublish_course(course_id)


# Instructor assignment
@router.get("/courses/{course_id}/instructors", response_model=list[UserResponse])
def list_course_instructors(
    course_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.get_course_instructors(course_id)


@router.post("/courses/{course_id}/instructors")
def assign_course_instructor(
    course_id,
    instructor_id: str = Body(..., embed=True),
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    return service.assign_instructor(course_id, instructor_id)


@router.delete("/courses/{course_id}/instructors/{instructor_id}", response_model=MessageResponse)
def unassign_course_instructor(
    course_id,
    instructor_id,
    current_user = Depends(get_current_user),
    service: AdminCourseService = Depends(get_admin_course_service),
):
    require_role(["admin"])(current_user)
    service.unassign_instructor(course_id, instructor_id)
    return {"message": "Instructor removed from course"}


# Product management
@router.get("/products", response_model=list[ProductResponse])
def list_products(
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.list_products()


@router.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.create_product(product)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.get_product(product_id)


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id,
    product: ProductUpdate,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.update_product(product_id, product)


@router.delete("/products/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    service.delete_product(product_id)
    return {"message": "Product deleted successfully"}


@router.patch("/products/{product_id}/publish", response_model=ProductResponse)
def publish_product(
    product_id,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.publish_product(product_id)


@router.patch("/products/{product_id}/unpublish", response_model=ProductResponse)
def unpublish_product(
    product_id,
    current_user = Depends(get_current_user),
    service: AdminProductService = Depends(get_admin_product_service),
):
    require_role(["admin"])(current_user)
    return service.unpublish_product(product_id)


# Product instructor assignment
@router.get("/products/{product_id}/instructors", response_model=list[UserResponse])
def list_product_instructors(
    product_id,
    current_user = Depends(get_current_user),
    service: ProductInstructorService = Depends(get_product_instructor_service),
):
    require_role(["admin"])(current_user)
    assignments = service.get_product_instructors(product_id)
    instructor_ids = [a.instructor_id for a in assignments]
    if not instructor_ids:
        return []
    from app.repositories.user_repository import UserRepository
    from app.database import SessionLocal
    with SessionLocal() as db:
        user_repo = UserRepository(db)
        return user_repo.get_by_ids(instructor_ids)


@router.post("/products/{product_id}/instructors")
def assign_product_instructor(
    product_id,
    instructor_id: str = Body(..., embed=True),
    current_user = Depends(get_current_user),
    service: ProductInstructorService = Depends(get_product_instructor_service),
):
    require_role(["admin"])(current_user)
    return service.assign_instructor(product_id, instructor_id)


@router.delete("/products/{product_id}/instructors/{instructor_id}", response_model=MessageResponse)
def unassign_product_instructor(
    product_id,
    instructor_id,
    current_user = Depends(get_current_user),
    service: ProductInstructorService = Depends(get_product_instructor_service),
):
    require_role(["admin"])(current_user)
    service.remove_instructor(product_id, instructor_id)
    return {"message": "Instructor removed from product"}