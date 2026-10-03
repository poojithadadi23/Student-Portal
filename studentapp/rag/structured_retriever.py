from studentapp.models import Student

def get_student_data(user):
    student = Student.objects.get(user=user)

    return {
        "student_id":student.id,
        "first_name":student.user.first_name,
        "last_name":student.user.last_name,
        "username":student.user.username,
        "contact":student.contact,
        "address":student.address,
        "course":student.course
    }

#convert  student db information into text
def student_data_to_context(student_data):
    return f"""
Student Information:

Name: {student_data["first_name"]}{student_data["last_name"]}
Username:{student_data["username"]}
Contact:{student_data["contact"]}
Address:{student_data["address"]}
Course:{student_data["course"]}
"""