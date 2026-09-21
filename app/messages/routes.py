from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app.messages import messages_bp
from app.extensions import db
from app.models.message import Message
from app.models.user import User
from app.models.post import Post


@messages_bp.route("/")
@login_required
def inbox():
    sent_to = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id)
    received_from = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user.id)
    contact_ids = {row[0] for row in sent_to.union(received_from).all()}

    contacts = User.query.filter(User.id.in_(contact_ids)).all() if contact_ids else []
    return render_template("messages/inbox.html", contacts=contacts)


@messages_bp.route("/<int:user_id>", methods=["GET", "POST"])
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    post_id = request.args.get("post_id", type=int)

    if request.method == "POST":
        content = request.form.get("content", "").strip()
        if content:
            message = Message(
                sender_id=current_user.id,
                receiver_id=other_user.id,
                post_id=request.form.get("post_id") or None,
                content=content,
            )
            db.session.add(message)
            db.session.commit()
        return redirect(url_for("messages.conversation", user_id=other_user.id, post_id=post_id))

    thread = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user.id),
            and_(Message.sender_id == other_user.id, Message.receiver_id == current_user.id),
        )
    ).order_by(Message.created_at.asc()).all()

    for m in thread:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    related_post = Post.query.get(post_id) if post_id else None
    return render_template("messages/conversation.html", other_user=other_user, thread=thread, related_post=related_post)