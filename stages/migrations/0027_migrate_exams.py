from django.db import migrations


def migrate_exams(apps, schema_editor):
    Student = apps.get_model('stages', 'Student')
    Examination = apps.get_model('stages', 'Examination')

    for student in Student.objects.all():
        if student.session or student.date_exam:
            Examination.objects.create(
                student=student, type_exam='exam',
                session=student.session, date_exam=student.date_exam,
                room=student.room, mark=student.mark, mark_acq=student.mark_acq,
                internal_expert=student.internal_expert, external_expert=student.expert,
                date_soutenance_mailed=student.date_soutenance_mailed,
                date_confirm_received=student.date_confirm_received,
            )
        if student.session_ep or student.date_exam_ep:
            Examination.objects.create(
                student=student, type_exam='entre',
                session=student.session_ep, date_exam=student.date_exam_ep,
                room=student.room_ep, mark=student.mark_ep, mark_acq=student.mark_ep_acq,
                internal_expert=student.internal_expert_ep, external_expert=student.expert_ep,
                date_soutenance_mailed=student.date_soutenance_ep_mailed,
                date_confirm_received=student.date_confirm_ep_received,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('stages', '0026_examination'),
    ]

    operations = [migrations.RunPython(migrate_exams)]
