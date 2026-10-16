from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, NumberRange, EqualTo, Length, Optional
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[
            ('', 'Please choose an option'),
            ('book', 'Book'),
            ('digital', 'Digital'),
            ('daily', 'Daily'),
            ('others', 'Others'),
        ],
        validators=[DataRequired()],
    )
    price = DecimalField(
        'Price',
        validators=[DataRequired(), NumberRange(min=0)],
    )
    description = TextAreaField('Description')
    image = FileField(
        'Image',
        validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only')],
        render_kw={'accept': '.jpg,.png,.jpeg'},
    )
    submit = SubmitField('Post')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16)])
    password_confirm = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password'), Length(min=8, max=16)],
    )
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16)])
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=10)])
    password = PasswordField('New Password', validators=[Optional(), Length(min=8, max=16)])
    password_confirm = PasswordField(
        'Confirm New Password',
        validators=[Optional(), EqualTo('password'), Length(min=8, max=16)],
    )
    submit = SubmitField('Update profile')


class PriceForm(FlaskForm):
    price = SelectField(
        'Price',
        choices=[
            ('a', '0~10'),
            ('b', '10~50'),
            ('c', '50~100'),
            ('d', '100~500'),
            ('e', '500~1000'),
            ('others', '1000+'),
        ],
    )
