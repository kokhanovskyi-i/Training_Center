from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestHrHospitalModels(TransactionCase):
    """Tests for main hospital model methods."""

    def setUp(self):
        """Prepare records used in tests."""
        super().setUp()

        self.Doctor = self.env['hr.hospital.doctor']
        self.Patient = self.env['hr.hospital.patient']
        self.Disease = self.env['hr.hospital.disease']
        self.Appointment = self.env['hr.hospital.appointment']

        self.intern_category = self.env.ref('hr_hospital.doctor_category_intern')
        self.specialist_category = self.env.ref('hr_hospital.doctor_category_specialist')

    def _create_doctor(self, name, category):
        """Create doctor for test cases."""
        return self.Doctor.create(
            {
                'name': name,
                'specialty': 'Test Specialty',
                'category_id': category.id,
                'email': f'{name.lower().replace(" ", "_")}@example.com',
                'phone': '+380501112233',
            }
        )

    def _create_patient(self, name):
        """Create patient for test cases."""
        return self.Patient.create(
            {
                'name': name,
                'email': f'{name.lower().replace(" ", "_")}@example.com',
                'phone': '+380671112233',
            }
        )

    def test_disease_complete_name_contains_parent_names(self):
        """Check disease full name with parent."""
        parent_disease = self.Disease.create(
            {
                'code': 'TEST-PARENT',
                'name': 'Test Parent Disease',
            }
        )
        child_disease = self.Disease.create(
            {
                'code': 'TEST-CHILD',
                'name': 'Test Child Disease',
                'parent_id': parent_disease.id,
            }
        )

        self.assertEqual(
            child_disease._get_complete_name(),
            'Test Parent Disease / Test Child Disease',
        )

    def test_disease_parent_cannot_be_recursive(self):
        """Check that disease recursion is not allowed."""
        parent_disease = self.Disease.create(
            {
                'code': 'TEST-RECURSIVE-PARENT',
                'name': 'Test Recursive Parent',
            }
        )
        child_disease = self.Disease.create(
            {
                'code': 'TEST-RECURSIVE-CHILD',
                'name': 'Test Recursive Child',
                'parent_id': parent_disease.id,
            }
        )

        with self.assertRaises(UserError):
            parent_disease.write({'parent_id': child_disease.id})

    def test_doctor_is_intern_depends_on_category(self):
        """Check intern flag from doctor category."""
        intern_doctor = self._create_doctor('Test Intern Doctor', self.intern_category)
        specialist_doctor = self._create_doctor(
            'Test Specialist Doctor',
            self.specialist_category,
        )

        self.assertTrue(intern_doctor.is_intern)
        self.assertFalse(specialist_doctor.is_intern)

    def test_intern_cannot_be_mentor(self):
        """Check that intern cannot be mentor."""
        intern_doctor = self._create_doctor(
            'Test Mentor Intern Doctor',
            self.intern_category,
        )

        with self.assertRaises(ValidationError):
            self.Doctor.create(
                {
                    'name': 'Test Doctor With Wrong Mentor',
                    'specialty': 'Test Specialty',
                    'category_id': self.specialist_category.id,
                    'mentor_id': intern_doctor.id,
                    'email': 'test_wrong_mentor@example.com',
                    'phone': '+380501114455',
                }
            )

    def test_same_disease_visit_count(self):
        """Check counter of visits with same disease."""
        doctor = self._create_doctor(
            'Test Appointment Doctor',
            self.specialist_category,
        )
        patient = self._create_patient('Test Appointment Patient')

        disease = self.Disease.create(
            {
                'code': 'TEST-SAME-DISEASE',
                'name': 'Test Same Disease',
            }
        )
        other_disease = self.Disease.create(
            {
                'code': 'TEST-OTHER-DISEASE',
                'name': 'Test Other Disease',
            }
        )

        first_appointment = self.Appointment.create(
            {
                'doctor_id': doctor.id,
                'patient_id': patient.id,
                'disease_id': disease.id,
            }
        )
        self.Appointment.create(
            {
                'doctor_id': doctor.id,
                'patient_id': patient.id,
                'disease_id': disease.id,
            }
        )
        self.Appointment.create(
            {
                'doctor_id': doctor.id,
                'patient_id': patient.id,
                'disease_id': other_disease.id,
            }
        )

        self.assertEqual(first_appointment.same_disease_visit_count, 2)
