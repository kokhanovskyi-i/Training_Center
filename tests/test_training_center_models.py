from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestTrainingCenterModels(TransactionCase):
    """Tests for main hospital model methods."""

    def setUp(self):
        """Prepare records used in tests."""
        super().setUp()

        self.Teacher = self.env['training.center.teacher']
        self.Student = self.env['training.center.student']
        self.Subject = self.env['training.center.subject']
        self.Lesson = self.env['training.center.lesson']

        self.assistant_category = self.env.ref('training_center.teacher_category_assistant')
        self.specialist_category = self.env.ref('training_center.teacher_category_specialist')

    def _create_teacher(self, name, category):
        """Create teacher for test cases."""
        return self.Teacher.create(
            {
                'name': name,
                'specialty': 'Test Specialty',
                'category_id': category.id,
                'email': f'{name.lower().replace(" ", "_")}@example.com',
                'phone': '+380501112233',
            }
        )

    def _create_student(self, name):
        """Create student for test cases."""
        return self.Student.create(
            {
                'name': name,
                'email': f'{name.lower().replace(" ", "_")}@example.com',
                'phone': '+380671112233',
            }
        )

    def test_subject_complete_name_contains_parent_names(self):
        """Check subject full name with parent."""
        parent_subject = self.Subject.create(
            {
                'code': 'TEST-PARENT',
                'name': 'Test Parent Subject',
            }
        )
        child_subject = self.Subject.create(
            {
                'code': 'TEST-CHILD',
                'name': 'Test Child Subject',
                'parent_id': parent_subject.id,
            }
        )

        self.assertEqual(
            child_subject._get_complete_name(),
            'Test Parent Subject / Test Child Subject',
        )

    def test_subject_parent_cannot_be_recursive(self):
        """Check that subject recursion is not allowed."""
        parent_subject = self.Subject.create(
            {
                'code': 'TEST-RECURSIVE-PARENT',
                'name': 'Test Recursive Parent',
            }
        )
        child_subject = self.Subject.create(
            {
                'code': 'TEST-RECURSIVE-CHILD',
                'name': 'Test Recursive Child',
                'parent_id': parent_subject.id,
            }
        )

        with self.assertRaises(UserError):
            parent_subject.write({'parent_id': child_subject.id})

    def test_teacher_is_assistant_depends_on_category(self):
        """Check assistant flag from teacher category."""
        assistant_teacher = self._create_teacher('Test Assistant Teacher', self.assistant_category)
        specialist_teacher = self._create_teacher(
            'Test Specialist Teacher',
            self.specialist_category,
        )

        self.assertTrue(assistant_teacher.is_assistant)
        self.assertFalse(specialist_teacher.is_assistant)

    def test_assistant_cannot_be_mentor(self):
        """Check that assistant cannot be mentor."""
        assistant_teacher = self._create_teacher(
            'Test Mentor Assistant Teacher',
            self.assistant_category,
        )

        with self.assertRaises(ValidationError):
            self.Teacher.create(
                {
                    'name': 'Test Teacher With Wrong Mentor',
                    'specialty': 'Test Specialty',
                    'category_id': self.specialist_category.id,
                    'mentor_id': assistant_teacher.id,
                    'email': 'test_wrong_mentor@example.com',
                    'phone': '+380501114455',
                }
            )

    def test_same_subject_lesson_count(self):
        """Check counter of lessons with same subject."""
        teacher = self._create_teacher(
            'Test Lesson Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test Lesson Student')

        subject = self.Subject.create(
            {
                'code': 'TEST-SAME-DISEASE',
                'name': 'Test Same Subject',
            }
        )
        other_subject = self.Subject.create(
            {
                'code': 'TEST-OTHER-DISEASE',
                'name': 'Test Other Subject',
            }
        )

        first_lesson = self.Lesson.create(
            {
                'teacher_id': teacher.id,
                'student_id': student.id,
                'subject_id': subject.id,
            }
        )
        self.Lesson.create(
            {
                'teacher_id': teacher.id,
                'student_id': student.id,
                'subject_id': subject.id,
            }
        )
        self.Lesson.create(
            {
                'teacher_id': teacher.id,
                'student_id': student.id,
                'subject_id': other_subject.id,
            }
        )

        self.assertEqual(first_lesson.same_subject_lesson_count, 2)
