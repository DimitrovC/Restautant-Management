import qrcode, io
from flask import render_template, flash, redirect, url_for, request, send_file
from sqlalchemy import func
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.forms import *
from app.models import *
from werkzeug.urls import url_parse

def init_app(app):
    @app.route('/')
    @app.route('/index')
    def index():
        random_items = MenuItem.query.order_by(func.random()).limit(3).all()
        return render_template('index.html', title='Ресторант Ритъм', random_items=random_items)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        return render_template('login.html', title='Sign In', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route('/reservations', methods=['GET', 'POST'])
    @login_required
    def reservations():
        form = ReservationForm()
        if form.validate_on_submit():
            reservation = Reservation(
                date=form.date.data,
                time=form.time.data,
                guests=form.guests.data,
                user_id=current_user.id
            )
            db.session.add(reservation)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('reservations.html', title='Reservations', form=form)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        form = TicketForm()
        if form.validate_on_submit():
            ticket = Ticket(subject=form.subject.data, message=form.message.data, user_id=current_user.id)
            db.session.add(ticket)
            db.session.commit()
            return redirect(url_for('profile_view_ticket', ticket_id=ticket.id))   
        return render_template('contact.html', title='Contact Us', form=form)

    @app.route('/menu/qr')
    def generate_qr():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        menu_url = url_for('menu', _external=True)
        qr.add_data(menu_url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)
        return send_file(buf, mimetype='image/png')

    @app.route('/menu', methods=['GET', 'POST'])
    def menu():
        categories = db.session.query(MenuItem.category).distinct().all()
        categories = [category[0] for category in categories]

        query = MenuItem.query

        if request.method == 'POST':
            selected_category = request.form.get('category')
            price_range = request.form.get('price_range')

            if selected_category:
                query = query.filter_by(category=selected_category)
            
            if price_range:
                min_price, max_price = map(int, price_range.split('-'))
                query = query.filter(MenuItem.price.between(min_price, max_price))

        menu_items = query.all()
        return render_template('menu.html', title='Menu', menu_items=menu_items, categories=categories)
    







    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        is_admin = current_user.is_admin
        form = UserProfileForm()
        if form.validate_on_submit():
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            if profile is None:
                profile = UserProfile(user_id=current_user.id)
            profile.address = form.address.data
            profile.phone_number = form.phone_number.data
            profile.preferences = form.preferences.data
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('profile'))
        elif request.method == 'GET':
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            if profile:
                form.address.data = profile.address
                form.phone_number.data = profile.phone_number
                form.preferences.data = profile.preferences
        return render_template('profile.html', title='Profile', form=form, is_admin=is_admin)

    @app.route('/profile/tickets')
    @login_required
    def profile_tickets():
        is_admin = current_user.is_admin
        tickets = Ticket.query.filter_by(user_id=current_user.id).all()
        return render_template('profile_tickets.html', title='Your Tickets', tickets=tickets, is_admin=is_admin)

    @app.route('/profile/reservations', methods=['GET', 'POST'])
    @login_required
    def profile_reservations():
        is_admin = current_user.is_admin
        if request.method == 'POST':
            reservation_id = request.form.get('reservation_id')
            action = request.form.get('action')
            
            if action == 'cancel' and reservation_id:
                reservation = Reservation.query.filter_by(id=reservation_id, user_id=current_user.id).first()
                if reservation:
                    db.session.delete(reservation)
                    db.session.commit()
                    flash('Резервацията беше успешно отказана.', 'success')
                else:
                    flash('Неуспешно отказанване на резервацията.', 'danger')

        reservations = Reservation.query.filter_by(user_id=current_user.id).all()
        return render_template('profile_reservations.html', title='Your Reservations', reservations=reservations, is_admin=is_admin)


    @app.route('/profile/settings', methods=['GET', 'POST'])
    @login_required
    def profile_settings():
        is_admin = current_user.is_admin
        form = UserProfileForm()
        if form.validate_on_submit():
            user = User.query.get(current_user.id)
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            if profile is None:
                profile = UserProfile(user_id=current_user.id)
            profile.first_name = form.first_name.data
            profile.last_name = form.last_name.data
            profile.address = form.address.data
            profile.phone_number = form.phone_number.data
            profile.preferences = form.preferences.data

            user.username = form.username.data
            user.email = form.email.data
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('profile_settings'))
        elif request.method == 'GET':
            user = User.query.get(current_user.id)
            profile = UserProfile.query.filter_by(user_id=current_user.id).first()
            if profile:
                form.first_name.data = profile.first_name
                form.last_name.data = profile.last_name
                form.address.data = profile.address
                form.phone_number.data = profile.phone_number
                form.preferences.data = profile.preferences
            form.username.data = user.username
            form.email.data = user.email
        return render_template('profile_settings.html', title='Account Settings', form=form, is_admin=is_admin)

    @app.route('/profile/ticket/<int:ticket_id>', methods=['GET', 'POST'])
    @login_required
    def profile_view_ticket(ticket_id):
        is_admin = current_user.is_admin
        ticket = Ticket.query.get_or_404(ticket_id)
        if ticket.user_id != current_user.id:
            return redirect(url_for('profile_tickets'))
        messages = Message.query.filter_by(ticket_id=ticket_id).all()
        description = Ticket.query.filter_by(id=ticket_id).all()
        if request.method == 'POST':
            if request.form['action'] == 'add_message':
                message = Message(content=request.form['message'], user_id=current_user.id, ticket_id=ticket.id)
                db.session.add(message)
                db.session.commit()
            elif request.form['action'] == 'close':
                ticket.status = 'Затворена'
                db.session.commit()
            return redirect(url_for('profile_view_ticket', ticket_id=ticket.id))
        return render_template('view_ticket.html', title='Ticket Details', ticket=ticket, messages=messages, is_admin=is_admin)

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        users = User.query.all()
        reservations = Reservation.query.all()
        tickets = Ticket.query.all()
        return render_template('admin/dashboard.html', title='Admin Dashboard', users=users, reservations=reservations, tickets=tickets)

    @app.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(user_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        user = User.query.get_or_404(user_id)
        form = UserForm(obj=user)
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

    @app.route('/admin/user/add', methods=['GET', 'POST'])
    @login_required
    def add_user():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        form = CreateUserForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_admin=form.is_admin.data
            )
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/add_user.html', title='Add User', form=form)

    @app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/reservation/<int:reservation_id>')
    @login_required
    def view_reservation(reservation_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        reservation = Reservation.query.get_or_404(reservation_id)
        return render_template('admin/view_reservation.html', title='Reservation Details', reservation=reservation)

    @app.route('/admin/reservation/delete/<int:reservation_id>', methods=['POST'])
    @login_required
    def delete_reservation(reservation_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        reservation = Reservation.query.get_or_404(reservation_id)
        db.session.delete(reservation)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/tickets')
    @login_required
    def view_tickets():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        tickets = Ticket.query.all()
        return render_template('admin/tickets.html', title='View Tickets', tickets=tickets)

    @app.route('/admin/ticket/<int:ticket_id>', methods=['GET', 'POST'])
    @login_required
    def view_ticket(ticket_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        ticket = Ticket.query.get_or_404(ticket_id)
        form = MessageForm()
        if form.validate_on_submit():
            message = Message(content=form.content.data, user_id=current_user.id, ticket_id=ticket.id)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('view_ticket', ticket_id=ticket.id))
        return render_template('admin/ticket.html', title='Ticket Details', ticket=ticket, form=form)

    @app.route('/admin/menu', methods=['GET', 'POST'])
    @login_required
    def admin_menu():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        form = MenuItemForm()
        if form.validate_on_submit():
            try:
                menu_item = MenuItem(
                    name=form.name.data,
                    description=form.description.data,
                    price=form.price.data,
                    category=form.category.data,
                    special=form.special.data,
                    promotion=form.promotion.data,
                    image_url=form.image_url.data
                )
                db.session.add(menu_item)
                db.session.commit()
                return redirect(url_for('admin_menu'))
            except Exception as e:
                flash(f'Възникна грешка при добавянето на продукт: {str(e)}')
        
        menu_items = MenuItem.query.all()
        return render_template('admin/menu.html', title='Manage Menu', form=form, menu_items=menu_items)


    @app.route('/admin/menu/add', methods=['GET', 'POST'])
    @login_required
    def add_menu_item():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        form = MenuItemForm()
        if form.validate_on_submit():
            menu_item = MenuItem(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                category=form.category.data,
                special=form.special.data,
                promotion=form.promotion.data,
                image_url=form.image_url.data
            )
            db.session.add(menu_item)
            db.session.commit()
            return redirect(url_for('menu'))
        return render_template('admin/add_menu_item.html', title='Add Menu Item', form=form)

    
    @app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    def edit_menu_item(item_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))
        menu_item = MenuItem.query.get_or_404(item_id)
        form = MenuItemForm(obj=menu_item)
        if form.validate_on_submit():
            form.populate_obj(menu_item)
            db.session.commit()
            return redirect(url_for('menu'))
        return render_template('admin/edit_menu_item.html', title='Edit Menu Item', form=form, menu_item=menu_item)

    @app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
    def delete_ticket(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)
        messages = Message.query.filter_by(ticket_id=ticket.id).all()
        for message in messages:
            db.session.delete(message)
        db.session.delete(ticket)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
    @login_required
    def delete_menu_item(item_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        menu_item = MenuItem.query.get_or_404(item_id)
        db.session.delete(menu_item)
        db.session.commit()
        return redirect(url_for('menu'))

    @app.route('/admin/employees')
    @login_required
    def view_employees():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        employees = Employee.query.all()
        return render_template('admin/employees.html', title='View Employees', employees=employees)

    @app.route('/admin/employees/add', methods=['GET', 'POST'])
    @login_required
    def add_employee():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        form = EmployeeForm()
        if form.validate_on_submit():
            employee = Employee(
                name=form.name.data,
                position=form.position.data,
                schedule=form.schedule.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                active=form.active.data
            )
            db.session.add(employee)
            db.session.commit()
            return redirect(url_for('view_employees'))
        return render_template('admin/add_employee.html', title='Add Employee', form=form)

    @app.route('/admin/employees/edit/<int:employee_id>', methods=['GET', 'POST'])
    @login_required
    def edit_employee(employee_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        employee = Employee.query.get_or_404(employee_id)
        form = EmployeeForm(obj=employee)
        if form.validate_on_submit():
            form.populate_obj(employee)
            db.session.commit()
            return redirect(url_for('view_employees'))
        return render_template('admin/edit_employee.html', title='Edit Employee', form=form, employee=employee)

    @app.route('/admin/employees/delete/<int:employee_id>', methods=['POST'])
    @login_required
    def delete_employee(employee_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return redirect(url_for('view_employees'))

    @app.route('/admin/reports')
    @login_required
    def view_reports():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        total_reservations = db.session.query(Reservation).count()
        total_users = db.session.query(User).count()
        total_sales = db.session.query(db.func.sum(Reservation.guests)).scalar()

        return render_template('admin/reports.html', title='View Reports', total_reservations=total_reservations, total_users=total_users, total_sales=total_sales)

    @app.route('/admin/inventory')
    @login_required
    def view_inventory():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        inventory_items = Inventory.query.all()
        return render_template('admin/inventory.html', title='View Inventory', inventory_items=inventory_items)

    @app.route('/admin/inventory/add', methods=['GET', 'POST'])
    @login_required
    def add_inventory_item():
        if not current_user.is_admin:
            return redirect(url_for('index'))

        form = InventoryForm()
        if form.validate_on_submit():
            inventory_item = Inventory(
                name=form.name.data,
                quantity=form.quantity.data,
                threshold=form.threshold.data,
                supplier=form.supplier.data
            )
            db.session.add(inventory_item)
            db.session.commit()
            return redirect(url_for('view_inventory'))
        return render_template('admin/add_inventory_item.html', title='Add Inventory Item', form=form)

    @app.route('/admin/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
    @login_required
    def edit_inventory_item(item_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        inventory_item = Inventory.query.get_or_404(item_id)
        form = InventoryForm(obj=inventory_item)
        if form.validate_on_submit():
            form.populate_obj(inventory_item)
            db.session.commit()
            return redirect(url_for('view_inventory'))
        return render_template('admin/edit_inventory_item.html', title='Edit Inventory Item', form=form, inventory_item=inventory_item)

    @app.route('/admin/inventory/delete/<int:item_id>', methods=['POST'])
    @login_required
    def delete_inventory_item(item_id):
        if not current_user.is_admin:
            return redirect(url_for('index'))

        inventory_item = Inventory.query.get_or_404(item_id)
        db.session.delete(inventory_item)
        db.session.commit()
        return redirect(url_for('view_inventory'))