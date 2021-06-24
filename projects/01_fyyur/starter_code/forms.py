from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Regexp, Optional, Length
from enum import Enum


# States enum
class StatesEnum(Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'


# Genres Enum
class GenresEnum(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Thtre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_n_B = 'R&B'
    Reggae = 'Reggae'
    RocknRoll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        # use the states enum's values as both the value and the label for state choices
        choices=[(member.value, member.value) for _, member in StatesEnum.__members__.items()]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Regexp(r'^[0-9]{3}-{1}[0-9]{3}-{1}[0-9]+$', message='phone format is xxx-xxx-xxx'), Length(min=11, max=12, message='Phone number has to be 9 or 10 digits')]
    )
    image_link = StringField(
        'image_link', validators=[URL(message='Image Link must be a valid URL'), Optional()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
         # use the genres enum's values as both the value and the label for genres choices
        choices=[(member.value, member.value) for _, member in GenresEnum.__members__.items()]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message='Facebook Link must be a valid URL'), Optional()]
    )
    website_link = StringField(
        'website_link', validators=[URL(message='Website Link must be a valid URL'), Optional()]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        # use the states enum's values as both the value and the label for state choices
        choices=[(member.value, member.value) for _, member in StatesEnum.__members__.items()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Regexp(r'^[0-9]{3}-{1}[0-9]{3}-{1}[0-9]+$', message='phone format is xxx-xxx-xxx'), Length(min=11, max=12, message='Phone number has to be 9 or 10 digits')]
    )
    image_link = StringField(
        'image_link', validators=[URL(message='Image Link must be a valid URL'), Optional()]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
         # use the genres enum's values as both the value and the label for genres choices
        choices=[(member.value, member.value) for _, member in GenresEnum.__members__.items()]
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL(message='Facebook Link must be a valid URL'), Optional()]
     )

    website_link = StringField(
        'website_link', validators=[URL(message='Website Link must be a valid URL'), Optional()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

