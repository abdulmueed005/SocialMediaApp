from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import engine, get_db
from typing import Optional, List
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
limit: int = 10, skip: int = 0, search: Optional[str] = ""):


 #   posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    
    return posts

    # if you want the app to only return posts from the ID that is signed in, the use:
    #posts = db.query(models.Post).filter(models.Post.owner_id==current_user.id).all()

# the follwing is what used to get all posts directly using SQL. 
# The above code is using sqlalchemy which really only just converts our python into sql so both code has same outcome.
#   cursor.execute("""SELECT * FROM posts""")
#  posts = cursor.fetchall()
#  return {"data": posts}


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    print (current_user)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
# the code above ** Post simply lets us not have to explicitly state all out fields in the models like this next line. 
#   new_post = models.Post(title=post.title, content=post.content, published=post.published)
# both give us the same output but with the first one, using ** means that when we create more fields in models.py we don't have to update this code.

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    # (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # return {"data": new_post}
#reson for using cursor.execute as two separate paramaets is to aboud sql injection attacks. %s intitialises a variable and post.blah then inputs the values.
#order matters

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int,db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
   # post = db.query(models.Post).filter(models.Post.id == id).first()
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""",(str(id)))
    # post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f"post with {id} was not found")
    
    # if you want a user to only see his/her post then add this:
    #if post.owner_id != current_user.id:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autorized to perform function")#
    
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""",(str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with {id} doesn't exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autorized to perform function")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate,db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    # (post.title, post.content, post.published,(str(id))))
    # conn.commit()
    # updated_post = cursor.fetchone()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"post with {id} doesn't exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not autorized to perform function")

    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()
