from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch
from .models import OdiUser, Assessee
from .services import registration, utils
from .services.registration import (
    validate_user_registration_data,
    validate_user_company_registration_data,
    save_company_from_request_data,
    register_company, validate_user_assessee_registration_data, save_assessee_from_request_data
)
from .services.utils import validate_password
from .exceptions.exceptions import InvalidRegistrationException
import json
from .services.utils import caller
from .models import Company

EXCEPTION_NOT_RAISED = 'Exception not raised'


class OdiUserTestCase(TestCase):
    def setUp(self) -> None:
        self.user_model = get_user_model()

    def test_create_complete_user(self):
        email = 'complete@email.com'
        password = 'mypassword'

        with patch.object(self.user_model, 'save') as mocked_save:
            new_user = self.user_model.objects.create_user(email=email, password=password)

            self.assertTrue(isinstance(new_user, OdiUser))
            self.assertEqual(new_user.email, email)
            self.assertTrue(new_user.check_password(raw_password=password))
            self.assertFalse(new_user.is_staff)
            self.assertFalse(new_user.is_superuser)
            mocked_save.assert_called_once()

    def test_create_user_with_no_email(self):
        email = ''
        password = 'mypassword'

        with self.assertRaises(ValueError):
            with patch.object(self.user_model, 'save') as mocked_save:
                self.user_model.objects.create_user(email=email, password=password)
                mocked_save.assert_not_called()


class OdiSuperUserTestCase(TestCase):
    def setUp(self) -> None:
        self.user_model = get_user_model()

    def test_superuser_complete(self):
        email = 'superuser@email.com'
        password = 'password'
        dummy_user = OdiUser(email=email)
        dummy_user.set_password(password)

        with patch.object(self.user_model.objects, 'create_user') as mocked_object_manager:
            with patch.object(self.user_model, 'save') as mocked_save:
                mocked_object_manager.return_value = dummy_user
                new_superuser = self.user_model.objects.create_superuser(email=email, password=password)

                self.assertEqual(new_superuser.email, email)
                self.assertTrue(new_superuser.check_password(password))
                self.assertTrue(new_superuser.is_staff)
                self.assertTrue(new_superuser.is_admin)
                self.assertTrue(new_superuser.is_superuser)
                mocked_save.assert_called_once()


class ViewsTestCase(TestCase):
    def test_register_company_when_complete_status_200(self):
        registration_data = {
            'email': 'test_email@gmail.com',
            'password': 'Password1234',
            'confirmed_password': 'Password1234',
            'company_name': 'Dummy Company Name',
            'company_description': 'Dummy company description',
            'company_address': 'Dummy company address'
        }

        response = self.client.post(
            '/users/register-company/',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        self.assertTrue(response.status_code == 200)

        response_content = json.loads(response.content)
        self.assertTrue(len(response_content) > 0)
        self.assertEqual(response_content['email'], registration_data['email'])
        self.assertEqual(response_content['company_name'], registration_data['company_name'])
        self.assertEqual(response_content['description'], registration_data['company_description'])
        self.assertEqual(response_content['address'], registration_data['company_address'])

    def test_register_assessee_when_complete_status_200(self):
        registration_data = {
            'email': 'assessee@gmail.com',
            'password': 'testPassword1234',
            'confirmed_password': 'testPassword1234',
            'first_name': 'Anastasia',
            'last_name': 'Yuliana',
            'phone_number': '+6281275725231',
            'date_of_birth': '1994-09-30T10:37:35.849Z'
        }

        response = self.client.post(
            '/users/register-assessee/',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        self.assertTrue(response.status_code == 200)

        response_content = json.loads(response.content)
        self.assertTrue(len(response_content) > 0)
        self.assertEqual(response_content['email'], registration_data['email'])
        self.assertEqual(response_content['first_name'], registration_data['first_name'])
        self.assertEqual(response_content['last_name'], registration_data['last_name'])
        self.assertEqual(response_content['phone_number'], registration_data['phone_number'])

        # TODO
        # self.assertEqual(response_content['date_of_birth'], registration_data['date_of_birth'])


class UserDataRegistrationTest(TestCase):
    def test_validate_user_registration_data_when_given_valid_data(self):
        request_data = {
            'email': 'email@email.com',
            'password': 'password',
            'confirmed_password': 'password'
        }

        with patch.object(utils, 'validate_password') as mocked_validate_password:
            mocked_validate_password.return_value = {
                'is_valid': True,
                'message': 'Hello'
            }
            validate_user_registration_data(request_data)

            try:
                registration.validate_user_registration_data(request_data)

            except InvalidRegistrationException as exception:
                self.fail(f'{exception} is raised')

    def test_validate_user_registration_data_when_email_not_present(self):
        request_data = {
            'email': None,
            'password': 'password',
            'confirmed_password': 'password'
        }

        try:
            registration.validate_user_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), 'Email must not be null')

    def test_validate_user_registration_data_when_email_is_invalid(self):
        request_data = {
            'email': 'sampleemail',
            'password': 'password',
            'confirmed_password': 'password'
        }

        try:
            registration.validate_user_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), 'Email is invalid')

    def test_validate_user_registration_data_when_password_not_present(self):
        request_data = {
            'email': 'email@email.com',
            'password': None,
            'confirmed_password': 'password'
        }

        try:
            registration.validate_user_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), 'Password must not be null')

    def test_validate_user_registration_data_when_password_does_not_match(self):
        request_data = {
            'email': 'email@email.com',
            'password': 'Password123',
            'confirmed_password': 'password'
        }

        try:
            registration.validate_user_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), 'Password must match password confirmation')


class CompanyDataRegistrationTest(TestCase):
    def test_validate_company_registration_data_when_given_valid_data(self):
        request_data = {
            'company_name': 'PT Indonesia Sejahtera',
            'company_description': 'An Indonesian Company',
            'company_address': 'Sample address'
        }

        try:
            registration.validate_user_company_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.fail(f'{exception} is raised')


class AssesseeDataRegistrationTest(TestCase):

    def test_validate_assessee_registration_data_when_given_valid_data(self):
        request_data = {
            'email': 'assessee@gmail.com',
            'password': 'testPassword1234',
            'confirmed_password': 'testPassword',
            'first_name': 'Anastasia',
            'last_name': 'Yuliana',
            'phone_number': '+6281275725231',
            'date_of_birth': '2022-09-30T10:37:35.849Z'
        }

        try:
            registration.validate_user_assessee_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.fail(f'{exception} is raised')


class UtilsTest(TestCase):
    def test_sample_test(self):
        with patch.object(utils, 'validate_password') as mocked_validate_password:
            mocked_validate_password.return_value = [True, None]
            self.assertTrue(caller()[0])

    def test_validate_password_when_valid(self):
        password = 'Pass1234'
        validation_result = validate_password(password)

        self.assertTrue(validation_result['is_valid'])
        self.assertIsNone(validation_result['message'])

    def test_validate_password_when_length_is_less(self):
        password = '123'
        error_message = 'Password length must be at least 8 characters'
        validation_result = validate_password(password)

        self.assertFalse(validation_result['is_valid'])
        self.assertEqual(validation_result['message'], error_message)

    def test_validate_password_when_no_uppercase(self):
        password = 'abcdefgh'
        error_message = 'Password length must contain at least 1 uppercase character'
        validation_result = validate_password(password)

        self.assertFalse(validation_result['is_valid'])
        self.assertEqual(validation_result['message'], error_message)

    def test_validate_password_when_no_lowercase(self):
        password = 'A12345678'
        error_message = 'Password length must contain at least 1 lowercase character'
        validation_result = validate_password(password)

        self.assertFalse(validation_result['is_valid'])
        self.assertEqual(validation_result['message'], error_message)

    def test_validate_password_when_no_number(self):
        password = 'Password'
        error_message = 'Password length must contain at least 1 number character'
        validation_result = validate_password(password)

        self.assertFalse(validation_result['is_valid'])
        self.assertEqual(validation_result['message'], error_message)

    def test_validate_email_when_valid(self):
        email = 'email@email.com'
        self.assertTrue(utils.validate_email(email))

    def test_validate_email_when_empty(self):
        email = ''
        self.assertFalse(utils.validate_email(email))

    def test_validate_email_when_invalid(self):
        email = 'email@email'
        self.assertFalse(utils.validate_email(email))

    def test_validate_date_format_when_valid(self):
        date_str = '2022-09-26T15:29:30.506Z'
        self.assertTrue(utils.validate_date_format(date_str))

        date_str = '2022-09-26'
        self.assertTrue(utils.validate_date_format(date_str))

    def test_validate_date_format_when_invalid(self):
        date_str = ''
        self.assertFalse(utils.validate_date_format(date_str))

        date_str = '2022-26'
        self.assertFalse(utils.validate_date_format(date_str))

    def test_get_date_from_valid_date_string(self):
        date_str = '2022-09-26T15:29:30.506Z'
        date = utils.get_date_from_string(date_str)

        self.assertEqual(date.day, 26)
        self.assertEqual(date.month, 9)
        self.assertEqual(date.year, 2022)


class UserRegistrationTest(TestCase):
    def test_validate_user_registration_data_when_request_is_valid(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                mocked_validate_email.return_value = True
                mocked_validate_password.return_value = {
                    'is_valid': True,
                    'message': None
                }

                request_data = {
                    'email': 'email@email.com',
                    'password': 'Password123',
                    'confirmed_password': 'Password123'
                }

                try:
                    validate_user_registration_data(request_data)
                except Exception as exception:
                    self.fail(f'{exception} is raised.')

    def test_validate_user_registration_when_email_is_missing(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                expected_error_message = 'Email must not be null'
                mocked_validate_email.return_value = True
                mocked_validate_password.return_value = {
                    'is_valid': True,
                    'message': None
                }

                request_data = {
                    'email': '',
                    'password': 'Password123',
                    'confirmed_password': 'Password123'
                }

                try:
                    validate_user_registration_data(request_data)
                    self.fail(EXCEPTION_NOT_RAISED)
                except InvalidRegistrationException as exception:
                    self.assertEqual(str(exception), expected_error_message)

    def test_validate_user_registration_when_password_is_missing(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                expected_error_message = 'Password must not be null'
                mocked_validate_email.return_value = True
                mocked_validate_password.return_value = {
                    'is_valid': True,
                    'message': None
                }

                request_data = {
                    'email': 'email@email.com',
                    'password': '',
                    'confirmed_password': ''
                }

                try:
                    validate_user_registration_data(request_data)
                    self.fail(EXCEPTION_NOT_RAISED)
                except InvalidRegistrationException as exception:
                    self.assertEqual(str(exception), expected_error_message)

    def test_validate_user_registration_when_password_does_not_match_confirmation(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                expected_error_message = 'Password must match password confirmation'
                mocked_validate_email.return_value = True
                mocked_validate_password.return_value = {
                    'is_valid': True,
                    'message': None
                }

                request_data = {
                    'email': 'email@email.com',
                    'password': 'Password123',
                    'confirmed_password': 'passWord123'
                }

                try:
                    validate_user_registration_data(request_data)
                    self.fail(EXCEPTION_NOT_RAISED)
                except InvalidRegistrationException as exception:
                    self.assertEqual(str(exception), expected_error_message)

    def test_validate_user_registration_when_email_is_invalid(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                expected_error_message = 'Email is invalid'
                mocked_validate_email.return_value = False
                mocked_validate_password.return_value = {
                    'is_valid': True,
                    'message': None
                }

                request_data = {
                    'email': 'email@email.com',
                    'password': 'Password123',
                    'confirmed_password': 'Password123'
                }

                try:
                    validate_user_registration_data(request_data)
                    self.fail('Exception not raised')
                except InvalidRegistrationException as exception:
                    self.assertEqual(str(exception), expected_error_message)

    def test_validate_user_registration_when_password_is_invalid(self):
        with patch.object(utils, 'validate_email') as mocked_validate_email:
            with patch.object(utils, 'validate_password') as mocked_validate_password:
                expected_error_message = 'Password length must contain at least 1 number character'
                mocked_validate_email.return_value = True
                mocked_validate_password.return_value = {
                    'is_valid': False,
                    'message': expected_error_message
                }

                request_data = {
                    'email': 'email@email.com',
                    'password': 'Password',
                    'confirmed_password': 'Password'
                }

                try:
                    validate_user_registration_data(request_data)
                    self.fail(EXCEPTION_NOT_RAISED)
                except InvalidRegistrationException as exception:
                    self.assertEqual(str(exception), expected_error_message)


class CompanyRegistrationTest(TestCase):
    def setUp(self) -> None:
        self.request_data = {
            'email': 'email@email.com',
            'password': 'Password123',
            'company_name': 'PT Indonesia Sejahtera',
            'company_description': 'PT Indonesia Sejahtera adalah sebuah PT',
            'company_address': 'JL. PPL Jaya'
        }

    def test_validate_user_company_registration_data_when_company_is_valid(self):
        request_data = dict(self.request_data)

        try:
            validate_user_company_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.fail(f'{exception} is raised.')

    def test_validate_user_company_registration_data_when_company_name_is_not_valid(self):
        exception_error_message = 'Company name must be more than 3 characters'
        request_data_missing_name = dict(self.request_data)
        request_data_missing_name['company_name'] = ''

        try:
            validate_user_company_registration_data(request_data_missing_name)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

        request_data_short_name = dict(self.request_data)
        request_data_short_name['company_name'] = 'PT'

        try:
            validate_user_company_registration_data(request_data_short_name)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_validate_user_company_registration_data_when_company_description_is_not_valid(self):
        exception_error_message = 'Company description must be more than 3 characters'
        request_data_missing_description = dict(self.request_data)
        request_data_missing_description['company_description'] = ''

        try:
            validate_user_company_registration_data(request_data_missing_description)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

        request_data_short_description = dict(self.request_data)
        request_data_short_description['company_description'] = 'PT'

        try:
            validate_user_company_registration_data(request_data_short_description)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_validate_user_company_registration_data_when_company_address_is_invalid(self):
        exception_error_message = 'Company address must be more than 3 characters'
        request_data_missing_address = dict(self.request_data)
        request_data_missing_address['company_address'] = ''

        try:
            validate_user_company_registration_data(request_data_missing_address)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

        request_data_short_address = dict(self.request_data)
        request_data_short_address['company_address'] = 'JL'

        try:
            validate_user_company_registration_data(request_data_short_address)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_save_company_from_request_data(self):
        request_data = dict(self.request_data)

        expected_company = Company(
            email=request_data.get('email'),
            password=request_data.get('Password123'),
            company_name=request_data.get('company_name'),
            description=request_data.get('company_description'),
            address=request_data.get('company_address'),
        )

        with patch.object(Company.objects, 'create_user') as mocked_create_user:
            mocked_create_user.return_value = expected_company
            saved_company = save_company_from_request_data(request_data)

            mocked_create_user.assert_called_once()
            self.assertEqual(saved_company, expected_company)

    def test_register_company(self):
        request_data = dict(self.request_data)

        expected_company = Company(
            email=request_data.get('email'),
            password=request_data.get('Password123'),
            company_name=request_data.get('company_name'),
            description=request_data.get('company_description'),
            address=request_data.get('company_address'),
        )

        with patch.object(registration, 'validate_user_registration_data') as mocked_validate_user_registration_data:
            with patch.object(registration, 'validate_user_company_registration_data') \
                    as mocked_validate_user_company_registration_data:
                with patch.object(registration, 'save_company_from_request_data') \
                        as mocked_save_company_from_request_data:
                    mocked_validate_user_registration_data.return_value = None
                    mocked_validate_user_company_registration_data.return_value = mocked_validate_user_company_registration_data
                    mocked_save_company_from_request_data.return_value = expected_company

                    dummy_company = registration.register_company(request_data)

                    mocked_validate_user_registration_data.assert_called_once()
                    mocked_validate_user_company_registration_data.assert_called_once()
                    mocked_save_company_from_request_data.assert_called_once()
                    self.assertEqual(dummy_company, expected_company)


class AssesseeRegistrationTest(TestCase):
    def setUp(self) -> None:
        self.request_data = {
            'email': 'assessee@gmail.com',
            'password': 'testPassword1234',
            'confirmed_password': 'testPassword1234',
            'first_name': 'Anastasia',
            'last_name': 'Yuliana',
            'phone_number': '+6281275725231',
            'date_of_birth': '1994-09-30T10:37:35.849Z'
        }

    def test_validate_user_assessee_registration_data_when_assessee_is_valid(self):
        request_data = dict(self.request_data)

        try:
            validate_user_assessee_registration_data(request_data)
        except InvalidRegistrationException as exception:
            self.fail(f'{exception} is raised.')

    def test_validate_user_assessee_registration_data_when_assessee_first_name_is_not_valid(self):
        exception_error_message = 'Assessee first name must not be null'
        request_data_missing_name = dict(self.request_data)
        request_data_missing_name['first_name'] = ''

        try:
            validate_user_assessee_registration_data(request_data_missing_name)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_validate_user_assessee_registration_data_when_assessee_last_name_is_not_valid(self):
        exception_error_message = 'Assessee last name must not be null'
        request_data_missing_name = dict(self.request_data)
        request_data_missing_name['last_name'] = ''

        try:
            validate_user_assessee_registration_data(request_data_missing_name)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_validate_user_assessee_registration_data_when_assessee_phone_number_is_not_valid(self):
        exception_error_message = 'Assessee phone number must not be null'
        request_data_missing_phone_number = dict(self.request_data)
        request_data_missing_phone_number['phone_number'] = ''

        try:
            validate_user_assessee_registration_data(request_data_missing_phone_number)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

        # TODO
        # exception_error_message = 'Phone number is invalid'
        # request_data_invalid_number = dict(self.request_data)
        # request_data_invalid_number['phone_number'] = '+620121275725231'
        # try:
        #     validate_user_assessee_registration_data(request_data_invalid_number)
        #     self.fail(EXCEPTION_NOT_RAISED)
        # except InvalidRegistrationException as exception:
        #     self.assertEqual(str(exception), exception_error_message)

    def test_validate_user_assessee_registration_data_when_date_of_birth_is_invalid(self):
        exception_error_message = 'Assessee date of birth must not be null'
        request_data_missing_dob = dict(self.request_data)
        request_data_missing_dob['date_of_birth'] = ''

        try:
            validate_user_assessee_registration_data(request_data_missing_dob)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

        exception_error_message = 'Invalid date of birth format'
        request_data_invalid_dob = dict(self.request_data)
        request_data_invalid_dob['date_of_birth'] = '08-29-1990'

        try:
            validate_user_assessee_registration_data(request_data_invalid_dob)
            self.fail(EXCEPTION_NOT_RAISED)
        except InvalidRegistrationException as exception:
            self.assertEqual(str(exception), exception_error_message)

    def test_save_assessee_from_request_data(self):
        request_data = dict(self.request_data)

        expected_assessee = Assessee(
            email=request_data.get('email'),
            password=request_data.get('password'),
            first_name=request_data.get('first_name'),
            last_name=request_data.get('last_name'),
            phone_number=request_data.get('phone_number'),
            date_of_birth=request_data.get('date_of_birth'),
        )

        with patch.object(Assessee.objects, 'create_user') as mocked_create_user:
            mocked_create_user.return_value = expected_assessee
            saved_assessee = save_assessee_from_request_data(request_data)

            mocked_create_user.assert_called_once()
            self.assertEqual(saved_assessee, expected_assessee)

    def test_register_company(self):
        request_data = dict(self.request_data)

        expected_assessee = Assessee(
            email=request_data.get('email'),
            password=request_data.get('password'),
            first_name=request_data.get('first_name'),
            last_name=request_data.get('last_name'),
            phone_number=request_data.get('phone_number'),
            date_of_birth=request_data.get('date_of_birth'),
        )

        with patch.object(registration, 'validate_user_registration_data') as mocked_validate_user_registration_data:
            with patch.object(registration, 'validate_user_assessee_registration_data') \
                    as mocked_validate_user_assessee_registration_data:
                with patch.object(registration, 'save_assessee_from_request_data') \
                        as mocked_save_assessee_from_request_data:
                    mocked_validate_user_registration_data.return_value = None
                    mocked_validate_user_assessee_registration_data.return_value = mocked_validate_user_assessee_registration_data
                    mocked_save_assessee_from_request_data.return_value = expected_assessee

                    dummy_assessee = registration.register_assessee(request_data)

                    mocked_validate_user_registration_data.assert_called_once()
                    mocked_validate_user_assessee_registration_data.assert_called_once()
                    mocked_save_assessee_from_request_data.assert_called_once()
                    self.assertEqual(dummy_assessee, expected_assessee)
