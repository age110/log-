from flask import Blueprint, render_template,redirect,url_for,flash,current_app, session,request
from app.forms import RegisterForm,LoginForm, UploadForm,ChangeMail,ChangePassword
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, photos
from app.models import User
from PIL import Image
import os

user = Blueprint('user', __name__)

@user.route("/test/")
@login_required
def test():
    return "xxxx"


@user.route('/login/',methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.username.data).first()
        if not u:
            flash("无效的用户名")
        elif not u.confirmed:
            flash("账户尚未激活，请激活后重新登录")
        elif u.verify_password(form.password.data):
            # session["username"] = form.username.data
            # 用户登录的简写 保存到session
            # 用户登录，顺便可以完成记住我的功能，还可以指定有效的时间
            login_user(u, remember=form.remember.data,)
            flash("登录成功")
            return redirect(request.args.get("next") or url_for("main.index"))
        else:
            flash("无效的密码")

    return render_template("user/login.html", form=form)
@user.route("/logout/")
def logout():
    # session.pop("username")
    # 退出登录的简写
    logout_user()
    flash("您已退出登录")
    return redirect(url_for("main.index"))



@user.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 根据表单数据创建User对象，然后保存到数据库
        u = User(username=form.username.data,
                 password=form.password.data,
                 email=form.email.data)
        #保存到数据库中
        db.session.add(u)
        # 此时还没有提交，所以新用户没有id ，需要手动提交
        db.session.commit()
        # 准备token
        # 发送激活邮件
        token = u.generate_activate_token()
        url = url_for("user.activate", token=token, _external=True)
        send_mail(form.email.data,"账户激活", "activate",
                  username=form.username.data, url=url)
        flash("注册成功")
        return redirect(url_for('main.index'))
    return render_template("user/register.html", form=form)


@user.route("/activate/<token>")
def activate(token):
    if User.check_activate_token(token):
        flash("激活成功")
        return redirect(url_for("user.login"))
    else:
        flash("激活失败")
    return redirect(url_for("user.login"))
# 用户详情
@user.route("/profile/")
@login_required
def profile():
    img_url = photos.url(current_user.icon)
    return render_template("user/profile.html",img_url=img_url)

def random_string(length=32):
    import random
    base_str = "abcdefghijklmnopqrstuvwxyz1234567890"
    return ''.join(random.choice(base_str) for i in range(length))


@user.route("/change_mail/",methods=['get','post'])
@login_required
def change_mail():
    form = ChangeMail()
    if form.validate_on_submit():
        mail = current_user.email
        user = User.query.filter(User.email ==mail).first()
        user.email=form.new_mail.data
        db.session.add(user)
        flash("邮箱已经被修改成功")
        return redirect(url_for("main.index"))
    return render_template("user/change_mail.html", form=form)

@user.route("/change_password/", methods=['get','post'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        password = current_user.password_hash
        user = User.query.filter(User.password_hash == password).first()
        user.password_hash = form.new_password.data
        db.session.add(user)
        flash("密码已经被修改")
        return redirect(url_for("main.index"))

    return render_template("user/change_password.html", form=form)
# 上传头像
@user.route("/change_icon/",methods=["GET","POST"])
def change_icon():
    form = UploadForm()
    if form.validate_on_submit():
        # 获取后缀
        suffix = os.path.splitext(form.icon.data.filename)[1]
        # 随机文件名
        filename = random_string() + suffix
        photos.save(form.icon.data, name=filename)
        # 生成缩略图
        pathname = os.path.join(current_app.config["UPLOADED_PHOTOS_DEST"], filename)
        img = Image.open(pathname)
        img.thumbnail((128,128))
        img.save(pathname)
        # 删除原来的头像(排除默认头像)
        if current_user.icon != "default.jpeg":
            os.remove(os.path.join(current_app.config["UPLOADED_PHOTOS_DEST"],current_user.icon))
        # 保存到数据库中
        current_user.icon = filename
        db.session.add(current_user)
        return redirect(url_for('user.change_icon'))
    img_url = photos.url(current_user.icon)
    return render_template("user/change_icon.html", form=form, img_url=img_url)