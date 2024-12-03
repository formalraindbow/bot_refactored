class User:
    def __init__(self, user_id, username, first_name):
        self.user_id = user_id
        self.username = username or user_id
        self.first_name = first_name
        self.registration_date = None
        self.is_registered = False
        self.name = None
        self.university = None
        self.faculty = None
        self.info_source = None
        self.is_payment_confirmed = False
        # Дополнительные поля...
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'registration_date': self.registration_date,
            'is_registered': self.is_registered,
            'name': self.name,
            'university': self.university,
            'faculty': self.faculty,
            'info_source': self.info_source,
            'is_payment_confirmed': self.is_payment_confirmed, 
            # Дополнительные поля...
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['user_id'], data.get('username'), data.get('first_name'))
        user.registration_date = data.get('registration_date')
        user.is_registered = data.get('is_registered', False)
        user.name = data.get('name')
        user.university = data.get('university')
        user.faculty = data.get('faculty')
        user.info_source = data.get('info_source')
        user.is_payment_confirmed = data.get('is_payment_confirmed', False)
        return user
    