from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(prefix='/orders', tags=['orders'])

session = Session(bind=engine)

@order_router.get('/')
async def hello(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"msg" : "hello world"}

@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        pizza_size = order.pizza_size,
        quantity = order.quantity
    )
    new_order.user_id = user.id
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size" : new_order.pizza_size,
        "quantity" : new_order.quantity,
        "id" : new_order.id,
        "order_status" : new_order.order_status
    }

    return jsonable_encoder(response)

@order_router.get('/orders')
async def list_all_orders(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    
    if user.is_staff:
        orders = session.query(Order).all()
        return jsonable_encoder(orders)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a staff member")

@order_router.get('/orders/{id}')
async def get_order_by_id(id: int, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    user = authorize.get_jwt_subject()
    current_user = session.query(User).filter(user == User.username).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a staff member")
    

@order_router.get('/user/orders')
async def get_user_orders(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    user = authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    return jsonable_encoder(current_user.orders)


@order_router.get('/user/orders/{id}')
async def get_spec_order(id: int, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    subject = authorize.get_jwt_subject()
    current_user = session.query(User).filter(subject == User.username).first()

    orders = current_user.orders
    for o in orders:
        if o.id == id:
            return o
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no order with current id")

@order_router.put('/order/update/{id}')
async def update_order(id:int, order: OrderModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    order_update = session.query(Order).filter(Order.id == id).first()
    order_update.quantity = order.quantity
    order_update.pizza_size = order.pizza_size

    session.commit()

    response = {
            "id" : order_update.id,
            "quantity" : order_update.quantity,
            "order_status" : order_update.order_status,
            "pizza_size" : order_update.pizza_size
        }    

    return jsonable_encoder(response)

@order_router.patch('/order/update/{id}')
async def update_order_status(id: int, order: OrderStatusModel, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    subject = authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == subject).first()

    if current_user.is_staff:
        order_status_update = session.query(Order).filter(Order.id == id).first()
        order_status_update.order_status = order.order_status

        session.commit()

        response = {
            "id" : order_status_update.id,
            "quantity" : order_status_update.quantity,
            "order_status" : order_status_update.order_status,
            "pizza_size" : order_status_update.pizza_size
        }

        return jsonable_encoder(response)
    
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not a staff member")
    
@order_router.delete('/order/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, authorize : AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    order_delete = session.query(Order).filter(Order.id == id).first()

    session.delete(order_delete)

    session.commit()

    return jsonable_encoder(order_delete)