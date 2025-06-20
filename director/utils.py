# # # import os

# # # def Document_folder(instance, filename):
# # #     base_path = "Document_folder"

# # #     if instance.student:
# # #         user = instance.student.user
# # #         year_level = (
# # #             instance.student.studentyearlevel_set.first().level.level_name
# # #             if instance.student.studentyearlevel_set.exists()
# # #             else "unknown_level"
# # #         )
# # #         folder_path = f"student/{year_level}/{user.first_name}_{user.last_name}"

# # #     elif instance.teacher:
# # #         user = instance.teacher.user
# # #         folder_path = f"teacher/{user.first_name}_{user.last_name}"

# # #     elif instance.guardian:
# # #         user = instance.guardian.user
# # #         folder_path = f"guardian/{user.first_name}_{user.last_name}"

# # #     elif instance.office_staff:
# # #         user = instance.office_staff.user
# # #         folder_path = f"office_staff/{user.first_name}_{user.last_name}"

# # #     else:
# # #         folder_path = "unknown"

# # #     # Debugging print statements
# # #     print(f"Detected role: {folder_path.split('/')[0]}")
# # #     print(f"Saving file for: {folder_path}")
# # #     print(f"Final path: {os.path.join(base_path, folder_path, filename)}")

# # #     return os.path.join(base_path, folder_path, filename)




# # import os
# # import logging

# # logger = logging.getLogger(__name__)

# # def Document_folder(instance, filename):
# #     base_path = "Document_folder"

# #     if instance.student:
# #         user = instance.student.user
# #         year_level = (
# #             instance.student.studentyearlevel_set.first().level.level_name
# #             if instance.student.studentyearlevel_set.exists()
# #             else "unknown_level"
# #         )
# #         folder_path = f"student/{year_level}/{user.first_name}_{user.last_name}"

# #     elif instance.teacher:
# #         user = instance.teacher.user
# #         folder_path = f"teacher/{user.first_name}_{user.last_name}"

# #     elif instance.guardian:
# #         user = instance.guardian.user
# #         folder_path = f"guardian/{user.first_name}_{user.last_name}"

# #     elif instance.office_staff:
# #         user = instance.office_staff.user
# #         folder_path = f"office_staff/{user.first_name}_{user.last_name}"

# #     else:
# #         folder_path = "unknown"

# #     # Logging output (instead of print)
# #     logger.warning(f"Detected role: {folder_path.split('/')[0]}")
# #     logger.warning(f"Saving file for: {folder_path}")
# #     logger.warning(f"Final path: {os.path.join(base_path, folder_path, filename)}")

# #     return os.path.join(base_path, folder_path, filename)

# # director/utils.py

# import os

# def Document_folder(instance, filename):
#     base_path = "Document_folder"

#     if instance.student:
#         user = instance.student.user
#         folder_path = f"student/{user.first_name}_{user.last_name}"

#     elif instance.teacher:
#         user = instance.teacher.user
#         folder_path = f"teacher/{user.first_name}_{user.last_name}"

#     elif instance.guardian:
#         user = instance.guardian.user
#         folder_path = f"guardian/{user.first_name}_{user.last_name}"

#     elif instance.office_staff:
#         user = instance.office_staff.user
#         folder_path = f"office_staff/{user.first_name}_{user.last_name}"

#     else:
#         folder_path = "unknown"

#     # FINAL PRINT CHECKS
#     print("DEBUG: ROLE DETECTED:", folder_path.split('/')[0])
#     print("DEBUG: FULL FOLDER PATH:", os.path.join(base_path, folder_path))
#     print("DEBUG: FILE PATH:", os.path.join(base_path, folder_path, filename))

#     return os.path.join(base_path, folder_path, filename)

# director/utils.py


#### commented as of 19 june25 at 11:11 PM from here
# import os

# def Document_folder(instance, filename):
#     base_path = "Document_folder"

#     if instance.student:
#         user = instance.student.user
#         # Get the year level (for example: "class1", "class2")
#         year_level = (
#             instance.student.studentyearlevel_set.first().level.level_name
#             if instance.student.studentyearlevel_set.exists()
#             else "unknown_level"
#         )
#         # Folder path with student's year level and name (first_name_last_name)
#         folder_path = f"student/{year_level}/{user.first_name}_{user.last_name}"

#     elif instance.teacher:
#         user = instance.teacher.user
#         folder_path = f"teacher/{user.first_name}_{user.last_name}"

#     elif instance.guardian:
#         user = instance.guardian.user
#         folder_path = f"guardian/{user.first_name}_{user.last_name}"

#     elif instance.office_staff:
#         user = instance.office_staff.user
#         folder_path = f"office_staff/{user.first_name}_{user.last_name}"

#     else:
#         folder_path = "unknown"

#     # Debugging print statements
#     print(f"DEBUG: ROLE DETECTED: {folder_path.split('/')[0]}")
#     print(f"DEBUG: FULL FOLDER PATH: {os.path.join(base_path, folder_path)}")
#     print(f"DEBUG: FILE PATH: {os.path.join(base_path, folder_path, filename)}")

#     return os.path.join(base_path, folder_path, filename)

#### commented as of 19 june25 at 11:11 PM till here










#### added as of 19 june25 at 11:11 PM from here

import os

def Document_folder(instance, filename):
    base_path = "Document_folder"

    if instance.student:
        user = instance.student.user

        # ✅ Use correct related_name here
        if instance.student.student_year_levels.exists():
            year_level = instance.student.student_year_levels.first().level.level_name
        else:
            year_level = "unknown_level"

        folder_path = f"student/{year_level}/{user.first_name}_{user.last_name}"

    elif instance.teacher:
        user = instance.teacher.user
        folder_path = f"teacher/{user.first_name}_{user.last_name}"

    elif instance.guardian:
        user = instance.guardian.user
        folder_path = f"guardian/{user.first_name}_{user.last_name}"

    elif instance.office_staff:
        user = instance.office_staff.user
        folder_path = f"office_staff/{user.first_name}_{user.last_name}"

    else:
        folder_path = "unknown"

    # Optional: Debug output
    print(f"DEBUG: ROLE DETECTED: {folder_path.split('/')[0]}")
    print(f"DEBUG: FULL FOLDER PATH: {os.path.join(base_path, folder_path)}")
    print(f"DEBUG: FILE PATH: {os.path.join(base_path, folder_path, filename)}")

    return os.path.join(base_path, folder_path, filename)

#### added as of 19 june25 at 11:11 PM till here

