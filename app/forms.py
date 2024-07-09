from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DateTimeField, DateField, TimeField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    password = PasswordField('Парола', validators=[DataRequired()])
    remember_me = BooleanField('Запомни ме')
    submit = SubmitField('Вход')

class RegistrationForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл адрес', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    password2 = PasswordField(
        'Повтори парола', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Регистрирайте се')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Потребителското име е заето, моля използвайте друго.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Имейл адресът е зает, моля използвайте друг.')

class TicketForm(FlaskForm):
    subject = StringField('Заглавие', validators=[DataRequired()])
    message = TextAreaField('Съобщение', validators=[DataRequired()])
    submit = SubmitField('Изпрати')

class MessageForm(FlaskForm):
    content = TextAreaField('Съобщение', validators=[DataRequired()])
    submit = SubmitField('Изпрати')

class ReservationForm(FlaskForm):
    date = DateField('Дата', format='%d.%m.%Y', validators=[DataRequired()])
    time = TimeField('Чат', format='%H:%M', validators=[DataRequired()])
    guests = IntegerField('Брой гости', validators=[DataRequired()])
    submit = SubmitField('Резервирай')

class UserForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл адрес', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Запази')

class CreateUserForm(FlaskForm):
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл адрес', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    is_admin = BooleanField('Администратор')
    submit = SubmitField('Добави потребител')

class MenuItemForm(FlaskForm):
    name = StringField('Име', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    category = SelectField('Категория', choices=[
        ('Предястие', 'Предястие'), 
        ('Основно ястие', 'Основно ястие'), 
        ('Десерт', 'Десерт'), 
        ('Напитка', 'Напитка'),
        ('Алкохол', 'Алкохол'),
        ('Хляб', 'Хляб'),
        ('Друго', 'Друго')], 
        validators=[DataRequired()]
    )
    special = BooleanField('Специално')
    promotion = BooleanField('Промоция')
    image_url = StringField('URL снимка на продукт')
    submit = SubmitField('Запази')


class EmployeeForm(FlaskForm):
    name = StringField('Име', validators=[DataRequired()])
    position = StringField('Позиция', validators=[DataRequired()])
    schedule = TextAreaField('График')
    start_date = DateField('Начална дата', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Крайна дата', format='%Y-%m-%d', validators=[Optional()])
    active = BooleanField('Активен')
    submit = SubmitField('Запази')

class InventoryForm(FlaskForm):
    name = StringField('Име', validators=[DataRequired()])
    quantity = IntegerField('Количество', validators=[DataRequired()])
    threshold = IntegerField('Лимит', validators=[DataRequired()])
    supplier = StringField('Доставчик')
    submit = SubmitField('Запази')

class UserProfileForm(FlaskForm):
    first_name = StringField('Име', validators=[Optional()])
    last_name = StringField('Фамилия', validators=[Optional()])
    username = StringField('Потребителско име', validators=[DataRequired()])
    email = StringField('Имейл адрес', validators=[DataRequired(), Email()])
    password = PasswordField('Нова парола', validators=[Optional()])
    address = StringField('Адрес', validators=[Optional()])
    phone_number = StringField('Телефонен номер', validators=[Optional()])
    preferences = TextAreaField('Предпочитания', validators=[Optional()])
    submit = SubmitField('Запази')


