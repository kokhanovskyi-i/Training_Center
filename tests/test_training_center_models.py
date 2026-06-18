from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestTrainingCenterModels(TransactionCase):
    "Tests for training center models."

    def setUp(self):
        "Prepare records used in tests."
        super().setUp()

        self.Teacher = self.env['training.center.teacher']
        self.Student = self.env['training.center.student']
        self.Subject = self.env['training.center.subject']
        self.Lesson = self.env['training.center.lesson']
        self.TeacherCategory = self.env['training.center.teacher.category']
        self.TeacherHistory = self.env['training.center.teacher.assignment.history']
        self.LessonReportWizard = self.env['training.center.lesson.report.wizard']

        self.assistant_category = self.env.ref('training_center.teacher_category_assistant')
        self.specialist_category = self.env.ref('training_center.teacher_category_specialist')

    def _create_teacher(self, name, category):
        "Create teacher for test cases."
        return self.Teacher.create(
            {
                'name': name,
                'specialty': 'Test Specialty',
                'category_id': category.id,
                'email': f'{name.lower().replace(" ", "_")}@example.com',
                'phone': '+380501112233',
            }
        )

    def _create_student(self, name, teacher=False):
        "Create student for test cases."
        values = {
            'name': name,
            'email': f'{name.lower().replace(" ", "_")}@example.com',
            'phone': '+380671112233',
        }

        if teacher:
            values['personal_teacher_id'] = teacher.id

        return self.Student.create(values)

    def _create_subject(self, code, name, parent=False):
        "Create subject for test cases."
        values = {
            'code': code,
            'name': name,
        }

        if parent:
            values['parent_id'] = parent.id

        return self.Subject.create(values)

    def test_teacher_category_is_created(self):
        "Check teacher category model."
        category = self.TeacherCategory.create(
            {
                'name': 'Test Teacher Level',
                'sequence': 99,
            }
        )

        self.assertEqual(category.name, 'Test Teacher Level')
        self.assertEqual(category.sequence, 99)

    def test_teacher_is_assistant_depends_on_category(self):
        "Check teacher model assistant flag."
        assistant_teacher = self._create_teacher(
            'Test Assistant Teacher',
            self.assistant_category,
        )
        specialist_teacher = self._create_teacher(
            'Test Specialist Teacher',
            self.specialist_category,
        )

        self.assertTrue(assistant_teacher.is_assistant)
        self.assertFalse(specialist_teacher.is_assistant)

    def test_student_personal_teacher_is_saved(self):
        "Check student model personal teacher field."
        teacher = self._create_teacher(
            'Test Student Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test Student', teacher)

        self.assertEqual(student.personal_teacher_id, teacher)

    def test_subject_complete_name_contains_parent_names(self):
        "Check subject model full name with parent."
        parent_subject = self._create_subject(
            'TEST-PARENT',
            'Test Parent Subject',
        )
        child_subject = self._create_subject(
            'TEST-CHILD',
            'Test Child Subject',
            parent_subject,
        )

        self.assertEqual(
            child_subject._get_complete_name(),
            'Test Parent Subject / Test Child Subject',
        )

    def test_subject_parent_cannot_be_recursive(self):
        "Check that subject recursion is not allowed."
        parent_subject = self._create_subject(
            'TEST-RECURSIVE-PARENT',
            'Test Recursive Parent',
        )
        child_subject = self._create_subject(
            'TEST-RECURSIVE-CHILD',
            'Test Recursive Child',
            parent_subject,
        )

        with self.assertRaises(UserError):
            parent_subject.write({'parent_id': child_subject.id})

    def test_lesson_same_subject_lesson_count(self):
        "Check lesson model counter of lessons with same subject."
        teacher = self._create_teacher(
            'Test Lesson Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test Lesson Student')
        subject = self._create_subject(
            'TEST-SAME-SUBJECT',
            'Test Same Subject',
        )
        other_subject = self._create_subject(
            'TEST-OTHER-SUBJECT',
            'Test Other Subject',
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

    def test_teacher_assignment_history_display_name(self):
        "Check teacher assignment history model."
        teacher = self._create_teacher(
            'Test History Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test History Student', teacher)

        history = self.TeacherHistory.create(
            {
                'student_id': student.id,
                'teacher_id': teacher.id,
                'assignment_date': '2026-01-10',
                'active': True,
            }
        )

        self.assertIn('Test History Student', history.display_name)
        self.assertIn('Test History Teacher', history.display_name)

    def test_assistant_cannot_be_mentor(self):
        "Check that assistant teacher cannot be mentor."
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

    def test_lesson_report_wizard_builds_action(self):
        "Check lesson report wizard action."
        teacher = self._create_teacher(
            'Test Report Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test Report Student', teacher)

        wizard = self.LessonReportWizard.create(
            {
                'teacher_ids': [(6, 0, [teacher.id])],
                'student_ids': [(6, 0, [student.id])],
                'only_done': True,
            }
        )
        action = wizard.action_show_lessons()

        self.assertEqual(action['res_model'], 'training.center.lesson')
        self.assertIn(('status', '=', 'done'), action['domain'])

    def test_res_partner_training_center_role(self):
        "Check extension of res.partner."
        partner = self.env['res.partner'].create(
            {
                'name': 'Test Partner',
                'training_center_role': 'student',
            }
        )

        self.assertEqual(partner.training_center_role, 'student')

    def test_res_users_training_center_profiles(self):
        "Check extension of res.users."
        teacher = self._create_teacher(
            'Test User Teacher',
            self.specialist_category,
        )
        student = self._create_student('Test User Student', teacher)

        self.env.user.write(
            {
                'training_center_teacher_id': teacher.id,
                'training_center_student_id': student.id,
            }
        )

        self.assertEqual(self.env.user.training_center_teacher_id, teacher)
        self.assertEqual(self.env.user.training_center_student_id, student)
